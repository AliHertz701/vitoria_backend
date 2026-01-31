# utils/wa_api.py
import requests
from urllib.parse import quote
import json
WAWP_BASE_URL = "https://wawp.net/wp-json/awp/v1/send"
INSTANCE_ID = "307CFB8A7EC9"      # replace with your Wawp instance_id
ACCESS_TOKEN = "Fu6JHEUkSsMq8j"    # replace with your Wawp access token

def send_wa_message(chat_id: str, message: str) -> dict:
    """
    Send a WhatsApp message via Wawp API.

    Args:
        chat_id (str): WhatsApp chat ID, e.g., "447441429009"
        message (str): Message text to send

    Returns:
        dict: API response as JSON
    """
    # URL encode the message
    encoded_message = quote(message)

    # Construct the request URL with query parameters
    url = f"{WAWP_BASE_URL}?instance_id={INSTANCE_ID}&access_token={ACCESS_TOKEN}&chatId={chat_id}&message={encoded_message}"

    try:
        response = requests.post(url)
        response.raise_for_status()
        return response.json()  # return JSON response
    except requests.exceptions.RequestException as e:
        # Return error details
        return {"success": False, "error": str(e)}

def format_libyan_number(number: str) -> str:
    """
    Normalize Libyan mobile numbers to international format +2189xxxxxxx
    Example: 0912345678 -> +218912345678
             912345678 -> +218912345678
    """
    number = number.strip()
    if number.startswith("0"):
        number = number[1:]
    if not number.startswith("9"):
        # assume user forgot leading 9
        number = "9" + number
    return f"+218{number}"

from decimal import Decimal, InvalidOperation


def parse_json_field(value, default=None):
    """
    Safely parse JSON fields sent as string or list
    """
    if default is None:
        default = []

    if value in (None, '', 'null'):
        return default

    if isinstance(value, list):
        return value

    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else default
        except json.JSONDecodeError:
            return default

    return default


def parse_bool(value, default=False):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes')
    return default