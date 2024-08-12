import os
import win32api
import PyPDF2
from tkinter import Tk, filedialog

def fusionar_pdfs(archivos, salida):
    pdf_writer = PyPDF2.PdfWriter()

    for archivo in sorted(archivos):
        pdf_reader = PyPDF2.PdfReader(archivo)
        for pagina in range(len(pdf_reader.pages)):
            pdf_writer.add_page(pdf_reader.pages[pagina])

    with open(salida, 'wb') as out_pdf:
        pdf_writer.write(out_pdf)
    print(f"PDF fusionado guardado como: {salida}")

def imprimir_pdf(ruta_archivo):
    try:
        win32api.ShellExecute(
            0,
            "print",
            ruta_archivo,
            None,
            ".",
            0
        )
        print(f"El archivo {os.path.basename(ruta_archivo)} se ha enviado a la impresora.")
    except Exception as e:
        print(f"No se pudo imprimir el archivo {os.path.basename(ruta_archivo)}. Error: {str(e)}")
