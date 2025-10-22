# -*- coding: utf-8 -*-
import os
import io
import base64
import requests
import mimetypes
import numpy as np
import json
import time
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from openai import OpenAI
from msal import ConfidentialClientApplication
from docx import Document
from PyPDF2 import PdfReader
from pptx import Presentation
from openpyxl import load_workbook
from pdf2image import convert_from_bytes
from pytesseract import image_to_string

# ======================================================
# CONFIGURACIÓN INICIAL
# ======================================================
load_dotenv()
app = FastAPI()

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
M365_TENANT_ID = os.getenv("M365_TENANT_ID")
M365_CLIENT_ID = os.getenv("M365_CLIENT_ID")
M365_CLIENT_SECRET = os.getenv("M365_CLIENT_SECRET")

client = OpenAI(api_key=OPENAI_KEY)
emb_client = OpenAI(api_key=OPENAI_KEY)
EMBED_MODEL = "text-embedding-3-small"
INDEX_FILE = "index.npy"
DRIVE_ID = "b!rwJYlL5mUEuss_GKf1rBSELmRer4qdhIv5HsDY3tNOgeIMFwY0seSr-QtklnZZRh"

# Limitar cantidad de archivos por lote (evita caídas por RAM)
MAX_FILES_PER_RUN = 5

# ======================================================
# AUTENTICACIÓN GRAPH
# ======================================================
def get_graph_token():
    app_msal = ConfidentialClientApplication(
        M365_CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{M365_TENANT_ID}",
        client_credential=M365_CLIENT_SECRET
    )
    token = app_msal.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    return token["access_token"]

# ======================================================
# LECTURA RECURSIVA DE SHAREPOINT
# ======================================================
def list_sharepoint_files(folder_id=None):
    """Lista archivos (recursivo) dentro de una carpeta o raíz"""
    token = get_graph_token()
    headers = {"Authorization": f"Bearer {token}"}
    if folder_id:
        url = f"https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{folder_id}/children"
    else:
        url = f"https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/root/children"

    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print(f"Error al listar archivos ({r.status_code})")
        return []
    items = r.json().get("value", [])
    files = []
    for item in items:
        if "file" in item:
            files.append(item)
        elif "folder" in item:
            sub = list_sharepoint_files(item["id"])
            files.extend(sub)
    return files

