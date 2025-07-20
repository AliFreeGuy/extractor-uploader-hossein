import asyncio
from os import environ as env
from pyrogram import Client, idle ,filters
from .utils import API_ID, API_HASH, BOT_TOKEN, SESSION_STRING, DEBUG, PROXY,setup_logger ,RedisCache , log_env_variables
from pyrogram.errors import UserAlreadyParticipant ,MessageNotModified
import httpx
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram.errors import FloodWait
from pyrogram.enums import ParseMode



logger = setup_logger("channel-bot", level="INFO")


bot_client = Client('bot-client',api_id=API_ID,api_hash=API_HASH,bot_token=BOT_TOKEN,proxy=PROXY)
self_client = Client("self_client",api_id=API_ID,api_hash=API_HASH,bot_token=SESSION_STRING, proxy=PROXY)


# ---------------------------------------------------------------------BOT HANDLER------------------------------------------------------------------------


@bot_client.on_message(filters.private ,group=0)
async def bot_message_handler(client, message):
    print('this is bot message handling ')







@self_client.on_message(group=1)
async def self_message_handler(client, message):
    print('this is self clilient message ')






redis_cache = RedisCache()

async def main():
    # لاگ گرفتن از env ها به محض شروع برنامه
    log_env_variables()

    logger.info('<<< starting clients and connecting to Redis >>>')

    await redis_cache.connect()
    logger.info("Redis connected.")

    await bot_client.start()
    await self_client.start()
    bot_info = await bot_client.get_me()
    logger.info(f"Clients {bot_info.username} started successfully.")
    logger.info("Clients are now listening for incoming messages... (Press Ctrl+C to exit)")

    try:
        await idle()  
    finally:
        await bot_client.stop()
        await self_client.stop()
        await redis_cache.close()
        
        logger.info("Clients stopped and Redis connection closed.")
