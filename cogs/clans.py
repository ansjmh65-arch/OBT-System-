# -*- coding: utf-8 -*-

import discord
from discord.ext import commands

from models import (
    db,
    Clan,
    ClanMember,
    ClanPointsLog
)


class ClanCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    # ==========================
    # إنشاء كلان
    # ==========================

    @commands.command(
        name="createclan",
        aliases=["انشاء_كلان"]
    )
    async def create_clan(
        self,
        ctx,
        tag: str,
        *,
        name: str
    ):

        exists = Clan.query.filter_by(
            guild_id=str(ctx.guild.id),
            tag=tag.upper()
        ).first()


        if exists:
            return await ctx.send(
                "❌ هذا الـ Tag مستخدم مسبقاً."
            )


        clan = Clan(

            guild_id=str(ctx.guild.id),

            clan_id=f"{ctx.guild.id}-{ctx.author.id}",

            name=name,

            tag=tag.upper(),

            owner_id=str(ctx.author.id),

            level=1,

            points=0

        )


        db.session.add(clan)
        db.session.commit()



        member = ClanMember(

            clan_id=clan.clan_id,

            user_id=str(ctx.author.id),

            role="owner"

        )


        db.session.add(member)
        db.session.commit()



        embed = discord.Embed(

            title="🛡️ تم إنشاء الكلان",

            description=(
                f"الكلان: **[{clan.tag}] {clan.name}**\n"
                f"القائد: {ctx.author.mention}"
            ),

            color=0x5865F2

        )


        await ctx.send(embed=embed)



    # ==========================
    # معلومات الكلان
    # ==========================


    @commands.command(
        name="clan",
        aliases=["كلان"]
    )
    async def clan_info(
        self,
        ctx,
        *,
        name=None
    ):


        if name:

            clan = Clan.query.filter_by(
                guild_id=str(ctx.guild.id),
                name=name
            ).first()

        else:

            clan = Clan.query.filter_by(
                guild_id=str(ctx.guild.id),
                owner_id=str(ctx.author.id)
            ).first()



        if not clan:

            return await ctx.send(
                "❌ لم يتم العثور على الكلان."
            )



        embed = discord.Embed(

            title=f"🛡️ [{clan.tag}] {clan.name}",

            color=0xffd700

        )


        embed.add_field(
            name="👑 القائد",
            value=f"<@{clan.owner_id}>"
        )


        embed.add_field(
            name="⭐ المستوى",
            value=clan.level
        )


        embed.add_field(
            name="🏆 النقاط",
            value=f"{clan.points:,}"
        )


        await ctx.send(embed=embed)



    # ==========================
    # دخول كلان
    # ==========================


    @commands.command(
        name="joinclan"
    )
    async def join_clan(
        self,
        ctx,
        tag:str
    ):


        clan = Clan.query.filter_by(
            guild_id=str(ctx.guild.id),
            tag=tag.upper()
        ).first()



        if not clan:

            return await ctx.send(
                "❌ الكلان غير موجود."
            )



        exists = ClanMember.query.filter_by(
            clan_id=clan.clan_id,
            user_id=str(ctx.author.id)
        ).first()



        if exists:

            return await ctx.send(
                "❌ أنت داخل كلان بالفعل."
            )



        member = ClanMember(

            clan_id=clan.clan_id,

            user_id=str(ctx.author.id),

            role="member"

        )


        db.session.add(member)
        db.session.commit()



        await ctx.send(
            f"✅ انضممت إلى كلان **{clan.name}**"
        )



    # ==========================
    # أعضاء الكلان
    # ==========================


    @commands.command(
        name="clanmembers"
    )
    async def clan_members(
        self,
        ctx
    ):


        clan = Clan.query.filter_by(
            owner_id=str(ctx.author.id)
        ).first()



        if not clan:

            return await ctx.send(
                "❌ أنت لا تملك كلان."
            )



        members = ClanMember.query.filter_by(
            clan_id=clan.clan_id
        ).all()



        text=""



        for m in members:

            text += (
                f"<@{m.user_id}> "
                f"ـ `{m.role}`\n"
            )



        embed=discord.Embed(

            title="👥 أعضاء الكلان",

            description=text,

            color=0x5865F2

        )


        await ctx.send(embed=embed)



    # ==========================
    # إضافة نقاط
    # ==========================


    @commands.command(
        name="clanaddpoints"
    )
    async def add_points(
        self,
        ctx,
        amount:int,
        *,
        reason="No reason"
    ):


        clan = Clan.query.filter_by(
            owner_id=str(ctx.author.id)
        ).first()



        if not clan:

            return await ctx.send(
                "❌ أنت لست قائد كلان."
            )



        clan.points += amount



        log = ClanPointsLog(

            clan_id=clan.clan_id,

            user_id=str(ctx.author.id),

            points=amount,

            reason=reason

        )


        db.session.add(log)

        db.session.commit()



        await ctx.send(
            f"✅ تمت إضافة {amount} نقطة للكلان."
        )



    # ==========================
    # ترتيب الكلانات
    # ==========================


    @commands.command(
        name="clanboard"
    )
    async def leaderboard(
        self,
        ctx
    ):


        clans = Clan.query.filter_by(
            guild_id=str(ctx.guild.id)
        ).order_by(
            Clan.points.desc()
        ).limit(10).all()



        text=""


        for i,c in enumerate(clans,1):

            text += (
                f"**#{i}** "
                f"[{c.tag}] {c.name} "
                f"ـ {c.points:,} نقطة\n"
            )



        embed=discord.Embed(

            title="🏆 ترتيب الكلانات",

            description=text,

            color=0xffd700

        )


        await ctx.send(embed=embed)



async def setup(bot):

    await bot.add_cog(
        ClanCog(bot)
            )
