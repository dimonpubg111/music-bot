import asyncio
import os
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("8570431888:AAEQY3Rwo8ElORJSShUzl6VesysFEkz7yyU")

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_data = {}

# ---------------- START ----------------
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🎧 Бот работает!\n\nОтправь название песни или ссылку")

# ---------------- LINKS (TikTok / YouTube) ----------------
@dp.message(lambda m: m.text and "http" in m.text)
async def handle_link(message: types.Message):
    url = message.text

    await message.answer("📥 Загружаю видео...")

    ydl_opts = {
        "format": "mp4",
        "outtmpl": "video.%(ext)s",
        "quiet": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(info)

        await message.answer_video(types.FSInputFile(file))

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎵 Скачать музыку", callback_data=f"music|{url}")]
        ])

        await message.answer("Выбери действие 👇", reply_markup=kb)

    except:
        await message.answer("❌ Не удалось скачать видео")

# ---------------- MUSIC MENU ----------------
@dp.callback_query(lambda c: c.data.startswith("music"))
async def music_menu(callback: types.CallbackQuery):
    url = callback.data.split("|")[1]

    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(url, download=False)

    title = info.get("title", "Unknown")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬇️ Скачать аудио", callback_data=f"dl|{url}")]
    ])

    await callback.message.answer(f"🎵 {title}", reply_markup=kb)

# ---------------- DOWNLOAD AUDIO ----------------
@dp.callback_query(lambda c: c.data.startswith("dl"))
async def download_audio(callback: types.CallbackQuery):
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
        await callback.message.answer("❌ Ошибка загрузки")

# ---------------- SEARCH ----------------
@dp.message()
async def search(message: types.Message):
    query = message.text

    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(f"ytsearch5:{query}", download=False)

    results = info.get("entries", [])

    if not results:
        await message.answer("❌ Ничего не найдено")
        return

    user_data[message.from_user.id] = results

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=r["title"][:40],
            callback_data=f"sel|{i}"
        )]
        for i, r in enumerate(results)
    ])

    await message.answer("🎧 Выбери трек:", reply_markup=kb)

# ---------------- SELECT TRACK ----------------
@dp.callback_query(lambda c: c.data.startswith("sel"))
async def select_track(callback: types.CallbackQuery):
    i = int(callback.data.split("|")[1])
    uid = callback.from_user.id

    url = user_data[uid][i]["webpage_url"]

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬇️ Скачать", callback_data=f"dl|{url}")]
    ])

    await callback.message.answer("Готово 👇", reply_markup=kb)

# ---------------- RUN ----------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
