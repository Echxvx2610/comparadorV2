# Autor: Cristian Echeverria
# Comparador de archivos con una estructura dada con automatizacion de impresion de reportes html

# py -3.12 -m PyInstaller --windowed "C:\comparador\app.py" convertir a ejecutable
# py -3.12 -m PyInstaller --windowed "C:\app.spec"

# 1er comando de auto-py-to-exe [presento problemas con playwright]
# pyinstaller --noconfirm --onefile --windowed --icon "C:/comparadorV2/comparador/ui/resources/icons8-compare-60.ico" --add-data "C:/comparadorV2/comparador;comparador/" --paths "C:/comparadorV2/comparador/ui/resources" --paths "C:/comparadorV2/comparador/tools"  "C:/comparadorV2/comparador/app.py"

# 2do comando auto-py-to-exe
#pyinstaller --noconfirm --onefile --console --icon "C:/comparadorV2/comparador/ui/resources/icons8-compare-60.ico" --add-data "C:/comparadorV2/comparador/ui/resources/LOGO_NAVICO_1_90-black.png;." --add-data "C:/comparadorV2/comparador;comparador/" --paths "C:/comparadorV2/comparador/ui/resources" --paths "C:/comparadorV2/comparador/tools" --collect-data "playwright"  "C:/comparadorV2/comparador/app.py"

# sistema
import sys
import os

# Pyside6
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# modulos propios
#import bom_check
import bom_check
from tools import logger
from tools import convertir_xlm_html
from tools import auto_print

# Analisis de datos y archivos
import pandas as pd
import csv
import openpyxl
import asyncio
from playwright.async_api import async_playwright

# multiprocesamiento
import time
import threading
from queue import Queue

# librerias manejo de PDF
import win32api
import PyPDF2

# ******************************** TO DO ************************************
# - Ordenar carpetas de proyecto [Solucionado]
# - Limpiar comentarios [Solucionado]
# - formato de codigo de barras incorrecto --> *%O* no se convierte en _ [Solucionado: se remplazo texto %O por _]

# - Optimizar código ( 
#                     - Funciones [x]
#                     - Clases    [x]
#                     - Variables globales []
#                     - Variables locales  []
#                     - Ciclos             []
#                     - Manejo de excepciones []
#                     - Manejo de errores con registro en log []
#                     )

# - Agregar comentarios de documentación
# - Generar ejecutable de escritorio
# - Generar guia de usuario
# - Subida de proyecto a github
# *******************************************************************************


# Obtener la ruta al directorio tools
tools_dir = os.path.dirname(os.path.abspath(__file__))
#log_file = os.path.join(tools_dir, r'comparador\tools\comp.log')
log_file = r'H:\Ingenieria\SMT\Flexa_vs_BOM\comp.log'
# Configurar el logger (asegurándote de que solo se configure una vez)
logger = logger.setup_logger(log_file)

# rutas default (generacion de reportes)
base_path = r'comparador\ui\resources\devices_flexa'
logo_path = r'ui\resources\LOGO_NAVICO_1_90-black.png'
css_path = r'C:\FujiFlexa\Client\Report\Definition\Feeder Setup_IndexReportStyle.css'
unit_xsl_file = r'C:\FujiFlexa\Client\Report\Definition\FeederReportUnit.xsl'
head_xsl_file = r'C:\FujiFlexa\Client\Report\Definition\FeederReportHead.xsl'

# print(unit_xsl_file)
# print(head_xsl_file)

# rutas archivos (generacion de reportes)
# device_path = r'H:\Publico\SMT-Prog-Status\DEVICES'
# html_path = r'H:\Publico\SMT-Prog-Status\DEVICES\html'


