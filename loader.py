import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums.parse_mode import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession


from handlers import user_router
from utils import settings
from db import create_engine, get_session_maker
from middleware import DbSessionMiddleware
from db.engine import init_models

async def on_shutdown(dp: Dispatcher):
    session: AsyncSession = dp.update.middleware['session']




async def start():
    bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(user_router)
    await init_models()

    async_engine = create_engine()
    session_maker = get_session_maker(async_engine)
    dp.update.middleware(DbSessionMiddleware(session_pool=session_maker))



    me = await bot.get_me()
    print('Started')
    print(me.username)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    except Exception as e:
        print(e)


if __name__ == "__main__":
    try:
        asyncio.run(start())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped')
