import asyncio
import os
import random
import uuid
import json

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

STICKERS_FILE = "stickers.txt"
STATS_FILE = "stats.json"

GOOD_WORDS = [
    "легенда",
    "император",
    "король",
    "магистр",
    "чемпион",
    "герой",
    "избранный",
    "гений",
    "маэстро",
    "мастер",
    "победитель",
    "повелитель удачи",
    "архимаг",
    "сверхразум",
    "лучик солнца",
    "главный красавчик",
    "великий стратег",
    "властелин мемов",
    "любимец судьбы",
    "источник вдохновения",
]

RITUAL_PHRASES = [
    "📡 Подключаюсь к космосу...",
    "🔮 Вхожу в поток...",
    "🃏 Перемешиваю карты...",
    "👁 Сканирую ауру...",
    "⚡ Запрашиваю высшие силы...",
    "🌌 Заглядываю в будущее...",
    "🧠 Открываю сознание...",
    "☄️ Считываю вибрации вселенной...",
    "🌫 Пробиваюсь через туман судьбы...",
    "📖 Листаю книгу пророчеств...",
    "🕯 Провожу древний ритуал...",
    "🐈 Консультируюсь с мудрым котом...",
    "🍀 Проверяю удачу пользователя...",
    "🛸 Отправляю запрос пришельцам...",
    "🎱 Трясу магический шар...",
    "💫 Ответ уже близко...",
]


def load_stickers():
    if not os.path.exists(STICKERS_FILE):
        return []

    with open(STICKERS_FILE, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def save_sticker(sticker_id):
    stickers = load_stickers()

    if sticker_id not in stickers:
        with open(STICKERS_FILE, "a", encoding="utf-8") as file:
            file.write(sticker_id + "\n")
        return True

    return False

def load_stats():
    if not os.path.exists(STATS_FILE):
        return {
            "total_predictions": 0,
            "users": {}
        }

    with open(STATS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_stats(stats):
    with open(STATS_FILE, "w", encoding="utf-8") as file:
        json.dump(stats, file, ensure_ascii=False, indent=4)


def add_prediction_to_stats(user):
    stats = load_stats()

    user_id = str(user.id)
    user_name = get_user_name(user)

    stats["total_predictions"] += 1

    if user_id not in stats["users"]:
        stats["users"][user_id] = {
            "name": user_name,
            "count": 0
        }

    stats["users"][user_id]["name"] = user_name
    stats["users"][user_id]["count"] += 1

    save_stats(stats)

    return stats["users"][user_id]["count"], stats["total_predictions"]

def get_user_name(user):
    if user.username:
        return f"@{user.username}"

    if user.first_name:
        return user.first_name

    return "Таинственный герой"


def get_prediction(user_name):
    title = random.choice(GOOD_WORDS)

    if user_name.lower() == "@kush0769" and random.randint(1, 100) <= 35:
        kush_predictions = [
            "🔮 А Никитулику карты советуют сегодня не спорить с судьбой",
            "🍀 Судьба считает, что Никитулик опять что-то натворит",
            "👁 Высшие силы внимательно наблюдают за Никитуликом",
            "🐸 Тайный совет жаб признал Никитулика подозрительно счастливым",
            "📡 Космос передаёт: Никитулик снова в центре событий",
            "🃏 Карты показали, что Никитулик слегка переоценивает свои силы",
            "🎱 Магический шар ответил: 'Это же Никитулик, всё возможно'",
            "🌫 Пророчество предупреждает: Никитулик может внезапно захотеть приключений",
            "⚡ Вселенная рекомендует Никитулику держаться подальше от сомнительных идей",
            "🦄 Мифическое существо подтвердило: Никитулик сегодня особенный",
        ]

        return random.choice(kush_predictions)

    special_events = [
        f"👑 УКАЗ ВСЕЛЕННОЙ: {user_name} получает титул Верховного {title}",
        f"🦄 МИФИЧЕСКИЙ ДРОП: {user_name} выбил ранг '{title}'",
        f"🏆 ДОСТИЖЕНИЕ ОТКРЫТО: {user_name} — {title}",
        f"⭐ ЗВЕЗДЫ ПОСТАНОВИЛИ: {user_name} официально {title}",
        f"🎉 ПРАЗДНИЧНОЕ ПРОРОЧЕСТВО: {user_name} — {title}",
    ]

    if random.randint(1, 100) <= 2:
        return random.choice(special_events)

    rare_predictions = [
        f"💎 РЕДКОЕ ПРОРОЧЕСТВО: {user_name} — легендарный {title}",
        f"👑 ВЫСШИЕ СИЛЫ ПОДТВЕРДИЛИ: {user_name} — великий {title}",
        f"🦄 МИФИЧЕСКОЕ ВИДЕНИЕ: {user_name} всемогущий {title}",
    ]

    if random.randint(1, 100) <= 5:
        return random.choice(rare_predictions)

    predictions = [
        f"🔮 Карты говорят: {user_name} — {title}",
        f"✨ Звезды сошлись: {user_name} сегодня {title}",
        f"👑 Древнее пророчество гласит: {user_name} — настоящий {title}",
        f"🍀 Судьба решила: {user_name} — {title}",
        f"🚀 Космос подтвердил: {user_name} радостный {title}",
        f"😎 Мудрость дня: {user_name} — {title}",
        f"🔥 Великий оракул сказал: {user_name} — абсолютный {title}",
    ]

    return random.choice(predictions)


def prediction_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 Еще предсказание",
                    callback_data="new_prediction"
                )
            ]
        ]
    )


