"""
Downloader Plugin
Download media from various sources (YouTube, direct URLs)
"""
import os
import time
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from config import config
from utils.decorators import log_errors, rate_limit
from utils.helpers import extract_args, is_url, clean_filename, get_readable_bytes, progress_callback

# Check if yt-dlp is available
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False


@Client.on_message(filters.command(["yt", "youtube"], prefixes=config.COMMAND_PREFIX))
@rate_limit(seconds=10)
@log_errors
async def youtube_download(client: Client, message: Message):
    """Download YouTube videos"""
    url = extract_args(message)
    
    if not url:
        await message.reply_text(
            f"❌ **Usage:** `{config.COMMAND_PREFIX}yt <youtube_url>`\n\n"
            f"**Example:** `{config.COMMAND_PREFIX}yt https://youtube.com/watch?v=...`"
        )
        return
    
    if not YT_DLP_AVAILABLE:
        await message.reply_text(
            "❌ yt-dlp is not installed.\n"
            "Install with: `pip install yt-dlp`"
        )
        return
    
    if not is_url(url) or 'youtube.com' not in url and 'youtu.be' not in url:
        await message.reply_text("❌ Please provide a valid YouTube URL")
        return
    
    status_msg = await message.reply_text("⏳ **Fetching video information...**")
    
    try:
        # Get video info
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            uploader = info.get('uploader', 'Unknown')
            
            # Check file size
            filesize = info.get('filesize') or info.get('filesize_approx', 0)
            
            if filesize > 50 * 1024 * 1024:  # 50MB limit
                await status_msg.edit_text(
                    f"❌ **File too large!**\n\n"
                    f"📹 **Title:** {title}\n"
                    f"📦 **Size:** {get_readable_bytes(filesize)}\n\n"
                    f"Maximum file size: 50MB"
                )
                return
        
        await status_msg.edit_text("⏬ **Downloading video...**")
        
        # Download video
        output_dir = "downloads"
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"{clean_filename(title)}.mp4")
        
        ydl_opts = {
            'format': 'best[filesize<50M]',
            'outtmpl': output_file,
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        if not os.path.exists(output_file):
            await status_msg.edit_text("❌ Download failed")
            return
        
        # Upload video
        await status_msg.edit_text("⏫ **Uploading video...**")
        
        caption = f"📹 **{title}**\n👤 **Uploader:** {uploader}"
        
        start_time = time.time()
        await client.send_video(
            message.chat.id,
            video=output_file,
            caption=caption,
            progress=progress_callback,
            progress_args=(status_msg, start_time, "Uploading")
        )
        
        await status_msg.delete()
        
        # Clean up
        try:
            os.remove(output_file)
        except:
            pass
            
    except Exception as e:
        await status_msg.edit_text(f"❌ **Error:** {str(e)}")


@Client.on_message(filters.command(["ytaudio", "yta"], prefixes=config.COMMAND_PREFIX))
@rate_limit(seconds=10)
@log_errors
async def youtube_audio_download(client: Client, message: Message):
    """Download YouTube audio"""
    url = extract_args(message)
    
    if not url:
        await message.reply_text(
            f"❌ **Usage:** `{config.COMMAND_PREFIX}ytaudio <youtube_url>`\n\n"
            f"**Example:** `{config.COMMAND_PREFIX}ytaudio https://youtube.com/watch?v=...`"
        )
        return
    
    if not YT_DLP_AVAILABLE:
        await message.reply_text(
            "❌ yt-dlp is not installed.\n"
            "Install with: `pip install yt-dlp`"
        )
        return
    
    if not is_url(url) or 'youtube.com' not in url and 'youtu.be' not in url:
        await message.reply_text("❌ Please provide a valid YouTube URL")
        return
    
    status_msg = await message.reply_text("⏳ **Fetching audio information...**")
    
    try:
        # Get video info
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            title = info.get('title', 'Unknown')
            uploader = info.get('uploader', 'Unknown')
        
        await status_msg.edit_text("⏬ **Downloading audio...**")
        
        # Download audio
        output_dir = "downloads"
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"{clean_filename(title)}.mp3")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_file,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Upload audio
        await status_msg.edit_text("⏫ **Uploading audio...**")
        
        caption = f"🎵 **{title}**\n👤 **Uploader:** {uploader}"
        
        start_time = time.time()
        await client.send_audio(
            message.chat.id,
            audio=output_file,
            caption=caption,
            title=title,
            performer=uploader,
            progress=progress_callback,
            progress_args=(status_msg, start_time, "Uploading")
        )
        
        await status_msg.delete()
        
        # Clean up
        try:
            os.remove(output_file)
        except:
            pass
            
    except Exception as e:
        await status_msg.edit_text(f"❌ **Error:** {str(e)}")


@Client.on_message(filters.command("download", prefixes=config.COMMAND_PREFIX))
@rate_limit(seconds=10)
@log_errors
async def download_file(client: Client, message: Message):
    """Download file from direct URL"""
    url = extract_args(message)
    
    if not url:
        await message.reply_text(
            f"❌ **Usage:** `{config.COMMAND_PREFIX}download <url>`\n\n"
            f"**Example:** `{config.COMMAND_PREFIX}download https://example.com/file.pdf`"
        )
        return
    
    if not is_url(url):
        await message.reply_text("❌ Please provide a valid URL")
        return
    
    status_msg = await message.reply_text("⏬ **Downloading file...**")
    
    try:
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await status_msg.edit_text(f"❌ Failed to download file (HTTP {resp.status})")
                    return
                
                # Get filename from URL or Content-Disposition
                filename = url.split('/')[-1] or 'downloaded_file'
                filename = clean_filename(filename)
                
                # Create downloads directory
                output_dir = "downloads"
                os.makedirs(output_dir, exist_ok=True)
                
                output_file = os.path.join(output_dir, filename)
                
                # Download file
                with open(output_file, 'wb') as f:
                    f.write(await resp.read())
        
        # Upload file
        await status_msg.edit_text("⏫ **Uploading file...**")
        
        start_time = time.time()
        await client.send_document(
            message.chat.id,
            document=output_file,
            caption=f"📄 **File:** {filename}",
            progress=progress_callback,
            progress_args=(status_msg, start_time, "Uploading")
        )
        
        await status_msg.delete()
        
        # Clean up
        try:
            os.remove(output_file)
        except:
            pass
            
    except Exception as e:
        await status_msg.edit_text(f"❌ **Error:** {str(e)}")
