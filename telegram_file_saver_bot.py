import os
import logging
from datetime import datetime
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define your bot token (get this from BotFather)
BOT_TOKEN = '7312151975:AAGVgS8HcfCrziK1B0fMOMqRqxKKV3vp4-0'

# Define the directory where files will be saved
BASE_DIR = '/Users/home/Yandex.Disk-penzyakoff.localized/Projects/file_saver_telegram-bot/'

# Ensure the base directory exists
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! Send me a file or image and I will save it for you.')

def save_file(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    username = user.username or f"user_{user.id}"
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    user_dir = os.path.join(BASE_DIR, username)
    day_dir = os.path.join(user_dir, date_str)
    
    # Ensure the user's daily directory exists
    try:
        os.makedirs(day_dir, exist_ok=True)
        logger.info(f'Created directories: {day_dir}')
    except Exception as e:
        logger.error(f'Failed to create directories {day_dir}: {e}')
        update.message.reply_text(f'Error creating directories: {str(e)}')
        return
    
    if update.message.document:
        file = update.message.document
        file_id = file.file_id
        file_name = file.file_name
    elif update.message.photo:
        file = update.message.photo[-1]  # Get the highest resolution photo
        file_id = file.file_id
        file_name = f'{file_id}.jpg'  # Use file_id to avoid duplicates, and assume .jpg extension
    else:
        update.message.reply_text('Please send a valid file or photo.')
        return

    logger.info(f"Received file: {file_name} with file_id: {file_id} from user: {username}")

    new_file = context.bot.get_file(file_id)
    file_path = os.path.join(day_dir, file_name)

    try:
        # Save the file to the specified directory
        new_file.download(file_path)
        update.message.reply_text(f'File saved to {file_path}')
        logger.info(f'File saved to {file_path}')
    except Exception as e:
        update.message.reply_text(f'Error saving file: {str(e)}')
        logger.error(f'Error saving file: {str(e)}')

def main() -> None:
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Register the handlers
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.document | Filters.photo, save_file))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()