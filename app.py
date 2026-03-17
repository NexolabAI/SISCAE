"""
PDF2Excel Pro — Módulo de Análisis BI
Entry Point con navegación multi-página.
"""
import streamlit as st

# ─── CONFIGURACIÓN DE PÁGINA ───────────────────────────────────

st.set_page_config(
    page_title="PDF2Excel Pro — BI Module",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── ESTILOS PREMIUM (OLED Dark Mode) ─────────────────────────

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Fira+Sans:wght@300;400;500;600;700&display=swap');

    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    [data-testid="stSidebar"] {
        background: #0f172a;
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    h1, h2, h3 {
        font-family: 'Fira Code', monospace !important;
        color: #3b82f6 !important;
    }
    p, span, label, .stMarkdown {
        font-family: 'Fira Sans', sans-serif !important;
    }
    .stButton>button {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
        font-weight: 600;
        cursor: pointer;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.5);
    }
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 8px 20px;
        background-color: rgba(255,255,255,0.05);
    }
    .stMetric {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# ─── NAVEGACIÓN ────────────────────────────────────────────────

# Definir las páginas
extractor_page = st.Page("pages/1_Extractor_PDF.py", title="Extractor PDF", icon="📄")
dashboard_page = st.Page("pages/2_Dashboard_BI.py", title="Dashboard BI", icon="📊")
analysis_page = st.Page("pages/3_Analisis.py", title="Análisis Avanzado", icon="🔬")
reports_page = st.Page("pages/4_Reportes.py", title="Reportes", icon="📋")

pg = st.navigation([extractor_page, dashboard_page, analysis_page, reports_page])
pg.run()
