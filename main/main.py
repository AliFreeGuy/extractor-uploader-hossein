# main/main.py

import asyncio
import uuid
from os import environ as env

from pyrogram import Client, filters, idle
from pyrogram.errors import MessageNotModified, UserAlreadyParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyromod import listen
from celery.result import AsyncResult

from .tasks import extractor_task
from .utils import (API_HASH, API_ID, BOT_TOKEN, DEBUG, PROXY,
                    RedisCache, UploaderTypes,
                    setup_logger, log_env_variables, ADMINS,
                    KeyboardBuilder, build_settings_message, extract_links)

logger = setup_logger("bot-log", level="INFO")

bot_client = Client('bot-client', api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, proxy=PROXY)
redis_cache = RedisCache() # نمونه‌سازی از ردیس کش

# ... (هندلر bot_client_handler بدون تغییر)
@bot_client.on_message(filters.chat(ADMINS))
async def bot_client_handler(client, message):
    links = extract_links(message)

    if links:
        post_data = {
            'user_chat_id': int(message.from_user.id),
            'input_message_id': int(message.id),
            'links': []
        }

        keyboard_rows = []
        for link in links:
            link_id = str(uuid.uuid4())
            post_data['links'].append({
                'id': link_id,
                'text': link['text'],
                'linked_text': link['linked_text'],
                'link': link['link'],
                'offset_start' : link['offset_start'] ,
                'offset_end' : link['offset_end'] ,
                'selected': True
            })
            button = InlineKeyboardButton(f"✅ {link['text']}", callback_data=f"toggle_{message.id}_{link_id}")
            keyboard_rows.append([button])

        await redis_cache.set(f"post:{message.id}", post_data)

        keyboard_rows.append([InlineKeyboardButton("🚀 شروع", callback_data=f"start_{message.id}")])
        reply_markup = InlineKeyboardMarkup(keyboard_rows)
        await message.reply_text("لینک‌های زیر پیدا شدند. موارد مورد نظر را انتخاب کرده و سپس دکمه 'شروع' را بزنید:", reply_markup=reply_markup, quote=True)
        return

    if message.text == '/start':
        keyboard = KeyboardBuilder.reply(["تنظیمات"])
        await message.reply('ربات در خدمت شماست! برای ارسال پست یا تغییر تنظیمات روی "تنظیمات" بزن.', quote=True, reply_markup=keyboard)

    elif message.text == 'تنظیمات':
        await command_setting_handler(client, message)


# <<<<<<< کدهای زیر جایگزین می‌شوند >>>>>>>
async def command_setting_handler(client, message):
    settings = await redis_cache.get_settings()
    text, keyboard = build_settings_message(settings)
    await message.reply(text, reply_markup=keyboard)

async def edit_settings_message(callback_query, settings):
    text, keyboard = build_settings_message(settings)
    try:
        await callback_query.message.edit_text(text, reply_markup=keyboard)
    except MessageNotModified:
        pass

