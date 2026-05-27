import os
import subprocess
from pyrogram import Client, filters
from pyrogram.types import Message
from config import BOT_TOKEN, API_ID, API_HASH

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

app = Client(
    "mirror_bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply_text(
        "Send /mirror <direct_link> to download and upload file."
    )

@app.on_message(filters.command("mirror"))
async def mirror(client, message: Message):
    try:
        link = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text("Usage: /mirror direct_link")

    status = await message.reply_text("Downloading file...")

    cmd = [
        "aria2c",
        "-x", "16",
        "-s", "16",
        "-d", DOWNLOAD_DIR,
        link
    ]

    process = subprocess.run(cmd, capture_output=True, text=True)

    if process.returncode != 0:
        return await status.edit("Download failed")

    files = os.listdir(DOWNLOAD_DIR)

    if not files:
        return await status.edit("No file downloaded")

    latest_file = max(
        [os.path.join(DOWNLOAD_DIR, f) for f in files],
        key=os.path.getctime
    )

    await status.edit("Uploading to Telegram...")

    sent = await client.send_document(
        chat_id=message.chat.id,
        document=latest_file,
        caption="Uploaded successfully"
    )

    file_id = sent.document.file_id

    mirror_link = f"https://t.me/{(await client.get_me()).username}?start={file_id}"

    await message.reply_text(
        f"Mirror Link:\n{mirror_link}"
    )

    os.remove(latest_file)

app.run()
