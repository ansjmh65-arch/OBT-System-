from datetime import datetime
from .base import db

class TicketSetting(db.Model):
    """إعدادات نظام التذاكر لكل سيرفر."""
    __tablename__ = 'ticket_settings'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    is_enabled = db.Column(db.Boolean, default=True, nullable=False)
    ticket_category_id = db.Column(db.String(32), nullable=True)
    support_role_id = db.Column(db.String(32), nullable=True)
    transcript_channel_id = db.Column(db.String(32), nullable=True)
    max_open_tickets = db.Column(db.Integer, default=1, nullable=False)

    panels = db.relationship('TicketPanel', backref='settings', lazy=True, cascade="all, delete-orphan")


class TicketPanel(db.Model):
    """لوحات فتح التذاكر (Panels)."""
    __tablename__ = 'ticket_panels'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    setting_id = db.Column(db.Integer, db.ForeignKey('ticket_settings.id', ondelete='CASCADE'), nullable=True)
    panel_name = db.Column(db.String(128), nullable=False)
    channel_id = db.Column(db.String(32), nullable=False)
    message_id = db.Column(db.String(32), unique=True, nullable=True, index=True)
    button_label = db.Column(db.String(64), default="فتح تذكرة", nullable=False)
    button_emoji = db.Column(db.String(64), nullable=True)

    tickets = db.relationship('Ticket', backref='panel', lazy=True)


class Ticket(db.Model):
    """التذاكر الفردية المفتوحة."""
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    channel_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    panel_id = db.Column(db.Integer, db.ForeignKey('ticket_panels.id', ondelete='SET NULL'), nullable=True)
    status = db.Column(db.String(32), default="open", nullable=False)
    claimed_by = db.Column(db.String(32), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    closed_at = db.Column(db.DateTime, nullable=True)

    messages = db.relationship('TicketMessage', backref='ticket', lazy=True, cascade="all, delete-orphan")
    transcript = db.relationship('TicketTranscript', backref='ticket', uselist=False, cascade="all, delete-orphan")


class TicketMessage(db.Model):
    """رسائل التذاكر المحفوظة للأرشفة."""
    __tablename__ = 'ticket_messages'

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id', ondelete='CASCADE'), nullable=False, index=True)
    sender_id = db.Column(db.String(32), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class TicketTranscript(db.Model):
    """نسخ محادثات التذاكر النهائية (HTML/Text)."""
    __tablename__ = 'ticket_transcripts'

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    html_content = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
  
