import os

class Config:
    TOKEN = os.getenv('TOKEN', 'YOUR_BOT_TOKEN')
    ADMIN_IDS = [int(id) for id in os.getenv('ADMIN_IDS', 'YOUR_USER_ID').split(',')]
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///database/aizen_bot.db')