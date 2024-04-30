import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from config import TOKEN
from middlewares.db import DataBaseSession
from database.engine import session_maker
from handlers.user_private import user_private_router
from handlers.admin_private import admin_router
from database.engine import create_db
from common.bot_cmds_list import private

ALLOWED_UPDATES = ['message, edited_message']

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)

dp = Dispatcher()

dp.include_router(user_private_router)
dp.include_router(admin_router)


async def main():
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await create_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)

asyncio.run(main())