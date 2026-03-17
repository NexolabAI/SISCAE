"""
Analytics Engine — Motor de Inteligencia
Estadísticas, tablas dinámicas, proyecciones y detección de outliers.
"""
import pandas as pd
import numpy as np


class AnalyticsEngine:
    """Motor de análisis estadístico avanzado."""

    # ─── ESTADÍSTICAS DESCRIPTIVAS ─────────────────────────────

    @staticmethod
    def describe(df):
        """Estadísticas descriptivas extendidas."""
        numeric = df.select_dtypes(include=["number"])
        if numeric.empty:
            return pd.DataFrame({"info": ["No hay columnas numéricas"]})

        stats = numeric.describe().T
        stats["mediana"] = numeric.median()
        stats["varianza"] = numeric.var()
        stats["rango"] = stats["max"] - stats["min"]
        stats["cv"] = (stats["std"] / stats["mean"] * 100).round(2)  # Coeficiente de variación
        stats = stats.round(3)
        return stats

    # ─── TABLA DINÁMICA (PIVOT) ────────────────────────────────

    @staticmethod
    def pivot_table(df, index, columns=None, values=None, aggfunc="sum"):
        """Crea una tabla dinámica tipo Power Pivot."""
        agg_map = {
            "sum": "sum",
            "mean": "mean",
            "count": "count",
            "max": "max",
            "min": "min",
            "median": "median",
        }

        func = agg_map.get(aggfunc, "sum")

        try:
            pivot = pd.pivot_table(
                df,
                index=index,
                columns=columns,
                values=values,
                aggfunc=func,
                margins=True,
                margins_name="TOTAL",
            )
            return pivot.round(2)
        except Exception as e:
            raise ValueError(f"Error creando tabla dinámica: {e}")

    # ─── CORRELACIONES ─────────────────────────────────────────

    @staticmethod
    def correlations(df, method="pearson"):
        """Calcula la matriz de correlaciones."""
        numeric = df.select_dtypes(include=["number"])
        if numeric.shape[1] < 2:
            return None
        return numeric.corr(method=method).round(3)

    # ─── PROYECCIÓN LINEAL ─────────────────────────────────────

    @staticmethod
    def linear_projection(df, x_col, y_col, periods=10):
        """
        Proyección lineal simple usando numpy.polyfit.
        Retorna el DataFrame original + filas proyectadas.
        """
        numeric_df = df[[x_col, y_col]].dropna()

        if len(numeric_df) < 3:
            return df, None

        # Si x es numérico
        if pd.api.types.is_numeric_dtype(numeric_df[x_col]):
            x_vals = numeric_df[x_col].values
        else:
            # Intentar como índice secuencial
            x_vals = np.arange(len(numeric_df))

        y_vals = numeric_df[y_col].values

        # Regresión lineal
        coeffs = np.polyfit(x_vals, y_vals, 1)
        slope, intercept = coeffs

        # Generar proyección
        last_x = x_vals[-1]
        future_x = np.arange(last_x + 1, last_x + 1 + periods)
        future_y = slope * future_x + intercept

        projection = pd.DataFrame({
            x_col: future_x,
            y_col: future_y.round(2),
            "__tipo__": ["Proyección"] * periods
        })

        # Marcar datos originales
        original = numeric_df.copy()
        original["__tipo__"] = "Real"

        combined = pd.concat([original, projection], ignore_index=True)

        stats = {
            "slope": round(slope, 4),
            "intercept": round(intercept, 4),
            "r_squared": round(np.corrcoef(x_vals, y_vals)[0, 1] ** 2, 4),
            "trend": "📈 Creciente" if slope > 0 else "📉 Decreciente",
        }

        return combined, stats

    # ─── DETECCIÓN DE OUTLIERS ─────────────────────────────────

    @staticmethod
    def detect_outliers(df, column, method="iqr"):
        """
        Detecta outliers usando el método IQR.
        Retorna un DataFrame con una columna extra '__outlier__'.
        """
        if not pd.api.types.is_numeric_dtype(df[column]):
            return df, 0

        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        result = df.copy()
        result["__outlier__"] = (result[column] < lower) | (result[column] > upper)
        outlier_count = result["__outlier__"].sum()

        return result, int(outlier_count)

    # ─── AGRUPACIONES ──────────────────────────────────────────

    @staticmethod
    def group_and_aggregate(df, group_by, agg_col, agg_func="sum"):
        """Agrupa y agrega datos tipo SQL GROUP BY."""
        agg_map = {
            "sum": "sum",
            "mean": "mean",
            "count": "count",
            "max": "max",
            "min": "min",
        }

        func = agg_map.get(agg_func, "sum")

        try:
            result = df.groupby(group_by)[agg_col].agg(func).reset_index()
            result.columns = [*group_by, f"{agg_col}_{agg_func}"] if isinstance(group_by, list) else [group_by, f"{agg_col}_{agg_func}"]
            return result.sort_values(f"{agg_col}_{agg_func}", ascending=False)
        except Exception as e:
            raise ValueError(f"Error en agrupación: {e}")

    # ─── TOP N ─────────────────────────────────────────────────

    @staticmethod
    def top_n(df, column, n=10, ascending=False):
        """Retorna los Top N valores de una columna."""
        return df.nlargest(n, column) if not ascending else df.nsmallest(n, column)
