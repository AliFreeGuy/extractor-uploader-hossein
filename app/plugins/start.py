from pyrogram import Client, filters
from utils import logger
from utils.db import User  # مدل یوزر رو ایمپورت کن

@Client.on_message(filters.command('start'))
async def say_hello(bot, msg):
    user_id = msg.from_user.id
    first_name = msg.from_user.first_name or "Unknown"

    # ثبت یا پیدا کردن یوزر
    user, created = await User.get_or_create(
        user_id=user_id,
        defaults={"name": first_name}
    )

    if created:
        text = f"سلام {first_name}! ثبت نام شدی. 🎉"
    else:
        text = f"سلام دوباره {user.name}! خوش برگشتی."

    await bot.send_message(user_id, text)
