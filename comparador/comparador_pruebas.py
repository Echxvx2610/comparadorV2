import pandas as pd
import openpyxl
from openpyxl import workbook,load_workbook
import csv
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import os
import functools as ft
import sys
import os
from tools import logger
import sqlite3

#configuracion de logger
logger = logger.setup_logger(r'H:\Ingenieria\SMT\Flexa_vs_BOM\comp.log')
#logger = logger.setup_logger(r'introduccion QT\comparador\tools\comp.log')

#......................:::: CONFIGURACION DEL DATAFRAME ::: :..................
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
#pd.set_option('expand_frame_repr', False)

#...........................:::: Variales Globales ::::....................
skipeados = ""
data_to_display = ""

# Clave maestra definida por el usuario
MASTER_KEY = "15310"

def create_database():
    connection = sqlite3.connect('usuarios.db')
    cursor = connection.cursor()

    # Crear tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    connection.commit()
    connection.close()
    
create_database()

def comparador(ruta_bom, ruta_flexa):
    logger.info(f"Comienza la comparacion con el archivo {ruta_flexa} vs {ruta_bom}")
    
    # Carga y conversión de Excel a DataFrame
    syteline = pd.read_excel(ruta_bom, engine='openpyxl')
    bom = pd.DataFrame(syteline)
    bom.rename(columns={'Designators ': 'Reference', 'Item': 'Part Number'}, inplace=True)
    bom = bom[['Level', 'Operation', 'Part Number', 'Description', 'Reference', 'Quantity']]
    bom_op20 = bom[bom['Operation'] == 20.0]
    bom_op10 = bom[bom['Operation'] == 10.0]
    
    bom_filter = bom_op20.merge(bom_op10, how='outer')
    #bom_filter = bom_filter[~bom_filter['Part Number'].str.startswith('051-')]
    bom_filter['Reference'] = bom_filter['Reference'].str.split()
    
    # Si hay elementos con un valor 2 en el level se descarta el elemento
    bom_filter = bom_filter[bom_filter['Level'] != 2]
    
    bom_filter = bom_filter.explode('Reference')
    bom_filter.reset_index(drop=True, inplace=True)
    
    #print(bom_filter["Operation"].unique())
    
    #***************************************** Solder Filter *****************************************
    # Verificar si el número de parte '140-0704-00' está en las operaciones 10 y/o 20
    op10_filter = bom_filter[(bom_filter['Part Number'] == '140-0704-00') & (bom_filter['Operation'] == 10.0) & (bom_filter['Quantity'] > 0)]

    op20_filter = bom_filter[(bom_filter['Part Number'] == '140-0704-00') & (bom_filter['Operation'] == 20.0) & (bom_filter['Quantity'] > 0)]
    
    # print(op10_filter)
    # print(op20_filter)
    
    # Determinar si el bom tiene Operation 10 y 20, solo 10, o solo 20
    operations = bom_filter['Operation'].unique()

    mensaje = ""

    if 10.0 in operations and 20.0 in operations:
        if op10_filter.empty or op20_filter.empty:
            mensaje = "Soldadura: '140-0704-00' no se encuentra en las operaciones 10 o 20"
    elif 10.0 in operations:
        if op10_filter.empty:
            mensaje = "Soldadura: '140-0704-00' no se encuentra en la operacion 10"
    elif 20.0 in operations:
        if op20_filter.empty:
            mensaje = "Soldadura: '140-0704-00' no se encuentra en la operacion 20"
            
    # Mostrar mensaje de error y manejar autenticación si es necesario
    if mensaje:
        logger.error(mensaje)
        QMessageBox.critical(None, "Error", mensaje)
        
        if show_confirmation_dialog():
            dialog = LoginDialog()
            if dialog.exec() and dialog.authenticated[0]:
                logger.info(f"Autenticación correcta por {dialog.authenticated[1]}. Continuando...")
                pass  # Continuar con la ejecución
            else:
                logger.warning("Autenticación fallida o cancelada. Operación detenida.")
                QMessageBox.critical(None, "Error", "Autenticación fallida o cancelada. Operación detenida.")
                return  # Detener la función si no se autentica correctamente
        else:
            return  # Detener la función si se cancela la autenticación
        
    # bom_filter = bom_filter[['Level','Operation','Part Number','Description','Reference']]
    bom_filter = bom_filter[['Operation','Part Number','Description','Reference']]
    
    #print(bom_filter)
    #bom_filter.to_csv(r'C:\Users\CECHEVARRIAMENDOZA\OneDrive - Brunswick Corporation\Documents\Proyectos_Python\PysimpleGUI\Proyectos\comparador\csv\bom_filter.csv',index=False)
    #******************************************************************* PLACEMENT ******************************************************************
    #Carga y conversion de placement flexa a dataframe
    flexa = pd.read_excel(ruta_flexa, engine='openpyxl')                                                # leemos el archivo excel de flexa
    placement = pd.DataFrame(flexa)                                                                     # convertimos a dataframe
    placement.rename(columns={'Ref.':'Reference'},inplace=True)                                         # Renombramos columna(Ref. a Reference)
    
    placement = placement[['Board','Part Number','Reference','Skip','Assign']]                          # Seleccionamos las columnas deseadas
    placement_carrusel = placement[['Board','Part Number','Assign']]                          # Seleccionamos las columnas deseadas para carrusel
    #print(placement_carrusel)
    
    # validar si hay componentes con skip
    if "Yes" in placement['Skip'].values:
        QMessageBox.warning(None, "Componentes Skip", "Se han encontrado componentes con skip en el archivo!")
        skipeados = placement[placement['Skip'] == 'Yes']
        skipeados = skipeados[['Board', 'Part Number', 'Reference', 'Assign']]
        logger.info(f"Se encontraron {len(skipeados)} componentes sin asignar, no.parte {skipeados['Part Number'].values} y referencia {skipeados['Reference'].values}")
        data_to_display = skipeados.values.tolist()
        TableDialog.show_table(data_to_display, skipeados)
        respuesta = QMessageBox.question(None, "Alerta", "¿Desea continuar con la comparación?", QMessageBox.Yes | QMessageBox.No)  
        if respuesta == QMessageBox.Yes:
            logger.info(f"Se decidió continuar con la comparación del archivo {ruta_flexa}")
            # Adaptar comparación + componentes skipeados
            pass
        else:
            logger.info(f"No se realizó la comparación del archivo {ruta_flexa}")
            # Salir del programa si no se desea continuar
            return
    
    # validar si hay componentes sin asignar ( valores nan)
    if placement['Assign'].isna().any():
        # Si se encuentra vacio el assign para un no.part en el archivo
        #logger.info(f'Se reviso archivo placement {ruta_flexa} y se encontraron componentes sin asignar')
        QMessageBox.warning(None,"Componentes sin asignar","Se han encontrado componentes sin asignar en el archivo!")
        sin_asignar = placement[placement['Assign'].isna()]
        logger.info(f"Se encontraron {len(sin_asignar)} componentes sin asignar, no.parte {sin_asignar['Part Number'].values} y referencia {sin_asignar['Reference'].values}")
        sin_asignar = sin_asignar[['Board','Part Number','Reference','Assign']]
        data_to_display = sin_asignar.values.tolist()                                                   # convertimos a lista todos los elementos sin asignar
        TableDialog.show_table(data_to_display, sin_asignar)                                                          # creamos la tabla y desplegamos la tabla
        
        #alerta
        #respuesta = sg.popup_yes_no("Desea continuar?",title=title)
        respuesta = QMessageBox.question(None, "Alerta", "¿Desea continuar con la comparación?", QMessageBox.Yes | QMessageBox.No)  
        if respuesta == QMessageBox.Yes:
            logger.info(f"Se decidio continuar con la comparacion del archivo {ruta_flexa}")
            #adaptar comparacion + componentes sin asignar
            pass
        else:
            logger.info(f"No se realizo la comparacion del archivo {ruta_flexa}")
            # salimos del programa si no quiere continuar
            return 
    #******************************************************************* COMPARACION ******************************************************************
    comparacion = bom_filter.merge(placement, on = ['Part Number','Reference'], how='outer',suffixes=('_izq', '_der'), indicator=True)          # Juntamos los dataframes
    comparacion.rename(columns={'_merge':'Comparacion'},inplace=True)                                                                           # renombramos la columna merge por Comparacion
    comparacion['Comparacion'] = comparacion['Comparacion'].replace({                                                                           # personalizamos la columna comparacion
    'left_only': 'Solo en BOM',
    'right_only': 'Solo en Placement',
    'both': 'En ambos archivos'
    })
    
    only_bom = comparacion[comparacion['Comparacion'] == 'left_only']
    only_placement = comparacion[comparacion['Comparacion'] == 'right_only']
    # comparacion final sera las diferencias de ambos archivos y ademas los componentes que lleven yes en skip
    comparacion_final = comparacion[(comparacion['Comparacion'] != 'En ambos archivos') | ((comparacion['Skip'] == 'Yes') | (comparacion['Skip'].isna()) | (comparacion['Assign'] == "") | (comparacion['Assign'].isna()))]
    
    # retiramos la fila completa si se encuentra un No.Parte en la columna No.Parte
    comparacion_final = comparacion_final[~comparacion_final['Part Number'].str.startswith('017-')]
    #comparacion_final = comparacion_final[~comparacion_final['Part Number'].str.startswith('014-')]  // esto es un numero de parte!!
    comparacion_final = comparacion_final[~comparacion_final['Part Number'].str.startswith('051-')]
    comparacion_final = comparacion_final[~comparacion_final['Part Number'].str.startswith('140-')] #// soldadura ( detectar para analisis )
    comparacion_final = comparacion_final[~comparacion_final['Part Number'].str.startswith('124-')]
    
    #print("comparacion final es vacia: ",comparacion_final.empty) #hasta ese punto si no hay diferencias el dataframe es vacio
    #print("comparacion final: ",comparacion_final)  
    
    if comparacion_final.empty:
        logger.info(f"No se encontraron diferencias en comparacion con el archivo {ruta_bom} y {ruta_flexa}")
        #QMessageBox.information(None,"Diferencias","No se encontraron diferencias")
        return None,None
    else:
        #QMessageBox.information(None,"Diferencias","Se encontraron diferencias :O")
        logger.info(f"Se encontraron diferencias entre {ruta_flexa} y {ruta_bom}")
        # creamos la carpeta y el csv de la comparacion
        nombre_excel_sin_extension = os.path.splitext(os.path.basename(ruta_flexa))[0]                                                             # creamos el nombre del archivo sin extension
        logger.info(f'Se realizo la comparacion entre {ruta_flexa} y {ruta_bom}')
        
        carpeta_nombre_archivo = r"H:\Ingenieria\SMT\Flexa_vs_BOM\{nombre_excel_sin_extension}".format(nombre_excel_sin_extension=nombre_excel_sin_extension) # creamos la carpeta donde se guardara el archivo
        #carpeta_nombre_archivo = r"introduccion QT\comparador\ui\resources\data\{nombre_excel_sin_extension}".format(nombre_excel_sin_extension=nombre_excel_sin_extension) # creamos la carpeta donde se guardara el archivo
        
        os.makedirs(carpeta_nombre_archivo, exist_ok=True)
        ruta_csv = os.path.join(carpeta_nombre_archivo,f"{nombre_excel_sin_extension}.csv")
        ruta_csv_carrusel = os.path.join(carpeta_nombre_archivo,f"{nombre_excel_sin_extension}_carrusel.csv")
        # creamos un dataframe que contenga las diferencias y lo guardamos en CSV
        #funcional --> comparacion_final = comparacion[comparacion['Comparacion'] != 'En ambos archivos']
        
        # retiramos la fila completa si se encuentra un No.Parte en la columna No.Parte
        comparacion_final = comparacion_final[~comparacion_final['Part Number'].str.startswith('017-')]
        #comparacion_final = comparacion_final[~comparacion_final['Part Number'].str.startswith('014-')]  // esto es un numero de parte!!
        comparacion_final = comparacion_final[~comparacion_final['Part Number'].str.startswith('051-')]
        comparacion_final = comparacion_final[~comparacion_final['Part Number'].str.startswith('140-')] #// soldadura ( detectar para analisis )
        comparacion_final = comparacion_final[['Operation','Board','Reference','Part Number','Skip','Assign','Description','Comparacion']]
        
        # generamos el csv para carrusel
        #placement_carrusel.to_csv(ruta_csv_carrusel,index=False)
        
        # generamos el CSV
        comparacion_final.to_csv(ruta_csv,index=False)
        logger.info(f'Se genero el CSV {ruta_csv} con las diferencias de la comparacion')
        logger.info("--------------------------------------------------------------\n")
        return True,ruta_csv
        
