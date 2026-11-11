import os
import re
import telebot
import yt_dlp
import imageio_ffmpeg

# ВСТАВЬ СЮДА СВОЙ ТОКЕН ОТ BOTFATHER ВНУТРИ КАВЫЧЕК
BOT_TOKEN = ""

bot = telebot.TeleBot(BOT_TOKEN)
ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

if not os.path.exists("downloads"):
    os.makedirs("downloads")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        "Привет! Я бот для скачивания видео.\n"
        "Просто отправь мне ссылку на YouTube Shorts, VK Видео (VK Клипы), Rutube или Pinterest, и я пришлю тебе готовый файл!"
    )

@bot.message_handler(content_types=['text'])
def handle_url(message):
    url = message.text.strip()

    if not re.match(r'^https?://', url):
        bot.reply_to(message, "❌ Ошибка: Неверный формат ссылки. Отправь ссылку, начинающуюся с http:// или https://")
        return

    status_msg = bot.reply_to(message, "⏳ Скачиваю видео, подожди немного...")
    file_path = f"downloads/video_{message.chat.id}_{message.message_id}.mp4"

    # Настройки для yt-dlp с защитой от файлов > 50 МБ
    ydl_opts = {
        'format': 'best[ext=mp4][filesize<50M]/bestvideo[ext=mp4][filesize<45M]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'outtmpl': file_path,
        'ffmpeg_location': ffmpeg_path,
        'max_filesize': 50 * 1024 * 1024,
        'noplaylist': True,
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path) / (1024 * 1024)
            if file_size > 50:
                bot.edit_message_text("❌ Ошибка: Файл слишком большой (более 50 МБ — ограничение Telegram).", message.chat.id, status_msg.message_id)
                return

            with open(file_path, 'rb') as video:
                bot.send_video(message.chat.id, video, caption="✅ Готово!")
            
            bot.delete_message(message.chat.id, status_msg.message_id)
        else:
            bot.edit_message_text("❌ Видео превышает лимит 50 МБ или недоступно для скачивания.", message.chat.id, status_msg.message_id)

    except Exception as e:
        bot.edit_message_text("❌ Произошла ошибка при скачивании.\nПроверь ссылку (видео должно быть открытым и до 50 МБ) или попробуй другое видео.", message.chat.id, status_msg.message_id)
        print(f"Ошибка: {e}")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

print("Бот успешно запущен и ждет сообщений...")
bot.infinity_polling()
