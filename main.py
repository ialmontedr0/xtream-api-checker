import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config.settings import settings
from config.logging import setup_logging

from app.telegram.routers import register_routers

logger = logging.getLogger(__name__)

bot_instance = None

async def on_startup(bot: Bot):
    bot_info = await bot.get_me()
    
    logger.info("========================")
    logger.info(" BOT INICIADO")
    logger.info(f" BOT: @{bot_info.username}")
    logger.info(f" ID: {bot_info.id}")
    logger.info("========================")

async def on_shutdown(bot: Bot):
    logger.warning(" Cerrando Bot...")
    
    await bot.close()
    
    logger.info(" SESSION HTTP CERRADA")
    
async def main():
    global bot_instance
    
    setup_logging()
    
    logging.info(" INICIANDO SISTEMA...")
    
    bot_instance = Bot(
        token=settings.BOT_TOKEN,
        
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )
    
    dp = Dispatcher()
    
    register_routers(dp)
    
    logger.info(" Routers registrados")
    
    await on_startup(bot_instance)
    
    try:
        logger.info(" INICIANDO POLLING...")
        
        await dp.start_polling(
            
            bot_instance,
            
            handle_as_tasks=True,
            
            polling_timeout=30
        )
    
    finally:
        
        await on_shutdown(bot_instance)
        
if __name__ == "__main__":
    
    try:
        asyncio.run(main())
        
    except KeyboardInterrupt:
        
        logger.warning(" Bot detenido manualmente")
        
    except Exception as e:
        
        logger.exception(f" ERROR CRITICO: {str(e)}")
        
        sys.exit(1)
