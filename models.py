from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ServerConfig(db.Model):
    __tablename__ = 'server_config'
    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(50), unique=True, nullable=False, default="default_guild")
    
    # حالات الأقسام الأساسية
    security_enabled = db.Column(db.Boolean, default=True)
    moderation_enabled = db.Column(db.Boolean, default=True)
    tickets_enabled = db.Column(db.Boolean, default=True)
    economy_enabled = db.Column(db.Boolean, default=True)
    welcome_enabled = db.Column(db.Boolean, default=True)
    
