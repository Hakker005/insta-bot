import os
import requests
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import aiohttp
from bs4 import BeautifulSoup


# Instagramdan video URL'ni olish
def get_instagram_video_url(post_url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(post_url, headers=headers)
        response.raise_for_status()

        # HTML parselash
        soup = BeautifulSoup(response.text, "html.parser")
        video_tag = soup.find("meta", property="og:video")

        if video_tag and video_tag["content"]:
            return video_tag["content"]
        else:
            return None
    except Exception as e:
        print(f"Xatolik: {e}")
        return None


# Videoni asinxron yuklash
async def download_video(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                print(f"Video yuklanmoqda: {url}")
                return await response.read()
            else:
                print(f"Xatolik: {response.status}")
                return None
    except Exception as e:
        print(f"Xatolik: {e}")
        return None


# /start komandasini ishlash funksiyasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Instagram video havolasini yuboring, men sizga videoni yuklab beraman."
    )


# Instagram havolasini qabul qilish va video yuklab berish
async def handle_instagram_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video_url = update.message.text.strip()

    # Foydalanuvchiga animatsiyani ko'rsatish
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_VIDEO)

    # Videoni yuklab olish uchun URL olish
    download_url = get_instagram_video_url(video_url)
    if download_url:
        try:
            # Asinxron sessiya yaratish
            async with aiohttp.ClientSession() as session:
                video_content = await download_video(session, download_url)
                if video_content:
                    video_path = "downloaded_video.mp4"

                    # Video faylni saqlash
                    with open(video_path, "wb") as video_file:
                        video_file.write(video_content)

                    # Video yuborish
                    with open(video_path, "rb") as video_file:
                        await update.message.reply_video(video=video_file)

                    # Faylni o'chirish
                    os.remove(video_path)
                else:
                    await update.message.reply_text("Video yuklashda xatolik yuz berdi.")
        except Exception as e:
            print(f"Video yuborishda xatolik: {e}")
            await update.message.reply_text(
                "Video yuborishda xatolik yuz berdi. Iltimos, qayta urinib ko'ring."
            )
    else:
        await update.message.reply_text(
            "Video yuklashda xatolik yuz berdi. Iltimos, to'g'ri Instagram havolasini yuboring. Masalan: https://www.instagram.com/p/xxxxxx/"
        )


# Asosiy bot dasturi
async def main():
    BOT_TOKEN = "6693824512:AAHdjkrF0mqVdUHgeBmb3_qPLfa7CzjKxYM"
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
    nest_asyncio.apply()
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

