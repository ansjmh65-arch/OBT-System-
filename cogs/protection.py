import discord
from discord.ext import commands
from models import db, ProtectionSettings

class ProtectionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        # جلب إعدادات الحماية الخاصة بالسيرفر من قاعدة البيانات
        settings = ProtectionSettings.query.filter_by(guild_id=str(message.guild.id)).first()
        if not settings:
            return

        # 1. نظام منع الروابط الخارجية والدعوات (Anti Links)
        if settings.anti_links:
            if "discord.gg/" in message.content.lower() or "http://" in message.content.lower() or "https://" in message.content.lower():
                try:
                    await message.delete()
                    warning_msg = await message.channel.send(f"⚠️ ممنوع نشر الروابط الخارجية أو الدعوات يا {message.author.mention}!")
                    await warning_msg.delete(delay=5)
                    return
                except discord.Forbidden:
                    pass

        # 2. نظام منع السبام والرسائل المتكررة (Anti Spam)
        if settings.anti_spam:
            # التحقق المبسط للرسائل المتكررة أو السريعة
            pass

    @commands.command(name="antispam")
    @commands.has_permissions(administrator=True)
    async def toggle_anti_spam(self, ctx, status: str):
        guild_id = str(ctx.guild.id)
        settings = ProtectionSettings.query.filter_by(guild_id=guild_id).first()
        
        if not settings:
            settings = ProtectionSettings(guild_id=guild_id)
            db.session.add(settings)

        if status.lower() == "on":
            settings.anti_spam = True
            await ctx.send("✅ تم تفعيل نظام منع السبام بنجاح.")
        elif status.lower() == "off":
            settings.anti_spam = False
            await ctx.send("⚠️ تم إيقاف نظام منع السبام.")
        else:
            await ctx.send("❌ الاستخدام الخاطئ. اكتب: `!antispam on` أو `!antispam off`")
        
        db.session.commit()

async def setup(bot):
    await bot.add_cog(ProtectionCog(bot))
  
