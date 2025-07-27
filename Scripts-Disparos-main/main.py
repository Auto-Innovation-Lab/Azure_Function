from funciones_utiles import *
from config import paths
import pandas as pd
import random
import time

# 1. Cargar y filtrar datos
df_contactos, df_links = cargar_datos(paths)
df_links, df_contactos = filtrar_datos(df_links, df_contactos)
remitentes = cargar_remitentes(paths['mails'])
rotador = RotadorRemitentes(remitentes)

# 2. Set para evitar duplicados por sesión
correos_enviados = set()
enlaces_usados = set()
log_envios = []

# 3. Agrupar links por dominio
for _, row in df_links.iterrows():
    dominio = str(row['Dominio']).lower().replace("www.", "").strip()
    descripcion = row['Descripcion']
    enlace = row['Enlace']

    # Buscar contacto más parecido
    match = dominio_mas_parecido(dominio, df_contactos['Cluster'].str.lower().tolist(), umbral=0.5)
    if not match:
        continue

    coincidente = df_contactos[df_contactos['Cluster'].str.lower() == match]
    if coincidente.empty:
        print(f"⚠️ Coincidencia '{match}' no tiene contacto asociado. Dominio original: {dominio}")
        continue

    contacto = coincidente.iloc[0]
    correo_contacto = contacto['Mail']

    # Evitar enviar dos veces al mismo contacto
    if correo_contacto in correos_enviados:
        continue

    # Buscar hasta 4 links del mismo dominio
    #mismos = df_links[df_links['Dominio'].str.lower().str.contains(match, na=False)].sample(n=random.randint(1, 4), replace=False)
    coincidentes = df_links[df_links['Dominio'].str.lower().str.contains(match, na=False) & ~df_links['Enlace'].isin(enlaces_usados)]

    if coincidentes.empty:
        print(f"⚠️ No se encontraron dominios que coincidan con: {match}")
        continue  # ← esto evita el crash

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

    # Enviar
    enviar_correo(remitente, correo_contacto, asunto, cuerpo)

    # Guardar en log
    log_envios.append({
        'Remitente': remitente['correo'],
        'Receptor': correo_contacto,
        'Cluster': match,
        'Cantidad Links': len(productos),
        'Descripcion Primer Link': productos[0]['descripcion']
    })

    correos_enviados.add(correo_contacto)

    espera = random.uniform(5, 10)
    time.sleep(espera)

# 4. Guardar log
df_log = pd.DataFrame(log_envios)
guardar_log(df_log, paths['log'])
