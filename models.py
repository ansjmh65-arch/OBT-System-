from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ServerConfig(db.Model):
    __tablename__ = 'server_config'
    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(50), unique=True, nullable=False, default="default_guild")
    
    # حالة الأقسام الـ 14 (تفعيل / تعطيل)
    security_enabled = db.Column(db.Boolean, default=True)
    moderation_enabled = db.Column(db.Boolean, default=True)
    tickets_enabled = db.Column(db.Boolean, default=True)
    clans_enabled = db.Column(db.Boolean, default=True)
    economy_enabled = db.Column(db.Boolean, default=True)
    content_creators_enabled = db.Column(db.Boolean, default=True)
    welcome_enabled = db.Column(db.Boolean, default=True)
    logs_enabled = db.Column(db.Boolean, default=True)
    auto_roles_enabled = db.Column(db.Boolean, default=True)
    backup_enabled = db.Column(db.Boolean, default=True)
    server_settings_enabled = db.Column(db.Boolean, default=True)
    commands_management_enabled = db.Column(db.Boolean, default=True)
    profile_enabled = db.Column(db.Boolean, default=True)
    home_enabled = db.Column(db.Boolean, default=True)

    # حقول إضافية للإعدادات
    welcome_message = db.Column(db.Text, nullable=True)
    welcome_channel = db.Column(db.String(50), nullable=True)
    logs_channel = db.Column(db.String(50), nullable=True)
    
