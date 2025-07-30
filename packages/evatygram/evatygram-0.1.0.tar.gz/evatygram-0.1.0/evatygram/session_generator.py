from telethon.sync import TelegramClient
from telethon.sessions import StringSession

def generate_session(api_id: int, api_hash: str):
    print("ابدأ عملية تسجيل الدخول للحصول على string session (حساب عادي)")
    with TelegramClient(StringSession(), api_id, api_hash) as client:
        print("سجّل الدخول إلى حسابك عن طريق الكود الذي سيُرسل لك...")
        string = client.session.save()
        print(f"\n✅ تم استخراج الجلسة بنجاح:\n{string}")
        return string

def generate_bot_session(api_id: int, api_hash: str, bot_token: str):
    print("يتم الآن تسجيل دخول البوت...")
    with TelegramClient(StringSession(), api_id, api_hash).start(bot_token=bot_token) as bot:
        string = bot.session.save()
        print(f"\n✅ تم استخراج string session للبوت:
{string}")
        return string