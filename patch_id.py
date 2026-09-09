import re

try:
    with open('/opt/v1bot/bot.py', 'r', encoding='utf-8') as f:
        code = f.read()

    # Умный поиск и замена блока блокировки
    pattern = r'if not await database\.is_admin\(message\.from_user\.id\):\s+return'
    new_block = """if not await database.is_admin(message.from_user.id):
        await message.answer(f"⛔️ Доступ закрыт. Твой ID: `{message.from_user.id}`")
        return"""

    code = re.sub(pattern, new_block, code)

    with open('/opt/v1bot/bot.py', 'w', encoding='utf-8') as f:
        f.write(code)
        
    print("✅ Авто-замена выполнена! Бот готов показать твой ID.")
except Exception as e:
    print(f"❌ Ошибка: {e}")
