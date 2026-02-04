"""
Utility Commands Plugin
Calculator, weather, translation, and other utility commands
"""
import re
from pyrogram import Client, filters
from pyrogram.types import Message
from config import config
from utils.decorators import log_errors, rate_limit
from utils.helpers import extract_args

try:
    import sympy
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False

try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False


@Client.on_message(filters.command("calc", prefixes=config.COMMAND_PREFIX))
@rate_limit(seconds=3)
@log_errors
async def calculate(client: Client, message: Message):
    """Calculate mathematical expressions"""
    expression = extract_args(message)
    
    if not expression:
        await message.reply_text(
            f"❌ **Usage:** `{config.COMMAND_PREFIX}calc <expression>`\n\n"
            f"**Examples:**\n"
            f"• `{config.COMMAND_PREFIX}calc 2 + 2`\n"
            f"• `{config.COMMAND_PREFIX}calc sqrt(144)`\n"
            f"• `{config.COMMAND_PREFIX}calc sin(pi/2)`\n"
            f"• `{config.COMMAND_PREFIX}calc (10 * 5) / 2`"
        )
        return
    
    if not SYMPY_AVAILABLE:
        # Fallback to eval (limited)
        try:
            # Security: Only allow safe characters
            if re.search(r'[^0-9+\-*/().\s]', expression):
                await message.reply_text("❌ Only basic arithmetic operations are allowed")
                return
            
            result = eval(expression)
            await message.reply_text(
                f"🧮 **Calculator**\n\n"
                f"**Expression:** `{expression}`\n"
                f"**Result:** `{result}`"
            )
        except Exception as e:
            await message.reply_text(f"❌ **Error:** {str(e)}")
    else:
        # Use sympy for advanced math
        try:
            result = sympy.sympify(expression)
            evaluated = result.evalf()
            
            await message.reply_text(
                f"🧮 **Calculator**\n\n"
                f"**Expression:** `{expression}`\n"
                f"**Result:** `{evaluated}`"
            )
        except Exception as e:
            await message.reply_text(f"❌ **Error:** Invalid expression")


@Client.on_message(filters.command("weather", prefixes=config.COMMAND_PREFIX))
@rate_limit(seconds=5)
@log_errors
async def weather(client: Client, message: Message):
    """Get weather information for a city"""
    city = extract_args(message)
    
    if not city:
        await message.reply_text(
            f"❌ **Usage:** `{config.COMMAND_PREFIX}weather <city>`\n\n"
            f"**Example:** `{config.COMMAND_PREFIX}weather London`"
        )
        return
    
    if not config.WEATHER_API_KEY:
        await message.reply_text(
            "❌ Weather API key not configured.\n\n"
            "Get a free API key from https://openweathermap.org/api"
        )
        return
    
    try:
        import aiohttp
        
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": config.WEATHER_API_KEY,
            "units": "metric"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    weather_text = (
                        f"🌤️ **Weather in {data['name']}, {data['sys']['country']}**\n\n"
                        f"🌡️ **Temperature:** {data['main']['temp']}°C\n"
                        f"🤔 **Feels Like:** {data['main']['feels_like']}°C\n"
                        f"📊 **Condition:** {data['weather'][0]['description'].title()}\n"
                        f"💧 **Humidity:** {data['main']['humidity']}%\n"
                        f"💨 **Wind Speed:** {data['wind']['speed']} m/s\n"
                        f"☁️ **Cloudiness:** {data['clouds']['all']}%\n"
                        f"🔽 **Min Temp:** {data['main']['temp_min']}°C\n"
                        f"🔼 **Max Temp:** {data['main']['temp_max']}°C"
                    )
                    
                    await message.reply_text(weather_text)
                elif resp.status == 404:
                    await message.reply_text(f"❌ City '{city}' not found")
                else:
                    await message.reply_text("❌ Failed to fetch weather data")
                    
    except Exception as e:
        await message.reply_text(f"❌ **Error:** {str(e)}")


@Client.on_message(filters.command(["translate", "tr"], prefixes=config.COMMAND_PREFIX))
@rate_limit(seconds=3)
@log_errors
async def translate_text(client: Client, message: Message):
    """Translate text to English"""
    text = extract_args(message)
    
    # Check if replying to a message
    if not text and message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption
    
    if not text:
        await message.reply_text(
            f"❌ **Usage:** `{config.COMMAND_PREFIX}translate <text>`\n"
            f"Or reply to a message with `{config.COMMAND_PREFIX}translate`"
        )
        return
    
    if not TRANSLATOR_AVAILABLE:
        await message.reply_text(
            "❌ Translation module not available.\n"
            "Install with: `pip install deep-translator`"
        )
        return
    
    try:
        # Detect language and translate to English
        translator = GoogleTranslator(source='auto', target='en')
        translated = translator.translate(text)
        
        # Try to detect source language
        from deep_translator import single_detection
        try:
            source_lang = single_detection(text, api_key='free')
        except:
            source_lang = "Unknown"
        
        await message.reply_text(
            f"🌐 **Translation**\n\n"
            f"**From:** {source_lang}\n"
            f"**To:** English\n\n"
            f"**Original:**\n{text[:500]}\n\n"
            f"**Translated:**\n{translated[:500]}"
        )
    except Exception as e:
        await message.reply_text(f"❌ **Translation Error:** {str(e)}")


@Client.on_message(filters.command("echo", prefixes=config.COMMAND_PREFIX))
@log_errors
async def echo_command(client: Client, message: Message):
    """Echo back the message"""
    text = extract_args(message)
    
    if not text:
        await message.reply_text(f"❌ **Usage:** `{config.COMMAND_PREFIX}echo <text>`")
        return
    
    await message.reply_text(text)


@Client.on_message(filters.command("reverse", prefixes=config.COMMAND_PREFIX))
@log_errors
async def reverse_text(client: Client, message: Message):
    """Reverse text"""
    text = extract_args(message)
    
    if not text:
        await message.reply_text(f"❌ **Usage:** `{config.COMMAND_PREFIX}reverse <text>`")
        return
    
    reversed_text = text[::-1]
    await message.reply_text(
        f"🔄 **Reversed Text:**\n\n"
        f"**Original:** {text}\n"
        f"**Reversed:** {reversed_text}"
    )


@Client.on_message(filters.command("uppercase", prefixes=config.COMMAND_PREFIX))
@log_errors
async def uppercase_text(client: Client, message: Message):
    """Convert text to uppercase"""
    text = extract_args(message)
    
    if not text and message.reply_to_message:
        text = message.reply_to_message.text
    
    if not text:
        await message.reply_text(f"❌ **Usage:** `{config.COMMAND_PREFIX}uppercase <text>`")
        return
    
    await message.reply_text(text.upper())


@Client.on_message(filters.command("lowercase", prefixes=config.COMMAND_PREFIX))
@log_errors
async def lowercase_text(client: Client, message: Message):
    """Convert text to lowercase"""
    text = extract_args(message)
    
    if not text and message.reply_to_message:
        text = message.reply_to_message.text
    
    if not text:
        await message.reply_text(f"❌ **Usage:** `{config.COMMAND_PREFIX}lowercase <text>`")
        return
    
    await message.reply_text(text.lower())
