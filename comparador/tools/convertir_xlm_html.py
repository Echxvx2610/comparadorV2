# Author: Cristian Echeverria
# Funcional para CP's y QP's!!
from lxml import etree
import os
from bs4 import BeautifulSoup
from PySide6.QtWidgets import QMessageBox

def generate_html_report(base_path, css_path, logo_path, head_xml_file, head_xsl_file, unit_xml_file, unit_xsl_file):
    def transform_xml(xml_file, xsl_file):
        dom = etree.parse(xml_file)
        xslt = etree.parse(xsl_file)
        transform = etree.XSLT(xslt)
        newdom = transform(dom)
        return str(newdom)
    
    # Transformar los archivos XML
    head_content = transform_xml(head_xml_file, head_xsl_file)
    unit_content = transform_xml(unit_xml_file, unit_xsl_file)

    soup = BeautifulSoup(head_content, 'xml')
    table = soup.find('table', class_='head')
    
    # Extraemos los datos de las tablas 
    data = {}
    for row in table.find_all('tr'):
        key = row.find('th').text.strip()
        value = row.find('td').text.strip()
        data[key] = value

    # Accesamos a valores especificos
    job_name = data.get('Recipe name')
    machine = data.get('Machine')
    code = data.get('Codigo de Barras')
    recipe_name = data.get('Recipe name')
    revision = data.get('Revision')
    
    # Imprimir los datos extraidos
    #print(f"Code: {code}")
    #print(f"Recipe Name: {recipe_name}")
    
    # Remover los asteriscos del código de barras para reemplazo
    code_formate = code.replace('%O', '_')
    clean_code = code_formate.replace('*', '')
    
    # filtrar recipe name y agregar revision
    recipe_name = recipe_name.split('_')[0]
    
    # cambiar formato revision
    revision = f'_{revision}'
    #cambiar formato machine
    machine = f'_{machine}'
    # creamos un nuevo recipe name agregano la revision
    recipe_name_filter = recipe_name + revision + machine
    
    # para depurar
    # print(f"Clean Code: {clean_code}")
    # print(f"Recipe Name: {recipe_name}")
    # print(f'Revision: {revision}')
    # print(f'Recipe Name Filter: {recipe_name_filter}')
    
    # Reemplazar el código en el contenido transformado por un canvas para el código de barras
    head_content = head_content.replace(code, '<canvas id="barcode" style="width: 300px; height: 25px;"></canvas>')
    
    # Crear el contenido HTML final
    html_content = f"""
    <html>
    <head>
        <meta http-equiv="content-type" content="text/html">
        <meta name="copy-right" content="Fuji Machine Mfg. Co., Ltd.">
        <meta http-equiv="Expires" content="{os.path.getmtime(head_xml_file)}">
        <link rel="stylesheet" href="{css_path}" type="text/css">
        <title>CP64321 Feeder Setup Report</title>
        <script src="https://cdn.jsdelivr.net/npm/jsbarcode@3.11.5/dist/JsBarcode.all.min.js"></script>
    </head>
    <body>
    <img class="logo" src="{logo_path}" width="70">
    <h1>Feeder Setup Report</h1>
    <blockquote>
        <hr>
        <div id="Target1">
            {head_content}
        </div>
        <hr>
        <div id="Target2">
            {unit_content}
        </div>
        <hr>
        <script>
            JsBarcode("#barcode", "{clean_code}", {{
                format: "CODE128",
                displayValue: false
            }});
        </script>
    </blockquote>
    </body>
    </html>
    """

    return html_content, recipe_name_filter

if __name__ == '__main__':
    generate_html_report()
# Ejemplo de uso
# base_path = r'comparador\ui\resources\devices_flexa'
# logo_path = r'comparador\ui\resources\LOGO_NAVICO.png'
# css_path = r'C:\FujiFlexa\Client\Report\Definition\Feeder Setup_IndexReportStyle.css'
# unit_xsl_file = r'C:\FujiFlexa\Client\Report\Definition\FeederReportUnit.xsl'
# head_xsl_file = r'C:\FujiFlexa\Client\Report\Definition\FeederReportHead.xsl'

# # Primer devices (Cp1)
# head_xml_file = r'C:\FujiFlexa\Client\Report\Jobdata\job0117/CP64321_FeederReportHead_B.xml'
# unit_xml_file = r'C:\FujiFlexa\Client\Report\Jobdata\job0117/CP64321_FeederReportUnit_B.xml'

# html_output = generate_html_report(base_path, css_path, logo_path, head_xml_file, head_xsl_file, unit_xml_file, unit_xsl_file)
# list_devices = [html_output]
# for i, html_content in enumerate(list_devices):
#     with open(f'output_report_{i+1}.html', 'w', encoding='utf-8') as file:
#         file.write(html_content[0])
    
# print("El archivo HTML ha sido generado con éxito.")