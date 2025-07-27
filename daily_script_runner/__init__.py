import logging
import azure.functions as func
import os
import sys

# Agrega el path al módulo Scripts-Disparos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Scripts-Disparos-main")))

from main import main as ejecutar_main

def main(mytimer: func.TimerRequest) -> None:
    logging.info("⏰ Ejecutando script diario desde Azure Function...")
    try:
        ejecutar_main()
        logging.info("✅ Script ejecutado exitosamente.")
    except Exception as e:
        logging.error(f"❌ Error al ejecutar el script: {e}")
