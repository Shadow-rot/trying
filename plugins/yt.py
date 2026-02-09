import os
import requests
from pyrogram import Client, filters

# CHANGE THIS TO YOUR REAL IP
API = "http://103.25.175.231:5000/download"


def download_audio(url):

    try:
        r = requests.post(
            f"{API}/download",
            json={"url": url},
            timeout=600
        )

        data = r.json()

        if data.get("status") == "ok":
            return data["file"]

        print("API Error:", data)

    except Exception as e:
        print("Request Error:", e)

    return None


@Client.on_message(filters.command("yta"))
async def yt_audio(client, msg):

    if len(msg.command) < 2:
        return await msg.reply("❌ Use: /yta <youtube link>")

    url = msg.command[1]

    status = await msg.reply("⏳ Downloading...")

    path = download_audio(url)
    print("FILE PATH:", path)

    print("🎵 FILE:", path)

    if not path or not os.path.exists(path):
        return await status.edit("❌ Download failed")

    await status.edit("⏫ Uploading...")

    await msg.reply_audio(path)

    # Clean up
    try:
        os.remove(path)
    except:
        pass

    await status.delete()