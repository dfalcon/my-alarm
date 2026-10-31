# my-alarm

Юзербот на [Telethon](https://github.com/LonamiWebs/Telethon): у реальному часі слухає канал **TLk News** і пересилає в групу **🚨 Тривога** пости з ключовими словами.

Ключові слова (ru/uk, будь-яке закінчення, без урахування регістру) — `KEYWORDS` в `alarm.py`:

- на город / на місто
- Салтовка / Салтівка
- Немышля / Немишля
- ракета
- Кулиничи
- Кутузовка / Кутузівка

Пересилання йде з вашого акаунта: інші учасники групи отримують сповіщення, а вам пост дублюється нагадуванням у «Збережене» (≈10 с: з меншою затримкою Telegram не сповіщає), щоб теж було сповіщення.

## Встановлення

Потрібен [uv](https://docs.astral.sh/uv/) і `api_id` / `api_hash` з https://my.telegram.org.

```sh
git clone git@github.com:dfalcon/my-alarm.git ~/projects/my-alarm && cd ~/projects/my-alarm
cp .env.example .env          # заповнити API_ID, API_HASH
uv run alarm.py --login       # QR: Налаштування → Пристрої → Підключити пристрій
uv run alarm.py --test        # самоперевірка ключових слів
```

Запуск як сервіс (перезапускається сам після падіння чи ребуту):

```sh
sudo cp my-alarm.service /etc/systemd/system/
sudo systemctl enable --now my-alarm
journalctl -u my-alarm -f     # лог пересилань
```

## Безпека

`user.session` — повний доступ до акаунта. Не комітити, права `600`.
