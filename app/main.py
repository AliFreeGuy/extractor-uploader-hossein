import asyncio
import uvloop
from pyrogram import Client, idle
from utils import logger
import config
from utils.db import init_db, close_db  # اضافه کن


async def main():
    # اتصال به دیتابیس
    await init_db()

    bot_client = Client(
        config.BOT_SESSION,
        config.API_ID,
        config.API_HASH,
        bot_token=config.BOT_TOKEN,
        workdir=config.WORK_DIR,
        plugins=dict(root="plugins")
    )

    if config.DEBUG == 'True':
        bot_client.proxy = config.PROXY

    await bot_client.start()
    logger.info("Bot started")

    # تا وقتی که بات فعال هست
    await idle()

    # وقتی که برنامه بسته می‌شه، دیتابیس رو ببند
    await close_db()


if __name__ == '__main__':
    uvloop.install()
    asyncio.run(main())
