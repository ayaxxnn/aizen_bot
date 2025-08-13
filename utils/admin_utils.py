from config import Config

class AdminUtils:
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
    
    def notify_admin(self, message):
        for admin_id in Config.ADMIN_IDS:
            try:
                self.bot.send_message(admin_id, f"👨‍💻 Admin Notification:\n{message}")
            except:
                continue
    
    def generate_premium_key(self, days):
        return self.db.generate_premium_key(days)