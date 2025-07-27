# Scripts-Disparos
# Envío Automatizado de Cotizaciones desde Sitios Web

Este codigo permite enviar correos automáticos a distintos contactos, cotizando repuestos encontrados en sus páginas web. La lógica incluye rotación de remitentes, selección aleatoria de productos, detección aproximada de dominios, y variación del mensaje para evitar correos repetitivos.

---

## Estructura del script

### `main.py`

Script principal que realiza el flujo completo de la automatización:

1. Carga los archivos necesarios (contactos, links y remitentes).
2. Agrupa los links por dominio.
3. Encuentra el contacto más adecuado para cada dominio.
4. Elige aleatoriamente hasta 4 productos por dominio.
5. Genera un cuerpo de correo con formato variado.
6. Envía el correo usando un remitente rotativo.
7. Guarda un log con los detalles de cada envío.

---

### `funciones_utiles.py`

Contiene funciones auxiliares que organizan y simplifican el flujo del `main.py`:

- `cargar_datos(paths)`: carga los archivos Excel desde las rutas configuradas.
- `filtrar_datos(df_links, df_contactos)`: limpia y filtra datos innecesarios.
- `cargar_remitentes(path)`: carga los remitentes disponibles para rotar los correos.
- `RotadorRemitentes`: clase que rota entre los distintos remitentes.
- `dominio_mas_parecido(dominio, lista_dominios, umbral)`: compara dominios usando coincidencia aproximada.
- `generar_cuerpo(productos)`: genera un mensaje variado y dinámico con los productos encontrados.
- `guardar_log(df_log, ruta)`: guarda el log de envíos exitosos.

---

### `funciones_enviar.py`

Contiene la función encargada de enviar los correos:

- `enviar_correo(remitente_info, destinatario, asunto, cuerpo)`: se conecta vía SMTP usando los datos del remitente, arma el correo con el cuerpo y asunto, y lo envía al destinatario.

Soporta autenticación TLS (puerto 587) y maneja errores individualmente por destinatario.

---

### `config.py`

Define las rutas de los archivos utilizados por el sistema:

```python
paths = {
    'contactos': r'c:\Users\repue\OneDrive - Innovación Automotriz Spa\AutoLab Post Ventas\0 Base Central\Contactos de Prueba.xlsx',
    'disparo': r'c:\Users\repue\OneDrive - Innovación Automotriz Spa\AutoLab Post Ventas\0 Base Central Alternativos\2025\Search Links Validos 20042025.xlsx',
    'mails': r'c:\Users\repue\OneDrive - Innovación Automotriz Spa\AutoLab Post Ventas\0 Base Central\Mails.xlsx',
    'log': r'log_envios_historico.xlsx'
}
```

## Archivos esperados
### `Search Link Validos 20042025.xlsx`
El nombre de este archivo puede ir cambiando dependiendo de la fecha asi que revisar antes de ejecutar
Debe contener las siguiente columnas:
* `Dominio`: dominio de origen del link (ej: www.ejemplo.cl)
* `Descripcion`: descripción del repuesto
* `Enlace`: URL del producto
  
En el codigo ya esta filtrado dependiendo de la ola que se encuentre. Actualmente estamos en la ola 3

### `Mails.xlsx`
Contiene los remitentes desde los cuales se enviarán los correos. Debe tener columnas como:
* E-mails
* Servidor SMPT
* Puerto
* Login
* Contraseña

Se puede especificar la hoja si quiere ocupar mails personales o mails de empresa.

### `Contactos Alternativos.xlsx`
Debe tener una columna `Cluster` con el dominio de cada contacto, y `Mail` con su dirección de correo.

## Como ejecutar el script
1. Asegúrate de tener los siguientes archivos en la misma carpeta del script:

   - `Contactos Alternativos.xlsx`
   - `Search Link Validos 20042025.xlsx`
   - `Mails.xlsx`

2. Ejecuta el script principal:
   Sea con el `Run` de VS code o el editor de codigo de preferencia o tambien se puede ejecutar en el terminal con `python main.py`


El sistema enviará correos personalizados con 1 a 4 links por contacto, evitando duplicados y rotando automáticamente los remitentes. Todos los envíos se registrarán en `log_envios.xlsx`.




