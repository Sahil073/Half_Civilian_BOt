from telegram.ext import Application, CommandHandler, MessageHandler, filters
import google.generativeai as genai
import logging
import asyncio
import httpx
import os
# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
TOKEN = os.getenv("TOKEN")

# Optional: Configure proxy as a URL string
PROXY_URL = "http://your-proxy:port"  # Replace with your actual proxy (e.g., "http://proxy.example.com:8080")

# Create the Application instance with proxy (if needed)
if PROXY_URL and PROXY_URL != "http://your-proxy:port":  # Check if proxy is set
    application = Application.builder().token(TOKEN).proxy(PROXY_URL).build()
else:
    application = Application.builder().token(TOKEN).build()

# Start command
async def start(update, context):
    await update.message.reply_text("Hello! Welcome to HalfCivilian!")

# Help command
async def help_command(update, context):
    await update.message.reply_text(
        """
/start --> Welcome
/channels --> For navigating to the channel which will make your defence journey easy
/Ai_Assers --> Get assistance from AI Assers, your GTO, IO, and Psych guide
/listmodels --> List available Gemini models
        """
    )

# Channels command
async def channels(update, context):
    await update.message.reply_text(
        "Here are our channels:\n"
        "- Channel 1: https://t.me/incrediblejourney14\n"
        "- Channel 2: https://t.me/halfcivilian07\n"
        "- Channel 3: https://t.me/ssbcorps\n"
        "Join us for updates!"
    )

# Ai_Assers command (using Gemini API) with free key handling
async def ai_assers(update, context):
    if context.args:
        user_query = " ".join(context.args)
        try:
            model = genai.GenerativeModel('gemini-1.5-pro-latest')
            response = model.generate_content(user_query)
            logger.info(f"Gemini response: {response.text}")
            await update.message.reply_text(response.text)
        except google.generativeai.types.generation_types.StoppedGeneration as sg:
            await update.message.reply_text("Generation stopped: Likely quota limit reached. Try again later.")
            logger.error(f"StoppedGeneration: {sg}")
        except Exception as e:
            error_msg = f"Error with Gemini API: {str(e)}"
            await update.message.reply_text(error_msg)
            logger.error(error_msg)
    else:
        await update.message.reply_text("Please provide a question after /Ai_Assers, e.g., /Ai_Assers What is the capital of France?")

# List models command
async def listmodels(update, context):
    try:
        models = genai.list_models()
        model_list = "\n".join([f"- {model.name}: {model.description}" for model in models])
        await update.message.reply_text(f"Available Gemini models:\n{model_list}")
    except Exception as e:
        await update.message.reply_text(f"Error listing models: {str(e)}")
        logger.error(f"Error listing models: {str(e)}")

# Echo or handle unknown commands
async def echo(update, context):
    await update.message.reply_text("Unknown command! Use /help to see available commands.")

# Error handler with retry logic
async def error(update, context):
    logger.error(f"Update {update} caused error {context.error}")
    if isinstance(context.error, httpx.ConnectError):
        logger.warning("Connection error detected. Attempting to retry...")
        await asyncio.sleep(5)
        await application.initialize()
        await application.run_polling()
    else:
        logger.error("Unexpected error occurred.")

# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("channels", channels))
application.add_handler(CommandHandler("Ai_Assers", ai_assers))
application.add_handler(CommandHandler("listmodels", listmodels))
application.add_handler(MessageHandler(filters.COMMAND, echo))
application.add_error_handler(error)

# Start the bot with try-except
if __name__ == '__main__':
    try:
        application.run_polling()
        print("Bot is running...")
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")