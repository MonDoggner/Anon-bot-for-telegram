import datetime
import telebot 
from data import TOKEN, GREETING, ADMIN_ID, DEFAULT_ANSWER

anon_bot = telebot.TeleBot(TOKEN)

@anon_bot.message_handler(commands=['start'])
def start(message):
    anon_bot.send_message(message.chat.id, GREETING)

@anon_bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.chat.id != ADMIN_ID:
        try:
            anon_bot.send_message(message.chat.id, DEFAULT_ANSWER)
            anon_bot.send_message(ADMIN_ID, f'Анонимное сообщение: {message.text}')
        except Exception as e:
            print(f'{datetime.datetime.now()} Error handling text: {e}')

@anon_bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if message.chat.id != ADMIN_ID:
        try:
            photo = message.photo[-1]  
            caption = message.caption if message.caption else "No caption"
            
            anon_bot.send_message(message.chat.id, DEFAULT_ANSWER)
            anon_bot.send_photo(ADMIN_ID, photo.file_id, caption=f'Анонимное фото\nПодпись: {caption}')
        except Exception as e:
            print(f'{datetime.datetime.now()} Error handling photo: {e}')

@anon_bot.message_handler(content_types=['document'])
def handle_document(message):
    if message.chat.id != ADMIN_ID:
        try:
            document = message.document
            caption = message.caption if message.caption else "No caption"
            
            anon_bot.send_message(message.chat.id, DEFAULT_ANSWER)
            anon_bot.send_document(ADMIN_ID, document.file_id, caption=f'Анонимный документ\nПодпись: {caption}')
        except Exception as e:
            print(f'{datetime.datetime.now()} Error handling document: {e}')

@anon_bot.message_handler(content_types=['voice'])
def handle_voice(message):
    if message.chat.id != ADMIN_ID:
        try:
            voice = message.voice
            
            anon_bot.send_message(message.chat.id, DEFAULT_ANSWER)
            anon_bot.send_voice(ADMIN_ID, voice.file_id, caption='Анонимное голосовое сообщение')
        except Exception as e:
            print(f'{datetime.datetime.now()} Error handling voice: {e}')

@anon_bot.message_handler(content_types=['video'])
def handle_video(message):
    if message.chat.id != ADMIN_ID:
        try:
            video = message.video
            caption = message.caption if message.caption else "No caption"
            
            anon_bot.send_message(message.chat.id, DEFAULT_ANSWER)
            anon_bot.send_video(ADMIN_ID, video.file_id, caption=f'Анонимное видео\nПодпись: {caption}')
        except Exception as e:
            print(f'{datetime.datetime.now()} Error handling video: {e}')

@anon_bot.message_handler(content_types=['sticker'])
def handle_sticker(message):
    if message.chat.id != ADMIN_ID:
        try:
            sticker = message.sticker
            
            anon_bot.send_message(message.chat.id, DEFAULT_ANSWER)
            anon_bot.send_sticker(ADMIN_ID, sticker.file_id)
            anon_bot.send_message(ADMIN_ID, 'Анонимный стикер')
        except Exception as e:
            print(f'{datetime.datetime.now()} Error handling sticker: {e}')

@anon_bot.message_handler(content_types=['audio', 'video_note', 'voice_note', 'location', 'contact'])
def handle_other(message):
    if message.chat.id != ADMIN_ID:
        try:
            anon_bot.send_message(message.chat.id, DEFAULT_ANSWER)
            anon_bot.send_message(ADMIN_ID, 'Получено анонимное сообщение другого типа')
        except Exception as e:
            print(f'{datetime.datetime.now()} Error handling other content: {e}')

anon_bot.infinity_polling()