# ======================================================
# LECTURA Y EXTRACCIÓN DE TEXTO
# ======================================================
def read_file_content(file_id, file_name):
    """Lee contenido de un archivo en SharePoint"""
    token = get_graph_token()
    meta = requests.get(
        f"https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{file_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    if meta.status_code != 200:
        return ""
    info = meta.json()
    download_url = info.get("@microsoft.graph.downloadUrl")
    if not download_url:
        return ""
    file_bytes = requests.get(download_url).content
    
    # --- Se reutiliza la lógica de extracción en una función separada ---
    return extract_text_from_bytes(file_bytes, file_name)

# --- NUEVO ---
# Función para procesar un archivo subido directamente
async def process_uploaded_file(file: UploadFile):
    """Extrae texto de un objeto UploadFile de FastAPI"""
    file_bytes = await file.read()
    file_name = file.filename
    return extract_text_from_bytes(file_bytes, file_name)

# --- NUEVO ---
# Lógica de extracción de texto, ahora en una función reutilizable
def extract_text_from_bytes(file_bytes, file_name):
    """Extrae texto de bytes de archivo según su tipo (PDF, DOCX, etc.)"""
    text = ""
    try:
        if file_name.lower().endswith(".pdf"):
            try:
                reader = PdfReader(io.BytesIO(file_bytes))
                text = "\n".join([page.extract_text() or "" for page in reader.pages])
                if not text.strip():
                    raise ValueError("PDF vacío, usar OCR")
            except Exception:
                pages = convert_from_bytes(file_bytes)
                text = "\n".join([image_to_string(p) for p in pages])
        elif file_name.lower().endswith(".docx"):
            doc = Document(io.BytesIO(file_bytes))
            text = "\n".join([p.text for p in doc.paragraphs])
        elif file_name.lower().endswith((".xlsx", ".xls")):
            wb = load_workbook(io.BytesIO(file_bytes), data_only=True)
            for sheet in wb.sheetnames:
                ws = wb[sheet]
                text += f"\n--- Hoja: {sheet} ---\n"
                for row in ws.iter_rows(values_only=True):
                    text += " | ".join([str(c) if c else "" for c in row]) + "\n"
        elif file_name.lower().endswith(".pptx"):
            prs = Presentation(io.BytesIO(file_bytes))
            for i, slide in enumerate(prs.slides, 1):
                text += f"\n--- Diapositiva {i} ---\n"
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        text += shape.text + "\n"
        else:
            text = file_bytes.decode("utf-8", errors="ignore")
    except Exception as e:
        text = f"[Error leyendo {file_name}: {e}]"

    return text[:12000]

# ======================================================
# INDEXADOR CONTROLADO (para evitar OOM)
# ======================================================
doc_chunks = []

def save_index():
    np.save(INDEX_FILE, doc_chunks, allow_pickle=True)

def load_index():
    global doc_chunks
    if os.path.exists(INDEX_FILE):
        doc_chunks[:] = np.load(INDEX_FILE, allow_pickle=True).tolist()
        print(f"📂 Índice cargado desde disco: {len(doc_chunks)} fragmentos.")
    else:
        print("⚠️ No se encontró índice local, generar con /reindex o subiendo un archivo.")

def build_sharepoint_index(folder_id=None):
    """Genera embeddings con control de carga desde SharePoint"""
    global doc_chunks
    doc_chunks = []
    files = list_sharepoint_files(folder_id)
    total_files = len(files)
    print(f"📁 Total archivos detectados en SharePoint: {total_files}")

    for i, f in enumerate(files[:MAX_FILES_PER_RUN], start=1):
        if "file" not in f:
            continue
        if not any(f["name"].lower().endswith(ext) for ext in [".docx", ".pdf", ".txt", ".xlsx", ".pptx"]):
            continue

        text = read_file_content(f["id"], f["name"])
        if not text.strip():
            continue

        print(f"📄 ({i}/{total_files}) Indexando desde SP: {f['name']} ({len(text)} caracteres)")
        for chunk in [text[i:i+1000] for i in range(0, len(text), 1000)]:
            try:
                vec = emb_client.embeddings.create(model=EMBED_MODEL, input=chunk).data[0].embedding
                doc_chunks.append({"text": chunk, "embedding": np.array(vec), "source": f["name"]})
            except Exception as e:
                print(f"❌ Error generando embedding para {f['name']}: {e}")
        time.sleep(0.2)  # pausa ligera entre documentos

    print(f"📚 Index generado con {len(doc_chunks)} fragmentos.")
    save_index()

def search_similar_chunks(query, top_k=3):
    if not doc_chunks:
        load_index()
        if not doc_chunks:
            print("⚠️ Índice vacío, generar nuevamente.")
            return []
    q_emb = emb_client.embeddings.create(model=EMBED_MODEL, input=query).data[0].embedding
    q_emb = np.array(q_emb)
    sims = [
        (np.dot(q_emb, d["embedding"]) / (np.linalg.norm(q_emb) * np.linalg.norm(d["embedding"])), d)
        for d in doc_chunks
    ]
    sims.sort(key=lambda x: x[0], reverse=True)
    return [d["text"] for _, d in sims[:top_k]]

# ======================================================
# MOTOR IA MEJORADO (respuestas inteligentes)
# ======================================================
def ask_openai(question, image_bytes=None):
    context_snippets = search_similar_chunks(question)
    context_text = "\n\n".join(context_snippets).strip()

    if not context_text:
        context_text = (
            "No se encontró información directa en los documentos indexados. "
            "Sin embargo, responde de forma útil y basada en conocimiento técnico general, "
            "sugiriendo posibles fuentes o documentos donde el usuario podría buscar la información."
        )

    messages = [
        {
            "role": "system",
            "content": (
                "Eres CyG Copilot IA, un asistente técnico y documental para empresas. "
                "Responde con claridad y profesionalismo, basándote en los documentos indexados "
                "de SharePoint u otras fuentes internas. Si no hay información suficiente, "
                "explica el contexto probable, sugiere qué documentos podrían contener la respuesta "
                "y entrega una orientación práctica al usuario."
            ),
        },
        {"role": "system", "content": f"Contexto documental:\n{context_text}"},
        {"role": "user", "content": question},
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.5,
        max_tokens=400
    )

    return response.choices[0].message.content

# ======================================================
# INTERFAZ WEB
# ======================================================
@app.get("/", response_class=HTMLResponse)
def index():
    # --- MODIFICADO --- Se añade un segundo formulario para la carga de archivos.
    return """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>CyG Copilot IA</title>
<script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 flex flex-col items-center min-h-screen p-4">
<div class="bg-white shadow-lg rounded-2xl w-full max-w-3xl flex flex-col h-[90vh]">
    <div class="p-4 border-b bg-orange-600 text-white rounded-t-2xl">
        <h2 class="text-xl font-bold">CyG Copilot IA</h2>
        <p class="text-xs opacity-80">Integrado con Microsoft 365 | Demo OVAL</p>
    </div>
    <div id="chatBox" class="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50"></div>
    
    <form id="uploadForm" class="p-4 border-t flex items-center gap-2 bg-gray-100">
        <input id="file" name="file" type="file" class="flex-1 text-sm text-slate-500
            file:mr-4 file:py-2 file:px-4
            file:rounded-full file:border-0
            file:text-sm file:font-semibold
            file:bg-orange-50 file:text-orange-700
            hover:file:bg-orange-100" required>
        <button type="submit" class="bg-gray-600 hover:bg-gray-700 text-white font-semibold px-4 py-2 rounded-lg transition">Cargar e Indexar</button>
    </form>
    
    <form id="chatForm" class="p-4 border-t flex items-center gap-2 bg-white">
        <input id="question" name="question" class="flex-1 border rounded-lg p-2 text-sm focus:ring-orange-500 focus:border-orange-500" placeholder="Escribe tu pregunta aquí..." required>
        <button type="submit" class="bg-orange-600 hover:bg-orange-700 text-white font-semibold px-4 py-2 rounded-lg transition">Enviar</button>
    </form>
</div>
<script>
const chatForm = document.getElementById('chatForm');
const uploadForm = document.getElementById('uploadForm');
const chatBox = document.getElementById('chatBox');

// --- NUEVO --- Lógica para el formulario de carga
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(uploadForm);
    const fileInput = document.getElementById('file');
    if (!fileInput.files || fileInput.files.length === 0) {
        alert("Por favor, selecciona un archivo para cargar.");
        return;
    }
    const userBubble = document.createElement('div');
    userBubble.className = 'text-center text-sm text-gray-500 p-2';
    userBubble.innerText = `Cargando archivo: ${fileInput.files[0].name}`;
    chatBox.appendChild(userBubble);
    uploadForm.reset();
    chatBox.scrollTop = chatBox.scrollHeight;

    const res = await fetch('/upload', { method: 'POST', body: formData });
    const html = await res.text();
    const botBubble = document.createElement('div');
    botBubble.className = 'bg-green-100 text-green-800 p-3 rounded-lg text-sm text-center';
    botBubble.innerHTML = html;
    chatBox.appendChild(botBubble);
    chatBox.scrollTop = chatBox.scrollHeight;
});

// Lógica para el formulario de chat (existente)
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(chatForm);
    const question = formData.get('question');
    const userBubble = document.createElement('div');
    userBubble.className = 'bg-orange-100 p-3 rounded-lg self-end text-right text-gray-800 ml-auto max-w-lg';
    userBubble.innerText = question;
    chatBox.appendChild(userBubble);
    chatForm.reset();
    chatBox.scrollTop = chatBox.scrollHeight;
    
    const thinking = document.createElement('div');
    thinking.className = 'text-sm text-gray-400 italic';
    thinking.innerText = 'Pensando...';
    chatBox.appendChild(thinking);
    
    const res = await fetch('/ask', { method: 'POST', body: formData });
    const html = await res.text();
    thinking.remove();
    
    const botBubble = document.createElement('div');
    botBubble.className = 'bg-gray-200 p-3 rounded-lg text-gray-800 max-w-lg';
    botBubble.innerHTML = html;
    chatBox.appendChild(botBubble);
    chatBox.scrollTop = chatBox.scrollHeight;
});
</script>
</body>
</html>"""

@app.post("/ask", response_class=HTMLResponse)
async def ask(question: str = Form(...)):
    reply = ask_openai(question)
    return f"<p class='whitespace-pre-line'>{reply}</p>"

@app.get("/reindex", response_class=HTMLResponse)
def reindex(folder: str = None):
    folder_id = None
    if folder and folder.upper() == "NORMATIVAS":
        folder_id = "01OUATYK2D4K7NSQKVUFGLSNPA63BXLWBV"
    build_sharepoint_index(folder_id)
    return f"<h3>✅ Índice regenerado desde SharePoint para carpeta '{folder or 'completa'}'.</h3><p>Procesados hasta {MAX_FILES_PER_RUN} archivos por lote.</p>"

# --- NUEVO ---
# Endpoint para manejar la carga de archivos
@app.post("/upload", response_class=HTMLResponse)
async def upload(file: UploadFile = File(...)):
    global doc_chunks
    if not file:
        return "<h3>❌ No se seleccionó ningún archivo.</h3>"

    print(f"📥 Archivo recibido: {file.filename}")
    text = await process_uploaded_file(file)
    
    if not text.strip() or "[Error leyendo" in text:
        return f"<h3>⚠️ No se pudo extraer texto del archivo '{file.filename}'.</h3><p>{text}</p>"

    # Generar embeddings para el nuevo contenido y añadirlo al índice
    new_chunks_count = 0
    for chunk in [text[i:i+1000] for i in range(0, len(text), 1000)]:
        try:
            vec = emb_client.embeddings.create(model=EMBED_MODEL, input=chunk).data[0].embedding
            doc_chunks.append({"text": chunk, "embedding": np.array(vec), "source": file.filename})
            new_chunks_count += 1
        except Exception as e:
            print(f"❌ Error generando embedding para {file.filename}: {e}")
    
    if new_chunks_count > 0:
        save_index()
        print(f"✅ Archivo '{file.filename}' indexado en {new_chunks_count} fragmentos.")
        return f"<h3>✅ Archivo '{file.filename}' indexado correctamente.</h3><p>Añadidos {new_chunks_count} nuevos fragmentos al conocimiento del asistente.</p>"
    else:
        return f"<h3>⚠️ No se generaron fragmentos para el archivo '{file.filename}'. Puede que esté vacío o no sea soportado.</h3>"

# ======================================================
# MAIN
# ======================================================
if __name__ == "__main__":
    load_index()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)