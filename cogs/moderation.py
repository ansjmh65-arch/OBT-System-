# -*- coding: utf-8 -*-

from datetime import timedelta, datetime

import discord
from discord.ext import commands

from models import (
    db,
    ModerationCaseModel,
    WarningModel
)


class ModerationCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.cases = {}


    def create_case(
        self,
        guild_id,
        user_id,
        moderator_id,
        action,
        reason,
        duration=None
    ):

        case = self.cases.get(
            guild_id,
            0
        ) + 1

        self.cases[guild_id] = case


        data = ModerationCaseModel(

            guild_id=str(guild_id),

            case_id=case,

            user_id=str(user_id),

            moderator_id=str(moderator_id),

            action=action,

            reason=reason,

            duration=duration

        )


        db.session.add(data)
        db.session.commit()


        return case



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


        warning = WarningModel(

            guild_id=str(ctx.guild.id),

            user_id=str(member.id),

            moderator_id=str(ctx.author.id),

            reason=reason,

            points=1

        )


        db.session.add(
            warning
        )


        case = self.create_case(

            ctx.guild.id,

            member.id,

            ctx.author.id,

            "WARN",

            reason

        )


        db.session.commit()



        await ctx.send(
            f"⚠️ تم تحذير {member.mention}\nCase: `{case}`"
        )



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


        case = self.create_case(

            ctx.guild.id,

            member.id,

            ctx.author.id,

            "KICK",

            reason

        )


        await member.kick(
            reason=reason
        )


        await ctx.send(
            f"👢 تم طرد {member.mention}\nCase: `{case}`"
        )



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


        case = self.create_case(

            ctx.guild.id,

            member.id,

            ctx.author.id,

            "BAN",

            reason

        )


        await member.ban(
            reason=reason
        )


        await ctx.send(
            f"🔨 تم حظر {member.mention}\nCase: `{case}`"
        )



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
        minutes: int = 5,
        *,
        reason="No reason"
    ):


        case = self.create_case(

            ctx.guild.id,

            member.id,

            ctx.author.id,

            "TIMEOUT",

            reason,

            minutes

        )


        await member.timeout(
            timedelta(
                minutes=minutes
            ),
            reason=reason
        )


        await ctx.send(
            f"⏳ تم إسكات {member.mention} لمدة {minutes} دقيقة\nCase: `{case}`"
        )



    @commands.command(
        name="cases"
    )
    @commands.has_permissions(
        manage_messages=True
    )
    async def cases(
        self,
        ctx,
        member: discord.Member
    ):


        logs = ModerationCaseModel.query.filter_by(
            guild_id=str(ctx.guild.id),
            user_id=str(member.id)
        ).all()


        if not logs:

            await ctx.send(
                "لا توجد مخالفات."
            )

            return


        embed = discord.Embed(
            title=f"📋 سجل {member}",
            color=0x5865F2
        )


        for case in logs[-10:]:

            embed.add_field(

                name=f"Case #{case.case_id}",

                value=f"{case.action}\n{case.reason}",

                inline=False

            )


        await ctx.send(
            embed=embed
        )



async def setup(bot):

    await bot.add_cog(
        ModerationCog(bot)
        )
