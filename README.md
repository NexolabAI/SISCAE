# 📊 PDF2Excel Pro — Business Intelligence Module

Plataforma de análisis de datos construida con Python y Streamlit que combina extracción de PDF, visualización interactiva (Plotly), tablas dinámicas, proyecciones y automatización de reportes. Persistencia en Firebase Firestore.

---

## ✨ Capacidades

| Módulo | Descripción |
|---|---|
| **📄 Extractor PDF** | Motor híbrido (pdfplumber + PyMuPDF) con selector de rango y cronómetro |
| **📊 Dashboard BI** | KPIs, gráficos Plotly interactivos, segmentadores (slicers) y filtrado cruzado |
| **🔬 Análisis Avanzado** | Tablas dinámicas, correlaciones, proyecciones lineales, detección de outliers |
| **📋 Reportes** | Generación automatizada de Excel multi-hoja con metadata |
| **💾 Persistencia** | Firebase Firestore para almacenar y recuperar datasets masivos |

---

## 🏗️ Arquitectura

```
PDF_Excel/
├── app.py                        # Entry point (navegación multi-página)
├── pages/
│   ├── 1_Extractor_PDF.py        # Extracción PDF con motor híbrido
│   ├── 2_Dashboard_BI.py         # Dashboard con KPIs, Plotly, slicers
│   ├── 3_Analisis.py             # Estadísticas, pivots, correlaciones
│   └── 4_Reportes.py             # Reportes Excel multi-hoja
├── modules/
│   ├── data_manager.py           # Carga unificada + Firebase Firestore
│   ├── chart_builder.py          # Fábrica de gráficos Plotly (Dark Mode)
│   └── analytics_engine.py       # Motor estadístico y proyecciones
├── libs/
│   ├── extractor.py              # Motor híbrido PDF (PyMuPDF + pdfplumber)
│   └── excel_engine.py           # Generador Excel premium (XlsxWriter)
├── design-system/                # Tokens de diseño (MASTER.md)
├── firebase.json                 # Config Firebase
├── firestore.rules               # Reglas Firestore
├── CHANGELOG.md                  # Historial de cambios
└── README.md                     # Este archivo
```

---

## 🚀 Instalación y Ejecución

### Requisitos
- Python 3.10+

### 1. Instalar Dependencias

```powershell
pip install streamlit pdfplumber pandas openpyxl xlsxwriter pymupdf plotly kaleido firebase-admin pymongo
```

### 2. Ejecutar

```powershell
python -m streamlit run app.py
```

Abre en `http://localhost:8501`

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología |
|---|---|
| UI | Streamlit (Multi-página) |
| Gráficos | Plotly (Dark Mode OLED) |
| Extracción PDF | PyMuPDF + pdfplumber |
| Análisis | Pandas + NumPy |
| Excel | XlsxWriter |
| Persistencia | Firebase Firestore |
| Tipografía | Fira Code + Fira Sans |

---

## 🔥 Firebase

- **Proyecto:** `pdf2excel-bi-module`
- **Servicio:** Firestore (base de datos NoSQL)
- **Almacenamiento:** Datasets en chunks de 500 filas
- **Autenticación:** ADC (Application Default Credentials)

---

## 📄 Licencia

Proyecto interno. Protocolo Aquiles V 3.4.
