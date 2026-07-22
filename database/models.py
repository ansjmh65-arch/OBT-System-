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


    # تفعيل الأنظمة
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


    # الترحيب
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


    # المغادرة
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



class DashboardPermissionModel(db.Model):
    __tablename__ = "dashboard_permissions"

    id = db.Column(db.Integer, primary_key=True)

    guild_id = db.Column(
        db.String(32),
        nullable=False,
        index=True
    )

    user_id = db.Column(
        db.String(32),
        nullable=False,
        index=True
    )


    # صلاحيات لوحة التحكم
    can_view_dashboard = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    can_manage_settings = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    can_manage_security = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    can_manage_tickets = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    can_manage_clans = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    can_view_logs = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )


    __table_args__ = (
        db.UniqueConstraint(
            "guild_id",
            "user_id",
            name="guild_user_dashboard_permission_uc"
        ),
    )



class AutoRoleModel(db.Model):
    __tablename__ = "auto_roles"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    guild_id = db.Column(
        db.String(32),
        nullable=False,
        index=True
    )

    role_id = db.Column(
        db.String(32),
        nullable=False
    )

    enabled = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
