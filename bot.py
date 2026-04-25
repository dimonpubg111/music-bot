import os
import asyncio
import logging
import yt_dlp

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ---------------- LOGGING ----------------
logging.basicConfig(level=logging.INFO)

# ---------------- CONFIG ----------------
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN is missing in environment variables")

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_data = {}

# ---------------- START ----------------
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🎧 Production Bot готов\n\n"
        "📌 Отправь название музыки\n"
        "📎 Или ссылку (YouTube / TikTok)"
    )

# ---------------- SEARCH ----------------
@dp.message()
async def handle(message: types.Message):
    text = message.text.strip()

    # ---------------- LINK ----------------
    if "http" in text:
        await message.answer("📥 Загружаю видео...")

        try:
            ydl_opts = {
                "format": "mp4",
                "outtmpl": "video.%(ext)s",
                "quiet": True,
                "socket_timeout": 8
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(text, download=True)
                file = ydl.prepare_filename(info)

            await message.answer_video(types.FSInputFile(file))

        except Exception as e:
            logging.error(e)
            await message.answer("❌ Ошибка загрузки видео")
        return

    # ---------------- MUSIC SEARCH ----------------
    await message.answer("🔎 Ищу музыку...")

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

    except Exception as e:
        logging.error(e)
        await message.answer("❌ Ошибка поиска")

# ---------------- SELECT ----------------
@dp.callback_query(lambda c: c.data.startswith("sel"))
async def select(callback: types.CallbackQuery):
    try:
        i = int(callback.data.split("|")[1])
        uid = callback.from_user.id

        url = user_data[uid][i]["webpage_url"]

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬇️ Скачать аудио", callback_data=f"dl|{url}")]
        ])

        await callback.message.answer("Готово 👇", reply_markup=kb)

    except Exception as e:
        logging.error(e)
        await callback.message.answer("❌ Ошибка выбора")

# ---------------- DOWNLOAD ----------------
@dp.callback_query(lambda c: c.data.startswith("dl"))
async def download(callback: types.CallbackQuery):
    url = callback.data.split("|")[1]

    file_path = "music.mp3"

    try:
        ydl_opts = {
            "format": "bestaudio",
            "outtmpl": file_path,
            "quiet": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        await callback.message.answer_audio(types.FSInputFile(file_path))

    except Exception as e:
        logging.error(e)
        await callback.message.answer("❌ Ошибка загрузки аудио")

# ---------------- MAIN ----------------
async def main():
    logging.info("Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
