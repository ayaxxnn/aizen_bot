from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime

Base = declarative_base()

class User(Base):
    """User model to store all bot users"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    first_name = Column(String(50))
    last_name = Column(String(50))
    is_premium = Column(Boolean, default=False)
    premium_expiry = Column(DateTime)
    has_redeemed = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    join_date = Column(DateTime, default=datetime.now)
    last_active = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', premium={self.is_premium})>"

class PremiumKey(Base):
    """Premium key model for key generation and tracking"""
    __tablename__ = 'premium_keys'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(32), unique=True)
    days_valid = Column(Integer)
    is_used = Column(Boolean, default=False)
    used_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    used_at = Column(DateTime)

    def __repr__(self):
        return f"<PremiumKey(key='{self.key}', days={self.days_valid}, used={self.is_used})>"

class AdminLog(Base):
    """Log admin actions for audit purposes"""
    __tablename__ = 'admin_logs'
    
    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer)
    action = Column(String(50))
    target_user = Column(Integer)
    details = Column(String(200))
    timestamp = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<AdminLog(admin={self.admin_id}, action='{self.action}')>"

class RedeemLog(Base):
    """Track all redeem requests"""
    __tablename__ = 'redeem_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    is_premium = Column(Boolean)
    timestamp = Column(DateTime, default=datetime.now)
    processed = Column(Boolean, default=False)

    def __repr__(self):
        return f"<RedeemLog(user={self.user_id}, premium={self.is_premium})>"