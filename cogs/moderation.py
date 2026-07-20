import discord
from discord.ext import commands

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 1. أمر الحظر (Ban)
    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban_member(self, ctx, member: discord.Member, *, reason=None):
        if member == ctx.author:
            await ctx.send("❌ لا يمكنك حظر نفسك!")
            return
        
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="🔨 تم حظر العضو",
            description=f"تم حظر العضو **{member}** بنجاح.\n**السبب:** {reason or 'بدون سبب مخصص'}",
            color=0xff0000
        )
        await ctx.send(embed=embed)

    # 2. أمر الطرد (Kick)
    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick_member(self, ctx, member: discord.Member, *, reason=None):
        if member == ctx.author:
            await ctx.send("❌ لا يمكنك طرد نفسك!")
            return
        
        await member.kick(reason=reason)
        embed = discord.Embed(
            title="👢 تم طرد العضو",
            description=f"تم طرد العضو **{member}** بنجاح.\n**السبب:** {reason or 'بدون سبب مخصص'}",
            color=0xffaa00
        )
        await ctx.send(embed=embed)

    # 3. أمر مسح الرسائل (Purge / Clear)
    @commands.command(name="clear", aliases=["purge"])
    @commands.has_permissions(manage_messages=True)
    async def clear_messages(self, ctx, amount: int = 10):
        if amount <= 0:
            await ctx.send("❌ يرجى تحديد عدد أكبر من الصفر لمسح الرسائل.")
            return

        deleted = await ctx.channel.purge(limit=amount + 1)
        msg = await ctx.send(f"🧹 تم مسح **{len(deleted) - 1}** رسالة بنجاح.")
        await msg.delete(delay=4)

    # 4. أمر قفل الروم (Lock)
    @commands.command(name="lock")
    @commands.has_permissions(manage_channels=True)
    async def lock_channel(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        embed = discord.Embed(
            title="🔒 قفل الروم",
            description="تم قفل هذه الروم بنجاح. لا يمكن للأعضاء الكتابة فيها حالياً.",
            color=0x2b2d31
        )
        await ctx.send(embed=embed)

    # 5. أمر فتح الروم (Unlock)
    @commands.command(name="unlock")
    @commands.has_permissions(manage_channels=True)
    async def unlock_channel(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        embed = discord.Embed(
            title="🔓 فتح الروم",
            description="تم فتح هذه الروم بنجاح. يمكن للأعضاء الكتابة الآن.",
            color=0x23a55a
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
  