def comparacion_nexim(ruta_bom,ruta_nexim):
    logger.info(f"Comienza la comparacion con el archivo {ruta_nexim} vs {ruta_bom}")
    #************************************************************** SYTELINE ******************************************************************
    # Carga y conversión de Excel a DataFrame
    syteline = pd.read_excel(ruta_bom, engine='openpyxl')
    bom = pd.DataFrame(syteline)
    bom.rename(columns={'Designators ': 'Reference', 'Item': 'Part Number'}, inplace=True)
    bom = bom[['Level', 'Operation', 'Part Number', 'Description', 'Reference', 'Quantity']]
    bom_op20 = bom[bom['Operation'] == 20.0]
    bom_op10 = bom[bom['Operation'] == 10.0]
    bom_filter = bom_op20.merge(bom_op10, how='outer')
    bom_filter['Reference'] = bom_filter['Reference'].str.split()
    bom_filter = bom_filter.explode('Reference')
    bom_filter.reset_index(drop=True, inplace=True)

    # Verificar si el número de parte '140-0704-00' está en las operaciones 10 y/o 20
    op10_filter = bom_filter[(bom_filter['Part Number'] == '140-0704-00') & (bom_filter['Operation'] == 10.0) & (bom_filter['Quantity'] > 0)]
    op20_filter = bom_filter[(bom_filter['Part Number'] == '140-0704-00') & (bom_filter['Operation'] == 20.0) & (bom_filter['Quantity'] > 0)]

    # Lógica de verificación
    if not op10_filter.empty and not op20_filter.empty:
        pass  # Soldadura en ambas operaciones
    elif not op10_filter.empty:
        pass  # Soldadura solo en operación 10
    elif not op20_filter.empty:
        pass  # Soldadura solo en operación 20
    else:
        # Mostrar mensaje de error
        logger.error("Soldadura: '140-0704-00' no existe en ninguna de las operaciones o su cantidad es igual a 0.")
        QMessageBox.critical(None, "Error", "Soldadura: '140-0704-00' no existe en ninguna de las operaciones o su cantidad es igual a 0.")
        if show_confirmation_dialog():
            dialog = LoginDialog()
            if dialog.exec() and dialog.authenticated[0]:
                #print("Autenticación correcta. Continuando...")
                logger.info(f"Autenticación correcta por {dialog.username}. Continuando...")
                pass
            else:
                logger.warning("Autenticación fallida o cancelada. Operación detenida.")
                QMessageBox.critical(None, "Error", "Autenticación fallida o cancelada. Operación detenida.")
                return  # Detener la función si no se autentica correctamente
        else:
            return  # Detener la función si se cancela la autenticación
                                                        
    bom_filter.reset_index(drop=True,inplace=True)
                                                        
    # Si hay elementos con un valor 2 en el level se descarta el elemento
    bom_filter = bom_filter[bom_filter['Level'] != 2]
    bom_filter = bom_filter[['Operation','Part Number','Description','Reference']]
    #print(bom_filter)
    #bom_filter.to_csv(r'comparador\bom_filter_nexim.csv',index=False)
    
    
    #******************************************************************* PLACEMENT ******************************************************************
    #Carga y conversion de placement nexim a dataframe
    nexim = pd.read_excel(ruta_nexim, engine='openpyxl')                                              
    placement = pd.DataFrame(nexim)                                                                    
    placement.rename(columns={'Ref.':'Reference'},inplace=True)
    placement = placement[['Board','Part Number','Reference','Skip','Assign']]
    
    
    # Validar que no existan componentes con Skip
    placement = placement[~placement['Part Number'].str.startswith("NOT")]
    
    if "Yes" in placement['Skip'].values:
        QMessageBox.warning(None, "Alerta", "Se encontraron componentes con Skip en el archivo placement")
        skipeados = placement[placement['Skip']=='Yes']
        logger.info(f"Se encontraron {len(skipeados)} componentes con Skip, no.parte {skipeados['Part Number'].values} y referencia {skipeados['Reference'].values}")
        skipeados = skipeados[['Board','Part Number','Reference','Assign']]
        data_to_display = skipeados.values.tolist()
        TableDialog.show_table(data_to_display,skipeados)
        respuesta = QMessageBox.question(None, "Alerta", "¿Desea continuar con la comparación?", QMessageBox.Yes | QMessageBox.No)
        if respuesta == QMessageBox.Yes:
            logger.info(f"Se decidio continuar con la comparacion del archivo {ruta_nexim}")
            # placement = placement
            pass
        else:
            logger.info(f"No se realizo la comparacion del archivo {ruta_nexim}")
            return
    
    # Validar si hay comoponentes sin asignar
    if placement['Assign'].isna().any():
        logger.info(f"Se reviso archivo placement {ruta_nexim} y se encontraron componentes sin asignar")
        QMessageBox.warning(None, "Alerta", "Se encontraron componentes sin asignar en el archivo placement")
        sin_asignar = placement[placement['Assign'].isna()]
        logger.info(f"Se encontraron {len(sin_asignar)} componentes sin asignar, no.parte {sin_asignar['Part Number'].values} y referencia {sin_asignar['Reference'].values}")
        sin_asignar = sin_asignar[['Board','Part Number','Reference','Assign']]
        data_to_display = sin_asignar.values.tolist()
        TableDialog.show_table(data_to_display,sin_asignar)
        respuesta = QMessageBox.question(None, "Alerta", "¿Desea continuar con la comparación?", QMessageBox.Yes | QMessageBox.No)
        if respuesta == QMessageBox.Yes:
            logger.info(f"Se decidio continuar con la comparacion del archivo {ruta_nexim}")
            # placement = placement
            pass
        else:
            logger.info(f"No se realizo la comparacion del archivo {ruta_nexim}")
            return
    
    
    #****************************************************************** COMPARACION ******************************************************************
    # Unimos ambos archivos y creamos el csv de comparacion
    comparacion = bom_filter.merge(placement,how='outer',on=['Part Number','Reference'],suffixes=('_bom','_placement'),indicator=True)
    #print(comparacion[comparacion['_merge']!='both'])
    comparacion.rename(columns={'_merge':'Comparacion'},inplace=True)
    comparacion["Comparacion"] = comparacion["Comparacion"].replace({
        "left_only": "Solo en Bom",
        "right_only": "Solo en Nexim",
        "both": "En ambos archivos"
    })
    # comparacion final sera las diferencias de ambos archivos y ademas los componentes que lleven yes en skip
    comparacion_final = comparacion[(comparacion['Comparacion'] != 'En ambos archivos') | ((comparacion['Skip'] == 'Yes') | (comparacion['Skip'].isna()) | (comparacion['Assign']=="") | (comparacion['Assign'].isna()))]
    #comparacion_final = comparacion[comparacion['Comparacion']!='En ambos archivos']
    
    # retiramos la fila completa si se encuentra un No.Parte en la columna No.Parte
    comparacion_final = comparacion_final[~comparacion_final['Part Number'].str.startswith('017-')]
    #comparacion_final = comparacion_final[~comparacion_final['Part Number'].str.startswith('014-')]  // esto es un numero de parte!!
    comparacion_final = comparacion_final[~comparacion_final['Part Number'].str.startswith('051-')]
    comparacion_final = comparacion_final[~comparacion_final['Part Number'].str.startswith('140-')]  #// soldadura (detectar para analisis)
    
    #print("Comparacion final es vacia: ",comparacion_final.empty)
    #print("Comparacion final: ",comparacion_final)
    
    if comparacion_final.empty:
        logger.info(f"No se encontraron diferencias en comparacion con el archivo {ruta_bom} y {ruta_nexim}")
        #QMessageBox.information(None,"Diferencias","No se encontraron diferencias")
        return None,None
    else:
        logger.info(f"Se encontraron diferencias entre {ruta_bom} y {ruta_nexim}")
        #QMessageBox.information(None,"Diferencias","Se encontraron diferencias :O")
        # creamos la carpeta y el csv de la comparacion
        nombre_excel_sin_extension = os.path.splitext(os.path.basename(ruta_nexim))[0]
        logger.info(f"Se realizo la comparacion entre {ruta_nexim} y {ruta_bom}")
        carpeta_nombre_archivo = r"H:\Ingenieria\SMT\Flexa_vs_BOM\Nexim\{nombre_excel_sin_extension}".format(nombre_excel_sin_extension=nombre_excel_sin_extension)
        #carpeta_nombre_archivo = r"introduccion QT\comparador\ui\resources\data\nexxim\{nombre_excel_sin_extension}".format(nombre_excel_sin_extension=nombre_excel_sin_extension) # creamos la carpeta donde se guardara el archivo
        os.makedirs(carpeta_nombre_archivo, exist_ok=True)
        ruta_csv = os.path.join(carpeta_nombre_archivo,f'{nombre_excel_sin_extension}.csv')
        
        # retiramos la fila completa si se encuentra un No.Parte en la columna No.Parte
        comparacion_final = comparacion_final[~comparacion_final['Part Number'].str.startswith('017-')]
        #comparacion_final = comparacion_final[~comparacion_final['Part Number'].str.startswith('014-')]  // esto es un numero de parte!!
        comparacion_final = comparacion_final[~comparacion_final['Part Number'].str.startswith('051-')]
        comparacion_final = comparacion_final[~comparacion_final['Part Number'].str.startswith('140-')] #// soldadura (detectar para analisis)
        comparacion_final = comparacion_final[['Operation','Board','Reference','Part Number','Skip','Assign','Description','Comparacion']]          
        # guardamos el csv
        comparacion_final.to_csv(ruta_csv,index=False)
        logger.info(f"Se genero el CSV {ruta_csv} con las diferencias entre {ruta_bom} y {ruta_nexim}")
        logger.info("----------------------------------------------------------------------------------")
        return True,ruta_csv
           
