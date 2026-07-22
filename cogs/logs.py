# -*- coding: utf-8 -*-

import discord

from discord.ext import commands

from models import db, LogSettingsModel, ServerLogModel


class LogsCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    def get_settings(self, guild_id):

        settings = LogSettingsModel.query.filter_by(
            guild_id=str(guild_id)
        ).first()

        return settings



    async def send_log(
        self,
        guild,
        log_type,
        action,
        user=None,
        details=None
    ):

        settings = self.get_settings(
            guild.id
        )

        if not settings:
            return


        if not settings.enabled:
            return


        if not settings.log_channel_id:
            return


        channel = guild.get_channel(
            int(settings.log_channel_id)
        )


        if not channel:
            return


        embed = discord.Embed(
            title=f"📋 {log_type}",
            color=0x5865F2
        )


        embed.add_field(
            name="Action",
            value=action,
            inline=False
        )


        if user:

            embed.add_field(
                name="User",
                value=user.mention,
                inline=False
            )


        if details:

            embed.add_field(
                name="Details",
                value=details,
                inline=False
            )


        await channel.send(
            embed=embed
        )


        log = ServerLogModel(

            guild_id=str(guild.id),

            user_id=str(user.id)
            if user else None,

            log_type=log_type,

            action=action,

            details=details

        )


        db.session.add(log)

        db.session.commit()



    # =====================
    # حذف رسالة
    # =====================

    @commands.Cog.listener()
    async def on_message_delete(
        self,
        message
    ):

        if not message.guild:
            return

        if message.author.bot:
            return


        await self.send_log(

            message.guild,

            "MESSAGE DELETE",

            "Message deleted",

            message.author,

            message.content[:500]

        )



    # =====================
    # تعديل رسالة
    # =====================

    @commands.Cog.listener()
    async def on_message_edit(
        self,
        before,
        after
    ):

        if not before.guild:
            return

        if before.content == after.content:
            return


        await self.send_log(

            before.guild,

            "MESSAGE EDIT",

            "Message edited",

            before.author,

            f"Before:\n{before.content}\n\nAfter:\n{after.content}"

        )



    # =====================
    # دخول عضو
    # =====================

    @commands.Cog.listener()
    async def on_member_join(
        self,
        member
    ):

        await self.send_log(

            member.guild,

            "MEMBER JOIN",

            "Member joined",

            member

        )



    # =====================
    # خروج عضو
    # =====================

    @commands.Cog.listener()
    async def on_member_remove(
        self,
        member
    ):

        await self.send_log(

            member.guild,

            "MEMBER LEAVE",

            "Member left",

            member

        )



    # =====================
    # حذف قناة
    # =====================

    @commands.Cog.listener()
    async def on_guild_channel_delete(
        self,
        channel
    ):

        await self.send_log(

            channel.guild,

            "CHANNEL DELETE",

            "Channel deleted",

            details=channel.name

        )



    # =====================
    # حذف رتبة
    # =====================

    @commands.Cog.listener()
    async def on_guild_role_delete(
        self,
        role
    ):

        await self.send_log(

            role.guild,

            "ROLE DELETE",

            "Role deleted",

            details=role.name

        )



async def setup(bot):

    await bot.add_cog(
        LogsCog(bot)
    )
