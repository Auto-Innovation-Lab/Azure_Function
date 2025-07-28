import logging
import pandas as pd
import random
import time

from funciones_utiles import *
from config import paths

def main():
    logging.info("🚀 Entrando a main.py")

    try:
        # 1. Cargar y filtrar datos
        logging.info("📥 Cargando datos desde OneDrive...")
        df_contactos, df_links = cargar_datos(paths)

        logging.info(f"🔎 Contactos cargados: {len(df_contactos)}, Links cargados: {len(df_links)}")
        df_links, df_contactos = filtrar_datos(df_links, df_contactos)

        remitentes = cargar_remitentes(paths['mails'])
        rotador = RotadorRemitentes(remitentes)

        correos_enviados = set()
        enlaces_usados = set()
        log_envios = []

        logging.info("📬 Comenzando envío de correos...")

        for _, row in df_links.iterrows():
            dominio = str(row['Dominio']).lower().replace("www.", "").strip()
            descripcion = row['Descripcion']
            enlace = row['Enlace']

            match = dominio_mas_parecido(dominio, df_contactos['Cluster'].str.lower().tolist(), umbral=0.5)
            if not match:
                continue

            coincidente = df_contactos[df_contactos['Cluster'].str.lower() == match]
            if coincidente.empty:
                logging.warning(f"⚠️ Coincidencia '{match}' no tiene contacto. Dominio: {dominio}")
                continue

            contacto = coincidente.iloc[0]
            correo_contacto = contacto['Mail']

            if correo_contacto in correos_enviados:
                continue

            coincidentes = df_links[
                df_links['Dominio'].str.lower().str.contains(match, na=False) &
                ~df_links['Enlace'].isin(enlaces_usados)
            ]

            if coincidentes.empty:
                logging.warning(f"⚠️ No se encontraron links coincidentes con dominio: {match}")
                continue

            n_links = min(len(coincidentes), random.randint(1, 4))
            mismos = coincidentes.sample(n=n_links, replace=False)
            enlaces_usados.update(mismos['Enlace'].tolist())

            productos = []
            for _, r in mismos.iterrows():
                productos.append({
                    'descripcion': r['Descripcion'],
                    'enlace': r['Enlace']
                })

            cuerpo = generar_cuerpo(productos)
            asuntos = [
                "Cotización de repuestos en su web",
                "Consulta precios",
                "Necesitamos cotizar estos repuestos en su pagina",
                "Cotizacion productos",
                "Duda repuestos de su pagina web",
                "Productos vistos en su sitio web"
            ]
            asunto = random.choice(asuntos)
            remitente = rotador.siguiente()

            logging.info(f"📧 Enviando a {correo_contacto} con {len(productos)} productos.")
            enviar_correo(remitente, correo_contacto, asunto, cuerpo)

            log_envios.append({
                'Remitente': remitente['correo'],
                'Receptor': correo_contacto,
                'Cluster': match,
                'Cantidad Links': len(productos),
                'Descripcion Primer Link': productos[0]['descripcion']
            })

            correos_enviados.add(correo_contacto)

            espera = random.uniform(5, 10)
            logging.info(f"⏳ Esperando {espera:.1f} segundos antes del siguiente envío...")
            time.sleep(espera)

        # 4. Guardar log
        logging.info("💾 Guardando log de envíos...")
        df_log = pd.DataFrame(log_envios)
        guardar_log(df_log, paths['log'])

        logging.info("✅ Script finalizado correctamente.")

    except Exception as e:
        logging.error(f"❌ Error en main.py: {e}")
        raise
