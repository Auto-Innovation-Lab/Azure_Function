import logging
import pandas as pd
import random
import time

from funciones_utiles import *
from config import get_paths  # ✅ CAMBIO AQUÍ

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    print("🚀 Iniciando main.py...")

    try:
        # 1. Cargar y filtrar datos
        print("📥 Cargando datos desde OneDrive...")
        paths = get_paths()  # ✅ CAMBIO AQUÍ
        print(f"📂 Paths obtenidos: {paths}")

        df_contactos, df_links = cargar_datos(paths)
        print(f"🔎 Contactos cargados: {len(df_contactos)}, Links cargados: {len(df_links)}")

        df_links, df_contactos = filtrar_datos(df_links, df_contactos)
        print(f"✅ Después de filtrar: {len(df_contactos)} contactos y {len(df_links)} links")

        remitentes = cargar_remitentes(paths['mails'])
        print(f"📧 Remitentes cargados: {len(remitentes)}")

        rotador = RotadorRemitentes(remitentes)

        correos_enviados = set()
        enlaces_usados = set()
        log_envios = []

        print("📬 Comenzando envío de correos...")

        for _, row in df_links.iterrows():
            dominio = str(row['Dominio']).lower().replace("www.", "").strip()
            descripcion = row['Descripcion']
            enlace = row['Enlace']

            match = dominio_mas_parecido(dominio, df_contactos['Cluster'].str.lower().tolist(), umbral=0.5)
            if not match:
                continue

            coincidente = df_contactos[df_contactos['Cluster'].str.lower() == match]
            if coincidente.empty:
                print(f"⚠️ Coincidencia '{match}' sin contacto. Dominio: {dominio}")
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
                print(f"⚠️ No se encontraron links coincidentes con dominio: {match}")
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

            print(f"📧 Enviando a {correo_contacto} con {len(productos)} productos desde {remitente['correo']}")
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
            print(f"⏳ Esperando {espera:.1f} segundos antes del siguiente envío...")
            time.sleep(espera)

        # 4. Guardar log
        print("💾 Guardando log de envíos...")
        df_log = pd.DataFrame(log_envios)
        guardar_log(df_log, paths['log'])

        print("✅ Script finalizado correctamente.")

    except Exception as e:
        print(f"❌ Error en main.py: {e}")
        logging.error(f"❌ Error en main.py: {e}")
        raise

if __name__ == "__main__":
    main()
