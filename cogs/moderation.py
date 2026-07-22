# -*- coding: utf-8 -*-

import discord
from discord.ext import commands

from models import db, ModerationCase, Warning


class ModerationCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    # ==========================
    # إنشاء Case
    # ==========================

    def create_case(
        self,
        guild_id,
        user_id,
        moderator_id,
        action,
        reason
    ):

        case = ModerationCase(

            guild_id=str(guild_id),

            user_id=str(user_id),

            moderator_id=str(moderator_id),

            action=action,

            reason=reason

        )

        db.session.add(case)
        db.session.commit()



    # ==========================
    # Warn
    # ==========================

    @commands.command(
        name="warn"
    )
    @commands.has_permissions(
        manage_messages=True
    )
    async def warn(
        self,
        ctx,
        member: discord.Member,
        *,
        reason="No reason"
    ):

        warning = Warning(

            guild_id=str(ctx.guild.id),

            user_id=str(member.id),

            moderator_id=str(ctx.author.id),

            reason=reason

        )


        db.session.add(warning)

        db.session.commit()


        self.create_case(

            ctx.guild.id,

            member.id,

            ctx.author.id,

            "WARN",

            reason

        )


        embed = discord.Embed(

            title="⚠️ Warning",

            description=
            f"{member.mention} تم تحذيره\n**السبب:** {reason}",

            color=0xFFA500

        )


        await ctx.send(
            embed=embed
        )



    # ==========================
    # Kick
    # ==========================

    @commands.command(
        name="kick"
    )
    @commands.has_permissions(
        kick_members=True
    )
    async def kick(
        self,
        ctx,
        member: discord.Member,
        *,
        reason="No reason"
    ):


        await member.kick(
            reason=reason
        )


        self.create_case(

            ctx.guild.id,

            member.id,

            ctx.author.id,

            "KICK",

            reason

        )


        await ctx.send(
            f"👢 تم طرد {member.mention}"
        )



    # ==========================
    # Ban
    # ==========================

    @commands.command(
        name="ban"
    )
    @commands.has_permissions(
        ban_members=True
    )
    async def ban(
        self,
        ctx,
        member: discord.Member,
        *,
        reason="No reason"
    ):


        await member.ban(
            reason=reason
        )


        self.create_case(

            ctx.guild.id,

            member.id,

            ctx.author.id,

            "BAN",

            reason

        )


        await ctx.send(
            f"🔨 تم حظر {member.mention}"
        )



    # ==========================
    # Timeout
    # ==========================

    @commands.command(
        name="timeout"
    )
    @commands.has_permissions(
        moderate_members=True
    )
    async def timeout(
        self,
        ctx,
        member: discord.Member,
        minutes: int = 10,
        *,
        reason="No reason"
    ):


        duration = discord.utils.utcnow()

        duration += discord.timedelta(
            minutes=minutes
        )


        await member.timeout(
            duration,
            reason=reason
        )


        self.create_case(

            ctx.guild.id,

            member.id,

            ctx.author.id,

            "TIMEOUT",

            reason

        )


        await ctx.send(
            f"⏱️ تم إعطاء {member.mention} تايم اوت لمدة {minutes} دقيقة"
        )



    # ==========================
    # عرض التحذيرات
    # ==========================

    @commands.command(
        name="warnings"
    )
    async def warnings(
        self,
        ctx,
        member: discord.Member
    ):


        data = Warning.query.filter_by(

            guild_id=str(ctx.guild.id),

            user_id=str(member.id)

        ).all()



        embed = discord.Embed(

            title=f"⚠️ تحذيرات {member}",

            color=0x5865F2

        )


        if not data:

            embed.description = "لا توجد تحذيرات"

        else:

            for warn in data:

                embed.add_field(

                    name="تحذير",

                    value=warn.reason,

                    inline=False

                )


        await ctx.send(
            embed=embed
        )



async def setup(bot):

    await bot.add_cog(
        ModerationCog(bot)
    )
