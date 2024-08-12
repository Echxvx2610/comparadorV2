import logging
import os

# Variable para almacenar el logger configurado
logger = None

def setup_logger(log_file):
    global logger
    if logger is None:
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        #list levelname = ['NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        
        # Crear un formateador de registro (yyyy MM dd - HH:MM:SS - Level - Message)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Crear un manejador para escribir los registros en un archivo
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # Agregar el manejador al logger
        logger.addHandler(file_handler)

        # Cambiar los permisos del archivo de registro para que sea de solo lectura para otros usuarios
        os.chmod(log_file, 0o644)  # Esto permite escritura por el propietario y lectura por otros

    return logger