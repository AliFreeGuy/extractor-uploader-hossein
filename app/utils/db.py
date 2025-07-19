from tortoise import Tortoise, fields
from tortoise.models import Model

# مدل نمونه
class User(Model):
    id = fields.IntField(pk=True)
    user_id = fields.BigIntField(unique=True)
    name = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "users"


async def init_db():
    await Tortoise.init(
        db_url="sqlite://db.sqlite3",  # می‌تونی mysql://user:pass@host:port/db هم بدی
        modules={"models": ["utils.db"]}  # آدرس ماژول مدل‌ها
    )
    await Tortoise.generate_schemas()  # ایجاد جدول‌ها اگر وجود ندارن


async def close_db():
    await Tortoise.close_connections()
