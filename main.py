import os
import instaloader
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import aiohttp
import ssl

# SSL kontekstini sozlash
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Instaloader orqali Instagramdan video URL olish
def download_instagram_video(post_url):
    try:
        # Instaloader ob'ektini yaratish
        L = instaloader.Instaloader()

        # Post URL'dan shortcode olish
        post_shortcode = post_url.split("/")[-2]
        post = instaloader.Post.from_shortcode(L.context, post_shortcode)

        # Video bo'lsa, URL ni olish
        if post.is_video:
            return post.video_url
        else:
            return None
    except Exception as e:
        print(f"Xatolik (Instagram yuklash): {e}")
        return None

# Videoni asinxron yuklash
async def download_video(session, url):
    try:
        async with session.get(url, ssl=ssl_context) as response:
            if response.status == 200:
                return await response.read()
            else:
                print(f"Xatolik: {response.status}, {await response.text()}")
                return None
    except Exception as e:
        print(f"Xatolik (video yuklash): {e}")
        return None

# /start komandasini ishlash funksiyasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Instagram video havolasini yuboring, men sizga videoni yuklab beraman.\n\n"
        "Masalan: https://www.instagram.com/p/xxxxxx/"
    )

# Instagram havolasini qabul qilish va video yuklab berish
async def handle_instagram_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video_url = update.message.text.strip()

    # Instagramdan video URLni olish
    download_url = download_instagram_video(video_url)

    if download_url:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_VIDEO)
        try:
            async with aiohttp.ClientSession() as session:
                video_content = await download_video(session, download_url)
                if video_content:
                    video_path = "downloaded_video.mp4"

                    # Videoni vaqtinchalik faylga saqlash
                    with open(video_path, "wb") as video_file:
                        video_file.write(video_content)

                    # Video yuborish
                    with open(video_path, "rb") as video_file:
                        await update.message.reply_video(video=video_file)

                    # Faylni o'chirish
                    os.remove(video_path)
                else:
                    await update.message.reply_text("Videoni yuklashda xatolik yuz berdi.")
        except Exception as e:
            print(f"Video yuborishda xatolik: {e}")
            await update.message.reply_text("Videoni yuborishda xatolik yuz berdi. Qayta urinib ko'ring.")
    else:
        await update.message.reply_text(
            "Havola noto'g'ri yoki video topilmadi. To'g'ri Instagram post havolasini yuboring.\n"
            "Masalan: https://www.instagram.com/p/xxxxxx/"
        )

# Asosiy bot dasturi
async def main():
    BOT_TOKEN = "6693824512:AAHdjkrF0mqVdUHgeBmb3_qPLfa7CzjKxYM"  # Bot tokeningizni kiriting
    if not BOT_TOKEN:
        print("Iltimos, bot tokenini kiriting.")
        return

    # Botni yaratish
    application = Application.builder().token(BOT_TOKEN).build()

    # Webhookni tozalash
    await application.bot.delete_webhook(drop_pending_updates=True)

    # Handlerlarni qo'shish
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_instagram_link))

    # Botni ishga tushirish
    await application.run_polling()

# Skriptni ishga tushirish
if __name__ == "__main__":
    asyncio.run(main())
