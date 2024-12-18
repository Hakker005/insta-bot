import os
import instaloader
import asyncio
import aiohttp
import nest_asyncio
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Instaloader orqali Instagramdan video URL olish
def download_instagram_video(post_url):
    try:
        # Instaloader ob'ektini yaratish
        loader = instaloader.Instaloader()

        # Post URL'dan shortcode olish
        post_shortcode = post_url.split("/")[-2]
        post = instaloader.Post.from_shortcode(loader.context, post_shortcode)

        # Video bo'lsa, URL ni olish
        if post.is_video:
            return post.video_url
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

    # Videoni yuklab olish
    download_url = download_instagram_video(video_url)
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
            "Video yuklashda xatolik yuz berdi. Iltimos, to'g'ri Instagram havolasini yuboring."
        )

# Asosiy bot dasturi
async def main():
    BOT_TOKEN = "6693824512:AAE7k1FvtjKN64BxSibWbcRoDXa_bHmvCGo"
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
