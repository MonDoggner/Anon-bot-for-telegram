import telebot 
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup
import backoff
import time
import logging
from data import TOKEN, GREETING, ADMIN_ID, DEFAULT_ANSWER

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('AnonBot')

telebot.apihelper.RETRY_ON_ERROR = True
telebot.apihelper.CONNECT_TIMEOUT = 15

state_storage = StateMemoryStorage()
anon_bot = telebot.TeleBot(
    TOKEN,
    state_storage=state_storage,
    parse_mode=None,
    threaded=True
)

@backoff.on_exception(
    backoff.expo,
    (Exception),
    max_tries=5
)
def send_message_with_retry(*args, **kwargs):
    return anon_bot.send_message(*args, **kwargs)

@backoff.on_exception(
    backoff.expo,
    (Exception),
    max_tries=5
)
def send_photo_with_retry(*args, **kwargs):
    return anon_bot.send_photo(*args, **kwargs)

@backoff.on_exception(
    backoff.expo,
    (Exception),
    max_tries=5
)
def send_document_with_retry(*args, **kwargs):
    return anon_bot.send_document(*args, **kwargs)

@backoff.on_exception(
    backoff.expo,
    (Exception),
    max_tries=5
)
def send_voice_with_retry(*args, **kwargs):
    return anon_bot.send_voice(*args, **kwargs)

@backoff.on_exception(
    backoff.expo,
    (Exception),
    max_tries=5
)
def send_video_with_retry(*args, **kwargs):
    return anon_bot.send_video(*args, **kwargs)

@backoff.on_exception(
    backoff.expo,
    (Exception),
    max_tries=5
)
def send_sticker_with_retry(*args, **kwargs):
    return anon_bot.send_sticker(*args, **kwargs)


@anon_bot.message_handler(commands=['start'])
def start(message):
    try:
        send_message_with_retry(message.chat.id, GREETING)
        logger.info('Команда /start выполнена')
    except Exception as e:
        logger.error(f'Error in start command: {e}')

@anon_bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.chat.id != ADMIN_ID:
        try:
            send_message_with_retry(message.chat.id, DEFAULT_ANSWER)
            send_message_with_retry(ADMIN_ID, f'Анонимное сообщение: {message.text}')
            logger.info('Сообщение успешно отправлено')
        except Exception as e:
            logger.error(f'Ошибка при отправке текста: {e}')

@anon_bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if message.chat.id != ADMIN_ID:
        try:
            photo = message.photo[-1]
            caption = message.caption if message.caption else 'No caption'
            
            send_message_with_retry(message.chat.id, DEFAULT_ANSWER)
            send_photo_with_retry(ADMIN_ID, photo.file_id, caption=f'Анонимное фото\nПодпись: {caption}')
            logger.info('Сообщение успешно отправлено')
        except Exception as e:
            logger.error(f'Ошибка при отправке фото: {e}')

@anon_bot.message_handler(content_types=['document'])
def handle_document(message):
    if message.chat.id != ADMIN_ID:
        try:
            document = message.document
            caption = message.caption if message.caption else 'No caption'
            
            send_message_with_retry(message.chat.id, DEFAULT_ANSWER)
            send_document_with_retry(ADMIN_ID, document.file_id, caption=f'Анонимный документ\nПодпись: {caption}')
            logger.info('Сообщение успешно отправлено')
        except Exception as e:
            logger.error(f'Ошибка при отправке документа: {e}')

@anon_bot.message_handler(content_types=['voice'])
def handle_voice(message):
    if message.chat.id != ADMIN_ID:
        try:
            voice = message.voice
            
            send_message_with_retry(message.chat.id, DEFAULT_ANSWER)
            send_voice_with_retry(ADMIN_ID, voice.file_id, caption='Анонимное голосовое сообщение')
            logger.info('Сообщение успешно отправлено')
        except Exception as e:
            logger.error(f'Ошибка при отправке голосовухи: {e}')

@anon_bot.message_handler(content_types=['video'])
def handle_video(message):
    if message.chat.id != ADMIN_ID:
        try:
            video = message.video
            caption = message.caption if message.caption else "No caption"
            
            send_message_with_retry(message.chat.id, DEFAULT_ANSWER)
            send_video_with_retry(ADMIN_ID, video.file_id, caption=f'Анонимное видео\nПодпись: {caption}')
            logger.info('Сообщение успешно отправлено')
        except Exception as e:
            logger.error(f'Ошибка при отправке видео: {e}')

@anon_bot.message_handler(content_types=['sticker'])
def handle_sticker(message):
    if message.chat.id != ADMIN_ID:
        try:
            sticker = message.sticker
            
            send_message_with_retry(message.chat.id, DEFAULT_ANSWER)
            send_sticker_with_retry(ADMIN_ID, sticker.file_id)
            send_message_with_retry(ADMIN_ID, 'Анонимный стикер')
            logger.info('Сообщение успешно отправлено')
        except Exception as e:
            logger.error(f'Ошибка при отправке стикера: {e}')

@anon_bot.message_handler(content_types=['audio', 'video_note', 'voice_note', 'location', 'contact'])
def handle_other(message):
    if message.chat.id != ADMIN_ID:
        try:
            send_message_with_retry(message.chat.id, DEFAULT_ANSWER)
            send_message_with_retry(ADMIN_ID, 'Получено анонимное сообщение другого типа')
        except Exception as e:
            logger.error(f'Ошибка при отправке других сообщений: {e}')

def run_bot():
    while True:
        try:
            logger.info('Запуск бота...')
            anon_bot.infinity_polling(
                timeout=60, 
                long_polling_timeout=60,
                restart_on_change=False,  
                skip_pending=True,        
                allowed_updates=["message"]  
            )
        except Exception as e:
            logger.error(f'Бот крашнулся с ошибкой: {e}')
            time.sleep(10)
            continue

if __name__ == '__main__':
    try:
        run_bot()
    except KeyboardInterrupt:
        logger.info('Остановка пользователем')
        anon_bot.stop_polling()
    except Exception as e:
        logger.error(f'Критическая ошибка: {e}')
        anon_bot.stop_polling()
