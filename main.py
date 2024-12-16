import os
import requests
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import instaloader
import nest_asyncio

# Instagram uchun sozlamalar
INSTAGRAM_USERNAME = "hozircha_03"  # Instagram login
INSTAGRAM_PASSWORD = "hokimjon0705"  # Instagram parol

def login_instagram():
    """Instaloader orqali Instagram akkauntga kirish"""
    loader = instaloader.Instaloader()
    try:
        loader.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        print("Instagramga muvaffaqiyatli kirdingiz!")
        return loader
    except Exception as e:
        print(f"Instagramga kirishda xatolik: {e}")
        return None

def download_instagram_video(post_url):
    """Instagram postining videosini yuklab olish"""
    loader = login_instagram()
    if not loader:
        return None

    try:
        post = instaloader.Post.from_shortcode(loader.context, post_url.split("/")[-2])
        if post.is_video:
            video_url = post.video_url
            print(f"Video URL: {video_url}")
            return video_url
        else:
            print("Berilgan postda video yo'q.")
            return None
    except Exception as e:
        print(f"Postni yuklashda xatolik: {e}")
        return None

# /start komandasini ishlash funksiyasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Instagram video havolani yuboring, men sizga videoni yuklab beraman."
    )

# Instagram havolasini qabul qilish va video yuklab berish
async def handle_instagram_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video_url = update.message.text.strip()

    # Foydalanuvchiga animatsiyani ko'rsatish
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_VIDEO)

    # Videoni yuklab olish
    download_url = download_instagram_video(video_url)
    if download_url:
        try:
            # Video kontentni yuklash
            video_content = requests.get(download_url).content
            video_path = "downloaded_video.mp4"

            # Video faylni saqlash
            with open(video_path, "wb") as video_file:
                video_file.write(video_content)

            # Video yuborish
            with open(video_path, "rb") as video_file:
                await update.message.reply_video(video=video_file)

            # Faylni o'chirish
            os.remove(video_path)
        except Exception as e:
            print(f"Video yuborishda xatolik: {e}")
            await update.message.reply_text(
                "Video yuborishda xatolik yuz berdi. Iltimos, qayta urinib ko'ring."
            )
    else:
        await update.message.reply_text(
            "Video yuklashda xatolik yuz berdi. Iltimos, to'g'ri Instagram havolasini yuboring."
        )

# Asosiy bot dasturi
async def main():
    BOT_TOKEN = "6693824512:AAE7k1FvtjKN64BxSibWbcRoDXa_bHmvCGo"  # Telegram bot tokenini olish
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
    try:
        nest_asyncio.apply()  # Joriy event loopga asinxron kodni bajarishga ruxsat berish
        asyncio.run(main())  # Yangi loop yaratib ishga tushirish
    except RuntimeError as e:
        if "Cannot close a running event loop" in str(e):
            print("Event loop allaqachon ishlayapti, mavjud loopdan foydalanamiz.")
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main())
