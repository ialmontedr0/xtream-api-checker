from aiogram import Dispatcher

from app.telegram.handlers.check.handler import router as check_router

def register_routers(dp: Dispatcher):
    
    dp.include_router(check_router)