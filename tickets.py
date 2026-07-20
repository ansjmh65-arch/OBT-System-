import discord
from discord.ext import commands
from models import db, Ticket

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="فتح تذاكر جديدة 🎫", style=discord.ButtonStyle.green, custom_id="create_ticket_btn")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user

        # التحقق مما إذا كانت هناك تذاكر مفتوحة بالفعل لنفس المستخدم
        existing_ticket = Ticket.query.filter_by(guild_id=str(guild.id), user_id=str(member.id), status="open").first()
        if existing_ticket:
            await interaction.response.send_message("❌ لديك تذاكر مفتوحة مسبقاً، يرجى إغلاقها أولاً.", ephemeral=True)
            return

        # إعطاء صلاحيات الرؤية والكتابة لصاحب التذكرة والإدارة فقط
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }

        # إنشاء روم التذكرة الجديد
        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{member.name}",
            overwrites=overwrites,
            reason=f"تم فتح التذكرة بواسطة {member}"
        )

        # حفظ التذكرة في قاعدة البيانات
        new_ticket = Ticket(
            guild_id=str(guild.id),
            channel_id=str(ticket_channel.id),
            user_id=str(member.id),
            status="open"
        )
        db.session.add(new_ticket)
        db.session.commit()

        # إرسال رسالة الترحيب داخل التذكرة مع زر الإغلاق
        close_view = TicketCloseView()
        embed = discord.Embed(
            title="🎫 نظام التذاكر - الدعم الفني",
            description=f"مرحباً بك {member.mention}!\nطاقم الإدارة سيقوم بالرد عليك في أقرب وقت ممكن.\nلإغلاق التذكرة اضغط على الزر أدناه.",
            color=0x5865F2
        )
        await ticket_channel.send(content=member.mention, embed=embed, view=close_view)
        await interaction.response.send_message(f"✅ تم إنشاء التذكرة بنجاح: {ticket_channel.mention}", ephemeral=True)

class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="إغلاق التذكرة 🔒", style=discord.ButtonStyle.red, custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel
        ticket = Ticket.query.filter_by(channel_id=str(channel.id)).first()
        
        if ticket:
            ticket.status = "closed"
            db.session.commit()

        await interaction.response.send_message("🔒 جاري إغلاق وحذف التذكرة خلال 5 ثوانٍ...")
        
        # حذف الروم بعد 5 ثوانٍ
        await channel.delete(delay=5)

class TicketsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ticketpanel")
    @commands.has_permissions(administrator=True)
    async def ticket_panel(self, ctx):
        embed = discord.Embed(
            title="🎫 مركز المساعدة والدعم الفني",
            description="اضغط على الزر أدناه لفتح تذكرة جديدة والتواصل مع الإدارة بكل سرية.",
            color=0x5865F2
        )
        view = TicketView()
        await ctx.send(embed=embed, view=view)
        await ctx.message.delete()

async def setup(bot):
    await bot.add_cog(TicketsCog(bot))
          
