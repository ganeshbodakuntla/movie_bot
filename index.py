from telegram import Bot, Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler, Dispatcher
import os
import requests
from io import BytesIO

TOKEN = os.getenv("TOKEN")
URL = "https://movie-bot-vert.vercel.app"
bot = Bot(TOKEN)

# This will handle webhook and incoming requests
def handle_update(request):
    """Handles the incoming request from Vercel."""
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        dispatcher = Dispatcher(bot, None, use_context=True)
        dispatcher.add_handler(CommandHandler('start', welcome))
        dispatcher.add_handler(MessageHandler(Filters.text, find_movie))
        dispatcher.add_handler(CallbackQueryHandler(movie_result))
        dispatcher.process_update(update)
        return 'ok'
    elif request.method == "GET":
        return set_webhook(request)
    else:
        return "Method not allowed", 405


# Webhook setup for Vercel
def set_webhook(request):
    """Sets the webhook for the Telegram bot."""
    s = bot.setWebhook(f'{URL}/{TOKEN}')
    if s:
        return "Webhook setup ok"
    else:
        return "Webhook setup failed"


# Welcome function
def welcome(update, context):
    update.message.reply_text(f"Hello {update.message.from_user.first_name}, Welcome to AI Movies.\n"
                              f"🔥 Download Your Favourite Movies For 💯 Free And 🍿 Enjoy it.")
    update.message.reply_text("👇 Enter Movie Name 👇")


# Movie search and handler
def find_movie(update, context):
    search_results = update.message.reply_text("Processing...")
    query = update.message.text
    movies_list = search_movies(query)
    if movies_list:
        keyboards = []
        for movie in movies_list:
            keyboard = InlineKeyboardButton(movie["title"], callback_data=movie["id"])
            keyboards.append([keyboard])
        reply_markup = InlineKeyboardMarkup(keyboards)
        search_results.edit_text('Search Results...', reply_markup=reply_markup)
    else:
        search_results.edit_text('Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Movie Name.')


def movie_result(update, context):
    query = update.callback_query
    s = get_movie(query.data)
    response = requests.get(s["img"])
    img = BytesIO(response.content)
    query.message.reply_photo(photo=img, caption=f"🎥 {s['title']}")
    link = ""
    links = s["links"]
    for i in links:
        link += "🎬" + i + "\n" + links[i] + "\n\n"
    caption = f"⚡ Fast Download Links :-\n\n{link}"
    if len(caption) > 4095:
        for x in range(0, len(caption), 4095):
            query.message.reply_text(text=caption[x:x + 4095])
    else:
        query.message.reply_text(text=caption)


# Main Vercel entry point function
def handler(request):
    """Main entry point for Vercel serverless function."""
    return handle_update(request)
