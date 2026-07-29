import os
import requests
from utils.logger import logger

class DiscordAlerter:
    def __init__(self):
        self.token = None
        self.channel_id = None
        self._load_credentials()
        
    def _load_credentials(self):
        try:
            with open("/home/mason/.hermes/.env", "r") as f:
                for line in f:
                    if line.startswith("DISCORD_BOT_TOKEN="):
                        self.token = line.strip().split("=", 1)[1]
                    elif line.startswith("DISCORD_HOME_CHANNEL="):
                        self.channel_id = line.strip().split("=", 1)[1]
        except Exception as e:
            logger.error(f"Failed to load Discord credentials from .hermes/.env: {e}")
            
    def send_alert(self, message: str):
        if not self.token or not self.channel_id:
            logger.warning("Discord alerter not configured properly, skipping alert.")
            return False
            
        url = f"https://discord.com/api/v10/channels/{self.channel_id}/messages"
        headers = {
            "Authorization": f"Bot {self.token}",
            "Content-Type": "application/json"
        }
        payload = {"content": message}
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to send Discord alert: {e}")
            return False

discord_alerter = DiscordAlerter()
