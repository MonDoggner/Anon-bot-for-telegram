import logging
import time
from datetime import datetime, timedelta, timezone
from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config import Config
from database import Database

class MoscowTimeFormatter(logging.Formatter):
    """Форматтер логов с московским временем (UTC+3)."""
    def converter(self, timestamp):
        return (datetime.fromtimestamp(timestamp, timezone.utc) + timedelta(hours=3)).timetuple()
    
class AnonymousBot:
    def __init__(self, token: str, admin_id: int):
        self.bot = TeleBot(
            token,
            state_storage=StateMemoryStorage(),
            parse_mode=None,
            threaded=True
        )
        self.admin_id = admin_id
        self.db = Database()
        self._setup_logging()
        self._register_handlers()

    def _setup_logging(self) -> None:
        """Настройка логирования с московским временем."""
        logger = logging.getLogger('AnonymousBot')
        logger.setLevel(logging.INFO)
        
        formatter = MoscowTimeFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Консольный вывод
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        # Запись в файл (для PythonAnywhere)
        fh = logging.FileHandler('bot.log')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
        self.logger = logger

    def _register_handlers(self) -> None:
        """Регистрация всех обработчиков сообщений."""
        
        @self.bot.message_handler(commands=['start'])
        def start(message):
            self._handle_start(message)

        @self.bot.message_handler(content_types=['text'])
        def handle_text(message):
            self._handle_user_message(message, 'text')

        @self.bot.message_handler(content_types=['photo'])
        def handle_photo(message):
            self._handle_user_message(message, 'photo')

        @self.bot.message_handler(content_types=['document'])
        def handle_document(message):
            self._handle_user_message(message, 'document')

        @self.bot.message_handler(content_types=['voice'])
        def handle_voice(message):
            self._handle_user_message(message, 'voice')

        @self.bot.message_handler(content_types=['video'])
        def handle_video(message):
            self._handle_user_message(message, 'video')

        @self.bot.message_handler(content_types=['audio'])
        def handle_audio(message):
            self._handle_user_message(message, 'audio')

        @self.bot.message_handler(content_types=['sticker'])
        def handle_sticker(message):
            self._handle_user_message(message, 'sticker')

        @self.bot.message_handler(content_types=['video_note'])
        def handle_video_note(message):
            self._handle_user_message(message, 'video_note')

        @self.bot.message_handler(content_types=['contact'])
        def handle_contact(message):
            self._handle_user_message(message, 'contact')

        @self.bot.message_handler(content_types=['location'])
        def handle_location(message):
            self._handle_user_message(message, 'location')

    def _handle_start(self, message) -> None:
        """Обработка команды /start."""
        try:
            self.bot.send_message(message.chat.id, Config.GREETING)
            self.db.increment_user_sends(message.chat.id)
            self.logger.info(f"User {message.chat.id} started the bot")
        except Exception as e:
            self.logger.error(f"Error in /start: {e}")

    def _send_to_admin(self, content_type: str, content_data, caption: str = "") -> None:
        """Универсальный метод отправки контента админу."""
        try:
            if content_type == 'text':
                self.bot.send_message(self.admin_id, f"Анонимное сообщение: {content_data}")
            elif content_type == 'photo':
                self.bot.send_photo(self.admin_id, content_data.file_id, caption=caption)
            elif content_type == 'document':
                self.bot.send_document(self.admin_id, content_data.file_id, caption=caption)
            elif content_type == 'voice':
                self.bot.send_voice(self.admin_id, content_data.file_id, caption=caption)
            elif content_type == 'video':
                self.bot.send_video(self.admin_id, content_data.file_id, caption=caption)
            elif content_type == 'audio':
                self.bot.send_audio(self.admin_id, content_data.file_id, caption=caption)
            elif content_type == 'sticker':
                self.bot.send_sticker(self.admin_id, content_data.file_id)
                self.bot.send_message(self.admin_id, "Анонимный стикер")
            elif content_type == 'video_note':
                self.bot.send_video_note(self.admin_id, content_data.file_id)
            elif content_type == 'contact':
                self.bot.send_contact(
                    self.admin_id,
                    phone_number=content_data.phone_number,
                    first_name=content_data.first_name
                )
            elif content_type == 'location':
                self.bot.send_location(
                    self.admin_id,
                    latitude=content_data.latitude,
                    longitude=content_data.longitude
                )
            
            self.logger.info(f"Forwarded {content_type} to admin {self.admin_id}")
        except Exception as e:
            self.logger.error(f"Error sending {content_type} to admin: {e}")

    def _handle_user_message(self, message, content_type: str) -> None:
        if message.chat.id == self.admin_id:
            return

        try:
            self.bot.send_message(message.chat.id, Config.DEFAULT_ANSWER)
            
            caption = getattr(message, 'caption', None) or "Без подписи"
            content_data = message.text if content_type == 'text' else getattr(message, content_type)
            
            if content_type not in ['text', 'sticker', 'video_note']:
                caption = f"Анонимное {content_type}\nПодпись: {caption}"
            
            self._send_to_admin(content_type, content_data, caption)
            self.db.increment_user_sends(message.chat.id)
            
        except Exception as e:
            self.logger.error(f"Error handling {content_type}: {e}")

    def run(self) -> None:
        """Запуск бота с автоматическим перезапуском при ошибках."""
        self.logger.info("Starting bot...")
        while True:
            try:
                self.bot.infinity_polling(
                    timeout=60,
                    long_polling_timeout=60,
                    skip_pending=True
                )
            except Exception as e:
                self.logger.error(f"Bot crashed: {e}. Restarting in 10s...")
                time.sleep(10)

if __name__ == '__main__':
    bot = AnonymousBot(Config.TOKEN, Config.ADMIN_ID)
    bot.run()