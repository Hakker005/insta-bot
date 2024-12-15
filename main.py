import os
import requests
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# RapidAPI kalitini bu yerga kiritamiz
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")  # Railway'da saqlangan RapidAPI kalitini olamiz

# Instagram postlarini olish funksiyasi
def get_instagram_posts(user_id):
    try:
        url = f"https://instagram-api-media-downloader.p.rapidapi.com/user/posts/{user_id}"  # Foydalanuvchi postlarini olish endpointi
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-HOST": "instagram-api-media-downloader.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()  # Postlar ro'yxatini qaytaradi
        else:
            print(f"Xatolik: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Xatolik: {e}")
        return None

# /start komandasini ishlash funksiyasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Instagram foydalanuvchi ID'sini yuboring, men sizga uning postlarini yuboraman."
    )

# Instagram ID yuborish va postlarni yuborish funksiyasi
async def handle_instagram_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.text.strip()

    # Foydalanuvchiga animatsiyani ko'rsatish
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)

    # Instagram postlarini olish
    posts = get_instagram_posts(user_id)
    if posts:
        try:
            # Postlar ro'yxatini yuborish
            for post in posts.get("data", []):
                post_image_url = post.get("image_url")  # Rasm yoki video URL manzilini olish
                if post_image_url:
                    await update.message.reply_photo(photo=post_image_url)
                else:
                    await update.message.reply_text("Rasm yoki video topilmadi.")
        except Exception as e:
            print(f"Post yuborishda xatolik: {e}")
            await update.message.reply_text(
                "Postlarni yuborishda xatolik yuz berdi. Iltimos, qayta urinib ko'ring."
            )
    else:
        await update.message.reply_text(
            "Postlarni olishda xatolik yuz berdi. Iltimos, to'g'ri foydalanuvchi ID'sini yuboring."
        )

# Asosiy bot dasturi
async def main():
    BOT_TOKEN = os.getenv("BOT_TOKEN")  # Railway'da saqlangan Bot tokenini olamiz
    if not BOT_TOKEN:
        print("Iltimos, bot tokenini kiriting.")
        return

    application = Application.builder().token(BOT_TOKEN).build()

    # Handlerlarni qo'shamiz
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_instagram_id))

    # Botni ishga tushiramiz
    await application.run_polling()

# Skriptni ishga tushirish
if __name__ == "__main__":
    import nest_asyncio
    import asyncio

    try:
        nest_asyncio.apply()  # Joriy event loopga asinxron kodni bajarishga ruxsat berish
        asyncio.run(main())  # Yangi loop yaratib ishga tushirish
    except RuntimeError as e:
        if "Cannot close a running event loop" in str(e):
            print("Event loop allaqachon ishlayapti, mavjud loopdan foydalanamiz.")
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main())
