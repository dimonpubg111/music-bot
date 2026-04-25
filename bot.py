import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import uvicorn

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()
app = FastAPI()

# ---------------- START ----------------
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🚀 Бот работает на Railway (webhook mode)")

# ---------------- WEBHOOK ----------------
@app.post("/webhook")
async def webhook(update: dict):
    telegram_update = types.Update(**update)
    await dp.feed_update(bot, telegram_update)
    return {"ok": True}

# ---------------- HEALTH CHECK ----------------
@app.get("/")
def home():
    return {"status": "bot running"}

# ---------------- RUN ----------------
async def main():
    webhook_url = os.getenv("WEBHOOK_URL")

    await bot.set_webhook(f"{webhook_url}/webhook")

    config = uvicorn.Config(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    server = uvicorn.Server(config)

    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
