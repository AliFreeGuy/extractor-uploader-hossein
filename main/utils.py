# utils.py

import logging
import os
from dotenv import load_dotenv
import os
import json
from typing import Optional
import redis.asyncio as redis
from pyrogram.types import (ReplyKeyboardMarkup, InlineKeyboardMarkup,InlineKeyboardButton , KeyboardButton , WebAppInfo)
from typing import Optional

load_dotenv(override=True) 

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv('BOT_TOKEN')
SESSION_STRING = os.getenv('SESSION_STRING')
DEBUG = os.getenv("BOT_DEBUG", "False").lower() in ["true", "1", "yes"]
PROXY = None
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))



if DEBUG:
    PROXY = {
        "scheme": os.getenv("PROXY_SCHEME", "socks5"),
        "hostname": os.getenv("PROXY_HOSTNAME", "127.0.0.1"),
        "port": int(os.getenv("PROXY_PORT", "1080"))
    }




class RedisCache:
    def __init__(self):
        self.redis = None

    async def connect(self):
        self.redis = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            encoding="utf-8",
            decode_responses=True,
        )

    async def close(self):
        if self.redis:
            await self.redis.close()

    async def set(self, key: str, value, expire: Optional[int] = None):
        val = json.dumps(value)
        if expire:
            await self.redis.set(key, val, ex=expire)
        else:
            await self.redis.set(key, val)

    async def get(self, key: str):
        val = await self.redis.get(key)
        if val:
            return json.loads(val)
        return None

    async def delete(self, key: str):
        await self.redis.delete(key)



import logging

def setup_logger(name="bot", level=logging.INFO, logfile="app.log"):
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    if not logger.hasHandlers():
        # Console handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(level)
        logger.addHandler(stream_handler)

        # File handler
        file_handler = logging.FileHandler(logfile, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

    return logger

logger = setup_logger("channel-bot", level=logging.INFO, logfile="channel-bot.log")












def log_env_variables():
    def last_8_chars(val: Optional[str]):
        if val and len(val) > 8:
            return "****" + val[-8:]
        elif val:
            return "****" + val
        return None

    safe_env = {
        "API_ID": API_ID,
        "API_HASH": API_HASH[:5] + "..." if API_HASH else None,
        "BOT_TOKEN": last_8_chars(BOT_TOKEN),
        "SESSION_STRING": last_8_chars(SESSION_STRING),
        "DEBUG": DEBUG,
        "REDIS_HOST": REDIS_HOST,
        "REDIS_PORT": REDIS_PORT,
        "REDIS_DB": REDIS_DB,
        "PROXY": PROXY or "Disabled",
    }
    logger.info("Loaded Environment Variables:\n" + json.dumps(safe_env, indent=4, ensure_ascii=False))
