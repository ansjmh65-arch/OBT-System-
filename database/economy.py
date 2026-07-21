from datetime import datetime
from .base import db

class EconomySetting(db.Model):
    """إعدادات الاقتصاد للسيرفر."""
    __tablename__ = 'economy_settings'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    currency_name = db.Column(db.String(64), default="Credit", nullable=False)
    currency_symbol = db.Column(db.String(16), default="$", nullable=False)
    start_balance = db.Column(db.Integer, default=100, nullable=False)
    daily_reward = db.Column(db.Integer, default=500, nullable=False)


class EconomyUser(db.Model):
    """أرصدة المستخدمين في الاقتصاد."""
    __tablename__ = 'economy_users'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    balance = db.Column(db.Integer, default=100, nullable=False)
    bank_balance = db.Column(db.Integer, default=0, nullable=False)
    last_daily = db.Column(db.DateTime, nullable=True)

    __table_args__ = (db.UniqueConstraint('guild_id', 'user_id', name='_guild_economy_user_uc'),)


class Item(db.Model):
    """عناصر المتجر (Shop Items)."""
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, default=-1, nullable=False)  # -1 تعني غير محدود

    inventories = db.relationship('Inventory', backref='item', lazy=True, cascade="all, delete-orphan")


class Inventory(db.Model):
    """حقيبة المستخدمين والعناصر التي يمتلكونها."""
    __tablename__ = 'inventories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id', ondelete='CASCADE'), nullable=False, index=True)
    quantity = db.Column(db.Integer, default=1, nullable=False)


class Transaction(db.Model):
    """سجل المعاملات المالية وتحويلات الأموال."""
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    sender_id = db.Column(db.String(32), nullable=False, index=True)
    receiver_id = db.Column(db.String(32), nullable=True, index=True)
    amount = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(32), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
  
