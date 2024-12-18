import os
import instaloader
import asyncio
import aiohttp
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging

# Loggerni sozlash
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Instaloader orqali Instagramdan video URL olish
def download_instagram_video(post_url):
    try:
        loader = instaloader.Instaloader()
        post_shortcode = post_url.split("/")[-2]
        post = instaloader.Post.from_shortcode(loader.context, post_shortcode)

        if post.is_video:
            return post.video_url
        else:
            return None
    except Exception as e:
        logger.error(f"Instagramdan video yuklashda xatolik: {e}")
        return None

# Videoni asinxron yuklash
async def download_video(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                logger.info(f"Video muvaffaqiyatli yuklandi: {url}")
                return await response.read()
            else:
                logger.error(f"Video yuklashda xatolik: {response.status}")
                return None
    except Exception as e:
        logger.error(f"Videoni yuklashda xatolik: {e}")
        return None

# /start komandasini ishlash funksiyasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Instagram video havolasini yuboring, men sizga videoni yuklab beraman.")

# Instagram havolasini qabul qilish va video yuklab berish
async def handle_instagram_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video_url = update.message.text.strip()
    logger.info(f"Instagram havolasi qabul qilindi: {video_url}")

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_VIDEO)

    download_url = download_instagram_video(video_url)
    if download_url:
        try:
            async with aiohttp.ClientSession() as session:
                video_content = await download_video(session, download_url)
                if video_content:
                    video_path = "downloaded_video.mp4"
                    with open(video_path, "wb") as video_file:
                        video_file.write(video_content)

                    with open(video_path, "rb") as video_file:
                        await update.message.reply_video(video=video_file)

                    os.remove(video_path)
                else:
                    await update.message.reply_text("Video yuklashda xatolik yuz berdi.")
        except Exception as e:
            logger.error(f"Video yuborishda xatolik: {e}")
            await update.message.reply_text("Video yuborishda xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")
    else:
        await update.message.reply_text("To'g'ri Instagram havolasini yuboring. Video yuklashda xatolik bo'ldi.")

# Asosiy bot dasturi
async def main():
    BOT_TOKEN = os.getenv("BOT_TOKEN")  # Muhit o'zgaruvchisidan tokenni olish
    if not BOT_TOKEN:
        logger.error("Bot tokeni topilmadi. Muhit o'zgaruvchisida BOT_TOKEN ni sozlang.")
        return

    application = Application.builder().token("6693824512:AAHdjkrF0mqVdUHgeBmb3_qPLfa7CzjKxYM").build()  # Tokenni muhit o'zgaruvchisidan olish
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_instagram_link))

    logger.info("Bot ishga tushmoqda...")
    await application.run_polling()

# Skriptni ishga tushirish
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "Cannot close a running event loop" in str(e):
            logger.warning("Mavjud event loop topildi, mavjud loopdan foydalanamiz.")
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main())
