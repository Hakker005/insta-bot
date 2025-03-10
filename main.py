import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from yt_dlp import YoutubeDL

# Botni yaratish
app = Client("my_bot", bot_token="YOUR_BOT_TOKEN")

# Videoni yuklab olish funksiyasi
def download_instagram_video(url: str) -> str:
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': 'video.mp4',
    }
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            return "video.mp4", info
        except Exception as e:
            if "private" in str(e).lower():
                raise ValueError("❗️Bu video yopiq akkauntga tegishli bo'lishi mumkin.")
            else:
                raise ValueError("❗️Yuklab olishda xatolik yuz berdi.")

# Fayl hajmini tekshirish funksiyasi
def is_file_too_large(file_path: str, max_size_mb: int = 50) -> bool:
    return os.path.getsize(file_path) > max_size_mb * 1024 * 1024

# /start komandasi
@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply_text(
        "Salom! 🎥 Videolarni yuklab olish uchun video havolasini yuboring."
    )

# Videoni yuklab olib, foydalanuvchiga jo'natish
@app.on_message(filters.text & ~filters.command)
async def download_video(client: Client, message: Message):
    url = message.text
    status_message = await message.reply_text("⏳ Video yuklanmoqda, kuting...")
    
    try:
        video_path, info = download_instagram_video(url)
        if is_file_too_large(video_path):
            await message.reply_text("❗️ Video hajmi 50MB dan katta. Yuklab bo‘lmadi.")
        else:
            keyboard = [[InlineKeyboardButton("Qo‘shiqni yuklab olish", callback_data=f"download_song|{url}")]]
            await message.reply_video(video=video_path, caption="😊 Videodan rohatlaning!", reply_markup=InlineKeyboardMarkup(keyboard))
        os.remove(video_path)
    except ValueError as ve:
        await message.reply_text(str(ve))
    except Exception:
        await message.reply_text("❗️Kutilmagan xatolik yuz berdi.")
    finally:
        await status_message.delete()

# Tugma bosilganda qo‘shiqni yoki MP3 audioni yuborish
@app.on_callback_query()
async def button(client: Client, callback_query: CallbackQuery):
    data = callback_query.data.split("|")
    if data[0] == "download_song":
        video_url = data[1]
        status_message = await callback_query.message.reply_text("⏳ Qo‘shiq yuklanmoqda, kuting...")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'song.mp3',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            await callback_query.message.reply_audio(audio="song.mp3", caption="🎶 Qo‘shiqdan rohatlaning!")
            os.remove("song.mp3")
        except Exception:
            await callback_query.message.reply_text("❗️Qo‘shiqni yuklab olishda xatolik yuz berdi.")
        finally:
            await status_message.delete()

# Botni ishga tushirish
if __name__ == "__main__":
    print("Bot ishga tushdi!")
    app.run()
