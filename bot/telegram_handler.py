import telegram

# import logger
from telegram import Update
from .services import ScenarioProcessor
import logging

logger = logging.getLogger(__name__)


class TelegramBotHandler:
    def __init__(self, bot):
        self.bot = bot
        self.telegram_bot = telegram.Bot(token=bot.token)

    def set_webhook(self):
        """Set webhook for Telegram bot"""
        try:
            # Формируем полный URL для вебхука
            webhook_url = (
                f"https://5f67e7e732a807.lhr.life/webhook/telegram/{self.bot.token}/"
            )

            # Устанавливаем вебхук
            result = self.telegram_bot.set_webhook(webhook_url)

            # Сохраняем URL вебхука в базе данных
            self.bot.webhook_url = "https://5f67e7e732a807.lhr.life"
            self.bot.save()

            logger.info(
                f"Webhook set successfully for bot {self.bot.name}: {webhook_url}"
            )
            return True

        except Exception as e:
            logger.error(f"Error setting webhook for bot {self.bot.name}: {e}")
            return False

    def delete_webhook(self):
        """Delete webhook for Telegram bot"""
        try:
            self.telegram_bot.delete_webhook()
            logger.info(f"Webhook deleted for bot {self.bot.name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting webhook for bot {self.bot.name}: {e}")
            return False

    def get_webhook_info(self):
        """Get webhook information"""
        try:
            return self.telegram_bot.get_webhook_info()
        except Exception as e:
            logger.error(f"Error getting webhook info for bot {self.bot.name}: {e}")
            return None

    def handle_update(self, update_data):
        """Handle incoming Telegram update"""
        logger.info(f"Received update for bot {self.bot.name}")

        try:
            update = Update.de_json(update_data, self.telegram_bot)

            if update.message and update.message.text:
                self._process_message(
                    update.message.chat.id,
                    update.message.text,
                    update.message.message_id,
                )
            elif update.callback_query:
                self._process_callback(update.callback_query)
            else:
                logger.warning(f"Unhandled update type: {update_data}")

        except Exception as e:
            logger.error(f"Error handling update for bot {self.bot.name}: {e}")

    def _process_message(self, chat_id, text, message_id=None):
        """Process incoming message"""
        try:
            logger.info(f"Processing message from {chat_id}: {text}")

            # Игнорируем команды, которые уже обрабатываются
            if text.startswith("/"):
                if text == "/start":
                    self._send_welcome_message(chat_id)
                return

            processor = ScenarioProcessor(self.bot, str(chat_id))
            response = processor.process_message(text)

            # Отправляем ответ
            self.telegram_bot.send_message(
                chat_id=chat_id, text=response, reply_to_message_id=message_id
            )

            logger.info(f"Response sent to {chat_id}")

        except Exception as e:
            logger.error(f"Error processing message for bot {self.bot.name}: {e}")
            try:
                self.telegram_bot.send_message(
                    chat_id=chat_id,
                    text="❌ Sorry, I encountered an error. Please try again later.",
                )
            except Exception as send_error:
                logger.error(f"Failed to send error message: {send_error}")

    def _process_callback(self, callback_query):
        """Process callback queries (для inline кнопок)"""
        try:
            chat_id = callback_query.message.chat.id
            data = callback_query.data

            # Обработка callback данных
            if data == "help":
                self.telegram_bot.send_message(
                    chat_id=chat_id,
                    text="ℹ️ I'm an AI-powered bot. Just send me a message and I'll respond!",
                )

            # Ответим на callback (убираем "часики")
            self.telegram_bot.answer_callback_query(callback_query.id)

        except Exception as e:
            logger.error(f"Error processing callback: {e}")

    def _send_welcome_message(self, chat_id):
        """Send welcome message"""
        welcome_text = """
🤖 *Welcome to AI Bot!*

I'm powered by Mistral AI and ready to help you with:

💬 General conversations
📚 Answering questions  
🔍 Problem solving
💡 Creative tasks

Just send me a message and I'll respond!

*Commands:*
/start - Show this welcome message
/help - Get help information

Let's start chatting! 🎉
        """
        try:
            self.telegram_bot.send_message(
                chat_id=chat_id, text=welcome_text, parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")

    def send_message(self, chat_id, text, parse_mode=None):
        """Send message to Telegram user"""
        try:
            self.telegram_bot.send_message(
                chat_id=chat_id, text=text, parse_mode=parse_mode
            )
            return True
        except Exception as e:
            logger.error(f"Error sending message to {chat_id}: {e}")
            return False
