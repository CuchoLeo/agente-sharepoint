# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [1.0.0] - 2025-01-XX

### Añadido
- ✨ Integración completa con Microsoft Graph API para acceso a SharePoint
- ✨ Sistema de embeddings vectoriales con OpenAI text-embedding-3-small
- ✨ Chat inteligente con GPT-4o-mini
- ✨ Soporte para múltiples formatos: DOCX, PDF, XLSX, PPTX, TXT
- ✨ Extracción de texto con OCR para PDFs escaneados (Tesseract)
- ✨ Carga directa de archivos desde la interfaz web
- ✨ Indexación automática y persistente (index.npy)
- ✨ Interfaz web responsive con Tailwind CSS
- ✨ Sistema de búsqueda semántica por similitud coseno
- ✨ Endpoint de reindexación manual para SharePoint
- ✨ Control de carga con límite de archivos por lote (MAX_FILES_PER_RUN)

### Características Técnicas
- FastAPI como framework web
- Sistema de autenticación con MSAL para Microsoft 365
- Almacenamiento vectorial local con NumPy
- Procesamiento asíncrono de archivos
- Manejo robusto de errores y excepciones

### Seguridad
- Variables de entorno para credenciales sensibles
- No almacenamiento de archivos originales
- Solo embeddings numéricos en el índice

## [Unreleased]

### Planeado
- Autenticación Entra ID para múltiples usuarios
- Soporte para análisis de imágenes con GPT-4 Vision
- Migración a base de datos vectorial (Pinecone/Weaviate/Chroma)
- Historial de conversaciones persistente
- API REST pública para integraciones
- Dashboard de métricas y analytics
- Modo offline con modelos locales
- Soporte multiidioma

---

**Nota**: Las fechas y versiones futuras están sujetas a cambios según el roadmap del proyecto.