#Comparacion entre bom y placement 
def comparacion_bom(ruta_bom,ruta_bom2):
    #************************************************************** BOM 1 ******************************************************************
    #Carga y conversion de excel syteline a dataframe
    syteline = pd.read_excel(ruta_bom, engine='openpyxl')                                               # leemos el archivo excel de syteline 
    bom = pd.DataFrame(syteline)                                                                        # convertimos a dataframe
    bom.rename(columns={'Designators ':'Reference'},inplace=True)                                       # Renombramos columna(Designators a Reference) para que conicida con Placement
    bom.rename(columns={'Item':'Part Number'},inplace=True)                                             # Renombramos columna(Item a Part Number) para que conicida con Placement
    #bom = bom[['Operation','Part Number','Description','Reference']]                                    # seleccionamos las columnas deseadas(Operation,Part Number,Description,Reference)
    bom = bom[['Operation','Part Number','Reference']] 
    bom_op20 = bom[bom['Operation']==20.0]                                                              # creamos un dataframe filtrando por operacion 20
    bom_op10 = bom[bom['Operation']==10.0]                                                              # creamos un dataframe filtrando por operacion 10
    bom_filter = bom_op20.merge(bom_op10,how='outer')                                                   # creamos un dataframe combinando con un join(outer)
    bom_filter['Reference'] = bom_filter['Reference'].str.split()                                       # de la columna reference desglamos los elementos en elementos unicos es decir
    bom_filter = bom_filter.explode('Reference')                                                        # desempaquetamos la lista de referencias
    bom_filter.reset_index(drop=True,inplace=True)                                                      # reseta el indice,debido que al desempaquetar agregamos mas elemenetos al dataframe
    #bom_filter.to_csv(r'comparador\csv\bom_filter.csv',index=False)
    #print(bom_filter)
    
    #************************************************************** BOM 2 ******************************************************************
    syteline2 = pd.read_excel(ruta_bom2, engine='openpyxl')                                               # leemos el archivo excel de syteline
    bom2 = pd.DataFrame(syteline2)    
    #print(bom2.columns)                                                                                  # convertimos a dataframe
    bom2.rename(columns={'Designators ':'Reference'},inplace=True)                                      # Renombramos columna(Designators a Reference) para que conicida con Placement
    bom2.rename(columns={'Item':'Part Number'},inplace=True)                                            # Renombramos columna(Item a Part Number) para que conicida con Placement
    #bom2 = bom2[['Operation','Part Number','Description','Reference']]                                   # seleccionamos las columnas deseadas(Operation,Part Number,Description,Reference)
    bom2 = bom2[['Operation','Part Number','Reference']]
    bom2_op20 = bom2[bom2['Operation']==20.0]                                                           # creamos un dataframe filtrando por operacion 20
    bom2_op10 = bom2[bom2['Operation']==10.0]                                                           # creamos un dataframe filtrando por operacion 10
    bom2_filter = bom2_op20.merge(bom2_op10,how='outer')                                                # creamos un dataframe combinando con un join(outer)
    bom2_filter['Reference'] = bom2_filter['Reference'].str.split()                                    # de la columna reference desglamos los elementos en elementos unicos es decir
    bom2_filter = bom2_filter.explode('Reference')                                                     # desempaquetamos la lista de referencias
    bom2_filter.reset_index(drop=True,inplace=True)                                                     # reseta el indice,debido que al desempaquetar agregamos mas elemenetos al dataframe
    #bom2_filter.to_csv(r'comparador\csv\bom2_filter.csv',index=False)
    #print(bom2_filter)
    
    # # ******************************************************************* COMPARACION ******************************************************************
    logger.info(f"Comienza la comparacion con el archivo {ruta_bom} vs {ruta_bom2}")
    comparacion = bom_filter.merge(bom2_filter,how='outer',suffixes = ('_izq', '_der'),indicator=True)
    comparacion.rename(columns={'_merge':'Comparacion'},inplace=True)
    comparacion['Comparacion'] = comparacion['Comparacion'].replace({
        'left_only': 'BOM_izq',
        'right_only': 'BOM_der',
        'both': 'En ambos archivos'
    })
    bom_izq = comparacion[comparacion['Comparacion']=='left_only']
    bom_der = comparacion[comparacion['Comparacion']=='right_only']
    
    comparacion_final = comparacion[comparacion['Comparacion']!='En ambos archivos']
    
    #print(comparacion)
    #comparacion.to_csv(r'C:\Users\CECHEVARRIAMENDOZA\OneDrive - Brunswick Corporation\Documents\Proyectos_Python\PysimpleGUI\Proyectos\comparador\data_comparacion\comparacion.csv',index=False)
    
    #si no hay diferencias solo alerta un Pop up completado con exito!, si hay diferencias crea el archivo csv
    if comparacion_final.empty:
        # sg.popup('No hay diferencias entre los BOM :)')
        logger.info(f'No se encontraron diferencias entre los BOM {ruta_bom} y {ruta_bom2}')
        #QMessageBox.information(None,"Diferencias","No se encontraron diferencias")
        return None,None
    else:
        logger.info(f'Se encontraron diferencias entre los BOM {ruta_bom} y {ruta_bom2}')
        #QMessageBox.information(None,"Diferencias","Se encontraron diferencias :O")
        # Comparacion final sera un dataframe que contenga los datos que sean diferentes en ambos archivos pero no es necesario mostrar los no.part que contenga NOT IN BOM
        nombre_excel_sin_extension = os.path.splitext(os.path.basename(ruta_bom2))[0]
        carpeta_nombre_archivo = r"H:\Ingenieria\SMT\Flexa_vs_BOM\BOM\{nombre_excel_sin_extension}".format(nombre_excel_sin_extension=nombre_excel_sin_extension)
        os.makedirs(carpeta_nombre_archivo, exist_ok=True)
        ruta_csv = os.path.join(carpeta_nombre_archivo,f"{nombre_excel_sin_extension}.csv")
        comparacion_final = comparacion[comparacion['Comparacion'] != 'En ambos archivos']
        comparacion_final.to_csv(ruta_csv,index=False)
        logger.info(f'Se realizo la comparacion entre los BOM y se genero el CSV {ruta_csv}')
        logger.info('--------------------------------------------------------------\n')   
        return True, ruta_csv

