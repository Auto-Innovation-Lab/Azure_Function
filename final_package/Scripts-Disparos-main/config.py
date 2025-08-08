# config.py
import os
import base64
import requests
from msal import PublicClientApplication, SerializableTokenCache

CLIENT_ID = "5d526496-c347-49e5-9f30-974b9f03de6d"
AUTHORITY = "https://login.microsoftonline.com/common"
SCOPES = ["Files.Read.All"]

# ✅ Fuerza archivo local en Windows, /tmp en Linux (Function)
if os.name == "nt":
    CACHE_PATH = os.path.join(os.path.dirname(__file__), "token_cache.json")
else:
    CACHE_PATH = "/tmp/token_cache.json"

def _tmp_file(nombre_local: str) -> str:
    if os.name == "nt":
        return os.path.join(os.path.dirname(__file__), nombre_local)
    return f"/tmp/{nombre_local}"

def obtener_token():
    # Si no hay archivo y (solo si NO estamos en Windows) existe TOKEN_CACHE_BASE64, lo crea
    if not os.path.exists(CACHE_PATH):
        contenido_cache = os.environ.get("TOKEN_CACHE_BASE64") if os.name != "nt" else None
        if contenido_cache:
            with open(CACHE_PATH, "w", encoding="utf-8") as f:
                f.write(base64.b64decode(contenido_cache).decode("utf-8"))

    cache = SerializableTokenCache()
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            cache.deserialize(f.read())

    app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY, token_cache=cache)
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
    else:
        raise Exception("❌ No hay token almacenado. Crea token_cache.json local o define TOKEN_CACHE_BASE64 en Function.")

    if cache.has_state_changed:
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            f.write(cache.serialize())

    if "access_token" not in result:
        raise Exception("❌ Error de autenticación: token inválido")
    return result["access_token"]

def cargar_excel_desde_onedrive(shared_url, nombre_local, access_token):
    import base64, requests
    encoded_url = base64.urlsafe_b64encode(shared_url.encode()).decode().rstrip("=")
    graph_url = f"https://graph.microsoft.com/v1.0/shares/u!{encoded_url}/driveItem"
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get(graph_url, headers=headers); r.raise_for_status()
    download_url = r.json()["@microsoft.graph.downloadUrl"]
    r2 = requests.get(download_url)
    local_path = _tmp_file(nombre_local)
    with open(local_path, "wb") as f:
        f.write(r2.content)
    return local_path

onedrive_urls = {
    "contactos_prueba": "https://innovacionautomotriz-my.sharepoint.com/:x:/g/personal/edesio_santos_autolab_live/EX784WzxA2VLrrF_EbI4Qo0BDW5N9j07Iogq0Piqg_4Dbg",
    "disparo": "https://innovacionautomotriz-my.sharepoint.com/:x:/g/personal/edesio_santos_autolab_live/Ec7XjRxRB3lPgFsQvtqH5m0B0PpKUSTASOqyjhkKT_VBHw",
    "mails": "https://innovacionautomotriz-my.sharepoint.com/:x:/g/personal/edesio_santos_autolab_live/ER0Hli50zIBKuGIFyLPBv3IBPn1y0eKo3GBZhDshO-DqMw"
}

def get_paths():
    access_token = obtener_token()
    return {
        "contactos": cargar_excel_desde_onedrive(onedrive_urls["contactos_prueba"], "contactos.xlsx", access_token),
        "disparo": cargar_excel_desde_onedrive(onedrive_urls["disparo"], "disparo.xlsx", access_token),
        "mails": cargar_excel_desde_onedrive(onedrive_urls["mails"], "mails.xlsx", access_token),
        "log": "log_envios_historico_CL_May.csv",
    }
