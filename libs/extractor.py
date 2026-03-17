import pdfplumber
import pandas as pd
import io
import fitz # PyMuPDF

class PDFExtractor:
    def __init__(self, pdf_file):
        """
        Inicializa con un objeto de archivo PDF (de Streamlit o path).
        """
        self.pdf_file = pdf_file

    def get_total_pages(self):
        """
        Retorna el número total de páginas del PDF.
        """
        # Usamos fitz para el conteo que es instantáneo
        doc = fitz.open(stream=self.pdf_file.read(), filetype="pdf")
        total = len(doc)
        self.pdf_file.seek(0) # Reset stream
        return total

    def extract_tables_generator(self, start_page=1, end_page=None, engine="pdfplumber"):
        """
        Generador que extrae tablas página por página.
        Soporta motores: 'pdfplumber' (precisión) y 'pymupdf' (velocidad).
        """
        if engine == "pymupdf":
            doc = fitz.open(stream=self.pdf_file.read(), filetype="pdf")
            total = len(doc)
            end = end_page if end_page and end_page <= total else total
            
            for i in range(start_page - 1, end):
                page = doc[i]
                # Estrategia agresiva para detectar tablas basadas en espacios o líneas ocultas
                tabs = page.find_tables(strategy="lines_strict" if i % 2 == 0 else "lines")
                if not tabs.tables:
                    # Intento secundario si el primero falla
                    tabs = page.find_tables(strategy="text")
                
                page_data = []
                for tab in tabs:
                    # PyMuPDF entrega las tablas con un formato listo .extract()
                    table = tab.extract()
                    if table:
                        clean_table = [row for row in table if any(cell is not None and str(cell).strip() != "" for cell in row)]
                        page_data.extend(clean_table)
                yield page_data, i + 1
            self.pdf_file.seek(0)
            
        else: # Default: pdfplumber
            with pdfplumber.open(self.pdf_file) as pdf:
                total = len(pdf.pages)
                end = end_page if end_page and end_page <= total else total
                
                for i in range(start_page - 1, end):
                    page = pdf.pages[i]
                    tables = page.extract_tables()
                    page_data = []
                    for table in tables:
                        if table:
                            clean_table = [row for row in table if any(cell is not None and str(cell).strip() != "" for cell in row)]
                            page_data.extend(clean_table)
                    yield page_data, i + 1


    def get_metadata(self):
        """
        Obtiene metadatos del archivo.
        """
        with pdfplumber.open(self.pdf_file) as pdf:
            return pdf.metadata
