import base64
import json

from google.cloud import storage
from google.oauth2 import service_account

from src.config import config


def get_gcp_credentials():
    if config.GCP_PRIVATE_KEY_BASE64:
        private_key_base64 = config.GCP_PRIVATE_KEY_BASE64
    else:
        raise Exception({"detail": "GCP_PRIVATE_KEY_BASE64가 없습니다."})

    try:
        private_key_json = base64.b64decode(private_key_base64)
    except:
        raise Exception({"detail": "잘못된 형식입니다. BASE64를 입력해주세요."})

    private_key = json.loads(private_key_json)
    return service_account.Credentials.from_service_account_info(private_key)


def create_storage_client():
    credentials = get_gcp_credentials()
    return storage.Client(credentials=credentials)


gcp_client = create_storage_client()
