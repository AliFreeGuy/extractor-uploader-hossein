import asyncio
from os import environ as env
from pyrogram import Client, idle ,filters
from .utils import API_ID, API_HASH, BOT_TOKEN, SESSION_STRING, DEBUG, PROXY,setup_logger ,RedisCache , log_env_variables ,User,init_db
from pyrogram.errors import UserAlreadyParticipant ,MessageNotModified
import httpx
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram.errors import FloodWait
from pyrogram.enums import ParseMode
from tortoise import Tortoise, fields
from tortoise.models import Model


logger = setup_logger("channel-bot", level="INFO")


bot_client = Client('bot-client',api_id=API_ID,api_hash=API_HASH,bot_token=BOT_TOKEN,proxy=PROXY)
self_client = Client("self_client",api_id=API_ID,api_hash=API_HASH,bot_token=SESSION_STRING, proxy=PROXY)


# ---------------------------------------------------------------------BOT HANDLER------------------------------------------------------------------------








@bot_client.on_message(filters.command("start"))
async def start_handler(client, message):
    print('this is bot client message')




@self_client.on_message(group=1)
async def self_message_handler(client, message):
    print('this is self clilient message ')













































# ---------------------------------------------------------------------BOT RUNNING------------------------------------------------------------------------


redis_cache = RedisCache()

async def main():
    log_env_variables()
    logger.info('<<< starting clients and connecting to Redis >>>')
    await init_db()
    logger.info("Database connected and schemas generated.")
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
        await Tortoise.close_connections()
        logger.info("Clients stopped, Redis connection closed, and DB connections closed.")
