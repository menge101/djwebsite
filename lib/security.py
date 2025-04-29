from aws_xray_sdk.core import xray_recorder
from html_sanitizer import Sanitizer
import secrets


@xray_recorder.capture("## Generating CSRF token")
def generate_csrf_token() -> str:
    return str(secrets.randbits(256))


@xray_recorder.capture("## Sanitizing user inputs")
def clean_data(data: dict[str, str]) -> dict[str, str]:
    sanitizer = Sanitizer()
    return {k: sanitizer.sanitize(v) for k, v in data.items()}
