import os
import requests
import subprocess
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

BOT_TOKEN = "520499803:AAEZDxiwsg-O5CO3Vk3QRlvNbds4Bs4sHZc"

VIDEO_DIR = "./videos/"
os.makedirs(VIDEO_DIR, exist_ok=True)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Send me a URL of a video, and I'll compress it for you!")

def handle_url(update: Update, context: CallbackContext):
    url = update.message.text.strip()
    user_id = update.message.chat_id

    if not (url.startswith("http://") or url.startswith("https://")):
        update.message.reply_text("Invalid URL! Please send a valid URL.")
        return

    try:
        response = requests.head(url, allow_redirects=True)
        if response.status_code != 200:
            update.message.reply_text(f"URL is not accessible! Status code: {response.status_code}")
            return
        content_length = response.headers.get('content-length', 'unknown')
        update.message.reply_text(f"URL is valid! File size: {content_length} bytes")
    except Exception as e:
        update.message.reply_text(f"Error validating URL: {e}")
        return

    update.message.reply_text("Downloading video... Please wait.")
    try:
        file_path = os.path.join(VIDEO_DIR, f"{user_id}_video.mp4")
        download_video(url, file_path)

        compressed_path = os.path.join(VIDEO_DIR, f"{user_id}_compressed.mp4")
        compress_video(file_path, compressed_path)

        update.message.reply_text("Video compressed successfully!")
        update.message.reply_document(open(compressed_path, "rb"))
    except Exception as e:
        update.message.reply_text(f"Error processing video: {e}")

def download_video(url: str, file_path: str):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

def compress_video(input_file: str, output_file: str):
    command = ["ffmpeg", "-i", input_file, "-vcodec", "libx264", "-crf", "32", output_file]
    subprocess.run(command, check=True)

def main():
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_url))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
