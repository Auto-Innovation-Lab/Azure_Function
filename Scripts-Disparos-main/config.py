# config.py
import os
import base64
import requests
from msal import PublicClientApplication, SerializableTokenCache

# === Configuración de MSAL ===
CLIENT_ID = "5d526496-c347-49e5-9f30-974b9f03de6d"
AUTHORITY = "https://login.microsoftonline.com/common"
SCOPES = ["Files.Read.All"]
CACHE_PATH = "/tmp/token_cache.json"

# === Autenticación y token ===
def obtener_token():
    cache = SerializableTokenCache()
    if os.path.exists(CACHE_PATH):
        cache.deserialize(open(CACHE_PATH, "r").read())

    app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY, token_cache=cache)
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
    else:
        raise Exception("No hay cuenta guardada. Ejecuta localmente para autenticar y subir token_cache.json")

    if cache.has_state_changed:
        with open(CACHE_PATH, "w") as f:
            f.write(cache.serialize())

    if "access_token" not in result:
        raise Exception("Autenticación fallida")

    return result["access_token"]

# === Cargar archivo desde OneDrive ===
def cargar_excel_desde_onedrive(shared_url, nombre_local, access_token):
    encoded_url = base64.urlsafe_b64encode(shared_url.encode()).decode().rstrip("=")
    graph_url = f"https://graph.microsoft.com/v1.0/shares/u!{encoded_url}/driveItem"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(graph_url, headers=headers)
    response.raise_for_status()
    download_url = response.json()["@microsoft.graph.downloadUrl"]

    excel_response = requests.get(download_url)
    local_path = f"/tmp/{nombre_local}"
    with open(local_path, "wb") as f:
        f.write(excel_response.content)

    return local_path

# === URLs compartidas de los archivos Excel ===
onedrive_urls = {
    "contactos_prueba": "https://.../EX784WzxA2VLrrF_EbI4Qo0BDW5N9j07Iogq0Piqg_4Dbg",
    "contactos_alternativos": "https://.../ER0Hli50zIBKuGIFyLPBv3IBPn1y0eKo3GBZhDshO-DqMw",
    "disparo": "https://.../EYxP44-3ubNKtKjt_IA4XckB7hqNtqRJXK3dOSPD2T0GXQ",
    "mails": "https://.../Ec7XjRxRB3lPgFsQvtqH5m0B0PpKUSTASOqyjhkKT_VBHw"
}
