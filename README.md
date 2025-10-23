# CyG Copilot IA 🤖

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-orange.svg)
![License](https://img.shields.io/badge/License-Propietario-red.svg)

Asistente documental inteligente desarrollado por **CANON Informática Chile**, diseñado para integrarse con Microsoft 365 (SharePoint Online). Permite realizar consultas en lenguaje natural sobre documentos corporativos y obtener respuestas contextuales generadas por inteligencia artificial.

## ✨ Características Principales

- 🔍 **Búsqueda Semántica**: Utiliza embeddings vectoriales (OpenAI text-embedding-3-small) para encontrar información relevante
- 📚 **Soporte Múltiple de Formatos**: DOCX, PDF, XLSX, PPTX, TXT con extracción inteligente de texto
- 🔗 **Integración Microsoft 365**: Acceso directo a documentos en SharePoint Online vía Microsoft Graph API
- 💬 **Chat Inteligente**: Interfaz conversacional con respuestas contextuales generadas por GPT-4o-mini
- 📤 **Carga de Archivos**: Indexación en tiempo real de documentos cargados directamente
- 🔄 **OCR Integrado**: Extracción de texto de PDFs escaneados usando Tesseract
- 💾 **Índice Persistente**: Sistema de almacenamiento vectorial local (NumPy) para consultas rápidas
- 🎨 **Interfaz Moderna**: UI responsive con Tailwind CSS

## 🏗️ Arquitectura del Sistema

```
┌─────────────┐
│   Usuario   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│   FastAPI Web Interface         │
│   • Chat UI (Tailwind CSS)      │
│   • File Upload                 │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│   Embeddings & Search Engine    │
│   • text-embedding-3-small      │
│   • Similarity Search (cosine)  │
│   • index.npy (vector store)    │
└────────┬────────────────────────┘
         │
         ├──────────────┬──────────────┐
         ▼              ▼              ▼
┌───────────────┐  ┌──────────┐  ┌──────────────┐
│  SharePoint   │  │  OpenAI  │  │ File Upload  │
│  (Graph API)  │  │  GPT-4o  │  │  (Direct)    │
└───────────────┘  └──────────┘  └──────────────┘
```

## 📋 Requisitos Previos

### Sistema
- Ubuntu Server 22.04 o superior (también compatible con otras distribuciones Linux)
- Python 3.10+
- Acceso a un tenant Microsoft 365 con permisos de Graph API
- Clave API activa de OpenAI

### Dependencias del Sistema
```bash
sudo apt update
sudo apt install tesseract-ocr poppler-utils -y
```

## 🚀 Instalación

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/cyg-copilot-ia.git
cd cyg-copilot-ia
```

### 2. Crear Entorno Virtual
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
Crear un archivo `.env` en la raíz del proyecto:

```env
# OpenAI API
OPENAI_API_KEY=sk-proj-XXXXXXXXXXXX

# Microsoft 365 Credentials
M365_TENANT_ID=70050740-2bb1-46d9-ad67-9800a0d00fe0
M365_CLIENT_ID=46b2c06f-9639-4a1f-8d83-8f6bbe442caa
M365_CLIENT_SECRET=LGh8Q~XXXXXXXXXXXX
```

> ⚠️ **IMPORTANTE**: Nunca subir el archivo `.env` a repositorios públicos. Añadir `.env` al `.gitignore`.

## 📦 Dependencias (requirements.txt)

```txt
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
openai>=1.0.0
msal>=1.25.0
python-docx>=0.8.11
PyPDF2>=3.0.0
openpyxl>=3.1.0
python-pptx>=0.6.21
pdf2image>=1.16.0
pytesseract>=0.3.10
numpy>=1.24.0
python-dotenv>=1.0.0
requests>=2.31.0
```

## 🎯 Uso

### Ejecutar el Servidor

```bash
source venv/bin/activate
uvicorn app:app --host 0.0.0.0 --port 8000
```

O con recarga automática para desarrollo:
```bash
python app.py
```

Acceder desde el navegador:
```
http://localhost:8000
```

### Reindexar Documentos de SharePoint

**Reindexar carpeta específica:**
```
http://localhost:8000/reindex?folder=NORMATIVAS
```

**Reindexar sitio completo** (limitado a 5 archivos por lote):
```
http://localhost:8000/reindex
```

El índice generado se guarda automáticamente en `index.npy`.

### Cargar Archivos Directamente

1. Usar el botón "Cargar e Indexar" en la interfaz web
2. Seleccionar archivo (DOCX, PDF, XLSX, PPTX, TXT)
3. El sistema extrae texto, genera embeddings y actualiza el índice automáticamente

### Realizar Consultas

Escribir preguntas en lenguaje natural, por ejemplo:
- "¿Qué establece la Resolución 1705 MC 2022?"
- "Busca información sobre políticas de seguridad"
- "Resume el documento de normativas vigentes"

## 🔧 Configuración Avanzada

### Ajustar Límite de Archivos por Indexación

En `app.py`, modificar:
```python
MAX_FILES_PER_RUN = 5  # Cambiar según recursos disponibles
```

### Configurar Swap (Recomendado para Servidores con RAM Limitada)

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Script de Reindexación Automática

Crear `rebuild.sh`:
```bash
#!/bin/bash
cd /path/to/project
source venv/bin/activate
python3 - <<'EOF'
from app import build_sharepoint_index
build_sharepoint_index("01OUATYK2D4K7NSQKVUFGLSNPA63BXLWBV")
EOF
deactivate
```

Ejecutar:
```bash
chmod +x rebuild.sh
./rebuild.sh
```

## 🔐 Seguridad

- ✅ Todas las credenciales se almacenan en `.env` y no se versionan
- ✅ No se almacenan archivos del cliente, solo embeddings numéricos
- ✅ Cumple con políticas de seguridad de Microsoft 365
- ✅ Puede extenderse con autenticación Entra ID
- ✅ Conexiones seguras vía HTTPS (recomendado en producción)

## 📊 Estructura del Proyecto

```
cyg-copilot-ia/
├── app.py                  # Backend principal (FastAPI)
├── .env                    # Variables de entorno (NO versionar)
├── .gitignore              # Archivos ignorados por Git
├── requirements.txt        # Dependencias Python
├── index.npy              # Índice vectorial (generado automáticamente)
├── rebuild.sh             # Script de reindexación automática
├── README.md              # Documentación del proyecto
└── Documentacion_tecnica.docx  # Documentación adicional
```

## 🚦 Estados del Sistema

| Componente | Estado | Descripción |
|------------|--------|-------------|
| FastAPI Server | ✅ | API REST funcional |
| OpenAI Integration | ✅ | GPT-4o-mini + text-embedding-3-small |
| MS Graph API | ✅ | Acceso a SharePoint |
| File Upload | ✅ | Indexación en tiempo real |
| OCR Support | ✅ | Tesseract para PDFs escaneados |
| Vector Search | ✅ | Búsqueda semántica con NumPy |

## 🛣️ Roadmap

- [ ] Autenticación Entra ID para múltiples usuarios
- [ ] Soporte para imágenes y análisis visual con GPT-4 Vision
- [ ] Base de datos vectorial (Pinecone, Weaviate, Chroma)
- [ ] Historial de conversaciones por usuario
- [ ] API de integración para terceros
- [ ] Soporte para más idiomas
- [ ] Dashboard de métricas y uso
- [ ] Modo offline con modelos locales

## 📈 Métricas de Ejemplo

- **Capacidad de indexación**: ~5 archivos por ciclo (configurable)
- **Tiempo de respuesta**: ~2-4 segundos por consulta
- **Precisión de búsqueda**: >85% en documentos técnicos
- **Formatos soportados**: 5 tipos (DOCX, PDF, XLSX, PPTX, TXT)


Este software es propietario y su uso requiere autorización explícita de CANON.


