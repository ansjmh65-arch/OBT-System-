import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key_change_me')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///obt_system.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN', '')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
  
