import telebot 
import logging
from data import TOKEN, GREETING, ADMIN_ID, DEFAULT_ANSWER

anon_bot = telebot.TeleBot(TOKEN)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger('AnonBot')

@anon_bot.message_handler(commands=['start'])
def start(message):
    anon_bot.send_message(message.chat.id, GREETING)
    logger.info('Команда /start выполнена')

@anon_bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.chat.id != ADMIN_ID:
        try:
            anon_bot.send_message(message.chat.id, DEFAULT_ANSWER)
            anon_bot.send_message(ADMIN_ID, f'Анонимное сообщение: {message.text}')
            logger.info('Сообщение успешно отправлено')
        except Exception as e:
            logger.error(f'Ошибка при отправке текста: {e}')

@anon_bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if message.chat.id != ADMIN_ID:
        try:
            photo = message.photo[-1]  
            caption = message.caption if message.caption else "No caption"
            
            anon_bot.send_message(message.chat.id, DEFAULT_ANSWER)
            anon_bot.send_photo(ADMIN_ID, photo.file_id, caption=f'Анонимное фото\nПодпись: {caption}')
            logger.info('Сообщение успешно отправлено')
        except Exception as e:
            logger.error(f'Ошибка при отправке фото: {e}')

@anon_bot.message_handler(content_types=['document'])
def handle_document(message):
    if message.chat.id != ADMIN_ID:
        try:
            document = message.document
            caption = message.caption if message.caption else "No caption"
            
            anon_bot.send_message(message.chat.id, DEFAULT_ANSWER)
            anon_bot.send_document(ADMIN_ID, document.file_id, caption=f'Анонимный документ\nПодпись: {caption}')
            logger.info('Сообщение успешно отправлено')
        except Exception as e:
            logger.error(f'Ошибка при отправке документа: {e}')

@anon_bot.message_handler(content_types=['voice'])
def handle_voice(message):
    if message.chat.id != ADMIN_ID:
        try:
            voice = message.voice
            
            anon_bot.send_message(message.chat.id, DEFAULT_ANSWER)
            anon_bot.send_voice(ADMIN_ID, voice.file_id, caption='Анонимное голосовое сообщение')
            logger.info('Сообщение успешно отправлено')
        except Exception as e:
            logger.error(f'Ошибка при отправке голосовухи: {e}')

@anon_bot.message_handler(content_types=['video'])
def handle_video(message):
    if message.chat.id != ADMIN_ID:
        try:
            video = message.video
            caption = message.caption if message.caption else "No caption"
            
            anon_bot.send_message(message.chat.id, DEFAULT_ANSWER)
            anon_bot.send_video(ADMIN_ID, video.file_id, caption=f'Анонимное видео\nПодпись: {caption}')
            logger.info('Сообщение успешно отправлено')
        except Exception as e:
            logger.error(f'Ошибка при отправке видео: {e}')

@anon_bot.message_handler(content_types=['sticker'])
def handle_sticker(message):
    if message.chat.id != ADMIN_ID:
        try:
            sticker = message.sticker
            
            anon_bot.send_message(message.chat.id, DEFAULT_ANSWER)
            anon_bot.send_sticker(ADMIN_ID, sticker.file_id)
            anon_bot.send_message(ADMIN_ID, 'Анонимный стикер')
            logger.info('Сообщение успешно отправлено')
        except Exception as e:
            logger.error(f'Ошибка при отправке стикера: {e}')

@anon_bot.message_handler(content_types=['audio', 'video_note', 'voice_note', 'location', 'contact'])
def handle_other(message):
    if message.chat.id != ADMIN_ID:
        try:
            anon_bot.send_message(message.chat.id, DEFAULT_ANSWER)
            anon_bot.send_message(ADMIN_ID, 'Получено анонимное сообщение другого типа')
        except Exception as e:
            logger.error(f'Ошибка при отправке других сообщений: {e}')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        anon_bot.infinity_polling()
    except KeyboardInterrupt:
        print(f'INFO:Выход')
    except Exception as e:
        logger.error(f'Ошибка при запуске бота\nЯ вообще без понятия что там сломалось, вот лог: {e}')
