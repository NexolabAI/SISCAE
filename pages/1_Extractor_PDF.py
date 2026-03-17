"""
Página 1: Extractor PDF
Funcionalidad original de PDF2Excel Pro con motor híbrido.
"""
import streamlit as st
import pandas as pd
import base64
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from libs.extractor import PDFExtractor
from libs.excel_engine import ExcelEngine
from modules.data_manager import DataManager

st.title("📄 Extractor PDF")
st.caption("Motor Híbrido Inteligente — pdfplumber (Precisión) + PyMuPDF (Turbo)")

# ─── SIDEBAR: CARGA DE ARCHIVO ────────────────────────────────

with st.sidebar:
    st.header("⚙️ Configuración")
    uploaded_file = st.file_uploader("Sube tu archivo PDF", type=["pdf"])
    st.divider()
    st.info("Sube un PDF con tablas para comenzar. Podrás filtrar, ordenar y elegir qué columnas exportar.")

# ─── LÓGICA PRINCIPAL ─────────────────────────────────────────

if uploaded_file:
    file_size_mb = uploaded_file.size / (1024 * 1024)
    extractor = PDFExtractor(uploaded_file)
    total_pages = extractor.get_total_pages()

    # Motor híbrido automático
    if file_size_mb > 10:
        engine = "pymupdf"
        engine_desc = "🚀 MODO TURBO (PyMuPDF)"
        engine_info = "Archivo grande detectado. Usando motor de alta velocidad."
    else:
        engine = "pdfplumber"
        engine_desc = "💎 MODO PRECISIÓN (pdfplumber)"
        engine_info = "Archivo pequeño. Priorizando máxima precisión estructural."

    st.sidebar.markdown(f"**Motor seleccionado:**\n{engine_desc}")
    st.sidebar.caption(engine_info)
    st.sidebar.success(f"📄 {total_pages} páginas | {file_size_mb:.2f} MB")

    # ─── PASO 1: SELECCIÓN DE RANGO ───────────────────────────
    st.markdown("### 1. Selecciona el Rango de Páginas")
    col_range1, col_range2 = st.columns(2)
    with col_range1:
        start_p = st.number_input("Página Inicial", min_value=1, max_value=total_pages, value=1)
    with col_range2:
        end_p = st.number_input("Página Final", min_value=1, max_value=total_pages, value=min(10, total_pages))

    if st.button("🔍 Iniciar Extracción Estructurada"):
        st.session_state.extraction_done = False
        total_to_process = end_p - start_p + 1

        status_container = st.empty()
        progress_bar = st.progress(0)
        timer_text = st.empty()

        all_data = []
        start_time = time.time()

        for page_data, current_p in extractor.extract_tables_generator(start_page=start_p, end_page=end_p, engine=engine):
            all_data.extend(page_data)

            processed_count = current_p - start_p + 1
            percent = processed_count / total_to_process
            progress_bar.progress(percent)

            elapsed = time.time() - start_time
            if processed_count > 0:
                avg_time_per_page = elapsed / processed_count
                remaining_pages = total_to_process - processed_count
                rem_time = remaining_pages * avg_time_per_page
                timer_text.markdown(f"⏱️ **Tiempo restante estimado:** `{int(rem_time // 60)}m {int(rem_time % 60)}s` | **Procesando página:** `{current_p}`")

        if all_data:
            dm = DataManager()
            df = pd.DataFrame(all_data)
            df = dm._clean_dataframe(df)

            st.session_state.raw_df = df
            st.session_state.extraction_done = True
            timer_text.empty()
            progress_bar.empty()
            st.success(f"¡Extracción de {total_to_process} páginas completada en {int(time.time() - start_time)}s!")

            # Guardar en Firebase
            with st.spinner("Guardando en la nube..."):
                dataset_id = dm.save_dataset(df, uploaded_file.name, uploaded_file.name)
                if dataset_id:
                    st.toast(f"💾 Dataset guardado en Firebase ({dataset_id})")
        else:
            st.error("No se encontraron tablas en el rango seleccionado.")

    # ─── PASO 2: PERSONALIZACIÓN ──────────────────────────────
    if st.session_state.get("extraction_done", False):
        df = st.session_state.raw_df
        st.markdown("---")
        st.markdown("### 2. Personaliza tu Excel Resultante")

        col1, col2 = st.columns([2, 1])

        with col1:
            all_cols = df.columns.tolist()
            selected_cols = st.multiselect("Selecciona las columnas que deseas incluir", all_cols, default=all_cols)

            st.markdown("**Filtros Rápidos**")
            filter_col = st.selectbox("Columna para filtrar", ["Ninguna"] + selected_cols)
            if filter_col != "Ninguna":
                unique_vals = df[filter_col].unique().tolist()
                filter_val = st.multiselect(f"Valores de '{filter_col}' a incluir", unique_vals, default=unique_vals)
                df_display = df[df[filter_col].isin(filter_val)]
            else:
                df_display = df

            sort_col = st.selectbox("Ordenar por", ["Sin orden"] + selected_cols)
            if sort_col != "Sin orden":
                ascending = st.radio("Dirección", ["Ascendente", "Descendente"]) == "Ascendente"
                df_display = df_display.sort_values(by=sort_col, ascending=ascending)

        with col2:
            st.markdown("**Estilo del Excel**")
            header_color = st.color_picker("Color de Cabecera", "#1E3A8A")
            font_color = st.color_picker("Color de Fuente Cabecera", "#FFFFFF")
            sheet_name = st.text_input("Nombre de la Hoja", "Reporte_Personalizado")

        # Previsualización
        st.markdown("### 🔎 Previsualización del Resultado")
        final_df = df_display[selected_cols]
        st.dataframe(final_df, use_container_width=True)

        # Exportación
        st.divider()
        if st.button("🚀 Generar y Descargar Excel"):
            excel_data = ExcelEngine.create_excel(
                final_df,
                sheet_name=sheet_name,
                header_color=header_color,
                font_color=font_color
            )
            b64 = base64.b64encode(excel_data).decode()
            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{sheet_name}.xlsx" style="text-decoration: none;"><button style="background-color: #10b981; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">📥 Descargar Ahora</button></a>'
            st.markdown(href, unsafe_allow_html=True)
            st.balloons()
    elif not st.session_state.get("extraction_done"):
        st.info("Selecciona un rango de páginas y haz clic en 'Iniciar Extracción' para comenzar.")
else:
    st.info("Esperando archivo PDF... Arrastra y suelta uno en el panel lateral.")
