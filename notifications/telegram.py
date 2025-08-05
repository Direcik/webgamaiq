import requests

TELEGRAM_BOT_TOKEN = "8172007385:AAFpqSNMxpy7q0iuDyw6k0hULyQMKBY47R8"
TELEGRAM_CHAT_ID = "-1002836643133"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Telegram mesaj hatası:", e)