def comparacion_job(ruta_bom):
    df = pd.read_excel(ruta_bom, sheet_name='SV9_005')
    # saltamos las primeras 5 filas
    df = df.iloc[5:]
    # quitamos las filas vacias
    df = df.dropna(how='all')
    # quitamos las columnas vacias
    df = df.dropna(axis=1, how='all')
    # quitamos las columnas vacias
    print(df)


class TableDialog(QDialog):
    def __init__(self, data_to_display, skipeados):
        super().__init__()
        self.setWindowIcon(QIcon(r'comparadorV2\comparador\ui\resources\icons8-compare-60.ico')) 
        self.setWindowTitle("Componentes skip/assign")
        # cargar estilos
        self.cargarEstilos(r"comparador\ui\resources\style.qss")
        # Crear la tabla
        table_widget = QTableWidget()
        num_rows = len(data_to_display)
        num_cols = len(data_to_display[0]) if num_rows > 0 else 0
        table_widget.setRowCount(num_rows)
        table_widget.setColumnCount(num_cols)
        table_widget.setHorizontalHeaderLabels(skipeados.columns.tolist())

        # Llenar la tabla con los datos
        for row in range(num_rows):
            for col in range(num_cols):
                item = QTableWidgetItem(str(data_to_display[row][col]))
                table_widget.setItem(row, col, item)

        table_widget.resizeColumnsToContents()
        table_widget.resizeRowsToContents()

        # Botón de aceptar
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)

        # Layout principal para el diálogo
        main_layout = QVBoxLayout()

        # Layout para centrar la tabla
        table_layout = QHBoxLayout()
        table_layout.addStretch()  # Espacio flexible a la izquierda
        table_layout.addWidget(table_widget)
        table_layout.addStretch()  # Espacio flexible a la derecha

        main_layout.addLayout(table_layout)
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)

        # Ajustar tamaño de la ventana al contenido
        self.adjustSize()

        # Establecer tamaño fijo para la ventana
        self.setFixedSize(self.size())

    @staticmethod
    def show_table(data_to_display, skipeados):
        dialog = TableDialog(data_to_display, skipeados)
        result = dialog.exec()
        return result == QDialog.Accepted
    
    def cargarEstilos(self, archivo_qss):
        '''
        Funcion carga estilos de archivos.qss para 
        aplicarlos a todos los elementos de la ventana
        Args:
            archivo_qss (str): ruta del archivo .qss
        '''
        estilo = QFile(archivo_qss)
        if estilo.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(estilo)
            self.setStyleSheet(stream.readAll())
            estilo.close()
        else:
            QMessageBox.critical(self, "Error", f"No fue posible cargar el archivo: {archivo_qss}")
    
    
