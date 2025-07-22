import asyncio
from os import environ as env
from pyrogram import Client, idle ,filters
from .utils import UploaderTypes, API_ID, API_HASH, BOT_TOKEN, SESSION_STRING, DEBUG, PROXY,setup_logger ,RedisCache , log_env_variables ,Settings,init_db,ADMINS ,KeyboardBuilder,build_settings_message
from pyrogram.errors import UserAlreadyParticipant ,MessageNotModified
import httpx
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram.errors import FloodWait
from pyrogram.enums import ParseMode
from tortoise import Tortoise, fields
from tortoise.models import Model
from pyromod import listen

logger = setup_logger("channel-bot", level="INFO")


bot_client = Client('bot-client',api_id=API_ID,api_hash=API_HASH,bot_token=BOT_TOKEN,proxy=PROXY)
self_client = Client("self_client",api_id=API_ID,api_hash=API_HASH,bot_token=SESSION_STRING, proxy=PROXY)


# ---------------------------------------------------------------------BOT HANDLER------------------------------------------------------------------------







@bot_client.on_message(filters.chat(ADMINS) & filters.text)
async def bot_client_handler(client, message):
    text = message.text

    if text == '/start':
        keyboard = KeyboardBuilder.reply(["تنظیمات"])
        await message.reply('ربات در خدمت شماست! برای استخراج لینک‌ها پست فوروارد کن یا روی "تنظیمات" بزن.',quote=True,reply_markup=keyboard)

    elif text == 'تنظیمات':
        await command_setting_handler(client, message)




async def command_setting_handler(client, message):
    settings = await Settings.get_singleton()
    text, keyboard = build_settings_message(settings)
    await message.reply(text, reply_markup=keyboard)


async def edit_settings_message(callback_query, settings):
    text, keyboard = build_settings_message(settings)
    await callback_query.message.edit_text(text, reply_markup=keyboard)



@bot_client.on_callback_query()
async def callback_handler(client, callback_query):
    data = callback_query.data
    settings = await Settings.get_singleton()

    if data == "toggle_auto_extractor":
        settings.is_auto_extractor = not settings.is_auto_extractor
        await settings.save()
        await callback_query.answer("وضعیت استخراج اتوماتیک تغییر کرد!")
        await edit_settings_message(callback_query, settings)


    elif data == "change_uploader":
        await callback_query.answer()
        ask_msg = await callback_query.message.reply_text("لطفا یوزرنیم آپلودر را ارسال کنید :")
        try:
            new_username_msg = await client.listen(callback_query.from_user.id, timeout=60)
        except TimeoutError:
            await ask_msg.edit_text("⏰ زمان وارد کردن یوزرنیم تمام شد. دوباره تلاش کن."); return
        if not new_username_msg or not new_username_msg.text:
            await ask_msg.edit_text("❌ یوزرنیم نامعتبر است. دوباره تلاش کن."); return
        settings.uploader_username = new_username_msg.text.strip()
        await settings.save()
        try: await ask_msg.delete(); await new_username_msg.delete()
        except: pass
        await edit_settings_message(callback_query, settings)


    elif data == "change_uploader_type":
        kb = KeyboardBuilder.inline(*[[(t, f"set_uploader_type_{t}")] for t in UploaderTypes.ALL])
        await callback_query.message.edit_text("نوع آپلودر را انتخاب کنید:", reply_markup=kb)
        await callback_query.answer()


    elif data.startswith("set_uploader_type_"):
        selected = data.replace("set_uploader_type_", "")
        if selected in UploaderTypes.ALL:
            settings.uploader_type = selected
            await settings.save()
            await callback_query.answer(f"نوع آپلودر روی {selected} تنظیم شد.")
            await edit_settings_message(callback_query, settings)
        else:
            await callback_query.answer("نوع آپلودر نامعتبر است!")

    else:
        await callback_query.answer()


























@self_client.on_message(group=1)
async def self_client_handler(client, message):
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
