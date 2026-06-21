import asyncio
import html
import json
import os
import random
from datetime import datetime, timezone, timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile,
)
from dotenv import load_dotenv
from PIL import Image

from tarot_cards import TAROT_CARDS

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

bot = Bot(token=TOKEN)
dp = Dispatcher()

DAILY_TAROT_FILE = "daily_tarot.json"
STATS_FILE = "stats.json"

APP_TIMEZONE = timezone(timedelta(hours=3))

TAROT_RITUAL_PHRASES = [
    "🕯 Зажигаю свечу...",
    "🃏 Перемешиваю колоду...",
    "🌌 Слушаю тишину между картами...",
    "🔮 Настраиваюсь на твой день...",
    "👁 Смотрю, какая карта тянется к тебе...",
    "🌫 Разгоняю туман вероятностей...",
    "✨ Карта почти открылась...",
]


def today_string():
    return datetime.now(APP_TIMEZONE).date().isoformat()


def load_json_file(file_path, default_value):
    if not os.path.exists(file_path):
        return default_value

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json_file(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def get_user_name(user):
    if user.username:
        return f"@{user.username}"

    if user.first_name:
        return user.first_name

    return "Таинственный герой"


def add_stat(user, event_name):
    stats = load_json_file(
        STATS_FILE,
        {
            "events": {},
            "users": {},
        },
    )

    user_id = str(user.id)
    user_name = get_user_name(user)

    stats["events"][event_name] = stats["events"].get(event_name, 0) + 1

    if user_id not in stats["users"]:
        stats["users"][user_id] = {
            "name": user_name,
            "events": {},
        }

    stats["users"][user_id]["name"] = user_name
    user_events = stats["users"][user_id]["events"]
    user_events[event_name] = user_events.get(event_name, 0) + 1

    save_json_file(STATS_FILE, stats)


def get_card_by_id(card_id):
    for card in TAROT_CARDS:
        if card["id"] == card_id:
            return card

    return None


def choose_orientation():
    # 70% — прямая карта, 30% — перевёрнутая
    if random.randint(1, 100) <= 30:
        return "reversed"

    return "upright"


def get_or_create_daily_card(user):
    daily_data = load_json_file(DAILY_TAROT_FILE, {})
    user_id = str(user.id)
    today = today_string()

    user_record = daily_data.get(user_id)

    if user_record and user_record.get("date") == today:
        card = get_card_by_id(user_record["card_id"])
        orientation = user_record["orientation"]

        if card:
            return card, orientation, True

    card = random.choice(TAROT_CARDS)
    orientation = choose_orientation()

    daily_data[user_id] = {
        "date": today,
        "card_id": card["id"],
        "orientation": orientation,
        "user_name": get_user_name(user),
    }

    save_json_file(DAILY_TAROT_FILE, daily_data)

    return card, orientation, False


def get_card_image_path(card, orientation):
    image_path = card["image"]

    if orientation == "upright":
        return image_path

    os.makedirs("generated", exist_ok=True)

    reversed_image_path = os.path.join(
        "generated",
        f"{card['id']}_reversed.jpg",
    )

    try:
        with Image.open(image_path) as image:
            rotated_image = image.rotate(180, expand=True)
            rotated_image.save(reversed_image_path)

        return reversed_image_path
    except Exception:
        return image_path


def format_card_caption(card, orientation, is_repeat):
    orientation_text = "🔺 Прямое положение" if orientation == "upright" else "🔻 Перевёрнутое положение"
    card_meaning = card[orientation]
    keywords = ", ".join(card["keywords"][orientation])

    repeat_text = ""
    if is_repeat:
        repeat_text = "\n\n🔁 Сегодня твоя карта уже открыта. Показываю её ещё раз."

    return (
        f"🃏 <b>Твоя карта дня: {html.escape(card['name'])}</b>\n"
        f"{orientation_text}\n"
        f"Аркан: {html.escape(card['arcana'])}"
        f"{repeat_text}\n\n"
        f"🔑 <b>Ключевые слова:</b>\n"
        f"{html.escape(keywords)}\n\n"
        f"📖 <b>Значение на день:</b>\n"
        f"{html.escape(card_meaning['meaning'])}\n\n"
        f"💡 <b>Совет:</b>\n"
        f"{html.escape(card_meaning['advice'])}\n\n"
        f"Возвращайся завтра за новой картой."
    )


def main_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔮 Получить карту дня",
                    callback_data="daily_tarot",
                )
            ]
        ]
    )


