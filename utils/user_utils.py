from config import Config

class UserUtils:
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
    
    def process_redeem(self, message):
        user_id = message.from_user.id
        username = message.from_user.username or "No username"
        self.db.add_user(user_id, username)
        
        # Forward to admin
        for admin_id in Config.ADMIN_IDS:
            try:
                self.bot.forward_message(admin_id, message.chat.id, message.message_id)
                self.bot.send_message(admin_id, f"🔄 Processing redeem for {username} ({user_id})")
            except:
                continue
        
        self.bot.reply_to(message, "✅ Your request has been forwarded to admin")
    
    def notify_all(self, message):
        users = self.db.get_all_users()
        for user_id in users:
            try:
                self.bot.send_message(user_id, message)
            except:
                continue