from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# جدول إعدادات السيرفر والأقسام
class ServerConfig(db.Model):
    __tablename__ = 'server_config'
    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(50), unique=True, nullable=False)
    
    # حالة الأقسام الأساسية (مفعل = True / معطل = False)
    security_enabled = db.Column(db.Boolean, default=True)
    moderation_enabled = db.Column(db.Boolean, default=True)
    tickets_enabled = db.Column(db.Boolean, default=True)
    clans_enabled = db.Column(db.Boolean, default=True)
    economy_enabled = db.Column(db.Boolean, default=True)
    creators_enabled = db.Column(db.Boolean, default=True)
    welcome_enabled = db.Column(db.Boolean, default=True)
    logs_enabled = db.Column(db.Boolean, default=True)
    autoroles_enabled = db.Column(db.Boolean, default=True)
    backup_enabled = db.Column(db.Boolean, default=True)
    
    # إعدادات عامة إضافية للسيرفر
    prefix = db.Column(db.String(10), default="!")
    welcome_channel = db.Column(db.String(50), nullable=True)
    log_channel = db.Column(db.String(50), nullable=True)

# جدول بيانات الأعضاء (الملف الشخصي والنقاط)
class UserProfile(db.Model):
    __tablename__ = 'user_profile'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False)
    balance = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)
    bio = db.Column(db.Text, nullable=True)
    
