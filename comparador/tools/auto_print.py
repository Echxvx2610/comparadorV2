
import os
import PyPDF2
import win32api
import re

# Pyside6
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *


def fusionar_pdfs(archivos, salida):
    """
    Fusiona múltiples archivos PDF en uno solo.

    Args:
        archivos (list): Lista de rutas a los archivos PDF que se van a fusionar.
        salida (str): Ruta donde se guardará el archivo PDF fusionado.

    Returns:
        None
    """
    pdf_writer = PyPDF2.PdfWriter()

    for archivo in sorted(archivos):
        pdf_reader = PyPDF2.PdfReader(archivo)
        for pagina in range(len(pdf_reader.pages)):
            pdf_writer.add_page(pdf_reader.pages[pagina])

    with open(salida, 'wb') as out_pdf:
        pdf_writer.write(out_pdf)
    #print(f"PDF fusionado guardado como: {salida}") # para debug

def leer_pdf(ruta_archivo):
    """
    Lee y extrae el texto de un archivo PDF.

    Args:
        ruta_archivo (str): Ruta al archivo PDF que se va a leer.

    Returns:
        str: Todo el texto contenido en el PDF.
    """
    with open(ruta_archivo, 'rb') as archivo:
        pdf_reader = PyPDF2.PdfReader(archivo)
        texto = ""
        for pagina in range(len(pdf_reader.pages)):
            texto += pdf_reader.pages[pagina].extract_text()
    return texto

def contar_filas_feeder_setup(texto):
    """
    Cuenta el número de filas en la sección 'Feeder setup' de un texto extraído de un PDF.

    Args:
        texto (str): Texto extraído del PDF.

    Returns:
        int: Número de filas encontradas en la sección 'Feeder setup'.
    """
    if "Feeder setup" in texto:
        seccion_setup = texto.split("Feeder setup")[1]
        #print(f'seccion_setup: {seccion_setup}')
        #contemplar una linea cuando empiece con "1- " y encuentre otro "1- "
        filas = re.findall(r'1- .*', seccion_setup)
        return len(filas)
    return 0

def determinar_impresion(texto):
    """
    Determina el modo de impresión (one side o both side) basado en el texto extraído de un PDF.

    Args:
        texto (str): Texto extraído del PDF.

    Returns:
        str: 'both side' si se cumple la condición para impresión a doble cara, 'one side' en caso contrario.
    """
    filas = contar_filas_feeder_setup(texto)
    #print(f'conteo de filas: {filas}')  # para debug
    if "CP" in texto:
        return "both side" if filas > 29 and filas < 83  else "one side"
    elif "QP" in texto:
        return "both side" if filas > 16 else "one side"
    else:
        return "Desconocido"

def agregar_pagina_blanco(pdf_path, modo_impresion):
    """
    Agrega una página en blanco al final de un archivo PDF.

    Args:
        pdf_path (str): Ruta al archivo PDF original.

    Returns:
        str: Ruta al nuevo archivo PDF con la página en blanco agregada.
    """
    if modo_impresion == "one side":
        pdf_writer = PyPDF2.PdfWriter()
        pdf_reader = PyPDF2.PdfReader(pdf_path)

        for pagina in range(len(pdf_reader.pages)):
            pdf_writer.add_page(pdf_reader.pages[pagina])

        # Agregar una página en blanco
        pdf_writer.add_blank_page()

        # Guardar el nuevo PDF temporalmente
        pdf_path_blanco = pdf_path.replace(".pdf", "_blanco.pdf")
        with open(pdf_path_blanco, 'wb') as out_pdf:
            pdf_writer.write(out_pdf)

        return pdf_path_blanco
    else:
        return pdf_path

def eliminar_pdfs_temporales(directorio):
    """
    Elimina todos los archivos PDF en el directorio especificado que terminen en '_blanco.pdf'.

    Args:
        directorio (str): Ruta al directorio donde se encuentran los archivos PDF.

    Returns:
        None
    """
    for archivo in os.listdir(directorio):
        if archivo.endswith("_blanco.pdf"):
            ruta_completa = os.path.join(directorio, archivo)
            os.remove(ruta_completa)
            #print(f"Archivo temporal eliminado: {ruta_completa}")  # para debug

def imprimir_pdf(ruta_archivo, modo_impresion):
    """
    Imprime un archivo PDF en el modo especificado (one side o both side).
    Agrega una página en blanco si el modo es 'one side' para que la impresión salga correctamente.

    Args:
        ruta_archivo (str): Ruta al archivo PDF que se va a imprimir.
        modo_impresion (str): Modo de impresión ('one side' o 'both side').

    Returns:
        None
    """
    try:
        win32api.ShellExecute(
            0,
            "print",
            ruta_archivo,
            None,
            ".",
            0
        )
        #print(f"El archivo {os.path.basename(ruta_archivo)} se ha enviado a la impresora en modo {modo_impresion}.")  # para debug
    except Exception as e:
        #print(f"No se pudo imprimir el archivo {os.path.basename(ruta_archivo)}. Error: {str(e)}")  # para debug
        #QMessageBox.critical(None, "Error", f"No se pudo imprimir el archivo {os.path.basename(ruta_archivo)}. Error: {str(e)}")
        return str(e)

    finally:
        # Eliminar todos los archivos temporales que terminan en '_blanco.pdf'
        eliminar_pdfs_temporales(os.path.dirname(ruta_archivo))
    