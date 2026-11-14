import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.handlers.main import router
from app.scheduler import start_scheduler
from app.db import client
from config import BOT_TOKEN

async def main():
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    start_scheduler()
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await client.close()

if __name__ == '__main__':
    asyncio.run(main())