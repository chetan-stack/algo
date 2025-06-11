from aiogram import Bot
from aiogram.types import Message, Update
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from aiogram.exceptions import TelegramAPIError
import asyncio
from your_module.dispatcher import Dispatcher  # Replace 'your_module' with the actual location of Dispatcher class

# Bot credentials
BOT_TOKEN = "5707293106:AAEPkxexnIdoUxF5r7hpCRS_6CHINgU4HTw"
BOT_CHAT_ID = "2027669179"  # Assuming this is a user ID


async def start_command_handler(message: Message):
    """Handler for the /start command."""
    await message.answer("Hello! I'm your bot. How can I help you?")

async def message_handler(message: Message):
    """Handler for text messages."""
    await message.answer(f"Received your message: {message.text}")

async def main():
    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dispatcher = Dispatcher(storage=storage, fsm_strategy=FSMStrategy.USER_IN_CHAT)

    # Register handlers
    dispatcher.update.register(start_command_handler, commands=["start"])
    dispatcher.update.register(message_handler)

    try:
        # Start polling
        print("Starting bot...")
        await dispatcher.start_polling(bot)
    except TelegramAPIError as e:
        print(f"Telegram API Error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
