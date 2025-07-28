import logging
import azure.functions as func
import os
import sys
import traceback

def main(mytimer: func.TimerRequest) -> None:
    logging.info("⏰ Ejecutando rutina diaria desde Azure Function...")

    try:
        # Agregar el path al módulo Scripts-Disparos-main donde está main.py
        SCRIPTS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Scripts-Disparos-main"))
        if SCRIPTS_PATH not in sys.path:
            sys.path.append(SCRIPTS_PATH)
            logging.info(f"📂 Ruta agregada al sys.path: {SCRIPTS_PATH}")

        # Intentar importar y ejecutar main
        from main import main as ejecutar_main
        logging.info("🚀 Módulo 'main.py' importado exitosamente. Ejecutando...")
        ejecutar_main()
        logging.info("✅ Rutina diaria ejecutada exitosamente.")

    except Exception as e:
        logging.error("❌ Error durante la ejecución:")
        logging.error(traceback.format_exc())
