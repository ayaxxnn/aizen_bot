import os
os.system("pip install python-telegram-bot==13.7 --user")
from flask import Flask
import telebot
import threading
import time
from config import Config
from database.db_handler import DatabaseHandler
from utils.admin_utils import AdminUtils
from utils.user_utils import UserUtils

app = Flask(__name__)
bot = telebot.TeleBot(Config.TOKEN)
db = DatabaseHandler()
admin_utils = AdminUtils(bot, db)
user_utils = UserUtils(bot, db)

# Global variable for free access status
free_access = False

@app.route('/')
def home():
    return "Aizen Bot is running!"

# Start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_msg = """Welcome To Aizen Bot ⚡️
Please Use /redeem Command For Get Prime video 🧑‍💻
For Premium use /premium"""
    bot.reply_to(message, welcome_msg)

# Redeem command
@bot.message_handler(commands=['redeem'])
def handle_redeem(message):
    user_id = message.from_user.id
    
    if db.is_user_banned(user_id):
        bot.reply_to(message, "🚫 You are banned from using this bot.")
        return
    
    if free_access:
        user_utils.process_redeem(message)
    else:
        if db.is_premium_user(user_id):
            user_utils.process_redeem(message)
        else:
            if db.has_user_redeemed(user_id):
                bot.reply_to(message, "🔑 Please Purchase Premium Key For Use")
            else:
                user_utils.process_redeem(message)
                db.mark_user_redeemed(user_id)
                admin_utils.notify_admin(f"New redeem from free user: {user_id}")

# Premium activation
@bot.message_handler(commands=['premium'])
def handle_premium(message):
    bot.reply_to(message, "🔑 Please enter your premium key:")
    bot.register_next_step_handler(message, process_premium_key)

def process_premium_key(message):
    user_id = message.from_user.id
    key = message.text.strip()
    
    if db.validate_premium_key(key):
        db.activate_premium(user_id, key)
        bot.reply_to(message, "⚡️ Premium Activated Successfully!")
        admin_utils.notify_admin(f"User {user_id} activated premium")
    else:
        bot.reply_to(message, "❌ Invalid premium key. Please try again.")

# Admin commands
@bot.message_handler(commands=['broadcast'])
def handle_broadcast(message):
    if not db.is_admin(message.from_user.id):
        return
    
    bot.reply_to(message, "📢 Send the broadcast message:")
    bot.register_next_step_handler(message, process_broadcast)

def process_broadcast(message):
    if not db.is_admin(message.from_user.id):
        return
    
    users = db.get_all_users()
    for user in users:
        try:
            bot.send_message(user, message.text)
        except:
            continue

@bot.message_handler(commands=['genk'])
def handle_gen_key(message):
    if not db.is_admin(message.from_user.id):
        return
    
    try:
        days = int(message.text.split()[1])
        key = admin_utils.generate_premium_key(days)
        bot.reply_to(message, f"🔑 Generated Key: {key}\n⏳ Valid for {days} days")
    except:
        bot.reply_to(message, "❌ Usage: /genk <days>")

@bot.message_handler(commands=['ban'])
def handle_ban(message):
    if not db.is_admin(message.from_user.id):
        return
    
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        db.ban_user(user_id)
        bot.reply_to(message, f"🚫 User {user_id} banned")
    else:
        bot.reply_to(message, "⚠️ Reply to a user's message to ban")

@bot.message_handler(commands=['unban'])
def handle_unban(message):
    if not db.is_admin(message.from_user.id):
        return
    
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        db.unban_user(user_id)
        bot.reply_to(message, f"✅ User {user_id} unbanned")
    else:
        bot.reply_to(message, "⚠️ Reply to a user's message to unban")

@bot.message_handler(commands=['on', 'freeaccess'])
def enable_free_access(message):
    global free_access
    if not db.is_admin(message.from_user.id):
        return
    
    free_access = True
    bot.reply_to(message, "⚡️ Free access enabled")
    user_utils.notify_all("🎉 Free Service Activated! Unlimited redeems now available!")

@bot.message_handler(commands=['off', 'banaccess'])
def disable_free_access(message):
    global free_access
    if not db.is_admin(message.from_user.id):
        return
    
    free_access = False
    bot.reply_to(message, "♻️ Free access disabled")
    user_utils.notify_all("🔒 Free Service Deactivated. Premium users only.")

def polling():
    while True:
        try:
            bot.polling(none_stop=True, interval=2)
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(5)

if __name__ == '__main__':
    # Start polling in background
    poll_thread = threading.Thread(target=polling)
    poll_thread.daemon = True
    poll_thread.start()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000)
