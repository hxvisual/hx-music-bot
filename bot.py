import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_name = message.from_user.first_name
    await message.answer(f"Привет, {user_name}!")

async def main():
    logger.info("Бот запущен")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 