# -*- coding: utf-8 -*-

import discord
from discord.ext import commands

from models import (
    db,
    TicketSettingsModel,
    TicketModel
)


class TicketView(discord.ui.View):

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot


    @discord.ui.button(
        label="فتح تذكرة",
        emoji="🎫",
        style=discord.ButtonStyle.green,
        custom_id="create_ticket"
    )
    async def create_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        guild = interaction.guild
        user = interaction.user


        settings = TicketSettingsModel.query.filter_by(
            guild_id=str(guild.id)
        ).first()


        if not settings:
            settings = TicketSettingsModel(
                guild_id=str(guild.id)
            )

            db.session.add(settings)
            db.session.commit()


        old_ticket = TicketModel.query.filter_by(
            guild_id=str(guild.id),
            owner_id=str(user.id),
            status="open"
        ).first()


        if old_ticket:

            await interaction.response.send_message(
                "❌ لديك تذكرة مفتوحة بالفعل.",
                ephemeral=True
            )
            return



        category = None

        if settings.ticket_category_id:

            category = guild.get_channel(
                int(settings.ticket_category_id)
            )


        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            category=category
        )


        ticket = TicketModel(

            guild_id=str(guild.id),

            ticket_number=channel.id,

            channel_id=str(channel.id),

            owner_id=str(user.id),

            status="open"

        )


        db.session.add(ticket)

        db.session.commit()



        await channel.set_permissions(
            user,
            view_channel=True,
            send_messages=True
        )


        embed = discord.Embed(
            title="🎫 تذكرة الدعم",
            description=
            "أهلاً بك\n"
            "اكتب مشكلتك وسيقوم فريق الدعم بالرد عليك.",
            color=0x5865F2
        )


        embed.set_footer(
            text=f"Ticket ID: {ticket.id}"
        )


        await channel.send(
            content=user.mention,
            embed=embed,
            view=CloseTicketView()
        )


        await interaction.response.send_message(
            f"✅ تم إنشاء تذكرتك: {channel.mention}",
            ephemeral=True
        )




class CloseTicketView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.button(
        label="إغلاق التذكرة",
        emoji="🔒",
        style=discord.ButtonStyle.red,
        custom_id="close_ticket"
    )
    async def close_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        channel = interaction.channel


        ticket = TicketModel.query.filter_by(
            channel_id=str(channel.id)
        ).first()


        if ticket:

            ticket.status = "closed"

            db.session.commit()


        await interaction.response.send_message(
            "🔒 سيتم إغلاق التذكرة.",
        )


        await channel.delete()



class TicketCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command(
        name="ticketpanel"
    )
    @commands.has_permissions(administrator=True)
    async def ticket_panel(
        self,
        ctx
    ):

        embed = discord.Embed(
            title="🎫 الدعم الفني",
            description=
            "اضغط الزر لإنشاء تذكرة.",
            color=0x5865F2
        )


        await ctx.send(
            embed=embed,
            view=TicketView(self.bot)
        )



async def setup(bot):

    await bot.add_cog(
        TicketCog(bot)
    )
