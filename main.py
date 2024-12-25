import os
import instaloader
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InputFile
from aiogram.filters import Command
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
        print(f"Xatolik: {e}")
        return None

# Videoni asinxron yuklash
async def download_video(session, url):
    try:
        async with session.get(url, ssl=ssl_context) as response:
            if response.status == 200:
                return await response.read()
            else:
                print(f"Xatolik: {response.status}")
                return None
    except Exception as e:
        print(f"Xatolik: {e}")
        return None

# Bot tokenini o'rnating
BOT_TOKEN = "6425621650:AAGeuGkMAhp-TTkSES6zYfNCtGFAzXpbV3U"
if not BOT_TOKEN:
    raise ValueError("Iltimos, bot tokenini kiriting.")

# Bot va Dispatcher yaratish
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# /start komandasi uchun handler
@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Salom! Instagram video havolasini yuboring, men sizga videoni yuklab beraman.")

# Instagram havolasi uchun handler
@dp.message()
async def handle_instagram_link(message: Message):
    video_url = message.text.strip()

    # Videoni yuklab olish uchun URL olish
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

                    # "Video yuborilmoqda..." animatsiyasini jo'natish
                    await bot.send_chat_action(chat_id=message.chat.id, action="upload_video")

                    # Video yuborish
                    try:
                        # Faylni InputFile obyektiga aylantirish
                        video_file = InputFile(path_or_bytesio=video_path)
                        await bot.send_video(chat_id=message.chat.id, video=video_file)

                        # Faylni o'chirish
                        os.remove(video_path)
                    except Exception as e:
                        print(f"Video yuborishda xatolik: {e}")
                        await message.answer("Video yuborishda xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")
                else:
                    await message.answer("Video yuklashda xatolik yuz berdi.")
        except Exception as e:
            print(f"Video yuborishda xatolik: {e}")
            await message.answer("Video yuklashda xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")
    else:
        await message.answer(
            "Video yuklashda xatolik yuz berdi. Iltimos, to'g'ri Instagram havolasini yuboring. Masalan: https://www.instagram.com/p/xxxxxx/"
        )

# Asosiy bot dasturi
async def main():
    await dp.start_polling(bot)

# Skriptni ishga tushirish
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
