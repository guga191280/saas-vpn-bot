import aiosqlite

DB_NAME = "bot_data.db"

async def init_db(super_admin_id):
    async with aiosqlite.connect(DB_NAME) as db:
        # База для рассылки
        await db.execute("CREATE TABLE IF NOT EXISTS users (telegram_id INTEGER PRIMARY KEY)")
        
        # Администраторы
        await db.execute("CREATE TABLE IF NOT EXISTS admins (telegram_id INTEGER PRIMARY KEY)")
        await db.execute("INSERT OR IGNORE INTO admins (telegram_id) VALUES (?)", (super_admin_id,))
        
        # Настройки (Обязательная подписка)
        await db.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
        
        # Черный список
        await db.execute("CREATE TABLE IF NOT EXISTS blacklist (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, value TEXT)")
        
        await db.commit()

# Базовые функции проверки
async def is_admin(telegram_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT 1 FROM admins WHERE telegram_id = ?", (telegram_id,)) as cursor:
            return await cursor.fetchone() is not None

async def get_force_sub_channel():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT value FROM settings WHERE key = 'force_sub'") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None
