from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import secrets
from config import Config

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    is_premium = Column(Boolean, default=False)
    premium_expiry = Column(DateTime)
    has_redeemed = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)

class PremiumKey(Base):
    __tablename__ = 'premium_keys'
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True)
    days_valid = Column(Integer)
    is_used = Column(Boolean, default=False)
    used_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)

class DatabaseHandler:
    def __init__(self):
        self.engine = create_engine(Config.DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def is_admin(self, user_id):
        return user_id in Config.ADMIN_IDS
    
    def add_user(self, user_id, username):
        session = self.Session()
        if not session.query(User).get(user_id):
            session.add(User(id=user_id, username=username))
            session.commit()
        session.close()
    
    def is_premium_user(self, user_id):
        session = self.Session()
        user = session.query(User).get(user_id)
        if user and user.is_premium and (not user.premium_expiry or user.premium_expiry > datetime.now()):
            session.close()
            return True
        session.close()
        return False
    
    def has_user_redeemed(self, user_id):
        session = self.Session()
        user = session.query(User).get(user_id)
        redeemed = user.has_redeemed if user else False
        session.close()
        return redeemed
    
    def mark_user_redeemed(self, user_id):
        session = self.Session()
        user = session.query(User).get(user_id)
        if user:
            user.has_redeemed = True
            session.commit()
        session.close()
    
    def ban_user(self, user_id):
        session = self.Session()
        user = session.query(User).get(user_id)
        if user:
            user.is_banned = True
            session.commit()
        session.close()
    
    def unban_user(self, user_id):
        session = self.Session()
        user = session.query(User).get(user_id)
        if user:
            user.is_banned = False
            session.commit()
        session.close()
    
    def is_user_banned(self, user_id):
        session = self.Session()
        user = session.query(User).get(user_id)
        banned = user.is_banned if user else False
        session.close()
        return banned
    
    def generate_premium_key(self, days):
        session = self.Session()
        key = secrets.token_urlsafe(12)
        new_key = PremiumKey(key=key, days_valid=days)
        session.add(new_key)
        session.commit()
        session.close()
        return key
    
    def validate_premium_key(self, key):
        session = self.Session()
        premium_key = session.query(PremiumKey).filter_by(key=key, is_used=False).first()
        if premium_key:
            premium_key.is_used = True
            session.commit()
            session.close()
            return True
        session.close()
        return False
    
    def activate_premium(self, user_id, key):
        session = self.Session()
        premium_key = session.query(PremiumKey).filter_by(key=key).first()
        if premium_key:
            user = session.query(User).get(user_id)
            if not user:
                user = User(id=user_id)
                session.add(user)
            
            user.is_premium = True
            user.premium_expiry = datetime.now() + timedelta(days=premium_key.days_valid)
            user.has_redeemed = False
            premium_key.used_by = user_id
            session.commit()
        session.close()
    
    def get_all_users(self):
        session = self.Session()
        users = session.query(User).all()
        user_ids = [user.id for user in users]
        session.close()
        return user_ids