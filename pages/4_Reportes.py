"""
Página 4: Reportes Automatizados
Generación y descarga de reportes multi-hoja con gráficos embebidos.
"""
import streamlit as st
import pandas as pd
import base64
import io
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_manager import DataManager
from modules.analytics_engine import AnalyticsEngine
from libs.excel_engine import ExcelEngine

st.title("📋 Reportes Automatizados")
st.caption("Generación de reportes ejecutivos multi-hoja con métricas y resúmenes")

dm = DataManager()
ae = AnalyticsEngine()

# ─── VERIFICAR DATOS ──────────────────────────────────────────

df = st.session_state.get("bi_df", st.session_state.get("raw_df", None))

if df is None or (hasattr(df, 'empty') and df.empty):
    st.warning("No hay datos cargados. Ve al **Dashboard BI** o al **Extractor PDF** para cargar datos primero.")
    st.stop()

num_cols = dm.get_numeric_columns(df)
cat_cols = dm.get_categorical_columns(df)

st.markdown("### Configuración del Reporte")

# ─── OPCIONES DEL REPORTE ─────────────────────────────────────

col1, col2 = st.columns(2)

with col1:
    report_name = st.text_input("Nombre del reporte", "Reporte_Ejecutivo")
    include_raw = st.checkbox("Incluir datos crudos", value=True)
    include_stats = st.checkbox("Incluir estadísticas descriptivas", value=True)
    include_summary = st.checkbox("Incluir resumen por categorías", value=True)

with col2:
    header_color = st.color_picker("Color de cabecera", "#1E40AF")
    font_color = st.color_picker("Color de fuente", "#FFFFFF")

    if cat_cols:
        summary_col = st.selectbox("Columna de resumen categórico", cat_cols)
    if num_cols:
        summary_value = st.selectbox("Valor a resumir", num_cols)

# ─── PREVIEW ──────────────────────────────────────────────────

st.markdown("### 🔎 Preview del Reporte")

tabs = []
tab_names = []

if include_raw:
    tab_names.append("📋 Datos")
if include_stats:
    tab_names.append("📊 Estadísticas")
if include_summary and cat_cols and num_cols:
    tab_names.append("📐 Resumen")

if tab_names:
    report_tabs = st.tabs(tab_names)
    tab_idx = 0

    if include_raw:
        with report_tabs[tab_idx]:
            st.dataframe(df.head(100), use_container_width=True)
            st.caption(f"Mostrando 100 de {len(df)} filas")
        tab_idx += 1

    if include_stats and num_cols:
        with report_tabs[tab_idx]:
            stats = ae.describe(df)
            st.dataframe(stats, use_container_width=True)
        tab_idx += 1

    if include_summary and cat_cols and num_cols:
        with report_tabs[tab_idx]:
            summary = ae.group_and_aggregate(df, summary_col, summary_value, "sum")
            st.dataframe(summary.head(20), use_container_width=True)
        tab_idx += 1

# ─── GENERACIÓN DEL REPORTE ───────────────────────────────────

st.divider()

if st.button("🚀 Generar Reporte Excel Multi-Hoja"):
    with st.spinner("Generando reporte ejecutivo..."):
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            workbook = writer.book

            # Formato de cabecera
            header_fmt = workbook.add_format({
                'bold': True, 'text_wrap': True, 'valign': 'top',
                'fg_color': header_color, 'font_color': font_color, 'border': 1
            })
            zebra_fmt = workbook.add_format({'bg_color': '#F3F4F6'})

            def write_sheet(dataframe, sheet_name):
                dataframe.to_excel(writer, index=False, sheet_name=sheet_name)
                ws = writer.sheets[sheet_name]
                for col_num, value in enumerate(dataframe.columns.values):
                    ws.write(0, col_num, value, header_fmt)
                for i, col in enumerate(dataframe.columns):
                    max_len = max(dataframe[col].astype(str).map(len).max(), len(str(col))) + 2
                    ws.set_column(i, i, min(max_len, 50))
                for row_num in range(1, min(len(dataframe) + 1, 65000)):
                    if row_num % 2 == 0:
                        ws.set_row(row_num, None, zebra_fmt)

            # Hojas del reporte
            if include_raw:
                write_sheet(df, "Datos_Completos")

            if include_stats and num_cols:
                stats = ae.describe(df)
                stats_reset = stats.reset_index()
                stats_reset.columns = ["Métrica"] + stats_reset.columns[1:].tolist()
                write_sheet(stats_reset, "Estadísticas")

            if include_summary and cat_cols and num_cols:
                summary = ae.group_and_aggregate(df, summary_col, summary_value, "sum")
                write_sheet(summary, "Resumen_Categorías")

            # Hoja de metadata
            meta = pd.DataFrame({
                "Propiedad": ["Nombre", "Filas", "Columnas", "Columnas Numéricas", "Columnas Categóricas", "Generado"],
                "Valor": [report_name, len(df), len(df.columns), len(num_cols), len(cat_cols),
                          pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")]
            })
            write_sheet(meta, "Metadata")

        # Descargar
        excel_data = output.getvalue()
        b64 = base64.b64encode(excel_data).decode()
        filename = f"{report_name}.xlsx"

        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}" style="text-decoration: none;"><button style="background:linear-gradient(90deg,#10b981,#059669);color:white;padding:12px 28px;border:none;border-radius:8px;cursor:pointer;font-weight:bold;font-size:16px;">📥 Descargar Reporte: {filename}</button></a>'

        st.markdown(href, unsafe_allow_html=True)
        st.balloons()
        st.success(f"Reporte '{filename}' generado exitosamente con {tab_idx + 1} hojas.")