async def play_ritual(message: Message):
    ritual = random.sample(TAROT_RITUAL_PHRASES, random.randint(5, 7))

    status_message = await message.answer(ritual[0])

    for phrase in ritual[1:]:
        await asyncio.sleep(1.3)
        await status_message.edit_text(phrase)

    await asyncio.sleep(1.5)
    await status_message.edit_text("🃏 Карта выбрана...")

    return status_message


async def send_daily_tarot(message: Message, user):
    add_stat(user, "daily_tarot_request")

    card, orientation, is_repeat = get_or_create_daily_card(user)

    if is_repeat:
        add_stat(user, "daily_tarot_repeat")
    else:
        add_stat(user, "daily_tarot_new")

    await play_ritual(message)

    image_path = get_card_image_path(card, orientation)
    caption = format_card_caption(card, orientation, is_repeat)

    if os.path.exists(image_path):
        await message.answer_photo(
            photo=FSInputFile(image_path),
            caption=caption,
            parse_mode="HTML",
            reply_markup=main_keyboard(),
        )
    else:
        await message.answer(
            caption,
            parse_mode="HTML",
            reply_markup=main_keyboard(),
        )


@dp.message(CommandStart())
async def start(message: Message):
    add_stat(message.from_user, "start")

    await message.answer(
        "🔮 <b>Таро Предсказание</b>\n\n"
        "Один раз в день бот вытягивает для тебя карту Таро, показывает её значение и совет на день.\n\n"
        "Нажми кнопку ниже или отправь команду /tarot.",
        parse_mode="HTML",
        reply_markup=main_keyboard(),
    )


@dp.message(Command("tarot"))
async def tarot_command(message: Message):
    await send_daily_tarot(message, message.from_user)


@dp.message(Command("version"))
async def version_command(message: Message):
    await message.answer("🤖 Версия бота: 2.0 Tarot MVP")


@dp.message(Command("stats"))
async def stats_command(message: Message):
    if OWNER_ID != 0 and message.from_user.id != OWNER_ID:
        await message.answer("⛔ Статистика доступна только владельцу бота.")
        return

    stats = load_json_file(
        STATS_FILE,
        {
            "events": {},
            "users": {},
        },
    )

    events = stats.get("events", {})
    users = stats.get("users", {})

    total_requests = events.get("daily_tarot_request", 0)
    new_cards = events.get("daily_tarot_new", 0)
    repeats = events.get("daily_tarot_repeat", 0)
    starts = events.get("start", 0)

    top_users = sorted(
        users.values(),
        key=lambda item: item.get("events", {}).get("daily_tarot_request", 0),
        reverse=True,
    )[:10]

    text = (
        "📊 <b>Статистика бота</b>\n\n"
        f"🚀 Запусков /start: {starts}\n"
        f"🔮 Запросов карты дня: {total_requests}\n"
        f"🆕 Новых карт: {new_cards}\n"
        f"🔁 Повторных показов: {repeats}\n"
        f"👥 Уникальных пользователей: {len(users)}\n\n"
        "🏆 <b>Топ пользователей:</b>\n"
    )

    if not top_users:
        text += "Пока пусто."
    else:
        for index, user_data in enumerate(top_users, start=1):
            user_name = html.escape(user_data["name"])
            count = user_data.get("events", {}).get("daily_tarot_request", 0)
            text += f"{index}. {user_name} — {count}\n"

    await message.answer(text, parse_mode="HTML")


@dp.callback_query(F.data == "daily_tarot")
async def daily_tarot_callback(callback: CallbackQuery):
    await callback.answer()
    await send_daily_tarot(callback.message, callback.from_user)


async def main():
    print("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())