import logging
import azure.functions as func
import os
import sys

# Agrega path donde están tus scripts
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Scripts-Disparos")))

from main import main as ejecutar_script

def main(mytimer: func.TimerRequest) -> None:
    logging.info('⏰ Ejecutando script diario desde Azure Function...')
    ejecutar_script()
