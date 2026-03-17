import pandas as pd
import io

class ExcelEngine:
    @staticmethod
    def create_excel(df, sheet_name="Data", header_color="#1E3A8A", font_color="#FFFFFF"):
        """
        Crea un archivo Excel en memoria con formato premium.
        """
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            
            workbook  = writer.book
            worksheet = writer.sheets[sheet_name]
            
            # Formatos
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': header_color,
                'font_color': font_color,
                'border': 1
            })

            # Aplicar formato a cabeceras
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                
            # Ajuste automático de columnas
            for i, col in enumerate(df.columns):
                column_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, column_len)
                
            # Zebra striping (Filas alternas)
            zebra_format = workbook.add_format({'bg_color': '#F3F4F6'})
            # Se aplica si hay datos
            if len(df) > 0:
                for row_num in range(1, len(df) + 1):
                    if row_num % 2 == 0:
                        worksheet.set_row(row_num, None, zebra_format)

        return output.getvalue()
