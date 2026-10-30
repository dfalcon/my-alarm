# /// script
# dependencies = ["telethon>=1.45", "qrcode"]
# ///
"""Слухає канал у реальному часі й пересилає в групу пости з ключовими словами.

  alarm.py           запуск (працює постійно)
  alarm.py --login   вхід акаунта через QR (читає канал)
  alarm.py --test    самоперевірка ключових слів

Пересилає з власного акаунта в групу (сповіщення для інших) і собі нагадуванням у «Збережене» (сповіщення для себе).
"""
import asyncio, re, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from telethon import TelegramClient, events

HERE = Path(__file__).parent
ENV_FILE = HERE / ".env"
env = dict(l.split("=", 1) for l in ENV_FILE.read_text().split() if "=" in l) if ENV_FILE.exists() else {}

SOURCE = int(env.get("SOURCE", "-1001673474387"))  # TLk News
TARGET = int(env.get("TARGET", "-5124807835"))  # 🚨 Тривога

# ru + uk, будь-яке закінчення; \b — щоб «ракет» не ловилось усередині інших слів
KEYWORDS = re.compile(
    r"\bна\s+(город|місто)"
    r"|\bсалт[оі]вк"
    r"|\bнем[иы]шл"
    r"|\bракет"
    r"|\bкулинич"
    r"|\bкутуз[оі]вк",
    re.IGNORECASE,
)


def strip_footer(text: str) -> str:
    # прибирає «📷 TlkInst | 🎞 Канал со стримами»
    return re.split(r"\n\s*📷", text)[0].strip()


def make_client(name: str) -> TelegramClient:
    return TelegramClient(str(HERE / name), int(env["API_ID"]), env["API_HASH"])


async def login():
    import qrcode, getpass
    from telethon.errors import SessionPasswordNeededError, PasswordHashInvalidError
    client = make_client("user")
    await client.connect()
    try:
        while True:
            qr = await client.qr_login()  # якщо QR уже відскановано, одразу кидає SessionPasswordNeeded
            q = qrcode.QRCode(border=1); q.add_data(qr.url); q.print_ascii(invert=True)
            print("Телефон: Налаштування → Пристрої → Підключити пристрій, відскануйте QR")
            try:
                await qr.wait(timeout=60)
                break
            except asyncio.TimeoutError:
                print("QR прострочено, новий:")
    except SessionPasswordNeededError:
        while True:
            try:
                await client.sign_in(password=getpass.getpass("Хмарний пароль 2FA: "))
                break
            except PasswordHashInvalidError:
                print("Невірний пароль, ще раз")
    print("Увійшли як", (await client.get_me()).first_name)


async def main():
    user = make_client("user")
    await user.connect()
    if not await user.is_user_authorized():
        sys.exit("Немає сесії: запустіть alarm.py --login")
    await user.get_dialogs()  # кеш сутностей, щоб SOURCE резолвився

    @user.on(events.NewMessage(chats=SOURCE))
    async def on_post(event):
        text = strip_footer(event.raw_text or "")
        if not KEYWORDS.search(text):
            return
        await event.forward_to(TARGET)
        # собі: свої повідомлення не сповіщають, а нагадування в «Збереженому» — так
        await event.forward_to("me", schedule=datetime.now(timezone.utc) + timedelta(seconds=2))
        print("→", text.replace("\n", " | "), flush=True)

    print("Слухаю…", flush=True)
    await user.run_until_disconnected()


if __name__ == "__main__":
    if "--test" in sys.argv:
        yes = ["Ударный на город⚠️", "Ракета на Салтовку", "Шахед на Немышлю", "Ракети на Салтівку",
               "Далее Кулиничи", "Курс Кутузовка", "Баллистика на Немишлю", "РАКЕТА"]
        no = ["Отбой для города❤️", "Реактивная шаболда на Лозовую⚠️", "Далее Левада/Центр⚠️",
              "Ударный на Шевченково⚠️", "Далее на Полтавскую область⚠️"]
        for s in yes:
            assert KEYWORDS.search(s), s
        for s in no:
            assert not KEYWORDS.search(s), s
        assert strip_footer("Ударный на город⚠️\n\n📷 TlkInst | 🎞 Канал со стримами") == "Ударный на город⚠️"
        print("ok")
    elif "--login" in sys.argv:
        asyncio.run(login())
    else:
        asyncio.run(main())
