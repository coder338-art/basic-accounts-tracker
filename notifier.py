import requests
from datetime import datetime

def send_discord_embed(webhook: str, mention: str, title: str, description: str, color: int, fields: list):
    if not webhook:
        return
    payload = {
        "embeds": [
            {
                "title": title,
                "description": description,
                "color": color,
                "fields": fields,
                "timestamp": datetime.now().isoformat(),
            }
        ]
    }
    if mention and mention != "<@id>":
        payload["content"] = mention
    try:
        r = requests.post(webhook, json=payload, timeout=10)
        r.raise_for_status()
    except requests.RequestException:
        pass
