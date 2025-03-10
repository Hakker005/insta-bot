
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
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
            return "video.mp4", info  # info'ni qaytarish
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

# Qo‘shiqni yuklab olish funksiyasi
def download_song(info: dict) -> str:
    song_opts = {
        'format': 'bestaudio/best',  # Eng yaxshi audio formatini tanlash
        'outtmpl': 'song.mp3',  # Qo‘shiq fayl nomi
    }
    with YoutubeDL(song_opts) as ydl:
        try:
            ydl.download([info['webpage_url']])  # Havoladan yuklab olish
            return "song.mp3"
        except Exception as e:
            raise ValueError("❗️Qo‘shiqni yuklab olishda xatolik yuz berdi.")

# Videodan MP3 formatida audio olish funksiyasi
def extract_audio_from_video(video_url: str) -> str:
    audio_path = "video_audio.mp3"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': audio_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([video_url])
            return audio_path
        except Exception as e:
            raise ValueError(f"❗️Videodan audio chiqarishda xatolik yuz berdi: {str(e)}")

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
        # Video havolasini saqlash
        context.user_data["video_url"] = url  # Havolani saqlash

        # Foydalanuvchiga yuklab olish boshlanishini aytish
        status_message = await update.message.reply_text("⏳ Video yuklanmoqda, kuting...")

        # Videoni yuklab olish
        video_path, info = download_instagram_video(url)

        # Fayl hajmini tekshirish
        if is_file_too_large(video_path):
            download_url = f"https://yourserver.com/{os.path.basename(video_path)}"  # Fayl URL-manzili (serverdan olingan URL)
            await update.message.reply_text(
                f"❗️ Video hajmi 50MB dan katta. Siz uni quyidagi havola orqali yuklab olishingiz mumkin:\n\n{download_url}"
            )
        else:
            # Foydalanuvchiga yuklangan videoni yuborish
            keyboard = [
                [InlineKeyboardButton("Qo‘shiqni yuklab olish", callback_data="download_song")]  # Tugma qo‘shish
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await context.bot.send_video(
                chat_id=update.effective_chat.id,
                video=open(video_path, 'rb'),
                caption="😊 Videodan rohatlaning!\n\nBot: @shoxsan_bot",
                reply_markup=reply_markup  # Tugmani yuborish
            )

        # Yuklangan videoni o‘chirish
        os.remove(video_path)

        # "Video yuklanmoqda..." xabarini o'chirish
        await status_message.delete()

    except ValueError as ve:
        await update.message.reply_text(str(ve))
    except Exception:
        await update.message.reply_text("❗️Uzr, kutilmagan xatolik yuz berdi. Iltimos, qayta urinib ko‘ring.")
    finally:
        # Faylni o‘chirish
        if os.path.exists("video.mp4"):
            os.remove("video.mp4")

# Tugma bosilganda qo‘shiqni yoki MP3 audioni yuborish
# Tugma bosilganda qo‘shiqni yoki MP3 audioni yuborish
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Tugma bosilganda javob qaytarish

    if query.data == "download_song":
        # Saqlangan video havolasini olish
        video_url = context.user_data.get("video_url")  # Havolani olish
        if video_url:
            try:
                # Foydalanuvchiga yuklab olish boshlanishini aytish
                status_message = await query.message.reply_text("⏳ Qo‘shiq yuklanmoqda, kuting...")

                try:
                    # Qo‘shiqni yuklab olishga harakat qilish
                    _, info = download_instagram_video(video_url)
                    song_path = download_song(info)

                    # Qo‘shiqni yuborish
                    await context.bot.send_audio(
                        chat_id=query.message.chat.id,
                        audio=open(song_path, 'rb'),
                        caption="🎶 Qo‘shiqdan rohatlaning!\n\nBot: @shoxsan_bot"
                    )

                    # Qo‘shiqni o‘chirish
                    os.remove(song_path)

                except ValueError:
                    # Agar qo‘shiq topilmasa, videodan MP3 olish
                    audio_path = extract_audio_from_video(video_url)

                    # Videodan audio yuborish
                    await context.bot.send_audio(
                        chat_id=query.message.chat.id,
                        audio=open(audio_path, 'rb'),
                        caption="🎧 Videodan audio chiqarildi. Marhamat!\n\nBot: @shoxsan_bot"
                    )

                    # Audioni o‘chirish
                    os.remove(audio_path)

                # "Qo‘shiq yuklanmoqda..." xabarini o'chirish
                await status_message.delete()

            except Exception as e:
                await query.message.reply_text(f"❗️Xatolik yuz berdi: {str(e)}")
                # "Qo‘shiq yuklanmoqda..." xabarini o'chirish
                if status_message:
                    await status_message.delete()
        else:
            await query.message.reply_text("❗️Iltimos, avval video havolasini yuboring.")

# Botni ishga tushirish
def run_bot():
    app = ApplicationBuilder().token("6693824512:AAHdjkrF0mqVdUHgeBmb3_qPLfa7CzjKxYM").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    app.add_handler(CallbackQueryHandler(button))  # Tugma bosilganda ishga tushadigan handler

    print("Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    import sys

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    run_bot()
