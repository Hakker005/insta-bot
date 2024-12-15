import os
import requests
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import instaloader
import nest_asyncio
import asyncio
from dotenv import load_dotenv

# .env faylni yuklash
load_dotenv()

# Instagram login va parolni olish
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

# Instagramdan video yuklab olish funksiyasi
def download_instagram_video(post_url):
    try:
        loader = instaloader.Instaloader()
        loader.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)  # Login qilish
        shortcode = post_url.split("/")[-2]  # Havoladan shortcode-ni ajratib olish
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        if post.is_video:
            return post.video_url
        else:
            return None
    except Exception as e:
        print(f"Xatolik: {e}")
        return None

# /start komandasini ishlash funksiyasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Instagram video havolani yuboring, men sizga videoni yuklab beraman."
    )

# Instagram havolasini qabul qilish va video yuklab berish
async def handle_instagram_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video_url = update.message.text.strip()

    # Havolani tozalash funksiyasi
    def clean_url(post_url):
        return post_url.split('?')[0]

    cleaned_url = clean_url(video_url)

    # Foydalanuvchiga animatsiyani ko'rsatish
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_VIDEO)

    # Videoni yuklab olish
    download_url = download_instagram_video(cleaned_url)
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
    BOT_TOKEN = os.getenv("BOT_TOKEN")  # Telegram bot tokenini olish
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
        asyncio.run(main())  # Yangi loop yaratib ishga tushirish
    except RuntimeError as e:
        if "Cannot close a running event loop" in str(e):
            print("Event loop allaqachon ishlayapti, mavjud loopdan foydalanamiz.")
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main())
