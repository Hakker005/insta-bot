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
                raise ValueError(
                    "❗️Bu video yopiq akkauntga tegishli bo'lishi mumkin.\n😕Hozirga bu videoni yuklab olish imkoni yo'q.\n👨‍💻Adminlar bu muammo ustida ishlashmoqda!"
                )
            else:
                raise ValueError("❗️Uzr, yuklab olishda xatolik yuz berdi. Havolani tekshirib qayta urinib ko‘ring.")

# Fayl hajmini tekshirish funksiyasi
def is_file_too_large(file_path: str, max_size_mb: int = 50) -> bool:
    return os.path.getsize(file_path) > max_size_mb * 1024 * 1024

# /start komandasi uchun handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.message.from_user.first_name
    user_last_name = update.message.from_user.last_name

    await update.message.reply_text(
        f"Salom, {user_first_name} {user_last_name if user_last_name else ''}!\n\n"
        "Botga xush kelibsiz!\n\n🎥 Videolarini yuklab olish uchun video havolasini yuboring."
    )

# Videoni yuklab olib, foydalanuvchiga jo'natish
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    try:
        # Foydalanuvchiga yuklab olish boshlanishini aytish
        status_message = await update.message.reply_text("⏳ Video yuklanmoqda, kuting...")

        # Videoni yuklab olish
        video_path = download_instagram_video(url)

        # Fayl hajmini tekshirish
        if is_file_too_large(video_path):
            download_url = f"https://buni ustida ish olib boryaptiz /{os.path.basename(video_path)}"  # Fayl URL-manzili
            await update.message.reply_text(
                f"❗️ Video hajmi 50MB dan katta. Siz uni quyidagi havola orqali yuklab olishingiz mumkin:\n\n{download_url}"
            )
        else:
            # Foydalanuvchiga yuklangan videoni yuborish
            await context.bot.send_video(
                chat_id=update.effective_chat.id,
                video=open(video_path, 'rb'),
                caption="😊 Videodan rohatlaning!\n\nBot: @shoxsan_bot"
            )

        # Yuklangan videoni o'chirish
        os.remove(video_path)

        # "Video yuklanmoqda..." xabarini o'chirish
        await status_message.delete()

    except ValueError as ve:
        await update.message.reply_text(str(ve))
    except Exception:
        await update.message.reply_text("❗️Uzr, kutilmagan xatolik yuz berdi. Iltimos, qayta urinib ko‘ring.")
    finally:
        # Faylni o'chirish
        if os.path.exists("video.mp4"):
            os.remove("video.mp4")

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
