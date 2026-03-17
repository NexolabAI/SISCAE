"""
Data Manager — Cerebro de Datos del Módulo BI
Carga unificada de PDF/Excel/CSV + persistencia en Firebase Firestore.
"""
import pandas as pd
import streamlit as st
import io
import json
import hashlib
from datetime import datetime

# Firebase Admin SDK
import firebase_admin
from firebase_admin import credentials, firestore

# Nuestro motor existente
from libs.extractor import PDFExtractor


class DataManager:
    """Gestiona la carga, limpieza y persistencia de datos."""

    SUPPORTED_FORMATS = {
        "pdf": "📄 PDF (Motor Híbrido)",
        "xlsx": "📊 Excel (.xlsx)",
        "xls": "📊 Excel (.xls)",
        "csv": "📋 CSV"
    }

    def __init__(self):
        self._init_firebase()

    def _init_firebase(self):
        """Inicializa la conexión con Firebase Firestore."""
        try:
            if not firebase_admin._apps:
                # Usa credenciales por defecto (ADC) o service account
                cred = credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred, {
                    'projectId': 'pdf2excel-bi-module'
                })
            self.db = firestore.client()
        except Exception as e:
            self.db = None
            print(f"⚠️ Firebase no disponible (modo offline): {e}")

    # ─── CARGA DE ARCHIVOS ─────────────────────────────────────

    def load_file(self, uploaded_file, engine="auto", start_page=1, end_page=None, progress_callback=None):
        """
        Carga unificada de datos desde PDF, Excel o CSV.
        Retorna un DataFrame limpio.
        """
        file_ext = uploaded_file.name.split(".")[-1].lower()
        file_size_mb = uploaded_file.size / (1024 * 1024)

        if file_ext == "pdf":
            return self._load_pdf(uploaded_file, engine, start_page, end_page, file_size_mb, progress_callback)
        elif file_ext in ("xlsx", "xls"):
            return self._load_excel(uploaded_file)
        elif file_ext == "csv":
            return self._load_csv(uploaded_file)
        else:
            raise ValueError(f"Formato no soportado: .{file_ext}")

    def _load_pdf(self, file, engine, start_page, end_page, file_size_mb, progress_callback=None):
        """Carga PDF usando el motor híbrido existente."""
        extractor = PDFExtractor(file)
        total_pages = extractor.get_total_pages()

        # Motor híbrido automático
        if engine == "auto":
            engine = "pymupdf" if file_size_mb > 10 else "pdfplumber"

        all_data = []
        end = end_page if end_page and end_page <= total_pages else total_pages

        for page_data, current_p in extractor.extract_tables_generator(
            start_page=start_page, end_page=end, engine=engine
        ):
            all_data.extend(page_data)
            if progress_callback:
                progress_callback(current_p, start_page, end)

        if not all_data:
            return pd.DataFrame()

        df = pd.DataFrame(all_data)
        df = self._clean_dataframe(df)
        return df

    def _load_excel(self, file):
        """Carga archivos Excel con detección automática de hojas."""
        try:
            # Leer todas las hojas
            xls = pd.ExcelFile(file)
            if len(xls.sheet_names) == 1:
                df = pd.read_excel(file, sheet_name=0)
            else:
                # Unir todas las hojas
                frames = []
                for sheet in xls.sheet_names:
                    sheet_df = pd.read_excel(file, sheet_name=sheet)
                    sheet_df["__origen_hoja__"] = sheet
                    frames.append(sheet_df)
                df = pd.concat(frames, ignore_index=True)
            return self._clean_dataframe(df, has_header=True)
        except Exception as e:
            raise ValueError(f"Error al leer Excel: {e}")

    def _load_csv(self, file):
        """Carga CSV con detección automática de delimitador."""
        try:
            content = file.read().decode("utf-8", errors="replace")
            file.seek(0)

            # Detectar delimitador
            import csv
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(content[:10000])
            delimiter = dialect.delimiter

            df = pd.read_csv(file, delimiter=delimiter)
            return self._clean_dataframe(df, has_header=True)
        except Exception as e:
            raise ValueError(f"Error al leer CSV: {e}")

    # ─── LIMPIEZA ──────────────────────────────────────────────

    def _clean_dataframe(self, df, has_header=False):
        """Limpia y normaliza un DataFrame."""
        if df.empty:
            return df

        # Si no tiene header (viene de PDF), usar primera fila
        if not has_header:
            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)

        # Limpiar nombres de columnas
        cols = pd.Series([str(c).replace("\n", " ").strip() for c in df.columns])

        # Desduplicar nombres
        for dupe in cols[cols.duplicated()].unique():
            dupe_idx = cols[cols == dupe].index
            cols.iloc[dupe_idx] = [
                f"{dupe}_{i}" if i != 0 else dupe
                for i in range(len(dupe_idx))
            ]
        df.columns = cols

        # Limpiar espacios en blanco de los valores string
        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace({"nan": None, "None": None, "": None})

        # Detectar y convertir tipos
        df = self._auto_detect_types(df)

        return df

    def _auto_detect_types(self, df):
        """Intenta convertir columnas a sus tipos reales."""
        for col in df.columns:
            # Primero: limpiar formatos monetarios ($, comas)
            if df[col].dtype == "object":
                cleaned = df[col].astype(str).str.replace(r'[$,\s]', '', regex=True)
                numeric = pd.to_numeric(cleaned, errors="coerce")
                if numeric.notna().sum() > len(df) * 0.4:
                    df[col] = numeric
                    continue

            # Intentar numérico directo
            numeric = pd.to_numeric(df[col], errors="coerce")
            if numeric.notna().sum() > len(df) * 0.5:
                df[col] = numeric
                continue

            # Intentar fecha
            try:
                dates = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
                if dates.notna().sum() > len(df) * 0.5:
                    df[col] = dates
            except Exception:
                pass

        return df

    # ─── PERSISTENCIA FIREBASE ─────────────────────────────────

    def save_dataset(self, df, name, source_file):
        """Guarda un dataset en Firestore para acceso futuro."""
        if not self.db:
            return None

        try:
            # Generar ID único basado en contenido
            content_hash = hashlib.md5(df.to_json().encode()).hexdigest()[:12]

            # Metadata del dataset
            doc_ref = self.db.collection("datasets").document(content_hash)
            doc_ref.set({
                "name": name,
                "source_file": source_file,
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": df.columns.tolist(),
                "column_types": {col: str(df[col].dtype) for col in df.columns},
                "created_at": datetime.now().isoformat(),
                "size_kb": df.memory_usage(deep=True).sum() / 1024
            })

            # Guardar datos en chunks (Firestore tiene límite de 1MB por doc)
            chunk_size = 500  # filas por chunk
            for i in range(0, len(df), chunk_size):
                chunk = df.iloc[i:i+chunk_size]
                chunk_ref = doc_ref.collection("data_chunks").document(f"chunk_{i//chunk_size}")
                # Convertir a registros serializables
                records = json.loads(chunk.to_json(orient="records", date_format="iso"))
                chunk_ref.set({"rows": records, "index": i//chunk_size})

            return content_hash
        except Exception as e:
            print(f"Error guardando en Firestore: {e}")
            return None

    def list_datasets(self):
        """Lista todos los datasets guardados."""
        if not self.db:
            return []

        try:
            docs = self.db.collection("datasets").stream()
            datasets = []
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                datasets.append(data)
            return datasets
        except Exception:
            return []

    def load_dataset(self, dataset_id):
        """Carga un dataset desde Firestore."""
        if not self.db:
            return None

        try:
            # Leer chunks
            chunks_ref = self.db.collection("datasets").document(dataset_id).collection("data_chunks")
            chunks = chunks_ref.order_by("index").stream()

            all_rows = []
            for chunk in chunks:
                all_rows.extend(chunk.to_dict()["rows"])

            df = pd.DataFrame(all_rows)
            df = self._auto_detect_types(df)
            return df
        except Exception as e:
            print(f"Error cargando dataset: {e}")
            return None

    def delete_dataset(self, dataset_id):
        """Elimina un dataset de Firestore."""
        if not self.db:
            return False

        try:
            doc_ref = self.db.collection("datasets").document(dataset_id)
            # Eliminar chunks primero
            chunks = doc_ref.collection("data_chunks").stream()
            for chunk in chunks:
                chunk.reference.delete()
            doc_ref.delete()
            return True
        except Exception:
            return False

    # ─── UTILIDADES ────────────────────────────────────────────

    @staticmethod
    def get_column_summary(df):
        """Retorna un resumen de las columnas del DataFrame."""
        summary = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            nulls = df[col].isna().sum()
            uniques = df[col].nunique()
            
            col_info = {
                "name": col,
                "type": dtype,
                "nulls": int(nulls),
                "null_pct": round(nulls / len(df) * 100, 1) if len(df) > 0 else 0,
                "unique": int(uniques),
            }

            if pd.api.types.is_numeric_dtype(df[col]):
                col_info["min"] = df[col].min()
                col_info["max"] = df[col].max()
                col_info["mean"] = round(df[col].mean(), 2)

            summary.append(col_info)
        return summary

    @staticmethod
    def get_numeric_columns(df):
        """Retorna las columnas numéricas."""
        return df.select_dtypes(include=["number"]).columns.tolist()

    @staticmethod
    def get_categorical_columns(df):
        """Retorna las columnas categóricas."""
        return df.select_dtypes(include=["object", "category"]).columns.tolist()

    @staticmethod
    def get_date_columns(df):
        """Retorna las columnas de fecha."""
        return df.select_dtypes(include=["datetime"]).columns.tolist()