class CompareResult(QDialog):
    def __init__(self, parent=None,color="lightgreen",message="No se encontraron diferencias"):
        super().__init__(parent)
        self.setGeometry(450,450,300, 100)
        self.setWindowIcon(QIcon(r'comparador\ui\resources\icons8-compare-60.ico'))  
        # cargar estilos
        self.cargarEstilos(r"comparador\ui\resources\style.qss")
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
        
        def cargarEstilos(self, archivo_qss):
            '''
            Funcion carga estilos de archivos.qss para 
            aplicarlos a todos los elementos de la ventana
            Args:
                archivo_qss (str): ruta del archivo .qss
            '''
            estilo = QFile(archivo_qss)
            if estilo.open(QFile.ReadOnly | QFile.Text):
                stream = QTextStream(estilo)
                self.setStyleSheet(stream.readAll())
                estilo.close()
            else:
                QMessageBox.critical(self, "Error", f"No fue posible cargar el archivo: {archivo_qss}")

def show_confirmation_dialog():
    reply = QMessageBox.question(None, 'Continuar', "¿Desea continuar?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    if reply == QMessageBox.Yes:
        return reply == QMessageBox.Yes
    else:
        return 
    
def register_user(nombre, password):
    connection = sqlite3.connect('usuarios.db')
    cursor = connection.cursor()

    # Verificar si el usuario ya existe
    cursor.execute('SELECT * FROM usuarios WHERE nombre = ?', (nombre,))
    if cursor.fetchone() is not None:
        connection.close()
        return False  # Usuario ya registrado
    
    # Insertar nuevo usuario
    cursor.execute('INSERT INTO usuarios (nombre, password) VALUES (?, ?)', (nombre, password))
    connection.commit()
    connection.close()
    return True  # Usuario registrado exitosamente

def validate_user(nombre, password):
    connection = sqlite3.connect('usuarios.db')
    cursor = connection.cursor()

    # Buscar usuario con las credenciales proporcionadas
    cursor.execute('SELECT * FROM usuarios WHERE nombre = ? AND password = ?', (nombre, password))
    user = cursor.fetchone()
    connection.close()

    return user is not None

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Autenticación')
        # cargar estilos
        self.cargarEstilos(r"comparador\ui\resources\style.qss")
        # Inicializar estado de autenticación
        self.authenticated = False

        # Crear elementos de la interfaz
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText('Nombre de usuario')

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText('Contraseña')
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.label_master_key = QLabel('Clave maestra para generar administradores:')
        self.master_key_input = QLineEdit(self)
        self.master_key_input.setPlaceholderText('Clave maestra')
        self.master_key_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton('Iniciar sesión', self)
        self.login_button.clicked.connect(self.verify_credentials)

        self.register_button = QPushButton('Registrar nuevo usuario', self)
        self.register_button.clicked.connect(self.register_new_user)

        layout = QVBoxLayout()
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.label_master_key)
        layout.addWidget(self.master_key_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)
        self.setLayout(layout)

    def verify_credentials(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Validar usuario
        if validate_user(username, password):
            QMessageBox.information(self, 'Éxito', 'Inicio de sesión exitoso')
            self.authenticated = True, username  # Actualizar estado de autenticación
            self.accept()
        else:
            QMessageBox.critical(self, 'Error', 'Credenciales incorrectas')
            self.authenticated = False  # Actualizar estado de autenticación

    def register_new_user(self):
        username = self.username_input.text()
        password = self.password_input.text()
        master_key = self.master_key_input.text()

        # Verificar clave maestra
        if master_key != MASTER_KEY:
            QMessageBox.critical(self, 'Error', 'Clave maestra incorrecta')
            return

        # Registrar usuario si la clave maestra es correcta
        if register_user(username, password):
            QMessageBox.information(self, 'Éxito', 'Usuario registrado exitosamente')
        else:
            QMessageBox.critical(self, 'Error', 'El usuario ya existe o hubo un error')
    
    def cargarEstilos(self, archivo_qss):
        '''
        Funcion carga estilos de archivos.qss para 
        aplicarlos a todos los elementos de la ventana
        Args:
            archivo_qss (str): ruta del archivo .qss
        '''
        estilo = QFile(archivo_qss)
        if estilo.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(estilo)
            self.setStyleSheet(stream.readAll())
            estilo.close()
        else:
            QMessageBox.critical(self, "Error", f"No fue posible cargar el archivo: {archivo_qss}")
 
 
