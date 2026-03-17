"""
Página 3: Análisis Avanzado
Tablas dinámicas, correlaciones, proyecciones y outliers.
"""
import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_manager import DataManager
from modules.chart_builder import ChartBuilder
from modules.analytics_engine import AnalyticsEngine

st.title("🔬 Análisis Avanzado")
st.caption("Tablas dinámicas, correlaciones, proyecciones y detección de outliers")

dm = DataManager()
cb = ChartBuilder()
ae = AnalyticsEngine()

# ─── VERIFICAR DATOS ──────────────────────────────────────────

df = st.session_state.get("bi_df", st.session_state.get("raw_df", None))

if df is None or (hasattr(df, 'empty') and df.empty):
    st.warning("No hay datos cargados. Ve al **Dashboard BI** o al **Extractor PDF** para cargar datos primero.")
    st.stop()

num_cols = dm.get_numeric_columns(df)
cat_cols = dm.get_categorical_columns(df)

# ─── TABS DE ANÁLISIS ─────────────────────────────────────────

tab_stats, tab_pivot, tab_corr, tab_proj, tab_outliers = st.tabs([
    "📊 Estadísticas", "📐 Tabla Dinámica", "🗺️ Correlaciones", "📈 Proyecciones", "🎯 Outliers"
])

# ─── TAB 1: ESTADÍSTICAS DESCRIPTIVAS ─────────────────────────

with tab_stats:
    st.markdown("### Estadísticas Descriptivas")
    if num_cols:
        stats = ae.describe(df)
        st.dataframe(stats, use_container_width=True)

        # Histogramas de distribución
        st.markdown("### Distribuciones")
        hist_col = st.selectbox("Columna para histograma", num_cols, key="hist_col")
        bins = st.slider("Número de bins", 10, 100, 30)
        fig = cb.histogram(df, hist_col, bins=bins)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No se encontraron columnas numéricas para estadísticas.")

# ─── TAB 2: TABLA DINÁMICA ────────────────────────────────────

with tab_pivot:
    st.markdown("### Tabla Dinámica (Power Pivot)")

    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    with col_p1:
        pivot_rows = st.selectbox("Filas (Agrupar por)", cat_cols if cat_cols else df.columns.tolist(), key="pivot_rows")
    with col_p2:
        pivot_cols = st.selectbox("Columnas (Desglosar por)", ["Ninguna"] + (cat_cols if cat_cols else df.columns.tolist()), key="pivot_cols")
    with col_p3:
        pivot_values = st.selectbox("Valores", num_cols if num_cols else df.columns.tolist(), key="pivot_values")
    with col_p4:
        pivot_func = st.selectbox("Función", ["sum", "mean", "count", "max", "min", "median"], key="pivot_func")

    if st.button("Generar Tabla Dinámica"):
        try:
            pivot = ae.pivot_table(
                df,
                index=pivot_rows,
                columns=pivot_cols if pivot_cols != "Ninguna" else None,
                values=pivot_values,
                aggfunc=pivot_func,
            )
            st.dataframe(pivot, use_container_width=True)

            # Gráfico asociado
            if pivot_cols == "Ninguna":
                pivot_flat = pivot.reset_index()
                fig = cb.bar_chart(pivot_flat.head(20), x=pivot_rows, y=pivot_values, title=f"{pivot_func}({pivot_values}) por {pivot_rows}")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creando tabla dinámica: {e}")

# ─── TAB 3: CORRELACIONES ─────────────────────────────────────

with tab_corr:
    st.markdown("### Mapa de Correlaciones")
    if len(num_cols) >= 2:
        method = st.selectbox("Método", ["pearson", "spearman", "kendall"])
        corr_matrix = ae.correlations(df, method=method)
        if corr_matrix is not None:
            fig = cb.heatmap(df, title=f"Correlaciones ({method})")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("**Matriz numérica**")
            st.dataframe(corr_matrix, use_container_width=True)
    else:
        st.info("Se necesitan al menos 2 columnas numéricas.")

# ─── TAB 4: PROYECCIONES ──────────────────────────────────────

with tab_proj:
    st.markdown("### Proyección Lineal de Tendencia")
    if len(num_cols) >= 2:
        col_proj1, col_proj2, col_proj3 = st.columns(3)
        with col_proj1:
            proj_x = st.selectbox("Variable X", num_cols, key="proj_x")
        with col_proj2:
            remaining = [c for c in num_cols if c != proj_x]
            proj_y = st.selectbox("Variable Y", remaining if remaining else num_cols, key="proj_y")
        with col_proj3:
            periods = st.number_input("Períodos a proyectar", 5, 50, 10)

        if st.button("Calcular Proyección"):
            combined, stats = ae.linear_projection(df, proj_x, proj_y, periods=periods)
            if stats:
                st.markdown(f"""
                | Métrica | Valor |
                |---|---|
                | **Tendencia** | {stats['trend']} |
                | **Pendiente** | {stats['slope']} |
                | **R² (Precisión)** | {stats['r_squared']} |
                """)

                fig = cb.scatter_chart(combined, x=proj_x, y=proj_y, color="__tipo__", title=f"Proyección de {proj_y}")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No hay suficientes datos para calcular la proyección.")
    else:
        st.info("Se necesitan al menos 2 columnas numéricas.")

# ─── TAB 5: DETECCIÓN DE OUTLIERS ─────────────────────────────

with tab_outliers:
    st.markdown("### Detección de Outliers (Método IQR)")
    if num_cols:
        outlier_col = st.selectbox("Columna a analizar", num_cols, key="outlier_col")

        result_df, count = ae.detect_outliers(df, outlier_col)
        st.metric("Outliers detectados", count, delta=f"{count/len(df)*100:.1f}% del total")

        if count > 0:
            fig = cb.scatter_chart(result_df, x=result_df.index, y=outlier_col, color="__outlier__",
                                  title=f"Outliers en {outlier_col}")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("**Registros outlier:**")
            st.dataframe(result_df[result_df["__outlier__"] == True].drop("__outlier__", axis=1), use_container_width=True)
    else:
        st.info("Se necesitan columnas numéricas.")
