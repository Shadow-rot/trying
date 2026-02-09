import os
import requests
from pyrogram import Client, filters

# Downloader API
API = "http://127.0.0.1:5000"


def download(url):
    try:
        r = requests.post(
            f"{API}/download",
            json={"url": url},
            timeout=600
        )

        data = r.json()

        if data.get("status") == "ok":
            return data["file"]

    except Exception as e:
        print("API error:", e)

    return None


@Client.on_message(filters.command("yta"))
async def yt_audio(client, msg):

    if len(msg.command) < 2:
        return await msg.reply("Use: /yta <url>")

    url = msg.command[1]

    m = await msg.reply("⏳ Downloading...")

    path = download(url)

    if not path or not os.path.exists(path):
        return await m.edit("❌ Download failed")

    await m.edit("⏫ Uploading...")

    await msg.reply_audio(path)

    try:
        os.remove(path)
    except:
        pass

    await m.delete()