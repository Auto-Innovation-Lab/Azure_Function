import pandas as pd
import random
import difflib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Carga y filtrado de datos
def cargar_datos(paths):
    import openpyxl
import logging

# Abrir el archivo descargado desde OneDrive
try:
    wb = openpyxl.load_workbook(paths['contactos'], read_only=True)
    hojas = wb.sheetnames
    logging.info(f"📄 Hojas encontradas en el archivo de contactos: {hojas}")
    wb.close()
except Exception as e:
    logging.error(f"❌ Error leyendo las hojas del archivo Excel: {e}")
    raise
    df_contactos = pd.read_excel(paths['contactos'], sheet_name='GM CL', header=1)
    df_links = pd.read_excel(paths['disparo'], sheet_name='CL', header=2)
    return df_contactos, df_links

def filtrar_datos(df_links, df_contactos):
    df_links = df_links[df_links['Ola'] == 3].copy()
    df_links = df_links[df_links['Precio c/IVA'].isna()].copy() 
    df_contactos = df_contactos[df_contactos['Marca'].str.lower() == 'zlink'].copy()
    return df_links, df_contactos


def cargar_remitentes(path='Mails.xlsx'):
    df = pd.read_excel(path, sheet_name='Mails AWS GD py', header=0)
    df = df[df['Activo'] == 'Si']

    remitentes = []
    for _, row in df.iterrows():
        remitentes.append({
            'correo': row['E-mails'],
            'servidor SMTP': row['Servidor SMTP'],
            'puerto': int(row['Puerto']),
            'usuario AWS': row['Login'],
            'clave AWS': row['Contraseña']
        })

    return remitentes  # ✅ Solo retornamos la lista de remitentes activos y formateados


class RotadorRemitentes:
    def __init__(self, df_remitentes):
        self.remitentes = df_remitentes.copy()
        random.shuffle(self.remitentes)
        self.index = 0

    def siguiente(self):
        remitente = self.remitentes[self.index]
        self.index = (self.index + 1) % len(self.remitentes)
        return remitente


# Coincidencia aproximada de dominios
def dominio_mas_parecido(dominio, lista_clusters, umbral=0.8):
    dominio = dominio.lower().replace("www.", "").strip()
    coincidencias = difflib.get_close_matches(dominio, lista_clusters, n=1, cutoff=umbral)
    return coincidencias[0] if coincidencias else None

# Generación del cuerpo del correo
def generar_cuerpo(productos):
    saludos = [
        "Estimado, espero que se encuentre bien.",
        "Hola, buenas.",
        "Saludos, espero que tenga una buena jornada.",
        "Buenas, le escribo esperando que esté bien.",
        "Buen dia, una consulta."
    ]

    introducciones = [
        "Encontre los siguientes repuestos en su web y me gustaria consultar si es solo online o tambien en tienda:",
        "Necesito una cotizacion formal para estos repuestos que vi en su sitio:",
        "Comparto el detalle de los repuestos encontrados en su web, queria saber si presencialmente es el mismo valor:",
        "Quiero cotizar los siguientes productos publicados en su web, podria mandarme una cotizacion formal de estos productos:",
    
    ]

    despedidas = [
        "Muchas gracias de antemano. Quedo atento. Saludos.",
        "Gracias por su atención. Espero su respuesta.",
        "Agradezco su ayuda. Saludos cordiales.",
        "Muchas gracias. Quedo atento a sus comentarios.",
        "Gracias por su tiempo. Espero su pronta respuesta."
    ]

    formatos = [
        lambda i, desc, link: f"- {desc}\n  {link}",
        lambda i, desc, link: f"{i+1}. {desc}\n   {link}",
        lambda i, desc, link: f"{desc}: {link}",
        lambda i, desc, link: f"{desc} ({link})",
        lambda i, desc, link: f"• {desc}\n  {link}"
    ]

    saludo = random.choice(saludos)
    introduccion = random.choice(introducciones)
    despedida = random.choice(despedidas)
    formato = random.choice(formatos)

    lista_items = "\n".join([formato(i, p['descripcion'], p['enlace']) for i, p in enumerate(productos)])

    cuerpo = f"""{saludo}

{introduccion}

{lista_items}

{despedida}
"""
    return cuerpo

# Envío del correo
def enviar_correo(remitente_info, destinatario, asunto, cuerpo):
    try:
        puerto = int(remitente_info['puerto'])
        correo = MIMEMultipart()
        correo['From'] = remitente_info['correo']
        correo['To'] = destinatario
        correo['Subject'] = asunto
        correo.attach(MIMEText(cuerpo, 'plain'))
        print(f"Usando remitente: {remitente_info}")

        if puerto == 587:
            with smtplib.SMTP(remitente_info['servidor SMTP'], puerto) as server:
                server.starttls()
                server.login(remitente_info['usuario AWS'], remitente_info['clave AWS'])
                server.sendmail(remitente_info['correo'], destinatario, correo.as_string())
                print(f"Correo enviado a {destinatario}")
    except Exception as e:
        print(f"❌ Error enviando a {destinatario}: {e}")

# Guardar log
def guardar_log(df_log, path):
    df_log.to_csv(path, index=False)



