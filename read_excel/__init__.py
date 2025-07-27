import logging
import os
import base64
import requests
import pandas as pd
import azure.functions as func
from msal import ConfidentialClientApplication

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("🔁 Procesando solicitud HTTP para leer Excel de OneDrive...")

    # ======= CREDENCIALES =======
    CLIENT_ID = "5d526496-c347-49e5-9f30-974b9f03de6d"
    TENANT_ID = "cf09ef95-0de5-4f9f-996d-dc7ad84572f2"
    CLIENT_SECRET = os.environ["CLIENT_SECRET"]

    # ======= AUTENTICACIÓN =======
    AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
    SCOPES = ["https://graph.microsoft.com/.default"]

    app = ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
    )

    result = app.acquire_token_for_client(scopes=SCOPES)
    if "access_token" not in result:
        return func.HttpResponse(
            f"❌ Error autenticando: {result.get('error_description')}",
            status_code=500
        )

    token = result["access_token"]

    # ======= ARCHIVO DE ONEDRIVE =======
    shared_url = "https://innovacionautomotriz-my.sharepoint.com/:x:/g/personal/edesio_santos_autolab_live/EUE7jfu1RbFDo3CpUD9g3YYBIKOhep453J-EpSMtULMr_A"
    encoded_url = base64.urlsafe_b64encode(shared_url.encode()).decode().rstrip("=")
    graph_url = f"https://graph.microsoft.com/v1.0/shares/u!{encoded_url}/driveItem"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        r = requests.get(graph_url, headers=headers)
        r.raise_for_status()
        item_info = r.json()
        download_url = item_info["@microsoft.graph.downloadUrl"]

        # Descargar y leer archivo
        file = requests.get(download_url)
        file.raise_for_status()
        with open("/tmp/temp.xlsx", "wb") as f:
            f.write(file.content)

        df = pd.read_excel("/tmp/temp.xlsx")
        return func.HttpResponse(df.head().to_json(orient="records"), mimetype="application/json")

    except Exception as e:
        logging.error(f"❌ Error general: {str(e)}")
        return func.HttpResponse(f"❌ Error: {str(e)}", status_code=500)