@bot_client.on_callback_query()
async def callback_handler(client, callback_query):
    data = callback_query.data
    logger.info(f'callback data : {data}')
    
    if data == "toggle_auto_remove_sign":
        settings = await redis_cache.get_settings()
        new_value = not settings.get('auto_remove_sign', False)
        await redis_cache.update_setting("auto_remove_sign", new_value)
        await callback_query.answer("وضعیت حذف خودکار امضا تغییر کرد!")
        settings['auto_remove_sign'] = new_value # به‌روزرسانی مقدار برای نمایش
        await edit_settings_message(callback_query, settings)
        return

    elif data == "toggle_auto_embed":
        settings = await redis_cache.get_settings()
        new_value = not settings.get('is_auto_embed_enabled', False)
        await redis_cache.update_setting("is_auto_embed_enabled", new_value)
        await callback_query.answer("وضعیت جاگذاری خودکار تغییر کرد!")
        settings['is_auto_embed_enabled'] = new_value # به‌روزرسانی مقدار برای نمایش
        await edit_settings_message(callback_query, settings)
        return
        
    parts = data.split("_")
    
    if parts[0] == "toggle" and len(parts) == 3 and parts[1].isdigit():
        message_id = int(parts[1])
        link_id_to_toggle = parts[2]

        post_data = await redis_cache.get(f"post:{message_id}")
        if not post_data:
            await callback_query.answer("خطا: اطلاعات این پست منقضی شده است.", show_alert=True)
            return

        for link in post_data['links']:
            if link['id'] == link_id_to_toggle:
                link['selected'] = not link['selected']
                break
        
        await redis_cache.set(f"post:{message_id}", post_data)

        keyboard_rows = []
        for link in post_data['links']:
            status_emoji = "✅" if link['selected'] else "❌"
            button_text = f"{status_emoji} {link['text']}"
            button_callback = f"toggle_{message_id}_{link['id']}"
            keyboard_rows.append([InlineKeyboardButton(button_text, callback_data=button_callback)])
        
        keyboard_rows.append([InlineKeyboardButton("🚀 شروع", callback_data=f"start_{message_id}")])
        reply_markup = InlineKeyboardMarkup(keyboard_rows)
        try:
            await callback_query.message.edit_reply_markup(reply_markup)
            await callback_query.answer("انتخاب شما به‌روز شد.")
        except MessageNotModified:
            await callback_query.answer()
        return

    elif parts[0] == "start" and len(parts) == 2 and parts[1].isdigit():
        message_id = int(parts[1])
        post_data = await redis_cache.get(f"post:{message_id}")
        if not post_data:
            await callback_query.answer("خطا: اطلاعات این پست منقضی شده است.", show_alert=True)
            return

    
        selected_links = [link for link in post_data['links'] if link.get('selected', False)]

        if not selected_links:
            await callback_query.answer("هیچ لینکی انتخاب نشده است!", show_alert=True)
            return
            
        task = extractor_task.delay(post_data)
        btn = KeyboardBuilder.inline([['کنسل' , f'cancel_task:{task.id}']])
        
        task_started_message = await callback_query.message.edit('عملیات استخراج شروع شد ...' , reply_markup =btn )
        await task_started_message.pin(both_sides = True)
        return

    if data == "change_uploader":
        await callback_query.answer()
        ask_msg = await callback_query.message.reply_text("لطفا یوزرنیم آپلودر را ارسال کنید:")
        try:
            new_username_msg = await client.listen(callback_query.from_user.id, timeout=60)
            if not new_username_msg or not new_username_msg.text:
                await ask_msg.edit_text("❌ یوزرنیم نامعتبر است. دوباره تلاش کن."); return
            new_username = new_username_msg.text.strip()
            await redis_cache.update_setting("uploader_username", new_username)
            settings = await redis_cache.get_settings()
            await edit_settings_message(callback_query, settings)
        except asyncio.TimeoutError:
            await ask_msg.edit_text("⏰ زمان وارد کردن یوزرنیم تمام شد. دوباره تلاش کن.")
        finally:
            if 'ask_msg' in locals(): await ask_msg.delete()
            if 'new_username_msg' in locals() and new_username_msg: await new_username_msg.delete()

    elif data == "change_uploader_type":
        kb = KeyboardBuilder.inline(*[[(t, f"set_uploader_type_{t}")] for t in UploaderTypes.ALL])
        await callback_query.message.edit_text("نوع آپلودر را انتخاب کنید:", reply_markup=kb)
        await callback_query.answer()

    elif data.startswith("set_uploader_type_"):
        selected = data.replace("set_uploader_type_", "")
        if selected in UploaderTypes.ALL:
            await redis_cache.update_setting("uploader_type", selected)
            await callback_query.answer(f"نوع آپلودر روی {selected} تنظیم شد.")
            settings = await redis_cache.get_settings()
            await edit_settings_message(callback_query, settings)
        else:
            await callback_query.answer("نوع آپلودر نامعتبر است!")
            
    elif data.startswith('cancel_task:') : 
        try :
            task_id = data.split(':')[1]
            task = AsyncResult(task_id)
            task.revoke(terminate=True)
            await callback_query.answer(f'عملیات با موفقیت کنسل شد !' , show_alert = True)
            await callback_query.message.delete()
        except Exception as e :
            logger.error(e)
        
    else:
        await callback_query.answer()

# ---------------------------------------------------------------------
# BOT RUNNING
# ---------------------------------------------------------------------

async def main():
    log_env_variables()
    logger.info('<<< starting clients and connecting to Redis >>>')
    # حذف فراخوانی init_db()
    # await init_db()
    # logger.info("Database connected and schemas generated.") # این خط هم حذف می‌شود
    await redis_cache.connect()
    logger.info("Redis connected.")
    await bot_client.start()
    bot_info = await bot_client.get_me()
    logger.info(f"Bot client {bot_info.username} started successfully.")
    logger.info("Clients are now listening for incoming messages... (Press Ctrl+C to exit)")
    try:
        await idle()
    finally:
        await bot_client.stop()
        await redis_cache.close()
        # حذف بستن ارتباط با دیتابیس
        # await Tortoise.close_connections()
        logger.info("Clients stopped and Redis connection closed.")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())