"""
Página 2: Dashboard BI
Visualización interactiva con KPIs, gráficos Plotly y segmentadores.
PRIORIDAD: Filtrado inteligente y presentación de datos.
"""
import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_manager import DataManager
from modules.chart_builder import ChartBuilder
from modules.analytics_engine import AnalyticsEngine

st.title("📊 Dashboard BI")
st.caption("Inteligencia de Negocio interactiva — Filtros, KPIs y Gráficos dinámicos")

dm = DataManager()
cb = ChartBuilder()

# ─── FUENTE DE DATOS ───────────────────────────────────────────

with st.sidebar:
    st.header("📂 Fuente de Datos")

    data_source = st.radio("Origen de los datos", [
        "📄 Cargar archivo nuevo",
        "💾 Dataset guardado (Firebase)",
        "📊 Datos del Extractor (sesión actual)"
    ])

    df = None

    if data_source == "📄 Cargar archivo nuevo":
        uploaded = st.file_uploader("Sube PDF, Excel o CSV", type=["pdf", "xlsx", "xls", "csv"])
        if uploaded:
            file_ext = uploaded.name.split(".")[-1].lower()

            if file_ext == "pdf":
                st.warning("Para PDFs, usa el **Extractor PDF** primero y luego vuelve aquí.")
            else:
                with st.spinner("Procesando archivo..."):
                    df = dm.load_file(uploaded)
                    st.session_state.bi_df = df
                    st.success(f"✅ {len(df)} filas × {len(df.columns)} columnas")

                    # Auto-guardar en Firebase
                    dataset_id = dm.save_dataset(df, uploaded.name, uploaded.name)
                    if dataset_id:
                        st.toast(f"💾 Guardado en Firebase")

    elif data_source == "💾 Dataset guardado (Firebase)":
        datasets = dm.list_datasets()
        if datasets:
            options = {d["id"]: f"{d['name']} ({d['rows']} filas)" for d in datasets}
            selected_id = st.selectbox("Selecciona un dataset", list(options.keys()),
                                       format_func=lambda x: options[x])
            if st.button("Cargar Dataset"):
                with st.spinner("Cargando desde Firebase..."):
                    df = dm.load_dataset(selected_id)
                    st.session_state.bi_df = df
                    st.success(f"✅ Cargado: {len(df)} filas")
        else:
            st.info("No hay datasets guardados aún.")

    elif data_source == "📊 Datos del Extractor (sesión actual)":
        if "raw_df" in st.session_state:
            df = st.session_state.raw_df
            st.session_state.bi_df = df
            st.success(f"✅ Usando datos del extractor: {len(df)} filas")
        else:
            st.info("No hay datos extraídos. Ve al Extractor PDF primero.")

# Usar el DataFrame de la sesión si existe
if df is None and "bi_df" in st.session_state:
    df = st.session_state.bi_df

# ─── DASHBOARD PRINCIPAL ──────────────────────────────────────

