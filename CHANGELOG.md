# Changelog — PDF2Excel Pro

Todas las modificaciones notables del proyecto se documentan aquí.

---

### [2026-03-12 15:05] — Creación Inicial del Proyecto
- **Añadido:** Estructura base del proyecto (`app.py`, `libs/extractor.py`, `libs/excel_engine.py`).
- **Añadido:** Extracción de tablas PDF con `pdfplumber`.
- **Añadido:** Interfaz Streamlit con diseño premium (Glassmorphism, Dark Mode).
- **Añadido:** Exportación de Excel con cabeceras de colores, zebra striping y ajuste automático de columnas.
- **Añadido:** Filtros dinámicos, selección de columnas y ordenamiento flexible.
- **Técnico:** Dependencias iniciales: `streamlit`, `pdfplumber`, `pandas`, `openpyxl`, `xlsxwriter`.

---

### [2026-03-12 16:37] — Selector de Rango de Páginas
- **Añadido:** Conteo instantáneo de páginas al subir un PDF.
- **Añadido:** Selector de página inicial y página final para procesamiento parcial.
- **Añadido:** Botón explícito "Iniciar Extracción Estructurada".
- **Modificado:** `extractor.py` → parámetros `start_page` y `end_page`.

---

### [2026-03-12 16:57] — Cronómetro de Tiempo Real
- **Añadido:** Barra de progreso visual y cronómetro dinámico.
- **Modificado:** `extractor.py` → patrón generador (`extract_tables_generator`).

---

### [2026-03-12 17:04] — Motor Híbrido Inteligente
- **Añadido:** `PyMuPDF (fitz)` como motor de alta velocidad.
- **Añadido:** Conmutación automática: >10MB = PyMuPDF, <10MB = pdfplumber.
- **Añadido:** Indicador visual "🚀 MODO TURBO" / "💎 MODO PRECISIÓN".

---

### [2026-03-12 17:11] — Corrección de Columnas Duplicadas
- **Corregido:** `ValueError: Duplicate column names found`.
- **Añadido:** Desduplicación automática de nombres de columna.

---

### [2026-03-12 17:21] — Detección Agresiva de Tablas PAC
- **Modificado:** Estrategia escalonada en PyMuPDF (`lines_strict` → `lines` → `text`).

---

### [2026-03-15 14:07] — Documentación Completa (Fase 1)
- **Añadido:** `README.md` y `CHANGELOG.md`.

---

### [2026-03-15 14:28] — Módulo de Análisis BI (Fase 2)
- **Añadido:** Arquitectura multi-página Streamlit (`st.navigation`).
- **Añadido:** `modules/data_manager.py` — Carga unificada PDF/Excel/CSV + persistencia Firebase Firestore.
- **Añadido:** `modules/chart_builder.py` — Fábrica de gráficos Plotly con tema Dark Mode OLED.
- **Añadido:** `modules/analytics_engine.py` — Tablas dinámicas, correlaciones, proyecciones lineales, outliers.
- **Añadido:** `pages/1_Extractor_PDF.py` — Migración del extractor como página independiente.
- **Añadido:** `pages/2_Dashboard_BI.py` — Dashboard con KPIs, segmentadores, gráficos interactivos.
- **Añadido:** `pages/3_Analisis.py` — Análisis avanzado: stats, pivots, correlaciones, proyecciones, outliers.
- **Añadido:** `pages/4_Reportes.py` — Generación de reportes Excel multi-hoja automatizados.
- **Añadido:** Proyecto Firebase `pdf2excel-bi-module` con Firestore.
- **Añadido:** App web Firebase (`PDF2Excel BI Web`).
- **Técnico:** Nuevas dependencias: `plotly`, `kaleido`, `pymongo`, `firebase-admin`.
