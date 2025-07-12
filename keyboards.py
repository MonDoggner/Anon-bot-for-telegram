from aiogram.utils.keyboard import InlineKeyboardBuilder


async def default_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Отправить анонимное сообщение", callback_data="send_message")
    builder.button(text="Игровой режим", callback_data="user_game_mode")
    builder.adjust(1)
    return builder


async def admin_game_mode_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Добавить карточку", callback_data="add_card")
    builder.button(text="Вернуться", callback_data="go_back")
    builder.adjust(1)
    return builder


async def user_game_mode_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Получить карточку", callback_data="add_card")
    builder.button(text="Вернуться", callback_data="go_back")
    builder.adjust(1)
    return builder