# MainApp Comparador
class ComparadorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # ********************************************* Ventana *******************************
        self.setWindowTitle("Comparador de archivos")
        # Establecer el icono de la ventana
        self.setWindowIcon(QIcon(r'comparador\ui\resources\icons8-compare-60.ico'))  # Reemplaza con la ruta de tu icono
        # cargar estilos
        self.cargarEstilos(r"comparador\ui\resources\style.qss")
        # dimensiones de la ventana
        self.setGeometry(300, 300, 600, 410)
        self.setMaximumSize(600, 410)
        self.setMinimumSize(350 ,400) 
        
        # *************************************************** Tabs *******************************
        # craacion de tabs para divir la app en 3 tabs
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.North)
        tabs.setMovable(False)
        # tabs.setStyleSheet(style)
        
        #**************************************** Tab 1 - Flexa *******************************
        #layout vertical
        layout = QVBoxLayout()
        logo_navico = QLabel("") # instancia de la etiqueta para cargar la imagen
        logo_navico.setPixmap(QPixmap(r"comparador\ui\resources\LOGO_NAVICO_1_90-black.png")) # carga de la imagen
        layout.addWidget(logo_navico)
        
        # seccion horizontal bom
        bom = QHBoxLayout()
        ruta_bom = QLineEdit()
        ruta_bom.setPlaceholderText("Ruta de archivo Bom Syteline")
        ruta_bom.setAlignment(Qt.AlignCenter)
        ruta_bom.setEnabled(False)
        ruta_bom.setStyleSheet("background-color: rgb(222, 222, 222);")
        bom.addWidget(ruta_bom)
        btn_cargar_bom = QPushButton("Cargar Bom")
        btn_cargar_bom.clicked.connect(self.cargar_bom_flexa)
        bom.addWidget(btn_cargar_bom)
        layout.addLayout(bom)
        
        
        # seccion horizontal flexa
        
        flexa = QHBoxLayout()
        ruta_flexa = QLineEdit()
        ruta_flexa.setPlaceholderText("Ruta de archivo Placement Flexa")
        ruta_flexa.setAlignment(Qt.AlignCenter)
        ruta_flexa.setEnabled(False)
        ruta_flexa.setStyleSheet("background-color: rgb(222, 222, 222);")
        flexa.addWidget(ruta_flexa)
        btn_cargar_flexa = QPushButton("Cargar Flexa")
        btn_cargar_flexa.clicked.connect(self.cargar_placement_flexa)
        flexa.addWidget(btn_cargar_flexa)
        layout.addLayout(flexa)
        
        #botones de comparacion
        buttons = QHBoxLayout()
        comparar = QPushButton("Comparar")
        comparar.clicked.connect(self.comparar_archivos)
        editar = QPushButton("Editar")
        editar.clicked.connect(self.editar_archivo)
        cancelar = QPushButton("Cancelar")    
        cancelar.clicked.connect(self.cancelar)
        
        # Ajustar tamaño máximo y mínimo de los botones
        comparar.setMinimumSize(20, 10)
        editar.setMinimumSize(5, 10)
        cancelar.setMinimumSize(5, 10)
        
        # agregar los botones al layout
        buttons.addWidget(comparar)
        buttons.addWidget(editar)
        buttons.addWidget(cancelar)
        layout.addLayout(buttons)
    
        # etiqueta owner
        label_owner_flexa = QLabel("Create by Cristian Echeverria")
        label_owner_flexa.setFont(QFont("Times", 8))
        label_owner_flexa.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_owner_flexa)
        
        
        # Configuraciones del layout
        #alineacion de el layout (horizontal y vertical centrado)
        layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        layout.setContentsMargins(50, 50, 50, 50) # margin
        layout.setSpacing(10) # padding
        
        #**************************************** Tab 2 - Placement *******************************
        #layout vertical
        layout2 = QVBoxLayout()
        logo_navico2 = QLabel("") # instancia de la etiqueta para cargar la imagen
        logo_navico2.setPixmap(QPixmap(r"comparador\ui\resources\LOGO_NAVICO_1_90-black.png")) # carga de la imagen
        layout2.addWidget(logo_navico2)
        
        # seccion horizontal bom
        bom_nexxim = QHBoxLayout()
        ruta_bom_nexxim = QLineEdit()
        ruta_bom_nexxim.setPlaceholderText("Ruta de archivo Bom Syteline")
        ruta_bom_nexxim.setAlignment(Qt.AlignCenter)
        ruta_bom_nexxim.setEnabled(False)
        ruta_bom_nexxim.setStyleSheet("background-color: rgb(222, 222, 222);")
        bom_nexxim.addWidget(ruta_bom_nexxim)
        btn_cargar_bom_nexxim = QPushButton("Cargar Bom")
        btn_cargar_bom_nexxim.clicked.connect(self.cargar_bom_nexxim)
        bom_nexxim.addWidget(btn_cargar_bom_nexxim)
        layout2.addLayout(bom_nexxim)
        
        
        # seccion horizontal flexa
        nexxim = QHBoxLayout()
        ruta_nexxim = QLineEdit()
        ruta_nexxim.setPlaceholderText("Ruta de archivo Placement Nexxim")
        ruta_nexxim.setAlignment(Qt.AlignCenter)
        ruta_nexxim.setEnabled(False)
        ruta_nexxim.setStyleSheet("background-color: rgb(222, 222, 222);")
        nexxim.addWidget(ruta_nexxim)
        btn_cargar_nexxim = QPushButton("Cargar Nexxim")
        btn_cargar_nexxim.clicked.connect(self.cargar_placement_nexxim)
        nexxim.addWidget(btn_cargar_nexxim)
        layout2.addLayout(nexxim)
        
        #botones de comparacion
        buttons_nexxim = QHBoxLayout()
        comparar_nexxim= QPushButton("Comparar")
        comparar_nexxim.clicked.connect(self.comparar_archivos)
        editar_nexxim= QPushButton("Editar")
        editar_nexxim.clicked.connect(self.editar_archivo)
        cancelar_nexxim= QPushButton("Cancelar")   
        cancelar_nexxim.clicked.connect(self.cancelar)
        
         
        # Ajustar tamaño máximo y mínimo de los botones
        comparar_nexxim.setMinimumSize(20, 10)
        editar_nexxim.setMinimumSize(5, 10)
        cancelar_nexxim.setMinimumSize(5, 10)
        
        buttons_nexxim.addWidget(comparar_nexxim)
        buttons_nexxim.addWidget(editar_nexxim)
        buttons_nexxim.addWidget(cancelar_nexxim)
        layout2.addLayout(buttons_nexxim)

        # etiqueta owner
        label_owner_nexxim = QLabel("Create by Cristian Echeverria")
        label_owner_nexxim.setFont(QFont("Times", 8))
        label_owner_nexxim.setAlignment(Qt.AlignCenter)
        layout2.addWidget(label_owner_nexxim)
        
        # Configuraciones del layout
        #alineacion de el layout (horizontal y vertical centrado)
        layout2.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        layout2.setContentsMargins(50, 50, 50, 50) # margin
        layout2.setSpacing(10) # padding
        
        
        #**************************************************** Tab 3 - Bom *****************************************************
        #layout vertical
        layout3 = QVBoxLayout()
        logo_navico3 = QLabel("") # instancia de la etiqueta para cargar la imagen
        logo_navico3.setPixmap(QPixmap(r"comparador\ui\resources\LOGO_NAVICO_1_90-black.png")) # carga de la imagen
        layout3.addWidget(logo_navico3)
        
        # seccion horizontal bom
        bom_izq = QHBoxLayout()
        ruta_izq = QLineEdit()
        ruta_izq.setPlaceholderText("Ruta de archivo Bom Styline (Izq)")
        ruta_izq.setAlignment(Qt.AlignCenter)
        ruta_izq.setEnabled(False)
        ruta_izq.setStyleSheet("background-color: rgb(222, 222, 222);")
        bom_izq.addWidget(ruta_izq)
        btn_cargar_izq = QPushButton("Cargar Bom Izq")
        btn_cargar_izq.clicked.connect(self.cargar_bom_izq)
        bom_izq.addWidget(btn_cargar_izq)
        layout3.addLayout(bom_izq)
        
        # seccion horizontal flexa
        bom_der = QHBoxLayout()
        ruta_der = QLineEdit()
        ruta_der.setPlaceholderText("Ruta de archivo Bom Styline (Der)")
        ruta_der.setAlignment(Qt.AlignCenter)
        ruta_der.setEnabled(False)
        ruta_der.setStyleSheet("background-color: rgb(222, 222, 222);")
        bom_der.addWidget(ruta_der)
        btn_cargar_der = QPushButton("Cargar Bom Der")
        btn_cargar_der.clicked.connect(self.cargar_bom_der)
        bom_der.addWidget(btn_cargar_der)
        layout3.addLayout(bom_der)
        
        #botones de comparacion
        buttons_bom = QHBoxLayout()
        comparar_bom = QPushButton("Comparar")
        editar_bom = QPushButton("Editar")
        cancelar_bom = QPushButton("Cancelar")    
        
        # Ajustar tamaño máximo y mínimo de los botones
        comparar_bom.setMinimumSize(20, 10)
        comparar_bom.clicked.connect(self.comparar_archivos)
        editar_bom.setMinimumSize(5, 10)
        editar_bom.clicked.connect(self.editar_archivo)
        cancelar_bom.setMinimumSize(5, 10)
        cancelar_bom.clicked.connect(self.cancelar)
        
        # agregar los botones al layout
        buttons_bom.addWidget(comparar_bom)
        buttons_bom.addWidget(editar_bom)
        buttons_bom.addWidget(cancelar_bom)
        layout3.addLayout(buttons_bom)
    
        # etiqueta owner
        label_owner_bom = QLabel("Create by Cristian Echeverria")
        label_owner_bom.setFont(QFont("Times", 8))
        label_owner_bom.setAlignment(Qt.AlignCenter)
        layout3.addWidget(label_owner_bom)
        
        
        # Configuraciones del layout
        #alineacion de el layout (horizontal y vertical centrado)
        layout3.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        layout3.setContentsMargins(50, 50, 50, 50) # margin
        layout3.setSpacing(10) # padding
        
        # ********************************************* Configuraciones *********************************************
        # asignar el layout al widget y el widget al tab
        self.flexa_widget = QWidget()
        self.flexa_widget.setLayout(layout)
        tabs.addTab(self.flexa_widget, "Flexa")
        
        self.nexxim_widget = QWidget()
        self.nexxim_widget.setLayout(layout2)
        tabs.addTab(self.nexxim_widget, "Nexxim")
        
        self.bom_widget = QWidget()
        self.bom_widget.setLayout(layout3)
        tabs.addTab(self.bom_widget, "Bom")
        
        # atributos de instancia ( para poder ser llamados desde otra funcion o clase)
        self.ruta_bom = ruta_bom
        self.ruta_flexa = ruta_flexa
        self.ruta_bom_nexxim = ruta_bom_nexxim
        self.ruta_nexxim = ruta_nexxim
        self.ruta_izq = ruta_izq
        self.ruta_der = ruta_der
        self.tabs = tabs
        
        # **************************************** Menu *********************************************
        #intanciar el menú
        menubar = QMenuBar()
        # Menú Archivo
        file_menu = menubar.addMenu("Archivo")

        # Acción Nuevo
        new_action = QAction("Nuevo archivo placement", self)
        new_action.triggered.connect(self.nuevo_archivo)
        file_menu.addAction(new_action)
        
        # Submenú Guardar devices como PDF
        save_pdf_action = QAction("Guardar devices como PDF", self)
        save_pdf_action.triggered.connect(self.guardar_devices_pdf)
        file_menu.addAction(save_pdf_action)
        
        # Submenú Reimprimir devices
        save_pdf_again = QAction("Imprimir Devices", self)
        save_pdf_again.triggered.connect(self.imprimir_devices)
        file_menu.addAction(save_pdf_again)
        
        # Menú Ayuda
        help_menu = menubar.addMenu("Ayuda")

        # Acción Acerca de
        about_action = QAction("Acerca de", self)
        about_action.triggered.connect(self.mostrar_acerca_de)
        help_menu.addAction(about_action)
        
        # Menu Log
        log_menu = menubar.addMenu("Log")
        
        # Acciones Log
        log_action = QAction("Log", self)
        log_action.triggered.connect(self.mostrar_log)
        log_menu.addAction(log_action)
        # agregamos el menu a la ventana
        self.setMenuBar(menubar)
        # **************************************** Tabs to Main *********************************************
        # agregamos el tab a la ventana
        self.setCentralWidget(tabs)
        
    # ****************************************** Funciones ******************************************
    def cargarEstilos(self, archivo_qss):
        '''
        Funcion carga estilos de archivos.qss para 
        aplicarlos a todos los elementos de la ventana
        '''
        estilo = QFile(archivo_qss)
        if estilo.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(estilo)
            self.setStyleSheet(stream.readAll())
            estilo.close()
        else:
            QMessageBox.critical(self, "Error", f"No fue posible cargar el archivo: {archivo_qss}")
         
    def cargar_bom_flexa(self):
        '''
        Funcion cargar archivo bom flexa
        abre una ventana de dialogo para seleccionar el archivo
        '''
        # Abrimos una ventana de seleccion de archivos
        filename = QFileDialog.getOpenFileName(self, 'Select File', '', 'Excel Files (*.xlsx *.xls)')
        # extraemos la ruta del archivo seleccionado para asignarla a una variable de referencia
        if filename[0]:
            ruta = filename[0]
            self.ruta_bom.setText(ruta)
            self.ruta_bom.setEnabled(False)
        else:
            pass
               
    def cargar_placement_flexa(self):
        '''
        Funcion cargar archivo placement flexa
        abre una ventana de dialogo para seleccionar el archivo
        '''
        # Abrimos una ventana de seleccion de archivos
        filename = QFileDialog.getOpenFileName(self, 'Select File', '', 'Excel Files (*.xlsx *.xls)')
        # extraemos la ruta del archivo seleccionado para asignarla a una variable de referencia
        if filename[0]:
            ruta = filename[0]
            #print(ruta)
            self.ruta_flexa.setText(ruta)
            self.ruta_flexa.setEnabled(False)
        else:
            pass
        
    def cargar_bom_nexxim(self):
        '''
        Funcion cargar archivo bom nexxim
        abre una ventana de dialogo para seleccionar el archivo
        '''
        # Abrimos una ventana de seleccion de archivos
        filename = QFileDialog.getOpenFileName(self, 'Select File', '', 'Excel Files (*.xlsx *.xls)')
        # extraemos la ruta del archivo seleccionado para asignarla a una variable de referencia
        if filename[0]:
            ruta = filename[0]
            #print(ruta)
            self.ruta_bom_nexxim.setText(ruta)
            self.ruta_bom_nexxim.setEnabled(False)
        else:
            pass
    
    def cargar_placement_nexxim(self):
        '''
        Funcion cargar archivo placement nexxim
        abre una ventana de dialogo para seleccionar el archivo
        '''
        # Abrimos una ventana de seleccion de archivos
        filename = QFileDialog.getOpenFileName(self, 'Select File', '', 'Excel Files (*.xlsx *.xls)')
        # extraemos la ruta del archivo seleccionado para asignarla a una variable de referencia
        if filename[0]:
            ruta = filename[0]
            #print(ruta)
            self.ruta_nexxim.setText(ruta)
            self.ruta_nexxim.setEnabled(False)
        else:
            pass
    
    def cargar_bom_izq(self):
        '''
        Funcion cargar archivo bom
        abre una ventana de dialogo para seleccionar el archivo
        '''
        # Abrimos una ventana de seleccion de archivos
        filename = QFileDialog.getOpenFileName(self, 'Select File', '', 'Excel Files (*.xlsx *.xls)')
        # extraemos la ruta del archivo seleccionado para asignarla a una variable de referencia
        if filename[0]:
            ruta = filename[0]
            #print(ruta)
            self.ruta_izq.setText(ruta)
            self.ruta_izq.setEnabled(False)
        else:
            pass
    
    def cargar_bom_der(self):
        '''
        Funcion cargar archivo bom
        abre una ventana de dialogo para seleccionar el archivo
        '''
        # Abrimos una ventana de seleccion de archivos
        filename = QFileDialog.getOpenFileName(self, 'Select File', '', 'Excel Files (*.xlsx *.xls)')
        # extraemos la ruta del archivo seleccionado para asignarla a una variable de referencia
        if filename[0]:
            ruta = filename[0]
            #print(ruta)
            self.ruta_der.setText(ruta)
            self.ruta_der.setEnabled(False)
        else:
            pass
    
    # def comparar_flexa(self):
    #     '''
    #     Funcion para comparar archivos
    #     Obtiene las rutas de los archivos y llama a la funcion de comparacion del modulo tools/bom_check.py
    #     un dialogo de alerta informa si se encontraron diferencias
    #     Si se encuentran diferencias, se abre el archivo csv con las diferencias
    #     '''
    #     if self.ruta_bom.text() == "" or self.ruta_flexa.text() == "":
    #         QMessageBox.information(self, 'Alerta', 'Por favor, cargue ambos archivos')
    #         logger.warning("Por favor, cargue ambos archivos")
    #         # dlg = CompareResult(color="tomato",message="Por favor, Cargue ambos archivos")
    #         # dlg.exec()
    #         return
    #     try:
    #         diferences_found,csv_path =bom_check.comparador(self.ruta_bom.text(),self.ruta_flexa.text())
    #         self.ruta_bom.setText("")
    #         self.ruta_flexa.setText("")
    #         if diferences_found is not None:
    #             dlg = CompareResult(color="tomato",message="Se encontraron diferencias! :O")
    #             dlg.exec()
    #             os.startfile(csv_path)
    #         else:
    #             QMessageBox.about(self, 'Resultado', 'No se encontraron diferencias')
    #             logger.info("No se encontraron diferencias")
    #             dlg = CompareResult(color="lightgreen",message="No se encontraron diferencias! :(")
    #             dlg.exec()
    #     except TypeError as te:
    #         QMessageBox.information(self, 'Alerta', "No se continuo con la comparación")
    #         logger.error(f'TypeError: {te}')
    #     except Exception as e:
    #         QMessageBox.critical(self, 'Error', f'Error: {e}')
    #         logger.error(str(e))
    
    # def comparar_nexxim(self):
    #     #Validar funcion con archivos nexxim    
    #     if self.ruta_bom_nexxim.text() == "" or self.ruta_nexxim.text() == "":
    #         QMessageBox.information(self, 'Alerta', 'Por favor, cargue ambos archivos')
    #         logger.warning("Por favor, cargue ambos archivos")
    #         # dlg = CompareResultOK(color="tomato",message="Por favor, Cargue ambos archivos")
    #         # dlg.exec()
    #         return
    #     try:
    #         diferences_found,csv_path =bom_check.comparacion_nexim(self.ruta_bom_nexxim.text(),self.ruta_nexxim.text())
    #         self.ruta_bom.setText("")
    #         self.ruta_flexa.setText("")
    #         if diferences_found is not None:
    #             dlg = CompareResult(color="tomato",message="Se encontraron diferencias! :O")
    #             dlg.exec()
    #             os.startfile(csv_path)
    #         else:
    #             QMessageBox.about(self, 'Resultado', 'No se encontraron diferencias')
    #             dlg = CompareResultOK(color="lightgreen",message="No se encontraron diferencias! :)")
    #             dlg.exec()
    #     except TypeError as te:
    #         logger.error(f'TypeError: {te}')
    #         QMessageBox.information(self, 'Alerta', "No se continuo con la comparación")
    #     except Exception as e:
    #         logger.error(str(e))
    #         QMessageBox.critical(self, 'Error', f'Error: {e}')
    
    # def comparar_boms(self):
    #     if self.ruta_izq.text() == "" or self.ruta_der.text() == "":
    #         QMessageBox.information(self, 'Alerta', 'Por favor, cargue ambos archivos')
    #         logger.warning("Por favor, cargue ambos archivos")
    #         # dlg = CompareResult(color="tomato",message="Por favor, Cargue ambos archivos")
    #         # dlg.exec()
    #         return
    #     try:
    #         diferences_found,csv_path =bom_check.comparacion_bom(self.ruta_izq.text(),self.ruta_der.text())
    #         self.ruta_izq.setText("")
    #         self.ruta_der.setText("")
    #         if diferences_found is not None:
    #             dlg = CompareResult(color="tomato",message="Se encontraron diferencias! :O")
    #             dlg.exec()
    #             os.startfile(csv_path)
    #         else:
    #             QMessageBox.about(self, 'Resultado', 'No se encontraron diferencias :)')
    #             dlg = CompareResult(color="lightgreen",message="No se encontraron diferencias!")
    #             dlg.exec()
    #     except TypeError as te:
    #         QMessageBox.information(self, 'Alerta', "No se continuo con la comparación")
    #         logger.error(f'TypeError: {te}')
    #     except Exception as e:
    #         QMessageBox.critical(self, 'Error', f'Error: {e}')
    #         logger.error(str(e))
    
    def comparar_archivos(self):
        # Si tab se encuentra en Flexa
        if self.tabs.currentIndex() == 0:
            if self.ruta_bom.text() == "" or self.ruta_flexa.text() == "":
                QMessageBox.information(self, 'Alerta', 'Por favor, cargue ambos archivos')
                logger.warning("Por favor, cargue ambos archivos")
                # dlg = CompareResult(color="tomato",message="Por favor, Cargue ambos archivos")
                # dlg.exec()
                return
            try:
                diferences_found,csv_path =bom_check.comparador(self.ruta_bom.text(),self.ruta_flexa.text())
                self.ruta_bom.setText("")
                self.ruta_flexa.setText("")
                if diferences_found is not None:
                    dlg = CompareResult(color="tomato",message="Se encontraron diferencias! :O")
                    dlg.exec()
                    os.startfile(csv_path)
                else:
                    QMessageBox.about(self, 'Resultado', 'No se encontraron diferencias')
                    logger.info("No se encontraron diferencias")
                    dlg = CompareResult(color="lightgreen",message="No se encontraron diferencias! :(")
                    dlg.exec()
            except TypeError as te:
                QMessageBox.information(self, 'Alerta', "No se continuo con la comparación")
                logger.error(f'TypeError: {te}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Error: {e}')
                logger.error(str(e))
        
        # si tab se encuentra en Nexxim
        elif self.tabs.currentIndex() == 1:
            #Validar funcion con archivos nexxim    
            if self.ruta_bom_nexxim.text() == "" or self.ruta_nexxim.text() == "":
                QMessageBox.information(self, 'Alerta', 'Por favor, cargue ambos archivos')
                logger.warning("Por favor, cargue ambos archivos")
                # dlg = CompareResultOK(color="tomato",message="Por favor, Cargue ambos archivos")
                # dlg.exec()
                return
            try:
                diferences_found,csv_path =bom_check.comparacion_nexim(self.ruta_bom_nexxim.text(),self.ruta_nexxim.text())
                self.ruta_bom_nexxim.setText("")
                self.ruta_nexxim.setText("")
                if diferences_found is not None:
                    dlg = CompareResult(color="tomato",message="Se encontraron diferencias! :O")
                    dlg.exec()
                    os.startfile(csv_path)
                else:
                    QMessageBox.about(self, 'Resultado', 'No se encontraron diferencias')
                    dlg = CompareResultOK(color="lightgreen",message="No se encontraron diferencias! :)")
                    dlg.exec()
            except TypeError as te:
                logger.error(f'TypeError: {te}')
                QMessageBox.information(self, 'Alerta', "No se continuo con la comparación")
            except Exception as e:
                logger.error(str(e))
                QMessageBox.critical(self, 'Error', f'Error: {e}')
                
        # si tab se encuentra en Bom
        elif self.tabs.currentIndex() == 2:
            if self.ruta_izq.text() == "" or self.ruta_der.text() == "":
                QMessageBox.information(self, 'Alerta', 'Por favor, cargue ambos archivos')
                logger.warning("Por favor, cargue ambos archivos")
                # dlg = CompareResult(color="tomato",message="Por favor, Cargue ambos archivos")
                # dlg.exec()
                return
            try:
                diferences_found,csv_path =bom_check.comparacion_bom(self.ruta_izq.text(),self.ruta_der.text())
                self.ruta_izq.setText("")
                self.ruta_der.setText("")
                if diferences_found is not None:
                    dlg = CompareResult(color="tomato",message="Se encontraron diferencias! :O")
                    dlg.exec()
                    os.startfile(csv_path)
                else:
                    QMessageBox.about(self, 'Resultado', 'No se encontraron diferencias :)')
                    dlg = CompareResult(color="lightgreen",message="No se encontraron diferencias!")
                    dlg.exec()
            except TypeError as te:
                QMessageBox.information(self, 'Alerta', "No se continuo con la comparación")
                logger.error(f'TypeError: {te}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Error: {e}')
                logger.error(str(e))
        
    # def editar_flexa(self):
    #     dlg = EditarDlg(color="white", message="Archivo a editar?", text_boton_izq="Bom", text_boton_der="Flexa")
    #     if dlg.exec() == QDialog.Accepted:
    #         resultado = dlg.obtener_resultado()
    #         if resultado == "Bom":
    #             if self.ruta_bom.text() != "":    
    #                 try:
    #                     os.startfile(self.ruta_bom.text())
    #                 except Exception as e:
    #                     QMessageBox.critical(self, 'Error', f'Error: {e}')
    #                     logger.error(str(e))
    #             else:
    #                 QMessageBox.information(self, 'Alerta', 'Por favor, cargue al menos un archivo')
    #         elif resultado == "Flexa":
    #             if self.ruta_flexa.text() != "":
    #                 try:
    #                     os.startfile(self.ruta_flexa.text())
    #                 except Exception as e:
    #                     QMessageBox.critical(self, 'Error', f'Error: {e}')
    #                     logger.error(str(e))
    #             else:
    #                 QMessageBox.information(self, 'Alerta', 'Por favor, cargue al menos un archivo')
    #     else:
    #         QMessageBox.information(self, 'Alerta', 'Por favor, cargue ambos archivos')
    
    # def editar_nexxim(self):
    #     dlg = EditarDlg(color="white", message="Archivo a editar?", text_boton_izq="Bom", text_boton_der="Nexxim")
    #     if dlg.exec() == QDialog.Accepted:
    #         resultado = dlg.obtener_resultado()
    #         if resultado == "Bom":
    #             if self.ruta_bom_nexxim.text() != "":    
    #                 try:
    #                     os.startfile(self.ruta_bom_nexxim.text())
    #                 except Exception as e:
    #                     QMessageBox.critical(self, 'Error', f'Error: {e}')
    #                     logger.error(str(e))
    #             else:
    #                 QMessageBox.information(self, 'Alerta', 'Por favor, cargue al menos un archivo')
    #         elif resultado == "Nexxim":
    #             if self.ruta_nexxim.text() != "":
    #                 try:
    #                     os.startfile(self.ruta_nexxim.text())
    #                 except Exception as e:
    #                     QMessageBox.critical(self, 'Error', f'Error: {e}')
    #                     logger.error(str(e))
    #             else:
    #                 QMessageBox.information(self, 'Alerta', 'Por favor, cargue al menos un archivo')
    #     else:
    #         QMessageBox.information(self, 'Alerta', 'Por favor, cargue ambos archivos')

    # def editar_boms(self):
    #     #print(self.tabs.currentIndex())
    #     dlg = EditarDlg(color="white", message="Archivo a editar?", text_boton_izq="Bom izq", text_boton_der="Bom der")
    #     if dlg.exec() == QDialog.Accepted:
    #         resultado = dlg.obtener_resultado()
    #         if resultado == "Bom izq":
    #             if self.ruta_izq.text() != "":    
    #                 try:
    #                     os.startfile(self.ruta_izq.text())
    #                 except Exception as e:
    #                     QMessageBox.critical(self, 'Error', f'Error: {e}')
    #                     logger.error(str(e))
    #             else:
    #                 QMessageBox.information(self, 'Alerta', 'Por favor, cargue al menos un archivo')
    #         elif resultado == "Bom der":
    #             if self.ruta_der.text() != "":
    #                 try:
    #                     os.startfile(self.ruta_der.text())
    #                 except Exception as e:
    #                     QMessageBox.critical(self, 'Error', f'Error: {e}')
    #                     logger.error(str(e))
    #             else:
    #                 QMessageBox.information(self, 'Alerta', 'Por favor, cargue al menos un archivo')
    #     else:
    #         QMessageBox.information(self, 'Alerta', 'Por favor, cargue ambos archivos')
    
    def editar_archivo(self):
        # si tab se encuentra en Flexa
        if self.tabs.currentIndex() == 0:
            dlg = EditarDlg(color="white", message="Archivo a editar?", text_boton_izq="Bom", text_boton_der="Flexa")
            if dlg.exec() == QDialog.Accepted:
                resultado = dlg.obtener_resultado()
                if resultado == "Bom":
                    if self.ruta_bom.text() != "":    
                        try:
                            os.startfile(self.ruta_bom.text())
                        except Exception as e:
                            QMessageBox.critical(self, 'Error', f'Error: {e}')
                            logger.error(str(e))
                    else:
                        QMessageBox.information(self, 'Alerta', 'Por favor, cargue al menos un archivo')
                elif resultado == "Flexa":
                    if self.ruta_flexa.text() != "":
                        try:
                            os.startfile(self.ruta_flexa.text())
                        except Exception as e:
                            QMessageBox.critical(self, 'Error', f'Error: {e}')
                            logger.error(str(e))
                    else:
                        QMessageBox.information(self, 'Alerta', 'Por favor, cargue al menos un archivo')
            else:
                pass
                #QMessageBox.information(self, 'Alerta', 'Por favor, cargue ambos archivos')
        # si tab se encuentra en Nexxim
        elif self.tabs.currentIndex() == 1:
            dlg = EditarDlg(color="white", message="Archivo a editar?", text_boton_izq="Bom", text_boton_der="Nexxim")
            if dlg.exec() == QDialog.Accepted:
                resultado = dlg.obtener_resultado()
                if resultado == "Bom":
                    if self.ruta_bom_nexxim.text() != "":    
                        try:
                            os.startfile(self.ruta_bom_nexxim.text())
                        except Exception as e:
                            QMessageBox.critical(self, 'Error', f'Error: {e}')
                            logger.error(str(e))
                    else:
                        QMessageBox.information(self, 'Alerta', 'Por favor, cargue al menos un archivo')
                elif resultado == "Nexxim":
                    if self.ruta_nexxim.text() != "":
                        try:
                            os.startfile(self.ruta_nexxim.text())
                        except Exception as e:
                            QMessageBox.critical(self, 'Error', f'Error: {e}')
                            logger.error(str(e))
                    else:
                        QMessageBox.information(self, 'Alerta', 'Por favor, cargue al menos un archivo')
            else:
                pass
                #QMessageBox.information(self, 'Alerta', 'Por favor, cargue ambos archivos')
        # si tab se encuentra en Bom
        elif self.tabs.currentIndex() == 2:
            dlg = EditarDlg(color="white", message="Archivo a editar?", text_boton_izq="Bom izq", text_boton_der="Bom der")
            if dlg.exec() == QDialog.Accepted:
                resultado = dlg.obtener_resultado()
                if resultado == "Bom izq":
                    if self.ruta_izq.text() != "":    
                        try:
                            os.startfile(self.ruta_izq.text())
                        except Exception as e:
                            QMessageBox.critical(self, 'Error', f'Error: {e}')
                            logger.error(str(e))
                    else:
                        QMessageBox.information(self, 'Alerta', 'Por favor, cargue al menos un archivo')
                elif resultado == "Bom der":
                    if self.ruta_der.text() != "":
                        try:
                            os.startfile(self.ruta_der.text())
                        except Exception as e:
                            QMessageBox.critical(self, 'Error', f'Error: {e}')
                            logger.error(str(e))
                    else:
                        QMessageBox.information(self, 'Alerta', 'Por favor, cargue al menos un archivo')
            else:
                pass
                #QMessageBox.information(self, 'Alerta', 'Por favor, cargue ambos archivos')
                
    # def cancelar_flexa(self):
    #     self.ruta_bom.setText("")
    #     self.ruta_flexa.setText("")     
        
    # def cancelar_nexxim(self):
    #     self.ruta_bom_nexxim.setText("")
    #     self.ruta_nexxim.setText("")
    
    # def cancelar_boms(self):
        self.ruta_izq.setText("")
        self.ruta_der.setText("")
    
    def cancelar(self):
        # si tab se encuentra en Flexa
        if self.tabs.currentIndex() == 0:
            self.ruta_bom.setText("")
            self.ruta_flexa.setText("")
        
        # si tab se encuentra en Nexxim
        elif self.tabs.currentIndex() == 1:
            self.ruta_bom_nexxim.setText("")
            self.ruta_nexxim.setText("")
            
        # si tab se encuentra en Bom
        elif self.tabs.currentIndex() == 2:
            self.ruta_izq.setText("")
            self.ruta_der.setText("")
            
    def nuevo_archivo(self):
        # crea un archivo excel en blanco en la ruta de downloads
        archivo = openpyxl.Workbook()
        nombre_archivo = QInputDialog.getText(self,
            title := "Nombre del archivo",
            label := "Ensamble a comparar",)
        archivo.save(f"C:\\Users\\CECHEVARRIAMENDOZA\\Downloads\\{nombre_archivo[0]}.xlsx")
        #os.startfile(r"C:\Users\CECHEVARRIAMENDOZA\Downloads\prueba.xlsx")
        self.ruta_flexa.setText(f"C:\\Users\\CECHEVARRIAMENDOZA\\Downloads\\{nombre_archivo[0]}.xlsx")

    #funciones de menu editar ( no disponibles )
    # def editar_boms(self):
    #     if self.tabs.currentIndex() == 0:
    #         # funcion abre el archivo de la ruta seleccionada para su edicion
    #         if self.ruta_bom.text() != "":
    #             os.startfile(self.ruta_bom.text())
    #         else:
    #             QMessageBox.information(self, 'Alerta', 'Por favor, cargue al menos un archivo')
    #     elif self.tabs.currentIndex() == 1:
    #         # funcion abre el archivo de la ruta seleccionada para su edicion
    #         if self.ruta_bom_nexxim.text() != "":
    #             os.startfile(self.ruta_bom_nexxim.text())
    #         else:
    #             QMessageBox.information(self, 'Alerta', 'Por favor, cargue al menos un archivo')
    #     elif self.tabs.currentIndex() == 2:
    #         # funcion abre el archivo de la ruta seleccionada para su edicion
    #         dlg = EditarDlg(color="white", message="Archivo a editar?", text_boton_izq="Bom izq", text_boton_der="Bom der")   
    #         if dlg.exec() == QDialog.Accepted:
    #             resultado = dlg.obtener_resultado()
    #             if resultado == "Bom izq":
    #                 if self.ruta_izq.text() != "":
    #                     os.startfile(self.ruta_izq.text())
    #                 else:
    #                     QMessageBox.information(self, 'Alerta', 'Por favor, cargue al menos un archivo')
    #             else:
    #                 if self.ruta_der.text() != "":
    #                     os.startfile(self.ruta_der.text())
    #                 else:
    #                     QMessageBox.information(self, 'Alerta', 'Por favor, cargue al menos un archivo')
                        
    # def editar_placements(self):
    #     # funcion abre el archivo de la ruta seleccionada para su edicion
    #     if self.ruta_flexa.text() != "":
    #         os.startfile(self.ruta_flexa.text())
    #     else:
    #         QMessageBox.information(self, 'Alerta', 'Por favor, cargue al menos un archivo')

    # def editar_bom_nexxim(self):
    #     # funcion abre el archivo de la ruta seleccionada para su edicion
    #     if self.ruta_bom_nexxim.text() != "":
    #         os.startfile(self.ruta_bom_nexxim.text())
    #     else:
    #         QMessageBox.information(self, 'Alerta', 'Por favor, cargue al menos un archivo')
    
    # def editar_placement_nexxim(self):
    #     # funcion abre el archivo de la ruta seleccionada para su edicion
    #     if self.ruta_nexxim.text() != "":
    #         os.startfile(self.ruta_nexxim.text())
    #     else:
    #         QMessageBox.information(self, 'Alerta', 'Por favor, cargue al menos un archivo')
        
    def mostrar_acerca_de(self):
        #print("Mostrar Acerca de seleccionado")
        dlg = AboutDlg()
        dlg.exec()
        
    def mostrar_log(self):
        dlg = LogsDlg()
        dlg.exec()
    
    def guardar_devices_pdf(self):
        # Crear una instancia de QFileDialog
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Archivos XML(*.xml)")
        file_dialog.setViewMode(QFileDialog.List)
        file_dialog.setDirectory("C:\FujiFlexa\Client\Report\Jobdata") # directorio default de apertura
        
        if file_dialog.exec():
            list_files = file_dialog.selectedFiles()
            # Filtrando archivos que contienen "FeederReport"
            files_filter = [file for file in list_files if "FeederReport" in file]

            print(files_filter)
            
            # segundo filtro
            # Categorizar archivos en listas basadas en 'head' y 'unit'
            head_files = {'B': [], 'T': []}
            unit_files = {'B': [], 'T': []}
            
            for file in files_filter:
                if 'Head_' in file:
                    if file.endswith("Head_T.xml"):
                        head_files['T'].append(file)
                    elif file.endswith("Head_B.xml"):
                        head_files['B'].append(file)
                elif 'Unit_' in file:
                    if file.endswith("Unit_T.xml"):
                        unit_files['T'].append(file)
                    elif file.endswith("Unit_B.xml"):
                        unit_files['B'].append(file)
                        
            # Mostrar las listas categorizadas para depuración
            print("Archivos 'head_B':", head_files['B'])
            print("Archivos 'head_T':", head_files['T'])
            print("Archivos 'unit_B':", unit_files['B'])
            print("Archivos 'unit_T':", unit_files['T'])
            
            # Verificar que hay un número par de archivos en cada categoría
            if (len(head_files['B']) != len(unit_files['B'])) or (len(head_files['T']) != len(unit_files['T'])):
                QMessageBox.warning(self, "Error", "La cantidad de archivos 'head' y 'unit' debe ser la misma para cada categoría.")
                return
            
            # Generar reportes HTML para cada combinación de archivos 'head' y 'unit'
            devices = []
            report_number = 1
            for head_type in ['B', 'T']:
                for unit_type in ['B', 'T']:
                    while head_files[head_type] and unit_files[unit_type]:
                        head_file = head_files[head_type].pop(0)
                        unit_file = unit_files[unit_type].pop(0)
                        
                        # Llama a la función para generar el reporte HTML
                        html_output = convertir_xlm_html.generate_html_report(base_path, css_path, logo_path, head_file, head_xsl_file, unit_file, unit_xsl_file)
                        #print(html_output)
                        # Guardar el reporte HTML generado
                        # Extraer el nombre del archivo antes del primer guion bajo
                        
                        #base_name = os.path.basename(head_file).split('_')[0]
                        base_name = html_output[1]
                        print(f"Base name: {base_name}")
                        #base_name_suffix = f"{base_name}_{head_type}"
                        base_name_suffix = f'{base_name}_{head_type}'
                        print(f"Base name suffix: {base_name_suffix}")
                        output_file = r'H:\Publico\SMT-Prog-Status\DEVICES\reportes_html\{base_name_suffix}.html'.format(base_name_suffix=base_name_suffix)
                        # output en comparador\ui\resources\reportes_html para probar
                        with open(output_file, 'w', encoding='utf-8') as file:
                            file.write(html_output[0])
                            devices.append(output_file)
                            
                        print(f"El archivo HTML '{base_name_suffix}' ha sido generado con éxito.")
                        report_number += 1
            
            self.convertir_a_pdf(devices)
        
    def imprimir_devices(self):
        # Crear una instancia de QFileDialog
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Archivos PDF (*.pdf)")
        file_dialog.setDirectory("H:\Publico\SMT-Prog-Status\DEVICES")
        #comparador\ui\resources\reportes_html para probar
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            # Obtener la ruta de la carpeta de los archivos seleccionados
            folder_path = os.path.dirname(selected_files[0])
            # Crear el nombre del archivo de salida
            output_filename = "devices_merged.pdf"
            # Combinar la ruta de la carpeta con el nombre del archivo de salida
            salida_pdf = os.path.join(folder_path, output_filename)
            # Llamar a las funciones para fusionar e imprimir los PDFs
            auto_print.fusionar_pdfs(selected_files, salida_pdf)
            auto_print.imprimir_pdf(salida_pdf)   
                  
        
    def convertir_a_pdf(self, files_to_convert):
        if not files_to_convert:
            return

        asyncio.run(self.convertir_html_a_pdf(files_to_convert))
    
    async def convertir_html_a_pdf(self, files_to_convert):
        progress_dialog = QProgressDialog("Generando PDFs...", "Cancelar", 0, len(files_to_convert), self)
        progress_dialog.setWindowTitle("Progreso")
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.show()

        for i, file_path in enumerate(files_to_convert):
            if progress_dialog.wasCanceled():
                break

            file_name = os.path.basename(file_path)
            #remover html del texto del nombre         
            file_name = file_name.replace('.html', '')
            file_prefix = file_name.split('_')[0]  # Asumiendo que el prefijo es la parte antes del primer guión bajo
            devices_path = r"H:\Publico\SMT-Prog-Status\DEVICES" #comparador\ui\resources\reportes_html para probar
            output_dir = os.path.join(devices_path, file_prefix)

            if not os.path.exists(output_dir):
                os.makedirs(output_dir)  # Crear la carpeta si no existe

            output_path = os.path.join(output_dir, f'{file_name}.pdf')

            await self.url_to_pdf(file_path, output_path)

            progress_dialog.setValue(i + 1)
            progress_dialog.setLabelText(f"Generando {file_name}...")

        progress_dialog.close()
    
    async def url_to_pdf(self, url, output_path):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)
            await page.pdf(path=output_path)
            await browser.close()
            print(f'Convertido {url} a {output_path}')
           
            
