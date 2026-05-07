import asyncio
from aiogram import Bot, Dispatcher
from config.settings import settings
from config.logging import setup_logging

async def main():
    setup_logging()
    
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    
    # routers van en la fase 2
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    asyncio.run(main())