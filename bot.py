import os
import asyncio
import yt_dlp

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ---------------- CONFIG ----------------
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 123456789  # <-- вставь свой Telegram ID

if not TOKEN:
    raise ValueError("BOT_TOKEN is missing")

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_data = {}

# ---------------- START ----------------
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🎧 PRO BOT готов\n\n"
        "📌 отправь название музыки\n"
        "📎 или ссылку (YouTube / TikTok)"
    )

# ---------------- ADMIN PANEL ----------------
@dp.message(Command("admin"))
async def admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ нет доступа")

    await message.answer(
        "🛠 ADMIN PANEL\n\n"
        "/stats - пользователи\n"
        "/ping - проверка"
    )

@dp.message(Command("stats"))
async def stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(f"👥 users: {len(user_data)}")

@dp.message(Command("ping"))
async def ping(message: types.Message):
    await message.answer("🏓 bot alive")

# ---------------- MAIN ----------------
@dp.message()
async def handle(message: types.Message):
    text = message.text

    # -------- VIDEO LINK --------
    if "http" in text:
        await message.answer("📥 скачиваю видео...")

        try:
            ydl_opts = {
                "format": "mp4",
                "outtmpl": "video.%(ext)s",
                "quiet": True,
                "socket_timeout": 10
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(text, download=True)
                file = ydl.prepare_filename(info)

            await message.answer_video(types.FSInputFile(file))

        except:
            await message.answer("❌ ошибка загрузки видео")

        return

    # -------- MUSIC SEARCH --------
    await message.answer("🔎 ищу музыку...")

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
            await message.answer("❌ ничего не найдено")
            return

        user_data[message.from_user.id] = results

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=r["title"][:40],
                callback_data=f"sel|{i}"
            )]
            for i, r in enumerate(results)
        ])

        await message.answer("🎧 выбери трек:", reply_markup=kb)

    except:
        await message.answer("❌ ошибка поиска")

# ---------------- SELECT TRACK ----------------
@dp.callback_query(lambda c: c.data.startswith("sel"))
async def select(callback: types.CallbackQuery):
    i = int(callback.data.split("|")[1])
    uid = callback.from_user.id

    url = user_data[uid][i]["webpage_url"]

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬇️ скачать аудио", callback_data=f"dl|{url}")]
    ])

    await callback.message.answer("готово 👇", reply_markup=kb)

# ---------------- DOWNLOAD AUDIO ----------------
@dp.callback_query(lambda c: c.data.startswith("dl"))
async def download(callback: types.CallbackQuery):
    url = callback.data.split("|")[1]

    file_path = "music.mp3"

    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": file_path,
            "quiet": True,
            "socket_timeout": 10
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        await callback.message.answer_audio(types.FSInputFile(file_path))

    except:
        await callback.message.answer("❌ ошибка загрузки аудио")

# ---------------- RUN ----------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
