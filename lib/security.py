from aws_xray_sdk.core import xray_recorder
from urllib.parse import quote
import secrets


@xray_recorder.capture("## Generating CSRF token")
def generate_csrf_token() -> str:
    return str(secrets.randbits(256))


@xray_recorder.capture("## Sanitizing user inputs")
def clean_data(data: dict[str, str]) -> dict[str, str]:
    return {k: quote(v) for k, v in data.items()}
