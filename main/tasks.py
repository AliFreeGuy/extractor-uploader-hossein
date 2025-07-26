from celery import Celery
from pyrogram import Client
import redis
from pyrogram.types import (ReplyKeyboardMarkup, InlineKeyboardMarkup,InlineKeyboardButton , KeyboardButton)
from dotenv import load_dotenv
from celery.signals import task_revoked, task_success,task_failure
import logging
from logging.handlers import RotatingFileHandler
from celery.exceptions import SoftTimeLimitExceeded
import os
import time
import sys
from os.path import abspath, dirname

parent_dir = dirname(dirname(abspath(__file__)))
sys.path.insert(0, parent_dir)

from .utils import setup_logger, SyncRedisCache


logger = setup_logger("tasks-log", level="INFO")


load_dotenv(override=True)

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv('BOT_TOKEN')
SESSION_STRING = os.getenv('SESSION_STRING')
DEBUG = os.getenv("BOT_DEBUG", "False").lower() in ["true", "1", "yes"]
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
ADMINS = [int(admin) for admin in os.getenv("ADMINS", "").split(",") if admin]
PROXY = {
        "scheme": os.getenv("PROXY_SCHEME", "socks5"),
        "hostname": os.getenv("PROXY_HOSTNAME", "127.0.0.1"),
        "port": int(os.getenv("PROXY_PORT", "1080"))
    }



r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT , db=REDIS_DB , decode_responses=True)
app = Celery('link_to_file' , backend=f'redis://{REDIS_HOST}:6379/6' , broker=f'redis://{REDIS_HOST}:6379/6')


app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json',],
    worker_concurrency=1,
    worker_prefetch_multiplier=1,
)


@app.task(name='tasks',bind=True,default_retry_delay=1,soft_time_limit=43200)
def extractor_task(self , data=None):

    logger.info(f"************ STARTING TASK ************")

    try:
        redis_client = SyncRedisCache()
        settings = redis_client.get_settings()
    
        self_client = Client('self-client-task' , api_id = API_ID , api_hash=API_HASH , session_string=SESSION_STRING , proxy = PROXY if DEBUG else None )
        
        with self_client as bot : 
            bot.send_message('alifreeguy' , 'hi user mother fucker')
            
            
    except Exception as e:
        logger.error(str(e))
        # self.retry(exc=e, countdown=60) 
        