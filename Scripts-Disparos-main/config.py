# config.py
import os
import base64
import requests
from msal import PublicClientApplication, SerializableTokenCache

# === CONFIGURACIÓN DE AUTENTICACIÓN MSAL ===
CLIENT_ID = "5d526496-c347-49e5-9f30-974b9f03de6d"
AUTHORITY = "https://login.microsoftonline.com/common"
SCOPES = ["Files.Read.All"]
CACHE_PATH = "/tmp/token_cache.json"

# === OBTENER TOKEN DE ACCESO DESDE CACHÉ O NUEVO ===
def obtener_token():
    # ⏳ Intenta restaurar desde variable de entorno si no existe archivo
    if not os.path.exists(CACHE_PATH):
        contenido_cache = os.environ.get("TOKEN_CACHE_BASE64")
        if contenido_cache:
            with open(CACHE_PATH, "w") as f:
                f.write(base64.b64decode(contenido_cache).decode("utf-8"))

    cache = SerializableTokenCache()
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r") as f:
            cache.deserialize(f.read())

    app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY, token_cache=cache)
    accounts = app.get_accounts()

    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
    else:
        raise Exception("❌ No hay token almacenado. Ejecuta localmente para autenticar y generar el cache.")

    if cache.has_state_changed:
        with open(CACHE_PATH, "w") as f:
            f.write(cache.serialize())

    if "access_token" not in result:
        raise Exception("❌ Error de autenticación: token inválido")

    return result["access_token"]

# === FUNCION GENÉRICA PARA DESCARGAR UN EXCEL DESDE ONEDRIVE ===
def cargar_excel_desde_onedrive(shared_url, nombre_local, access_token):
    encoded_url = base64.urlsafe_b64encode(shared_url.encode()).decode().rstrip("=")
    graph_url = f"https://graph.microsoft.com/v1.0/shares/u!{encoded_url}/driveItem"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(graph_url, headers=headers)
    response.raise_for_status()
    download_url = response.json()["@microsoft.graph.downloadUrl"]

    response_excel = requests.get(download_url)
    local_path = f"/tmp/{nombre_local}"
    with open(local_path, "wb") as f:
        f.write(response_excel.content)

    return local_path

# === URLS DE ARCHIVOS EXCEL EN ONEDRIVE ===
onedrive_urls = {
    "contactos_prueba": "https://innovacionautomotriz-my.sharepoint.com/:x:/g/personal/edesio_santos_autolab_live/EX784WzxA2VLrrF_EbI4Qo0BDW5N9j07Iogq0Piqg_4Dbg",
    "contactos_alternativos": "https://innovacionautomotriz-my.sharepoint.com/:x:/g/personal/edesio_santos_autolab_live/ER0Hli50zIBKuGIFyLPBv3IBPn1y0eKo3GBZhDshO-DqMw",
    "disparo": "https://innovacionautomotriz-my.sharepoint.com/:x:/g/personal/edesio_santos_autolab_live/EYxP44-3ubNKtKjt_IA4XckB7hqNtqRJXK3dOSPD2T0GXQ",
    "mails": "https://innovacionautomotriz-my.sharepoint.com/:x:/g/personal/edesio_santos_autolab_live/Ec7XjRxRB3lPgFsQvtqH5m0B0PpKUSTASOqyjhkKT_VBHw"
}

# === FUNCION FINAL QUE DEVUELVE TODOS LOS PATHS DE FORMA SEGURA ===
def get_paths():
    access_token = obtener_token()
    return {
        "contactos": cargar_excel_desde_onedrive(onedrive_urls["contactos_prueba"], "contactos.xlsx", access_token),
        "disparo": cargar_excel_desde_onedrive(onedrive_urls["disparo"], "disparo.xlsx", access_token),
        "mails": cargar_excel_desde_onedrive(onedrive_urls["mails"], "mails.xlsx", access_token),
        "log": "log_envios_historico_CL_May.csv",
        "alternativos": cargar_excel_desde_onedrive(onedrive_urls["contactos_alternativos"], "contactos_alt.xlsx", access_token)
    }