async def play_ritual_and_send(message: Message, user_name: str, user_count=None, total_count=None):
    ritual = random.sample(RITUAL_PHRASES, random.randint(3, 5))

    status_msg = await message.answer(ritual[0])

    for phrase in ritual[1:]:
        await asyncio.sleep(1)
        await status_msg.edit_text(phrase)

    await asyncio.sleep(1)

    prediction_text = get_prediction(user_name)

    if user_count is not None and total_count is not None:
        prediction_text += (
            f"\n\n📊 Твоё предсказание №{user_count}"
            f"\n🌍 Всего предсказаний: {total_count}"
        )

    await status_msg.edit_text(
        prediction_text,
        reply_markup=prediction_keyboard()
    )

    stickers = load_stickers()

    if stickers:
        await message.answer_sticker(random.choice(stickers))


async def send_random_prediction(message: Message):
    user_name = get_user_name(message.from_user)
    user_count, total_count = add_prediction_to_stats(message.from_user)

    await play_ritual_and_send(
        message,
        user_name,
        user_count,
        total_count
    )


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🔮 <b>Стикер Таро Предсказание</b>\n\n"
        "Нажми кнопку ниже и узнай великое пророчество.",
        reply_markup=prediction_keyboard(),
        parse_mode="HTML"
    )


@dp.message(Command("predict"))
async def predict_command(message: Message):
    await send_random_prediction(message)


@dp.message(F.sticker)
async def get_sticker_id(message: Message):
    sticker_id = message.sticker.file_id
    is_new = save_sticker(sticker_id)

    if is_new:
        await message.answer("✅ Стикер добавлен в базу предсказаний")
    else:
        await message.answer("ℹ️ Такой стикер уже есть в базе")


@dp.message(F.text == "🔮 Получить предсказание")
async def predict_text_button(message: Message):
    await send_random_prediction(message)


@dp.callback_query(F.data == "new_prediction")
async def new_prediction(callback: CallbackQuery):
    await callback.answer()

    user_name = get_user_name(callback.from_user)
    user_count, total_count = add_prediction_to_stats(callback.from_user)

    await play_ritual_and_send(
        callback.message,
        user_name,
        user_count,
        total_count
    )


@dp.message(Command("stats"))
async def stats_command(message: Message):
    stats = load_stats()

    total = stats.get("total_predictions", 0)
    users = stats.get("users", {})

    if not users:
        await message.answer("📊 Статистики пока нет.")
        return

    top_users = sorted(
        users.values(),
        key=lambda user: user["count"],
        reverse=True
    )[:10]

    text = f"📊 <b>Статистика предсказаний</b>\n\n🌍 Всего предсказаний: {total}\n\n🏆 Топ пользователей:\n"

    for index, user in enumerate(top_users, start=1):
        text += f"{index}. {user['name']} — {user['count']}\n"

    await message.answer(text, parse_mode="HTML")

@dp.inline_query()
async def inline_prediction(inline_query: InlineQuery):
    user_name = get_user_name(inline_query.from_user)
    prediction = get_prediction(user_name)

    result = InlineQueryResultArticle(
        id=str(uuid.uuid4()),
        title="🔮 Получить предсказание",
        description=prediction,
        input_message_content=InputTextMessageContent(
            message_text=prediction
        )
    )

    await inline_query.answer(
        results=[result],
        cache_time=0,
        is_personal=True
    )


async def main():
    print("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())