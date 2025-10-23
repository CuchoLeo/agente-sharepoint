# 🤖 CyG Copilot IA - OVAL Agente IA

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-orange.svg)
![License](https://img.shields.io/badge/License-Propietario-red.svg)

**Asistente documental inteligente** desarrollado por **CyG Informática / CyberGuard Chile**, diseñado para integrarse con **Microsoft 365 (SharePoint Online)**. Permite realizar consultas en lenguaje natural sobre documentos corporativos y obtener respuestas contextuales generadas por inteligencia artificial.

---

## 🚀 Inicio Rápido (Quick Start)

```bash
# 1. Clonar el repositorio
git clone https://github.com/CuchoLeo/agente-sharepoint.git
cd agente-sharepoint

# 2. Instalar dependencias del sistema (Ubuntu/Debian)
sudo apt install -y python3 python3-pip python3-venv tesseract-ocr poppler-utils

# 3. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# 4. Instalar dependencias de Python
pip install -r requirements.txt

# 5. Configurar credenciales
cp env.example .env
nano .env  # Editar con tus credenciales

# 6. Ejecutar el servidor
python app.py

# 7. Abrir navegador en http://localhost:8000
```

---

## 📖 Tabla de Contenidos

- [Inicio Rápido](#-inicio-rápido-quick-start)
- [Características Principales](#-características-principales)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación Paso a Paso](#-instalación-paso-a-paso)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [Configuración Avanzada](#-configuración-avanzada)
- [Seguridad](#-seguridad)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Solución de Problemas](#-solución-de-problemas)
- [Roadmap](#-roadmap)
- [Contribuciones](#-contribuciones)
- [Licencia](#-licencia)

---

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

### Diagrama de Arquitectura

```
┌──────────────────────────────────────────────────────────────┐
│                         USUARIO                              │
│              (Navegador Web - Interfaz Chat)                 │
└───────────────────────────┬──────────────────────────────────┘
                            │
                    HTTP/REST API
                            │
┌───────────────────────────▼──────────────────────────────────┐
│                    FASTAPI APPLICATION                       │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │  Chat UI   │  │ File Upload  │  │  Reindex API     │    │
│  │ (Tailwind) │  │   Handler    │  │   Endpoints      │    │
│  └────────────┘  └──────────────┘  └──────────────────┘    │
└───────────────────────────┬──────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐  ┌────────────────┐  ┌──────────────────┐
│ PROCESAMIENTO │  │   EMBEDDINGS   │  │  BÚSQUEDA Y IA   │
│  DE ARCHIVOS  │  │   & VECTORES   │  │                  │
├───────────────┤  ├────────────────┤  ├──────────────────┤
│ • DOCX        │  │ OpenAI         │  │ • GPT-4o-mini    │
│ • PDF (+OCR)  │──▶│ Embeddings     │─▶│ • Cosine Sim.    │
│ • XLSX        │  │ API            │  │ • Context Ret.   │
│ • PPTX        │  │ text-emb-3-sm  │  │ • Answer Gen.    │
│ • TXT         │  │                │  │                  │
└───────┬───────┘  └────────┬───────┘  └─────────▲────────┘
        │                   │                     │
        │                   ▼                     │
        │          ┌────────────────┐             │
        │          │ ALMACENAMIENTO │             │
        │          │   VECTORIAL    │             │
        │          ├────────────────┤             │
        │          │ • index.npy    │─────────────┘
        │          │ • index_log.js │
        │          │ • NumPy Arrays │
        │          └────────────────┘
        │
        ▼
┌────────────────────────────────────────────┐
│          FUENTES DE DATOS                  │
├────────────────────┬───────────────────────┤
│   SharePoint       │   Upload Directo      │
│   (MS Graph API)   │   (Archivos Locales)  │
│                    │                       │
│ • Sites.Read.All   │ • Multipart Upload   │
│ • Files.Read.All   │ • Procesamiento      │
│ • OAuth2/MSAL      │   Inmediato          │
└────────────────────┴───────────────────────┘
```

### Flujo de Datos

#### 1. Indexación de Documentos

```
SharePoint/Upload → Descarga → Extracción de Texto → Chunking (1000 chars)
                                                           ↓
                    ← Persistencia ← Generación de Embeddings
                         (NPY)              (OpenAI API)
```

#### 2. Procesamiento de Consultas

```
Usuario → Pregunta → Embedding → Búsqueda Similitud → Top K Chunks
                                                            ↓
                    ← Respuesta ← GPT-4o-mini ← Contexto + Pregunta
```

### Componentes Principales

| Componente | Tecnología | Función |
|------------|-----------|---------|
| **Frontend** | HTML + Tailwind CSS | Interfaz de usuario responsive |
| **Backend** | FastAPI + Python 3.10+ | API REST y lógica de negocio |
| **Autenticación** | MSAL + OAuth2 | Acceso a Microsoft Graph API |
| **Procesamiento de Docs** | python-docx, PyPDF2, openpyxl, python-pptx | Extracción de texto |
| **OCR** | Tesseract + pdf2image | Texto de PDFs escaneados |
| **Embeddings** | OpenAI text-embedding-3-small | Vectorización semántica |
| **IA Generativa** | OpenAI GPT-4o-mini | Generación de respuestas |
| **Almacenamiento** | NumPy + JSON | Índice vectorial local |
| **Búsqueda** | Cosine Similarity | Recuperación de contexto |

### Características Técnicas

- **Arquitectura**: RESTful API + Server-Side Rendering
- **Concurrencia**: ASGI con Uvicorn
- **Persistencia**: Sistema de archivos local
- **Escalabilidad**: Procesamiento por lotes configurable
- **Seguridad**: Variables de entorno + OAuth2
- **Performance**: Índice en memoria para búsquedas rápidas

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

## 🚀 Instalación Paso a Paso

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/CuchoLeo/agente-sharepoint.git
cd agente-sharepoint
```

### Paso 2: Instalar Dependencias del Sistema

Para Ubuntu/Debian:
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv tesseract-ocr poppler-utils
```

Para macOS:
```bash
brew install python3 tesseract poppler
```

### Paso 3: Crear y Activar Entorno Virtual

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate  # En Linux/macOS
# En Windows usar: venv\Scripts\activate
```

> 💡 **Tip**: Asegúrate de que el prompt de tu terminal muestre `(venv)` al inicio, indicando que el entorno virtual está activo.

### Paso 4: Instalar Dependencias de Python

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Esto instalará las siguientes dependencias:
- `fastapi` - Framework web moderno
- `uvicorn` - Servidor ASGI de alto rendimiento
- `openai` - Cliente oficial de OpenAI
- `msal` - Autenticación Microsoft
- `python-docx`, `PyPDF2`, `openpyxl`, `python-pptx` - Procesamiento de documentos
- `pdf2image`, `pytesseract` - OCR para PDFs escaneados
- `numpy` - Operaciones vectoriales
- `python-dotenv` - Gestión de variables de entorno
- `requests` - Cliente HTTP

### Paso 5: Configurar Credenciales

#### 5.1 Copiar el archivo de ejemplo

```bash
cp env.example .env
```

#### 5.2 Obtener credenciales de OpenAI

1. Ve a [OpenAI Platform](https://platform.openai.com)
2. Accede a tu cuenta o crea una nueva
3. Navega a **API Keys** en el menú lateral
4. Haz clic en **Create new secret key**
5. Copia la clave generada (comienza con `sk-proj-...`)

#### 5.3 Obtener credenciales de Microsoft 365

1. Accede al [Azure Portal](https://portal.azure.com)
2. Ve a **Azure Active Directory** > **App registrations**
3. Haz clic en **New registration**
4. Completa:
   - **Name**: `CyG Copilot IA`
   - **Supported account types**: Selecciona según tu caso
   - **Redirect URI**: Déjalo en blanco por ahora
5. Una vez creada la app, copia:
   - **Application (client) ID**
   - **Directory (tenant) ID**
6. Ve a **Certificates & secrets** > **New client secret**
7. Crea un secreto y copia su **Value**

#### 5.4 Configurar permisos de Microsoft Graph

1. En tu aplicación registrada, ve a **API permissions**
2. Haz clic en **Add a permission**
3. Selecciona **Microsoft Graph** > **Application permissions**
4. Agrega los siguientes permisos:
   - `Sites.Read.All`
   - `Files.Read.All`
5. Haz clic en **Grant admin consent**

#### 5.5 Editar el archivo `.env`

Abre el archivo `.env` con tu editor favorito:

```bash
nano .env  # o usa vim, code, etc.
```

Y completa con tus credenciales:

```env
# OpenAI API Configuration
OPENAI_API_KEY=sk-proj-TU_CLAVE_AQUI

# Microsoft 365 / Graph API Configuration
M365_TENANT_ID=tu-tenant-id-aqui
M365_CLIENT_ID=tu-client-id-aqui
M365_CLIENT_SECRET=tu-client-secret-aqui
```

> ⚠️ **SEGURIDAD CRÍTICA**:
> - **NUNCA** compartas tu archivo `.env`
> - **NUNCA** subas `.env` a repositorios públicos
> - El archivo `.gitignore` ya está configurado para ignorar `.env`
> - Rota tus credenciales regularmente

### Paso 6: Verificar Instalación

```bash
# Verifica que Python y las dependencias estén correctamente instaladas
python --version  # Debe mostrar Python 3.10 o superior
pip list | grep fastapi  # Debe mostrar fastapi instalado
tesseract --version  # Debe mostrar Tesseract instalado
```

## ⚙️ Configuración

### Variables de Entorno

El archivo `.env` contiene todas las credenciales y configuraciones necesarias:

```env
# OpenAI API Configuration
OPENAI_API_KEY=sk-proj-XXXXXXXXXXXX

# Microsoft 365 / Graph API Configuration
M365_TENANT_ID=tu-tenant-id-aqui
M365_CLIENT_ID=tu-client-id-aqui
M365_CLIENT_SECRET=tu-client-secret-aqui
```

### Configuración del Drive de SharePoint

Edita `app.py` línea 38 para configurar el ID de tu drive:

```python
DRIVE_ID = "b!rwJYlL5mUEuss_GKf1rBSELmRer4qdhIv5HsDY3tNOgeIMFwY0seSr-QtklnZZRh"
```

### Configuración de Carpetas Indexables

Por defecto, el sistema está configurado para indexar la carpeta "PRUEBAS". Puedes agregar más carpetas editando `app.py` líneas 54-56:

```python
SHAREPOINT_FOLDERS = {
    "PRUEBAS": "01OUATYK74IICILGLVQBDIXLFNJN6ESTI6",
    "NORMATIVAS": "ID_DE_TU_CARPETA_AQUI",
    "DOCUMENTOS": "ID_DE_TU_CARPETA_AQUI"
}
```

### Parámetros Configurables

En `app.py` puedes ajustar:

| Parámetro | Línea | Valor Default | Descripción |
|-----------|-------|---------------|-------------|
| `EMBED_MODEL` | 44 | `text-embedding-3-small` | Modelo de embeddings de OpenAI |
| `MAX_FILES_PER_RUN` | 47 | `10` | Archivos procesados por lote |
| `INDEX_FILE` | 45 | `index.npy` | Nombre del archivo de índice |
| `INDEX_LOG_FILE` | 46 | `index_log.json` | Log de archivos indexados |

## 📦 Dependencias

### Dependencias del Sistema

- **Python 3.10+**: Lenguaje de programación principal
- **Tesseract OCR**: Reconocimiento óptico de caracteres para PDFs escaneados
- **Poppler**: Herramientas para procesamiento de PDFs

### Dependencias de Python (requirements.txt)

```txt
fastapi>=0.100.0          # Framework web moderno y rápido
uvicorn[standard]>=0.23.0  # Servidor ASGI de alto rendimiento
openai>=1.0.0              # Cliente oficial de OpenAI
msal>=1.25.0               # Microsoft Authentication Library
python-docx>=0.8.11        # Procesamiento de archivos Word
PyPDF2>=3.0.0              # Lectura de archivos PDF
openpyxl>=3.1.0            # Procesamiento de archivos Excel
python-pptx>=0.6.21        # Procesamiento de archivos PowerPoint
pdf2image>=1.16.0          # Conversión de PDF a imágenes
pytesseract>=0.3.10        # Wrapper de Python para Tesseract OCR
numpy>=1.24.0              # Operaciones numéricas y vectoriales
python-dotenv>=1.0.0       # Carga de variables de entorno
requests>=2.31.0           # Cliente HTTP para llamadas API
```

## 🎯 Uso

### Paso 1: Iniciar el Servidor

#### Método 1: Ejecución Estándar

```bash
# Activar el entorno virtual (si no está activo)
source venv/bin/activate

# Iniciar el servidor
uvicorn app:app --host 0.0.0.0 --port 8000
```

#### Método 2: Modo Desarrollo (con auto-reload)

```bash
# Activar el entorno virtual (si no está activo)
source venv/bin/activate

# Iniciar con recarga automática
python app.py
```

> 💡 **Tip**: El modo desarrollo detecta cambios en el código y recarga automáticamente el servidor.

Deberías ver un mensaje similar a:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
```

### Paso 2: Acceder a la Interfaz Web

Abre tu navegador web y accede a:

```
http://localhost:8000
```

O si accedes desde otra máquina en la red:
```
http://IP-DEL-SERVIDOR:8000
```

### Paso 3: Configurar el ID del Drive de SharePoint

Antes de indexar, necesitas configurar el ID del Drive de SharePoint en `app.py`:

```python
# Línea 38 en app.py
DRIVE_ID = "tu-drive-id-aqui"
```

#### ¿Cómo obtener el DRIVE_ID?

**Opción 1: Usando Graph Explorer**
1. Ve a [Graph Explorer](https://developer.microsoft.com/graph/graph-explorer)
2. Inicia sesión con tu cuenta de Microsoft 365
3. Ejecuta: `GET https://graph.microsoft.com/v1.0/sites?search=*`
4. Busca tu sitio de SharePoint en los resultados
5. Ejecuta: `GET https://graph.microsoft.com/v1.0/sites/{site-id}/drives`
6. Copia el `id` del drive que deseas indexar

**Opción 2: Desde la URL de SharePoint**
1. Ve a tu sitio de SharePoint
2. Navega a la biblioteca de documentos
3. La URL tendrá el formato: `https://tenant.sharepoint.com/sites/sitename/Shared%20Documents`
4. Usa Graph API para obtener el drive ID del sitio

### Paso 4: Indexar Documentos de SharePoint

#### Desde la Interfaz Web

1. Haz clic en el **icono de configuración** (engranaje) en la esquina superior derecha
2. Selecciona la carpeta a indexar del menú desplegable (o deja vacío para indexar todo)
3. Haz clic en **Indexar** para indexación incremental
4. O haz clic en **Forzar Todo** para reindexar completamente

#### Desde la API (Navegador o cURL)

**Indexar carpeta específica:**
```bash
curl http://localhost:8000/reindex?folder=PRUEBAS
```

**Indexar sitio completo:**
```bash
curl http://localhost:8000/reindex
```

**Forzar reindexación completa:**
```bash
curl http://localhost:8000/reindex?full=true
```

> ⚠️ **Nota**: Por defecto, el sistema procesa hasta 10 archivos por lote para evitar sobrecarga. Esto se puede ajustar en `app.py` modificando `MAX_FILES_PER_RUN`.

### Paso 5: Cargar Archivos Directamente

Si deseas indexar archivos sin subirlos a SharePoint:

1. En la interfaz web, usa el selector de archivos en la parte inferior
2. Haz clic en **Seleccionar archivo**
3. Elige un archivo compatible: `.pdf`, `.docx`, `.xlsx`, `.pptx`, `.txt`
4. Haz clic en **Cargar e Indexar**
5. Espera la confirmación de indexación exitosa

El sistema automáticamente:
- Extrae el texto del archivo
- Genera embeddings vectoriales
- Actualiza el índice
- Guarda los cambios en `index.npy`

### Paso 6: Realizar Consultas

Escribe tus preguntas en lenguaje natural en el campo de texto en la parte inferior de la interfaz.

#### Ejemplos de Consultas

**Consultas generales:**
```
¿Qué archivos tienes indexados?
¿Qué documentos conoces?
```

**Búsqueda por contenido:**
```
¿Qué establece la Resolución 1705 MC 2022?
Busca información sobre políticas de seguridad
Resume el documento de normativas vigentes
```

**Búsqueda por documento específico:**
```
¿Qué dice el archivo Normativas.docx sobre cumplimiento?
Resume el contenido de Informe_Anual.pdf
```

El sistema utilizará:
- **Búsqueda por nombre**: Si mencionas un archivo específico
- **Búsqueda semántica**: Si haces una pregunta general, buscará los fragmentos más relevantes

### Paso 7: Verificar el Estado del Índice

Puedes verificar el estado del índice revisando los archivos generados:

```bash
# Ver el archivo del índice vectorial
ls -lh index.npy

# Ver el log de archivos indexados
cat index_log.json | python -m json.tool
```

El archivo `index_log.json` contiene metadatos de todos los archivos indexados, incluyendo:
- Ruta del archivo
- ID del archivo en SharePoint
- Fecha de última modificación
- Nombre del archivo

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

## 🔍 Solución de Problemas

### Problema: Error al obtener token de Microsoft Graph

**Síntomas:**
```
❌ Error al obtener token: AADSTS7000215: Invalid client secret provided
```

**Solución:**
1. Verifica que las credenciales en `.env` sean correctas
2. Asegúrate de haber copiado el **Value** del secret, no el **Secret ID**
3. Verifica que el secreto no haya expirado en Azure Portal
4. Regenera el secreto si es necesario

### Problema: No se pueden indexar archivos de SharePoint

**Síntomas:**
```
❌ Error al conectar con SharePoint: 403 Forbidden
```

**Solución:**
1. Verifica que hayas configurado los permisos de Microsoft Graph correctamente
2. Asegúrate de haber otorgado **admin consent** a los permisos
3. Verifica que el `DRIVE_ID` sea correcto
4. Espera unos minutos después de otorgar permisos (pueden tardar en propagarse)

### Problema: Error de OCR en PDFs escaneados

**Síntomas:**
```
TesseractNotFoundError: tesseract is not installed
```

**Solución:**
```bash
# Ubuntu/Debian
sudo apt install tesseract-ocr tesseract-ocr-spa

# macOS
brew install tesseract tesseract-lang

# Verificar instalación
tesseract --version
```

### Problema: Memoria insuficiente al indexar

**Síntomas:**
```
MemoryError: Unable to allocate array
```

**Solución:**
1. Reduce el valor de `MAX_FILES_PER_RUN` en `app.py`:
```python
MAX_FILES_PER_RUN = 5  # Reduce de 10 a 5
```

2. Configura swap (Linux):
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Problema: Dependencias de Python no se instalan

**Síntomas:**
```
ERROR: Could not find a version that satisfies the requirement...
```

**Solución:**
```bash
# Actualizar pip
pip install --upgrade pip setuptools wheel

# Reinstalar dependencias
pip install -r requirements.txt --no-cache-dir
```

### Problema: Puerto 8000 ya en uso

**Síntomas:**
```
ERROR: [Errno 48] Address already in use
```

**Solución:**
```bash
# Opción 1: Usar otro puerto
uvicorn app:app --host 0.0.0.0 --port 8080

# Opción 2: Liberar el puerto (Linux/macOS)
lsof -ti:8000 | xargs kill -9
```

### Problema: No aparece la imagen OVAL

**Síntomas:**
La interfaz web no muestra la imagen del logo.

**Solución:**
1. Verifica que exista el archivo `oval.jpg` en el directorio raíz del proyecto
2. Asegúrate de que el servidor tenga acceso de lectura al archivo:
```bash
ls -la oval.jpg
chmod 644 oval.jpg  # Si es necesario
```

### Problema: Error al procesar archivos Excel

**Síntomas:**
```
BadZipFile: File is not a zip file
```

**Solución:**
- Asegúrate de que el archivo sea realmente un `.xlsx` válido
- Verifica que el archivo no esté corrupto
- Intenta abrir y guardar el archivo nuevamente en Excel

### Obtener Ayuda Adicional

Si encuentras un problema no listado aquí:

1. Revisa los logs del servidor en la terminal
2. Verifica el archivo `index_log.json` para diagnóstico
3. Consulta la [documentación de Microsoft Graph API](https://docs.microsoft.com/graph)
4. Consulta la [documentación de OpenAI](https://platform.openai.com/docs)

## 🤝 Contribuciones

Este es un proyecto propietario de CyG Informática. Para consultas sobre licenciamiento o colaboraciones, contactar a:

**Eugenio Castro** – CTO CyG Informática
📧 ecastro@cyberguard.cl
📱 +56 9 3097 8947
🌐 [cyginformatica.cl](https://cyginformatica.cl)

## 📄 Licencia

Copyright © 2025 CyG Informática / CyberGuard Chile. Todos los derechos reservados.

Este software es propietario y su uso requiere autorización explícita de CyG Informática.

## 🙏 Agradecimientos

- Equipo CyG IA / CyberGuard Chile
- OpenAI por GPT-4o-mini y embeddings
- Microsoft Graph API
- Comunidad open source de FastAPI y Python

---

**Desarrollado con ❤️ por CyG Informática**
