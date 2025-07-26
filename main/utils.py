# main/utils.py

import logging
import os
from dotenv import load_dotenv
import json
from typing import Optional
import redis.asyncio as redis
from pyrogram.types import (ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, WebAppInfo)
from datetime import datetime
from zoneinfo import ZoneInfo
import redis as sync_redis # <--- تغییر اصلی: نام کتابخانه را تغییر می‌دهیم



load_dotenv(override=True)

# ... (بقیه متغیرهای شما بدون تغییر باقی می‌مانند)
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv('BOT_TOKEN')
SESSION_STRING = os.getenv('SESSION_STRING')
DEBUG = os.getenv("BOT_DEBUG", "False").lower() in ["true", "1", "yes"]
PROXY = None
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
ADMINS = [int(admin) for admin in os.getenv("ADMINS", "").split(",") if admin]

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
        
    # توابع جدید برای مدیریت تنظیمات در Redis
    async def get_settings(self) -> dict:
        """تنظیمات را از هش Redis می‌خواند و اگر وجود نداشته باشد، با مقادیر پیش‌فرض ایجاد می‌کند."""
        settings_key = "app_settings"
        settings = await self.redis.hgetall(settings_key)
        if not settings:
            # مقادیر پیش‌فرض
            default_settings = {
                "uploader_username": "",
                "uploader_type": UploaderTypes.ZERO,
                "auto_remove_sign": "False",
                "is_auto_embed_enabled": "False"
            }
            await self.redis.hmset(settings_key, default_settings)
            return default_settings
        # تبدیل مقادیر بولی از رشته به بولین
        settings['auto_remove_sign'] = settings.get('auto_remove_sign') == 'True'
        settings['is_auto_embed_enabled'] = settings.get('is_auto_embed_enabled') == 'True'
        return settings

    async def update_setting(self, key: str, value):
        """یک مقدار خاص را در هش تنظیمات Redis به‌روزرسانی می‌کند."""
        settings_key = "app_settings"
        # مقادیر بولی را به رشته تبدیل می‌کنیم تا در Redis ذخیره شوند
        if isinstance(value, bool):
            value = str(value)
        await self.redis.hset(settings_key, key, value)



# ... (کلاس TehranFormatter و تابع setup_logger بدون تغییر)
class TehranFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        tz = ZoneInfo("Asia/Tehran")
        dt = datetime.fromtimestamp(record.created, tz)
        if datefmt:
            return dt.strftime(datefmt)
        else:
            return dt.isoformat()

def setup_logger(name="bot", level=logging.INFO, logfile="app.log"):
    formatter = TehranFormatter(
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
logger.info("ربات با موفقیت راه‌اندازی شد!")


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



# <<<<<<< کد زیر جایگزین می‌شود >>>>>>>
def build_settings_message(settings: dict):
    # مقادیر را با get و مقدار پیش‌فرض می‌خوانیم تا در صورت نبودن کلید، خطا ندهد
    uploader_username = settings.get('uploader_username', 'انتخاب نشده')
    uploader_type = settings.get('uploader_type', 'انتخاب نشده')
    auto_remove_sign = settings.get('auto_remove_sign', False)
    is_auto_embed_enabled = settings.get('is_auto_embed_enabled', False)

    text = (
        f"آپلودر: `{uploader_username or 'انتخاب نشده'}`\n"
        f"نوع آپلودر: `{uploader_type or 'انتخاب نشده'}`\n"
        f"حذف خودکار امضا: `{'✅ روشن' if auto_remove_sign else '❌ خاموش'}`\n"
        f"جاگذاری خودکار در پست: `{'✅ روشن' if is_auto_embed_enabled else '❌ خاموش'}`"
    )
    
    toggle_sign_text = "خاموش کردن حذف امضا" if auto_remove_sign else "روشن کردن حذف امضا"
    toggle_embed_text = "خاموش کردن جاگذاری خودکار" if is_auto_embed_enabled else "روشن کردن جاگذاری خودکار"

    keyboard = KeyboardBuilder.inline(
        [(f"تغییر آپلودر (فعلی: {uploader_username or '---'})", "change_uploader")],
        [(f"تغییر نوع آپلودر (فعلی: {uploader_type or '---'})", "change_uploader_type")],
        [(toggle_sign_text, "toggle_auto_remove_sign")],
        [(toggle_embed_text, "toggle_auto_embed")],
    )
    return text, keyboard


# ... (کلاس KeyboardBuilder و UploaderTypes و تابع extract_links بدون تغییر)
class KeyboardBuilder:
    @staticmethod
    def reply(*rows, resize=True, one_time=False):

        keyboard = [list(row) if isinstance(row, (list, tuple)) else [row] for row in rows]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=resize, one_time_keyboard=one_time)

    @staticmethod
    def inline(*rows):

        keyboard = []
        for row in rows:
            buttons = []
            for btn in row:
                buttons.append(InlineKeyboardButton(btn[0], callback_data=btn[1]))
            keyboard.append(buttons)
        return InlineKeyboardMarkup(keyboard)





