import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, CallbackQuery

from keyboards import *
from database_manager import DatabaseManager
from config import TEST_FIELD_TOKEN, ADMIN_ID, CREATOR_ID, GREETING, DEFAULT_ANSWER

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('Anonka')

bot = Bot(token=TEST_FIELD_TOKEN)
dp = Dispatcher()

# Инициализация синхронной БД
database = DatabaseManager()

# Глобальный флаг для отслеживания ожидания сообщения
awaiting_message = {}


@dp.message(Command("start"))
async def start(message: Message):
    try:
        user = message.from_user
        logger.info(f"Пользователь {user.username} добавлен в базу")

        greeting_image = FSInputFile(
            r"C:\Users\admin\Desktop\Проекты\Bots\Бесплатно\Анонимка Ники\start_image.jpg",
            filename="start_image.jpg"
        )

        keyboard = await default_keyboard()

        await message.answer_photo(
            photo=greeting_image,
            caption=GREETING,
            parse_mode="HTML",
            reply_markup=keyboard.as_markup()
        )
    except Exception as e:
        logger.error(e)


@dp.callback_query(F.data == "send_message")
async def request_message(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        awaiting_message[user_id] = True

        await callback.message.answer("Отправьте нам своё анонимное сообщение")
        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка в request_message: {e}")
        await callback.answer("⚠️ Произошла ошибка")


@dp.callback_query(F.data == "user_game_mode")
async def game_mode(callback: CallbackQuery):
    user_id = callback.from_user.id
    admin_keyboard = await admin_game_mode_keyboard()
    user_keyboard = await user_game_mode_keyboard()

    if user_id == ADMIN_ID:
        await callback.message.answer(
            "Добро пожаловать в настройки игрового режима",
            reply_markup=admin_keyboard
        )

    await callback.message.answer(
        "Добро пожаловать в игровой режим",
        reply_markup=user_keyboard
    )
    await callback.answer()

@dp.message()
async def handle_user_message(message: Message):
    try:
        user_id = message.from_user.id

        # Игнорируем сообщения от админа и если не ожидаем сообщения
        if user_id == ADMIN_ID or not awaiting_message.get(user_id):
            return

        content_type = message.content_type
        caption = message.caption or ""

        # Формируем текст для пересылки
        forward_text = "📨 Анонимное сообщение"
        if caption:
            forward_text += f"\nПодпись: {caption}"

        # Пересылаем контент
        if content_type == "text":
            await bot.send_message(ADMIN_ID, f"✉️ {message.text}")
        elif content_type == "photo":
            await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=forward_text)
        elif content_type == "video":
            await bot.send_video(ADMIN_ID, message.video.file_id, caption=forward_text)
        else:
            await bot.send_message(ADMIN_ID, f"{forward_text}\nТип контента: {content_type}")

        keyboard = await default_keyboard()

        # Подтверждение пользователю
        await message.answer(
            DEFAULT_ANSWER,
            reply_markup=keyboard.as_markup()
        )
        awaiting_message[user_id] = False

    except Exception as e:
        logger.error(f"Ошибка в handle_user_message: {e}")
        await message.answer("⚠️ Ошибка обработки сообщения")


async def main():
    logger.info("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
