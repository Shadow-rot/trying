import os
import requests
from pyrogram import Client, filters

# Your downloader API
API = "http://127.0.0.1:5000"


def download(url, mode="video"):
    r = requests.post(
        f"{API}/download",
        json={"url": url, "mode": mode},
        timeout=600
    )

    data = r.json()

    if data.get("status") == "ok":
        return data["file"]

    return None


@Client.on_message(filters.command("yt"))
async def yt_video(client, msg):

    if len(msg.command) < 2:
        return await msg.reply("Use: /yt <url>")

    url = msg.command[1]

    m = await msg.reply("⏳ Downloading...")

    path = download(url, "video")

    if not path or not os.path.exists(path):
        return await m.edit("❌ Failed")

    await m.edit("⏫ Uploading...")

    await msg.reply_video(path)

    os.remove(path)
    await m.delete()


@Client.on_message(filters.command("yta"))
async def yt_audio(client, msg):

    if len(msg.command) < 2:
        return await msg.reply("Use: /yta <url>")

    url = msg.command[1]

    m = await msg.reply("⏳ Downloading...")

    path = download(url, "audio")

    if not path or not os.path.exists(path):
        return await m.edit("❌ Failed")

    await m.edit("⏫ Uploading...")

    await msg.reply_audio(path)

    os.remove(path)
    await m.delete()