import asyncio
import logging
import os
import uuid
import urllib.parse
from aiogram import Bot, Dispatcher, types
import extractor

TOKEN = "8011501394:AAEZ0enx8uFE-62EcRcGqyuIBA4eKrBlyJg"
DATA_DIR = "data"
SERVER_IP = "169.58.119.116"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message()
async def handle_link(message: types.Message):
    text = message.text
    if text and text.startswith("happ://"):
        keys = await asyncio.to_thread(extractor.extract_vless_keys, text)
        if keys and len(keys) > 0:
            unique_id = str(uuid.uuid4())[:8]
            os.makedirs(DATA_DIR, exist_ok=True)
            file_path = os.path.join(DATA_DIR, unique_id)
            
            with open(file_path, "w") as f:
                f.write("\n".join(keys))
            
            # Формируем сырую ссылку через IP и порт 5002 (как у донора)
            raw_sub = f"http://{SERVER_IP}:5002/sub/{unique_id}"
            
            # Заворачиваем в быстрый конвертер с URL-кодированием
            encoded_raw = urllib.parse.quote(raw_sub, safe="")
            sub_url = f"https://tetragidropiranilciklopentiltetragidropiridopiridinovye.online/exec?url={encoded_raw}"
            
            await message.answer(sub_url)

async def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.main(main()) if hasattr(asyncio, "main") else asyncio.run(main())
