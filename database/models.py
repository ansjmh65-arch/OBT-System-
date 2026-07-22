# -*- coding: utf-8 -*-
from datetime import datetime
from . import db


class ServerConfigModel(db.Model):
    __tablename__ = "server_configs"

    id = db.Column(db.Integer, primary_key=True)

    # معلومات السيرفر
    guild_id = db.Column(
        db.String(32),
        unique=True,
        nullable=False,
        index=True
    )

    prefix = db.Column(
        db.String(10),
        default="!",
        nullable=False
    )

    language = db.Column(
        db.String(10),
        default="ar",
        nullable=False
    )

    timezone = db.Column(
        db.String(50),
        default="UTC",
        nullable=False
    )

    embed_color = db.Column(
        db.String(20),
        default="#5865F2",
        nullable=False
    )


    # حالة الأنظمة
    security_enabled = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    tickets_enabled = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    clans_enabled = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    economy_enabled = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    levels_enabled = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )


    # إعدادات الترحيب
    welcome_enabled = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    welcome_channel_id = db.Column(
        db.String(32),
        nullable=True
    )

    welcome_message = db.Column(
        db.Text,
        nullable=True
    )


    # إعدادات المغادرة
    goodbye_enabled = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    goodbye_channel_id = db.Column(
        db.String(32),
        nullable=True
    )

    goodbye_message = db.Column(
        db.Text,
        nullable=True
    )


    # الوقت
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
