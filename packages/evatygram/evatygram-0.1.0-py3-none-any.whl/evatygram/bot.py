from telethon import TelegramClient
from telethon.sessions import StringSession

class EvatyBot:
    def __init__(self, api_id, api_hash, string_session):
        self.client = TelegramClient(StringSession(string_session), api_id, api_hash)

    def start(self):
        print("✅ تم تشغيل البوت بنجاح.")
        self.client.start()
        self.client.run_until_disconnected()