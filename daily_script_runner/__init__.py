import logging
import azure.functions as func
import os
import sys

# Añade el path al módulo Scripts-Disparos
RUTA_SCRIPTS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Scripts-Disparos-main"))
if RUTA_SCRIPTS not in sys.path:
    sys.path.append(RUTA_SCRIPTS)

try:
    from main import main as ejecutar_main
except ImportError as e:
    raise ImportError(f"No se pudo importar main desde Scripts-Disparos-main: {e}")

def main(mytimer: func.TimerRequest) -> None:
    logging.info("⏰ Ejecutando script diario desde Azure Function...")

    try:
        ejecutar_main()
        logging.info("✅ Script diario ejecutado correctamente.")
    except Exception as e:
        logging.error(f"❌ Error al ejecutar el script diario: {e}")
