import logging
import azure.functions as func
import os
import sys

# Agregar el path al módulo Scripts-Disparos-main donde está main.py
SCRIPTS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Scripts-Disparos-main"))
if SCRIPTS_PATH not in sys.path:
    sys.path.append(SCRIPTS_PATH)

try:
    from main import main as ejecutar_main
except ImportError as e:
    logging.error(f"❌ No se pudo importar 'main' desde Scripts-Disparos-main: {e}")
    raise

def main(mytimer: func.TimerRequest) -> None:
    logging.info("⏰ Ejecutando rutina diaria desde Azure Function...")

    try:
        ejecutar_main()
        logging.info("✅ Rutina diaria ejecutada exitosamente.")
    except Exception as e:
        logging.error(f"❌ Error al ejecutar rutina diaria: {e}")
