# ==========================
# Security Models
# ==========================


class SecuritySettingsModel(db.Model):
    __tablename__ = "security_settings"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    guild_id = db.Column(
        db.String(32),
        unique=True,
        nullable=False,
        index=True
    )


    # تفعيل الحمايات
    anti_spam = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    anti_raid = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    anti_link = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    anti_mention = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    anti_webhook = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    anti_bot = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    anti_mass_role = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    anti_channel_delete = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    anti_role_delete = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )


    # إعدادات السبام
    spam_limit = db.Column(
        db.Integer,
        default=5,
        nullable=False
    )

    spam_interval = db.Column(
        db.Integer,
        default=5,
        nullable=False
    )


    # إعدادات الرايد
    raid_join_limit = db.Column(
        db.Integer,
        default=10,
        nullable=False
    )

    raid_time = db.Column(
        db.Integer,
        default=10,
        nullable=False
    )


    # العقوبات
    punishment_type = db.Column(
        db.String(30),
        default="timeout",
        nullable=False
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



class SecurityWhitelistModel(db.Model):
    __tablename__ = "security_whitelist"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    guild_id = db.Column(
        db.String(32),
        nullable=False,
        index=True
    )

    target_id = db.Column(
        db.String(32),
        nullable=False
    )

    target_type = db.Column(
        db.String(20),
        default="user",
        nullable=False
    )

    reason = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )


    __table_args__ = (
        db.UniqueConstraint(
            "guild_id",
            "target_id",
            name="security_whitelist_unique"
        ),
    )



class SecurityLogModel(db.Model):
    __tablename__ = "security_logs"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    guild_id = db.Column(
        db.String(32),
        nullable=False,
        index=True
    )

    user_id = db.Column(
        db.String(32),
        nullable=True
    )

    action = db.Column(
        db.String(100),
        nullable=False
    )

    reason = db.Column(
        db.Text,
        nullable=True
    )

    details = db.Column(
        db.Text,
        nullable=True
    )

    severity = db.Column(
        db.String(20),
        default="medium",
        nullable=False
    )

    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )



class AutoModRuleModel(db.Model):
    __tablename__ = "automod_rules"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    guild_id = db.Column(
        db.String(32),
        nullable=False,
        index=True
    )

    rule_type = db.Column(
        db.String(50),
        nullable=False
    )

    value = db.Column(
        db.Text,
        nullable=False
    )

    enabled = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    action = db.Column(
        db.String(30),
        default="delete",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
