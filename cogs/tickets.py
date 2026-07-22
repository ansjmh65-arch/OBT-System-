# -*- coding: utf-8 -*-

import discord
from discord.ext import commands

from models import db, TicketSettings, Ticket


class TicketCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    # ==========================
    # جلب إعدادات التذاكر
    # ==========================

    def get_settings(self, guild_id):

        settings = TicketSettings.query.filter_by(
            guild_id=str(guild_id)
        ).first()

        if not settings:

            settings = TicketSettings(
                guild_id=str(guild_id),
                enabled=True
            )

            db.session.add(settings)
            db.session.commit()

        return settings



    # ==========================
    # إنشاء تذكرة
    # ==========================

    @commands.command(
        name="ticket"
    )
    async def create_ticket(
        self,
        ctx
    ):

        settings = self.get_settings(
            ctx.guild.id
        )


        if not settings.enabled:

            return await ctx.send(
                "❌ نظام التذاكر مغلق."
            )



        existing = Ticket.query.filter_by(
            guild_id=str(ctx.guild.id),
            owner_id=str(ctx.author.id),
            status="open"
        ).first()


        if existing:

            return await ctx.send(
                "⚠️ لديك تذكرة مفتوحة بالفعل."
            )



        category = None


        if settings.category_id:

            category = discord.utils.get(
                ctx.guild.categories,
                id=int(settings.category_id)
            )



        overwrites = {

            ctx.guild.default_role:
            discord.PermissionOverwrite(
                view_channel=False
            ),


            ctx.author:
            discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True
            )

        }



        channel = await ctx.guild.create_text_channel(

            name=f"ticket-{ctx.author.name}",

            category=category,

            overwrites=overwrites

        )



        ticket = Ticket(

            guild_id=str(ctx.guild.id),

            channel_id=str(channel.id),

            owner_id=str(ctx.author.id),

            status="open"

        )


        db.session.add(ticket)

        db.session.commit()



        embed = discord.Embed(

            title="🎫 Ticket",

            description=
            "اكتب مشكلتك هنا وسيتم الرد عليك من الإدارة.",

            color=0x5865F2

        )


        embed.set_footer(
            text="OBT System"
        )


        await channel.send(
            content=ctx.author.mention,
            embed=embed
        )


        await ctx.send(
            f"✅ تم إنشاء التذكرة: {channel.mention}"
        )



    # ==========================
    # إغلاق التذكرة
    # ==========================

    @commands.command(
        name="close"
    )
    async def close_ticket(
        self,
        ctx
    ):


        ticket = Ticket.query.filter_by(

            channel_id=str(ctx.channel.id),

            status="open"

        ).first()



        if not ticket:

            return await ctx.send(
                "❌ هذه ليست تذكرة."
            )



        ticket.status = "closed"

        db.session.commit()



        await ctx.send(
            "🔒 سيتم إغلاق التذكرة."
        )


        await ctx.channel.delete()



    # ==========================
    # إعداد لوحة التذاكر
    # ==========================

    @commands.command(
        name="ticketsetup"
    )
    @commands.has_permissions(
        administrator=True
    )
    async def ticket_setup(
        self,
        ctx
    ):


        settings = self.get_settings(
            ctx.guild.id
        )


        settings.enabled = True


        settings.category_id = str(
            ctx.channel.category.id
        ) if ctx.channel.category else None



        db.session.commit()



        embed = discord.Embed(

            title="🎫 نظام التذاكر",

            description=
            "اكتب !ticket لإنشاء تذكرة.",

            color=0x5865F2

        )


        await ctx.send(
            embed=embed
        )



async def setup(bot):

    await bot.add_cog(
        TicketCog(bot)
    )
