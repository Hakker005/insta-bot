import os
import requests
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# RapidAPI kalitini bu yerga kiritamiz
RAPIDAPI_KEY = "7ea1caf5a1msh56c0d672c066325p17f7eajsnde7cddd47a77"  # Siz bergan kalit

# Instagram postini yuklab olish funksiyasi
def download_instagram_reel(post_url):
    try:
        # URL tozalash
        cleaned_url = clean_url(post_url)

        # API URL va parametrlar
        url = "https://instagram-api-media-downloader.p.rapidapi.com/instantdownloader"
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "Content-Type": "application/json"
        }
        payload = {"url": cleaned_url}  # Tozalangan URL

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()  # Video URL'sini qaytaradi
        else:
            print(f"Xatolik: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Xatolik: {e}")
        return None

# /start komandasini ishlash funksiyasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Instagram post havolasini yuboring, men sizga videoni yoki rasmni yuboraman."
    )
def clean_url(post_url):
    # Instagram URL'ini tozalash
    return post_url.split('?')[0]

# Instagram post havolasini qabul qilish va yuborish funksiyasi
async def handle_instagram_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post_url = update.message.text.strip()

    # Foydalanuvchiga animatsiyani ko'rsatish
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_VIDEO)

    # Instagram postini yuklab olish
    post_data = download_instagram_post(post_url)
    if post_data:
        try:
            # Agar video URL bo'lsa, video yuboriladi
            video_url = post_data.get("video_url")
            if video_url:
                video_content = requests.get(video_url).content
                with open("video.mp4", "wb") as video_file:
                    video_file.write(video_content)

                with open("video.mp4", "rb") as video_file:
                    await update.message.reply_video(video=video_file)

                os.remove("video.mp4")
            else:
                # Agar rasm bo'lsa, rasm yuboriladi
                image_url = post_data.get("image_url")
                if image_url:
                    await update.message.reply_photo(photo=image_url)
                else:
                    await update.message.reply_text("Rasm yoki video topilmadi.")
        except Exception as e:
            print(f"Xatolik: {e}")
            await update.message.reply_text(
                "Postni yuborishda xatolik yuz berdi. Iltimos, qayta urinib ko'ring."
            )
    else:
        await update.message.reply_text(
            "Postni olishda xatolik yuz berdi. Iltimos, to'g'ri Instagram havolasini yuboring."
        )

# Asosiy bot dasturi
async def main():
    BOT_TOKEN = "6693824512:AAE7k1FvtjKN64BxSibWbcRoDXa_bHmvCGo"  # Telegram bot tokenini kiritasiz
    if not BOT_TOKEN:
        print("Iltimos, bot tokenini kiriting.")
        return

    application = Application.builder().token(BOT_TOKEN).build()

    # Handlerlarni qo'shamiz
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_instagram_link))

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
