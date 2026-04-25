import asyncio
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_data = {}

# ---------------- START ----------------
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🎧 Fast bot ready")

# ---------------- SEARCH (FAST FIX) ----------------
@dp.message()
async def search(message: types.Message):
    text = message.text

    await message.answer("🔎 ищу...")

    try:
        ydl_opts = {
            "quiet": True,
            "noplaylist": True,
            "socket_timeout": 5
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch3:{text}", download=False)

        results = info.get("entries", [])

        if not results:
            await message.answer("❌ не найдено")
            return

        user_data[message.from_user.id] = results

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=r["title"][:35],
                callback_data=f"sel|{i}"
            )]
            for i, r in enumerate(results)
        ])

        await message.answer("🎧 выбери:", reply_markup=kb)

    except:
        await message.answer("❌ ошибка поиска")

# ---------------- SELECT ----------------
@dp.callback_query(lambda c: c.data.startswith("sel"))
async def select(callback: types.CallbackQuery):
    i = int(callback.data.split("|")[1])
    uid = callback.from_user.id

    url = user_data[uid][i]["webpage_url"]

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬇️ скачать", callback_data=f"dl|{url}")]
    ])

    await callback.message.answer("готово 👇", reply_markup=kb)

# ---------------- DOWNLOAD ----------------
@dp.callback_query(lambda c: c.data.startswith("dl"))
async def download(callback: types.CallbackQuery):
    url = callback.data.split("|")[1]

    file_path = "music.mp3"

    ydl_opts = {
        "format": "bestaudio",
        "outtmpl": file_path,
        "quiet": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        await callback.message.answer_audio(types.FSInputFile(file_path))

    except:
        await callback.message.answer("❌ ошибка загрузки")

# ---------------- RUN ----------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
