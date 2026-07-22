# -*- coding: utf-8 -*-

import time
from collections import defaultdict

import discord
from discord.ext import commands

from models import db, ProtectionSettings, SecurityLog


class ProtectionCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.spam_cache = defaultdict(list)
        self.raid_cache = defaultdict(list)


    # ==========================
    # جلب إعدادات الحماية
    # ==========================

    def get_settings(self, guild_id):

        settings = ProtectionSettings.query.filter_by(
            guild_id=str(guild_id)
        ).first()

        if not settings:

            settings = ProtectionSettings(
                guild_id=str(guild_id)
            )

            db.session.add(settings)
            db.session.commit()

        return settings


    # ==========================
    # تسجيل اللوقات
    # ==========================

    def create_log(
        self,
        guild_id,
        user_id,
        action,
        reason
    ):

        try:

            log = SecurityLog(

                guild_id=str(guild_id),

                user_id=str(user_id)
                if user_id else None,

                action=action,

                reason=reason

            )

            db.session.add(log)
            db.session.commit()

        except Exception:

            db.session.rollback()



    # ==========================
    # Anti Links
    # ==========================

    @commands.Cog.listener()
    async def on_message(self, message):

        if (
            message.author.bot
            or not message.guild
        ):
            return


        settings = self.get_settings(
            message.guild.id
        )


        # منع الروابط

        if getattr(settings, "anti_links", False):

            blocked = [

                "discord.gg/",

                "discord.com/invite/",

                "http://",

                "https://"

            ]


            if any(
                x in message.content.lower()
                for x in blocked
            ):


                try:

                    await message.delete()

                    warn = await message.channel.send(
                        f"⚠️ {message.author.mention} يمنع نشر الروابط هنا."
                    )

                    await warn.delete(
                        delay=5
                    )


                except discord.Forbidden:
                    pass


                self.create_log(

                    message.guild.id,

                    message.author.id,

                    "ANTI_LINK",

                    "External link blocked"

                )


                return



        # ==========================
        # Anti Spam
        # ==========================


        if getattr(settings, "anti_spam", False):

            now = time.time()

            user = message.author.id


            self.spam_cache[user].append(now)


            self.spam_cache[user] = [

                t for t in self.spam_cache[user]

                if now - t <= 5

            ]


            limit = getattr(
                settings,
                "spam_limit",
                5
            )


            if len(
                self.spam_cache[user]
            ) >= limit:


                try:

                    await message.author.timeout(

                        discord.utils.utcnow(),

                        reason="Anti Spam"

                    )

                except Exception:

                    pass



                self.create_log(

                    message.guild.id,

                    message.author.id,

                    "ANTI_SPAM",

                    "Spam detected"

                )


                self.spam_cache[user].clear()



    # ==========================
    # Anti Raid
    # ==========================


    @commands.Cog.listener()
    async def on_member_join(
        self,
        member
    ):


        settings = self.get_settings(
            member.guild.id
        )


        if not getattr(
            settings,
            "anti_raid",
            False
        ):
            return



        now = time.time()


        self.raid_cache[
            member.guild.id
        ].append(now)



        self.raid_cache[
            member.guild.id
        ] = [

            x for x in self.raid_cache[
                member.guild.id
            ]

            if now - x <= 10

        ]



        raid_limit = getattr(
            settings,
            "raid_limit",
            10
        )



        if len(
            self.raid_cache[
                member.guild.id
            ]
        ) >= raid_limit:


            self.create_log(

                member.guild.id,

                member.id,

                "ANTI_RAID",

                "Raid detected"

            )



    # ==========================
    # أمر حالة الحماية
    # ==========================


    @commands.command(
        name="protection"
    )
    @commands.has_permissions(
        administrator=True
    )
    async def protection_status(
        self,
        ctx
    ):


        settings = self.get_settings(
            ctx.guild.id
        )


        embed = discord.Embed(
            title="🛡 نظام الحماية",
            color=0x5865F2
        )


        embed.add_field(
            name="Anti Spam",
            value="ON"
            if settings.anti_spam
            else "OFF"
        )


        embed.add_field(
            name="Anti Links",
            value="ON"
            if settings.anti_links
            else "OFF"
        )


        embed.add_field(
            name="Anti Raid",
            value="ON"
            if getattr(settings, "anti_raid", False)
            else "OFF"
        )


        await ctx.send(
            embed=embed
        )



    # ==========================
    # تشغيل / إيقاف Anti Spam
    # ==========================


    @commands.command(
        name="antispam"
    )
    @commands.has_permissions(
        administrator=True
    )
    async def anti_spam(
        self,
        ctx,
        status: str
    ):


        settings = self.get_settings(
            ctx.guild.id
        )


        if status.lower() == "on":

            settings.anti_spam = True

            msg = "✅ تم تفعيل Anti Spam"


        elif status.lower() == "off":

            settings.anti_spam = False

            msg = "⚠️ تم إيقاف Anti Spam"


        else:

            msg = "❌ استخدم: !antispam on/off"



        db.session.commit()


        await ctx.send(
            msg
        )



async def setup(bot):

    await bot.add_cog(
        ProtectionCog(bot)
            )