class UploaderTypes:
    ZERO = "zero"
    TORANG = "torang"
    FUCKER='fucker'
    ALL = [ZERO, TORANG , FUCKER]







def extract_links(message):
    results = []

    def process_entities(text, entities):
        if not text or not entities:
            return
        lines = text.splitlines()

        for entity in entities:
            if str(entity.type) == "MessageEntityType.TEXT_LINK":
                url = entity.url
                offset = entity.offset
                length = entity.length
                linked_text = text[offset:offset+length]

                # پیدا کردن خطی که شامل offset هست
                line = None
                start_pos = 0
                for l in lines:
                    end_pos = start_pos + len(l) + 1  # +1 برای newline
                    if start_pos <= offset < end_pos:
                        line = l
                        break
                    start_pos = end_pos

                results.append({
                    "text": line if line else linked_text,  
                    "link": url,                            
                    "offset_start" : str(offset) , 
                    "offset_end" : str(offset+length) ,
                    "linked_text": linked_text 
                })

    process_entities(message.text, message.entities)
    process_entities(message.caption, message.caption_entities)

    return results

















# این کدها را در انتهای فایل main/utils.py قرار دهید یا جایگزین کلاس قبلی کنید


# این کلاس UploaderTypes باید قبل از SyncRedisCache تعریف شده باشد
class UploaderTypes:
    ZERO = "zero"
    TORANG = "torang"
    FUCKER='fucker'
    ALL = [ZERO, TORANG , FUCKER]

class SyncRedisCache:
    """
    کلاینت همزمان (Synchronous) ردیس که از نامی متفاوت برای جلوگیری از تداخل استفاده می‌کند.
    """
    def __init__(self):
        # ✅ از نام جدید sync_redis برای ساختن کلاینت استفاده می‌کنیم
        self.redis = sync_redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            encoding="utf-8",
            decode_responses=True,
        )

    def get_settings(self) -> dict:
        """
        تنظیمات را به صورت همزمان (Sync) از هش ردیس دریافت می‌کند.
        """
        settings_key = "app_settings"
        settings = self.redis.hgetall(settings_key) # <-- این خط دیگر coroutine برنمی‌گرداند

        if not settings:
            default_settings_map = {
                "uploader_username": "",
                "uploader_type": UploaderTypes.ZERO,
                "auto_remove_sign": "False",
                "is_auto_embed_enabled": "False"
            }
            # از hset به جای hmset برای سازگاری با نسخه‌های جدیدتر redis-py استفاده می‌کنیم
            self.redis.hset(settings_key, mapping=default_settings_map)
            
            # مقادیر بولی واقعی را برای بازگشت آماده می‌کنیم
            return {
                "uploader_username": "",
                "uploader_type": UploaderTypes.ZERO,
                "auto_remove_sign": False,
                "is_auto_embed_enabled": False
            }

        # تبدیل مقادیر رشته‌ای به بولین پایتون
        settings['auto_remove_sign'] = settings.get('auto_remove_sign') == 'True'
        settings['is_auto_embed_enabled'] = settings.get('is_auto_embed_enabled') == 'True'
        
        return settings

    def update_setting(self, key: str, value):
        """
        یک مقدار خاص را در هش تنظیمات به صورت همزمان (Sync) به‌روزرسانی می‌کند.
        """
        settings_key = "app_settings"
        if isinstance(value, bool):
            value = str(value)
        self.redis.hset(settings_key, key, value)