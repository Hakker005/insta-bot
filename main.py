import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL

# Videoni yuklab olish funksiyasi
def download_instagram_video(url: str) -> str:
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': 'video.mp4',  # Yuklab olingan fayl nomi
    }
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            return "video.mp4"
        except Exception as e:
            if "private" in str(e).lower():
                raise ValueError("❗️Bu video yopiq akkauntga tegishli bo'lishi mumkin.\n😕Hozirga bu videoni yuklab olish imkoni yo'q.\n👨‍💻Adminlar bu muammo ustida ishlashmoqda!")
            else:
                raise e

# /start komandasi uchun handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.message.from_user.first_name  # Foydalanuvchining ismi
    user_last_name = update.message.from_user.last_name  # Foydalanuvchining familiyasi (agar bo'lsa)
    
    # Foydalanuvchiga salom yuborish
    await update.message.reply_text(f"Salom, {user_first_name} {user_last_name if user_last_name else ''}!\n\nBotga xush kelibsiz!")


# Videoni yuklab olib, foydalanuvchiga jo'natish
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    try:
        # Foydalanuvchi yuborgan havolani o'chirish
        await update.message.delete()

        # Foydalanuvchiga yuklab olish boshlanishini aytish
        status_message = await update.message.reply_text("⏳Video yuklanmoqda, kuting...")

        # Botning statusini o'zgartirish
        await update.message.chat.send_action(action="upload_video")

        # Videoni yuklab olish
        video_path = download_instagram_video(url)

        # Foydalanuvchiga yuklangan videoni yuborish
        await update.message.reply_video(
            video=open(video_path, 'rb'),
            caption=" 😊Shunchaki foydalaning\n@shoxsan_bot\ndo'stlarga ham ulashing"
        )

        # Yuklangan videoni o'chirish
        os.remove(video_path)

        # "Video yuklanmoqda..." xabarini o'chirish
        await status_message.delete()

    except ValueError as ve:
        await update.message.reply_text(f"Xatolik: {ve}")
    except Exception as e:
        await update.message.reply_text(f"Xatolik yuz berdi: {e}")

# Botni ishga tushirish
def run_bot():
    app = ApplicationBuilder().token("6693824512:AAHdjkrF0mqVdUHgeBmb3_qPLfa7CzjKxYM").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    import sys

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    run_bot()
