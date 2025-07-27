import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_correo(remitente_info, destinatario, asunto, cuerpo):
    try:
        # Convertir a int el puerto por si viene como texto
        puerto = int(remitente_info['puerto'])
        
        # Crear mensaje MIME
        correo = MIMEMultipart()
        correo['From'] = remitente_info['correo']
        correo['To'] = destinatario
        correo['Subject'] = asunto
        correo.attach(MIMEText(cuerpo, 'plain'))

        # Conexión SMTP con STARTTLS
        if puerto == 587:
            with smtplib.SMTP(remitente_info['servidor SMTP'], puerto) as server:
                server.starttls()
                server.login(remitente_info['usuario AWS'], remitente_info['clave AWS'])
                server.sendmail(remitente_info['correo'], destinatario, correo.as_string())
                print(f"Correo enviado a {destinatario} desde {remitente_info['correo']}")
        else:
            print(f"⚠️ Puerto {puerto} no soportado en este flujo.")

    except Exception as e:
        print(f"❌ Error al enviar correo desde {remitente_info['correo']} a {destinatario}: {e}")
