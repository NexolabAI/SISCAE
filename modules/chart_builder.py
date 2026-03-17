"""
Chart Builder — Fábrica de Visualizaciones Interactivas
Genera gráficos Plotly con tema unificado (Dark Mode OLED).
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


# ─── TEMA GLOBAL (Design System MASTER.md) ─────────────────────

THEME = {
    "primary": "#1E40AF",
    "secondary": "#3B82F6",
    "accent": "#F59E0B",
    "background": "#0f172a",
    "paper": "#1e293b",
    "text": "#f8fafc",
    "grid": "rgba(255,255,255,0.06)",
    "palette": ["#3B82F6", "#F59E0B", "#10B981", "#EF4444", "#8B5CF6",
                "#EC4899", "#14B8A6", "#F97316", "#6366F1", "#84CC16"],
}

LAYOUT_DEFAULTS = dict(
    template="plotly_dark",
    paper_bgcolor=THEME["paper"],
    plot_bgcolor=THEME["background"],
    font=dict(family="Fira Sans, Inter, sans-serif", color=THEME["text"]),
    margin=dict(l=40, r=20, t=50, b=40),
    hoverlabel=dict(bgcolor=THEME["paper"], font_size=13),
    xaxis=dict(gridcolor=THEME["grid"]),
    yaxis=dict(gridcolor=THEME["grid"]),
)


class ChartBuilder:
    """Genera gráficos Plotly con estética premium consistente."""

    # ─── BARRAS ────────────────────────────────────────────────

    @staticmethod
    def bar_chart(df, x, y, title="", color=None, orientation="v", barmode="group"):
        """Gráfico de barras (vertical u horizontal)."""
        fig = px.bar(
            df, x=x, y=y, color=color,
            title=title,
            orientation=orientation,
            barmode=barmode,
            color_discrete_sequence=THEME["palette"],
        )
        fig.update_layout(**LAYOUT_DEFAULTS)
        fig.update_traces(marker_line_width=0, opacity=0.9)
        return fig

    # ─── LÍNEAS ────────────────────────────────────────────────

    @staticmethod
    def line_chart(df, x, y, title="", color=None, area=False):
        """Gráfico de líneas (con área opcional)."""
        fn = px.area if area else px.line
        fig = fn(
            df, x=x, y=y, color=color,
            title=title,
            color_discrete_sequence=THEME["palette"],
        )
        fig.update_layout(**LAYOUT_DEFAULTS)
        fig.update_traces(line_width=2.5)
        return fig

    # ─── PIE / DONUT ───────────────────────────────────────────

    @staticmethod
    def pie_chart(df, names, values, title="", donut=True):
        """Gráfico circular o donut."""
        fig = px.pie(
            df, names=names, values=values,
            title=title,
            hole=0.45 if donut else 0,
            color_discrete_sequence=THEME["palette"],
        )
        fig.update_layout(**LAYOUT_DEFAULTS)
        fig.update_traces(textposition="inside", textinfo="percent+label")
        return fig

    # ─── SCATTER ───────────────────────────────────────────────

    @staticmethod
    def scatter_chart(df, x, y, title="", color=None, size=None, trendline=False):
        """Gráfico de dispersión con línea de tendencia opcional."""
        fig = px.scatter(
            df, x=x, y=y, color=color, size=size,
            title=title,
            trendline="ols" if trendline else None,
            color_discrete_sequence=THEME["palette"],
        )
        fig.update_layout(**LAYOUT_DEFAULTS)
        return fig

    # ─── HEATMAP ───────────────────────────────────────────────

    @staticmethod
    def heatmap(df, title="Mapa de Correlaciones"):
        """Heatmap de correlaciones para columnas numéricas."""
        numeric_df = df.select_dtypes(include=["number"])
        if numeric_df.empty:
            return None

        corr = numeric_df.corr()
        fig = go.Figure(data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.columns,
            colorscale="RdBu_r",
            zmin=-1, zmax=1,
            text=corr.values.round(2),
            texttemplate="%{text}",
            hovertemplate="<b>%{x}</b> vs <b>%{y}</b><br>Correlación: %{z:.3f}<extra></extra>"
        ))
        fig.update_layout(title=title, **LAYOUT_DEFAULTS)
        return fig

    # ─── HISTOGRAMA ────────────────────────────────────────────

    @staticmethod
    def histogram(df, column, title="", bins=30, color=None):
        """Histograma de distribución."""
        fig = px.histogram(
            df, x=column, nbins=bins, color=color,
            title=title or f"Distribución de {column}",
            color_discrete_sequence=THEME["palette"],
        )
        fig.update_layout(**LAYOUT_DEFAULTS)
        return fig

    # ─── TREEMAP ───────────────────────────────────────────────

    @staticmethod
    def treemap(df, path, values, title=""):
        """Treemap jerárquico."""
        fig = px.treemap(
            df, path=path, values=values,
            title=title,
            color_discrete_sequence=THEME["palette"],
        )
        fig.update_layout(**LAYOUT_DEFAULTS)
        return fig

    # ─── KPI CARD (Métrica Plotly) ─────────────────────────────

    @staticmethod
    def kpi_indicator(value, title="", reference=None, suffix=""):
        """Indicador KPI tipo gauge."""
        fig = go.Figure(go.Indicator(
            mode="number+delta" if reference else "number",
            value=value,
            title={"text": title, "font": {"size": 16}},
            delta={"reference": reference} if reference else None,
            number={"suffix": suffix, "font": {"size": 36, "color": THEME["accent"]}},
        ))
        fig.update_layout(
            paper_bgcolor=THEME["paper"],
            font=dict(color=THEME["text"], family="Fira Sans"),
            height=150,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        return fig

    # ─── UTILIDADES ────────────────────────────────────────────

    @staticmethod
    def get_chart_types():
        """Retorna los tipos de gráficos disponibles."""
        return {
            "bars": "📊 Barras",
            "line": "📈 Líneas",
            "area": "📈 Área",
            "pie": "🥧 Circular (Pie)",
            "donut": "🍩 Donut",
            "scatter": "⚡ Dispersión (Scatter)",
            "histogram": "📉 Histograma",
            "heatmap": "🗺️ Mapa de Calor",
            "treemap": "🌳 Treemap",
        }
