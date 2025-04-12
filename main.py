import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ForceReply
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from data import TOKEN, GREETING, ADMIN_ID, DEFAULT_ANSWER
from database_manager import DatabaseManager

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('AnonBot')

# Инициализация бота
bot = Bot(token=TOKEN)
dp = Dispatcher()
db = DatabaseManager()

# Мидлварь для управления БД
@dp.update.middleware
async def db_middleware(handler, event, data):
    await db.connect()
    data["db"] = db
    result = await handler(event, data)
    await db.close()
    return result

# Клавиатура админ-панели
async def admin_panel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
        InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")
    )
    builder.row(
        InlineKeyboardButton(text="⬆️ Повысить уровень", callback_data="admin_promote")
    )
    return builder.as_markup()

# Обработчик /start
@dp.message(Command("start"))
async def start_handler(message: Message, db: DatabaseManager):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Anonymous"
        
        # Регистрация пользователя
        if not await db.get_user(user_id):
            await db.insert(username, user_id)
            logger.info(f"Новый пользователь: {username}")

        # Проверка уровня доступа
        user = await db.get_user(user_id)
        keyboard = None
        if user and user[3] == 2:  # user[3] = level
            keyboard = await admin_panel_kb()

        await message.answer(GREETING, reply_markup=keyboard)

    except Exception as e:
        logger.error(f'Ошибка: {e}')
        await message.answer("⚠️ Ошибка, попробуйте позже")

# Обработчик админ-действий
@dp.callback_query(F.data.startswith("admin_"))
async def admin_actions(callback: types.CallbackQuery, db: DatabaseManager):
    user = await db.get_user(callback.from_user.id)
    if not user or user[3] != 2:
        await callback.answer("❌ Доступ запрещён!")
        return

    action = callback.data.split("_")[1]

    if action == "stats":
        users = await db.get_all_users()
        stats = "\n".join([f"{u[1]}: {u[4]} сообщ." for u in users])
        await callback.message.edit_text(
            f"📊 Статистика:\n\n{stats}",
            reply_markup=await admin_panel_kb()
        )

    elif action == "broadcast":
        await callback.message.answer(
            "Введите сообщение для рассылки:",
            reply_markup=ForceReply(selective=True)
        )

    elif action == "promote":
        await callback.message.answer(
            "Введите Telegram ID пользователя:",
            reply_markup=ForceReply(selective=True)
        )

# Обработчик ответов
@dp.message(F.reply_to_message)
async def handle_replies(message: Message, db: DatabaseManager):
    admin = await db.get_user(message.from_user.id)
    if not admin or admin[3] != 2:
        return

    reply_text = message.reply_to_message.text

    if "рассылк" in reply_text:
        users = await db.get_users_by_level(1)
        success = 0
        for user in users:
            try:
                await bot.send_message(user[2], message.text)
                success += 1
            except:
                pass
        await message.answer(f"✅ Отправлено: {success}/{len(users)}")

    elif "повышени" in reply_text:
        try:
            tg_id = int(message.text)
            target = await db.get_user(tg_id)
            if target:
                await db.update_user_level(tg_id, 2)
                await message.answer(f"✅ Уровень {tg_id} повышен!")
            else:
                await message.answer("❌ Пользователь не найден")
        except:
            await message.answer("❌ Неверный ID")

# Обработчик сообщений
@dp.message()
async def handle_content(message: Message, db: DatabaseManager):
    try:
        if message.from_user.id == ADMIN_ID:
            return

        user = await db.get_user(message.from_user.id)
        if not user:
            await message.answer("❌ Сначала выполните /start")
            return

        # Учёт сообщений
        await db.increment_message_count(message.from_user.id)

        # Пересылка контента админу
        if message.text:
            await bot.send_message(ADMIN_ID, f"✉️ Аноним: {message.text}")
        elif message.photo:
            await bot.send_photo(
                ADMIN_ID,
                message.photo[-1].file_id,
                caption=f"📸 Анонимное фото\n{message.caption or ''}"
            )
        elif message.video:  # Новый блок для видео
            await bot.send_video(
                ADMIN_ID,
                message.video.file_id,
                caption=f"🎥 Анонимное видео\n{message.caption or ''}"
            )

        await message.answer(DEFAULT_ANSWER)

    except Exception as e:
        logger.error(f"Ошибка: {e}")

# Запуск бота
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")