if df is not None and not df.empty:

    # ─── SEGMENTADORES (SLICERS) ──────────────────────────────
    st.markdown("### 🎛️ Segmentadores")

    with st.expander("Configurar filtros avanzados", expanded=True):
        cat_cols = dm.get_categorical_columns(df)
        num_cols = dm.get_numeric_columns(df)
        date_cols = dm.get_date_columns(df)

        filtered_df = df.copy()

        # Todas las columnas categóricas disponibles para filtrar
        filter_cols = st.multiselect(
            "Columnas para filtrar",
            cat_cols,
            default=cat_cols,
            help="Selecciona las columnas categóricas que deseas usar como filtro."
        )

        # Búsqueda global por texto (aplica a TODAS las columnas)
        st.markdown("**🔍 Búsqueda rápida por texto**")
        search_text = st.text_input("Buscar en todos los datos...", "", placeholder="Ej: F. PUBLICA, SINSA, etc.")
        if search_text.strip():
            mask = df.apply(lambda row: row.astype(str).str.contains(search_text.strip(), case=False, na=False).any(), axis=1)
            filtered_df = filtered_df[filtered_df.index.isin(df[mask].index)]
            st.caption(f"🔎 Encontrados **{mask.sum()}** registros que contienen \"{search_text}\"")

        # Segmentadores por columna
        if filter_cols:
            # Agrupar en filas de 3 columnas
            cols_per_row = 3
            for row_start in range(0, len(filter_cols), cols_per_row):
                row_cols = filter_cols[row_start:row_start + cols_per_row]
                slicer_cols = st.columns(len(row_cols))
                for idx, col in enumerate(row_cols):
                    with slicer_cols[idx]:
                        unique_vals = sorted(filtered_df[col].dropna().unique().tolist(), key=str)
                        n_unique = len(unique_vals)

                        st.caption(f"**{col}** ({n_unique} valores)")

                        if n_unique > 100:
                            # Para columnas con muchos valores: usar selectbox con búsqueda
                            filter_mode = st.radio(f"Modo {col}", ["Incluir", "Excluir"], key=f"mode_{col}", horizontal=True)
                            filter_val = st.multiselect(
                                f"🔽 {col}",
                                unique_vals,
                                default=[],
                                key=f"slicer_{col}",
                                help=f"Escribe para buscar entre {n_unique} valores"
                            )
                            if filter_val:
                                if filter_mode == "Incluir":
                                    filtered_df = filtered_df[filtered_df[col].isin(filter_val)]
                                else:
                                    filtered_df = filtered_df[~filtered_df[col].isin(filter_val)]
                        else:
                            # Para columnas con pocos valores: multiselect con todos seleccionados
                            selected = st.multiselect(
                                f"🔽 {col}",
                                unique_vals,
                                default=unique_vals,
                                key=f"slicer_{col}"
                            )
                            filtered_df = filtered_df[filtered_df[col].isin(selected)]

        # Filtros por columnas numéricas
        if num_cols:
            st.markdown("**📊 Filtros numéricos**")
            num_filter_col = st.selectbox("Filtrar por rango numérico", ["Ninguna"] + num_cols)
            if num_filter_col != "Ninguna":
                clean_col = filtered_df[num_filter_col].dropna()
                if not clean_col.empty:
                    col_min = float(clean_col.min())
                    col_max = float(clean_col.max())
                    if col_min < col_max:
                        range_val = st.slider(
                            f"Rango de {num_filter_col}",
                            min_value=col_min,
                            max_value=col_max,
                            value=(col_min, col_max),
                        )
                        filtered_df = filtered_df[
                            (filtered_df[num_filter_col] >= range_val[0]) &
                            (filtered_df[num_filter_col] <= range_val[1])
                        ]

    st.caption(f"Mostrando **{len(filtered_df)}** de {len(df)} registros")

    # ─── KPI CARDS ─────────────────────────────────────────────
    st.markdown("### 📐 Métricas Clave")

    if num_cols:
        kpi_cols = st.columns(min(len(num_cols), 4))
        for idx, col in enumerate(num_cols[:4]):
            with kpi_cols[idx]:
                val = filtered_df[col].sum()
                avg = filtered_df[col].mean()
                st.metric(
                    label=col,
                    value=f"{val:,.2f}",
                    delta=f"Promedio: {avg:,.2f}",
                )

    # ─── VISUALIZACIONES ──────────────────────────────────────
    st.markdown("### 📈 Visualizaciones")

    tab_bar, tab_line, tab_pie, tab_table = st.tabs(["📊 Barras", "📈 Líneas", "🥧 Circular", "📋 Tabla"])

    with tab_bar:
        if cat_cols and num_cols:
            col_config1, col_config2 = st.columns(2)
            with col_config1:
                bar_x = st.selectbox("Eje X (Categoría)", cat_cols, key="bar_x")
            with col_config2:
                bar_y = st.selectbox("Eje Y (Valor)", num_cols, key="bar_y")

            # Agrupar datos para el gráfico
            agg = AnalyticsEngine.group_and_aggregate(filtered_df, bar_x, bar_y, "sum")
            fig = cb.bar_chart(agg.head(20), x=bar_x, y=f"{bar_y}_sum", title=f"{bar_y} por {bar_x}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Se necesitan columnas categóricas y numéricas para gráficos de barras.")

    with tab_line:
        if num_cols and len(num_cols) >= 2:
            col_l1, col_l2 = st.columns(2)
            with col_l1:
                line_x = st.selectbox("Eje X", df.columns.tolist(), key="line_x")
            with col_l2:
                line_y = st.selectbox("Eje Y", num_cols, key="line_y")
            use_area = st.checkbox("Mostrar como área")
            fig = cb.line_chart(filtered_df, x=line_x, y=line_y, title=f"Tendencia de {line_y}", area=use_area)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Se necesitan al menos 2 columnas numéricas para gráficos de líneas.")

    with tab_pie:
        if cat_cols and num_cols:
            pie_names = st.selectbox("Categoría", cat_cols, key="pie_names")
            pie_values = st.selectbox("Valor", num_cols, key="pie_values")
            use_donut = st.checkbox("Donut", value=True)
            agg_pie = AnalyticsEngine.group_and_aggregate(filtered_df, pie_names, pie_values, "sum")
            fig = cb.pie_chart(agg_pie.head(10), names=pie_names, values=f"{pie_values}_sum",
                             title=f"Distribución de {pie_values}", donut=use_donut)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Se necesitan columnas categóricas y numéricas.")

    with tab_table:
        st.markdown("**Datos filtrados**")
        st.dataframe(filtered_df, use_container_width=True, height=400)

        # Exportación rápida
        from libs.excel_engine import ExcelEngine
        import base64
        if st.button("📥 Exportar vista actual a Excel"):
            excel_data = ExcelEngine.create_excel(filtered_df, sheet_name="Dashboard_Export")
            b64 = base64.b64encode(excel_data).decode()
            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="dashboard_export.xlsx"><button style="background:#10b981;color:white;padding:10px 20px;border:none;border-radius:5px;cursor:pointer;font-weight:bold;">📥 Descargar</button></a>'
            st.markdown(href, unsafe_allow_html=True)

else:
    st.info("👈 Selecciona una fuente de datos en el panel lateral para comenzar.")
    st.markdown("""
    **Opciones disponibles:**
    - 📄 Cargar un archivo nuevo (Excel, CSV o PDF)
    - 💾 Abrir un dataset guardado en Firebase
    - 📊 Usar los datos extraídos del Extractor PDF
    """)