# Dialogos personalizados
class CompareResult(QDialog):
    def __init__(self, parent=None,color="lightgreen",message="No se encontraron diferencias"):
        super().__init__(parent)
        self.setGeometry(450,450,300, 100)
        self.setWindowIcon(QIcon(r'comparador\ui\resources\icons8-compare-60.ico'))  
        # Configurar el fondo verde
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)
        
        # Configurar el diseño del diálogo
        layout = QVBoxLayout(self)
        
        # Texto informativo
        label = QLabel(message, self)
        label.setStyleSheet("font-size: 15px; font-weight: italic;color: black;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        # Botón de aceptar
        #ok_button = QPushButton("Aceptar", self)
        #layout.addWidget(ok_button)
        
        self.setWindowTitle("Alerta")
        
class EditarDlg(QDialog):
    def __init__(self, parent=None, color="white", message="Archivo a editar?", text_boton_izq="Bom", text_boton_der="Flexa"):
        super().__init__(parent)
        self.setWindowTitle("Alerta")
        self.setWindowIcon(QIcon(r'comparador\ui\resources\icons8-compare-60.ico')) 
        self.setGeometry(450, 450, 200, 100)  # Ajusta el tamaño según necesites
        
        # Configurar el fondo
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)
        
        # Configurar el diseño del diálogo
        layout = QVBoxLayout(self)
        
        # Texto informativo
        label = QLabel(message, self)
        label.setStyleSheet("font-size: 15px; font-weight: italic;color: black;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        # Botones
        botones_layout = QHBoxLayout()
        self.boton_izq = QPushButton(text_boton_izq, self)
        self.boton_izq.clicked.connect(self.on_boton_izq_click)
        self.boton_der = QPushButton(text_boton_der, self)
        self.boton_der.clicked.connect(self.on_boton_der_click)
        botones_layout.addWidget(self.boton_izq)
        botones_layout.addWidget(self.boton_der)
        layout.addLayout(botones_layout)
        
        # Atributo para almacenar el resultado del botón presionado
        self.resultado = None

    def on_boton_izq_click(self):
        self.resultado = self.boton_izq.text()
        self.accept()

    def on_boton_der_click(self):
        self.resultado = self.boton_der.text()
        self.accept()

    def obtener_resultado(self):
        return self.resultado

class AboutDlg(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(450,450,300, 200)
        self.setMaximumHeight(200)
        self.setMinimumHeight(200)
        self.setMinimumWidth(300)
        self.setMaximumWidth(300)
        self.setWindowTitle("Acerca de")
        self.setWindowIcon(QIcon(r'comparador\ui\resources\icons8-compare-60.ico'))  
        
        # Crear un objeto QPalette
        palette = self.palette()

        # Crear un gradiente lineal
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor("#0F2027"))  # Color inicial del gradiente (blanco)
        gradient.setColorAt(1.0, QColor("#2C5364"))      # Color final del gradiente (verde)

        # Establecer el fondo como el gradiente
        palette.setBrush(QPalette.Window, gradient)
        self.setPalette(palette)
        
        # Configurar el diseño del diálogo
        layout = QVBoxLayout(self)
        titulo = QLabel("Comparador de archivos")
        titulo.setStyleSheet("font-size: 20px; font-weight: bold;color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        # Texto informativo
        label = QLabel("""SOFTWARE UTILIZADO: \n- PySide6\n- Python 3.12 \n- Pandas\n- Openpyxl\nDESARROLLADO POR: \nC.Echevarria Mendoza \nCONTACTO: \nhttps://github.com/Echxvx2610""",self)
        label.setStyleSheet("font-size: 12px; font-weight: italic;color: white;")
        alignment = Qt.AlignLeft | Qt.AlignVCenter
        label.setAlignment(alignment)
        layout.addWidget(label)
        
        
        self.setWindowTitle("Alerta")     

class CustomMessageBox(QDialog):
    def __init__(self):
        super().__init__()

        # Configurar el mensaje personalizado
        self.show_custom_message()

    def show_custom_message(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Message Box Personalizada")
        msg_box.setText("Esta es una alerta personalizada con un icono.")  
        self.setWindowIcon(QIcon(r'comparador\ui\resources\compare_4222.ico'))  
        
        # Establecer un icono personalizado
        custom_icon = QPixmap(r"comparador\ui\resources\compare_4222.ico")  # Reemplaza con la ruta a tu icono
        msg_box.setIconPixmap(custom_icon)

        # Configurar botones
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg_box.setDefaultButton(QMessageBox.Ok)

        # Mostrar el cuadro de mensaje
        result = msg_box.exec()
        if result == QMessageBox.Ok:
            print("OK clicked")
        elif result == QMessageBox.Cancel:
            print("Cancel clicked")

class LogsDlg(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(r'comparador\ui\resources\icons8-compare-60.ico'))
        self.setWindowTitle("Logs")
        
        # Carga el archivo log
        with open(r'H:\Ingenieria\SMT\Flexa_vs_BOM\comp.log', 'r') as f:
            contents = f.read()
        
        # Configura el QTextEdit
        self.textEdit = QTextEdit()
        self.textEdit.setReadOnly(True)
        self.textEdit.setText(contents)
        
        # Aplica colores según las palabras clave
        self.apply_format('INFO', QColor(Qt.blue))
        self.apply_format('DEBUG', QColor(Qt.yellow))
        self.apply_format('ERROR', QColor(Qt.red))
        self.apply_format("skip", QColor(Qt.magenta))
        self.apply_format("sin asignar", QColor(Qt.darkGreen))
        
        # Configura el layout
        layout = QVBoxLayout()
        layout.addWidget(self.textEdit)
        self.setLayout(layout)
        self.show()
    
    def apply_format(self, keyword, color):
        cursor = self.textEdit.textCursor()
        format = QTextCharFormat()
        format.setForeground(color)
        
        # Busca la palabra clave y aplica el formato
        cursor.beginEditBlock()
        while not cursor.isNull() and not cursor.atEnd():
            cursor = self.textEdit.document().find(keyword, cursor)
            if not cursor.isNull():
                cursor.mergeCharFormat(format)
        cursor.endEditBlock()
    
app = QApplication(sys.argv)

window = ComparadorApp()

window.show()
app.exec()