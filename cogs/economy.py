import discord
from discord.ext import commands
from datetime import datetime, timedelta
from models import db, EconomyUser

class EconomyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # دالة مساعدة لجلب أو إنشاء رصيد المستخدم في قاعدة البيانات
    def get_user_account(self, guild_id, user_id):
        account = EconomyUser.query.filter_by(guild_id=str(guild_id), user_id=str(user_id)).first()
        if not account:
            account = EconomyUser(guild_id=str(guild_id), user_id=str(user_id), wallet=500, bank=1000)
            db.session.add(account)
            db.session.commit()
        return account

    # 1. أمر الرصيد (Balance)
    @commands.command(name="balance", aliases=["bal", "رصيدي"])
    async def balance(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        account = self.get_user_account(ctx.guild.id, target.id)

        embed = discord.Embed(
            title=f"💰 رصيد الحساب لـ {target.name}",
            color=0x23a55a
        )
        embed.add_field(name="المحفظة (Wallet)", value=f"{account.wallet:,} 🪙", inline=True)
        embed.add_field(name="البنك (Bank)", value=f"{account.bank:,} 💳", inline=True)
        embed.add_field(name="الإجمالي", value=f"{(account.wallet + account.bank):,} 🪙", inline=False)
        embed.set_thumbnail(url=target.display_avatar.url)
        
        await ctx.send(embed=embed)

    # 2. أمر الراتب اليومي (Daily)
    @commands.command(name="daily", aliases=["راتب"])
    async def daily(self, ctx):
        account = self.get_user_account(ctx.guild.id, ctx.author.id)
        now = datetime.utcnow()

        if account.last_daily and now - account.last_daily < timedelta(hours=24):
            remaining = timedelta(hours=24) - (now - account.last_daily)
            hours, remainder = divmod(int(remaining.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            await ctx.send(f"⏳ لقد استلمت راتبك اليومي مسبقاً. يمكنك الاستلام مرة أخرى بعد **{hours} ساعة و {minutes} دقيقة**.")
            return

        daily_amount = 1000
        account.wallet += daily_amount
        account.last_daily = now
        db.session.commit()

        embed = discord.Embed(
            title="🎁 استلام الراتب اليومي",
            description=f"مبارك لك يا {ctx.author.mention}! تم إضافة **{daily_amount:,} 🪙** إلى محفظتك.",
            color=0x23a55a
        )
        await ctx.send(embed=embed)

    # 3. أمر التحويل المالي (Pay / Transfer)
    @commands.command(name="pay", aliases=["تحويل"])
    async def pay(self, ctx, member: discord.Member, amount: int):
        if member.bot or member == ctx.author:
            await ctx.send("❌ لا يمكنك التحويل لنفسك أو لبوت.")
            return

        if amount <= 0:
            await ctx.send("❌ يرجى تحديد مبلغ صحيح أكبر من الصفر.")
            return

        sender_account = self.get_user_account(ctx.guild.id, ctx.author.id)
        if sender_account.wallet < amount:
            await ctx.send("❌ ليس لديك رصيد كافٍ في المحفظة لإتمام هذه العملية.")
            return

        receiver_account = self.get_user_account(ctx.guild.id, member.id)

        # تنفيذ عملية النقل المالي
        sender_account.wallet -= amount
        receiver_account.wallet += amount
        db.session.commit()

        embed = discord.Embed(
            title="💸 عملية تحويل ناجحة",
            description=f"تم تحويل **{amount:,} 🪙** بنجاح من {ctx.author.mention} إلى العضو {member.mention}.",
            color=0x5865F2
        )
        await ctx.send(embed=embed)

    # 4. لوحة صدارة الأثرياء (Leaderboard / Top)
    @commands.command(name="richest", aliases=["top", "أثرياء"])
    async def richest(self, ctx):
        top_users = EconomyUser.query.filter_by(guild_id=str(ctx.guild.id)).order_by((EconomyUser.wallet + EconomyUser.bank).desc()).limit(10).all()

        if not top_users:
            await ctx.send("❌ لا توجد بيانات اقتصادية مسجلة بعد في هذا السيرفر.")
            return

        description = ""
        for index, acc in enumerate(top_users, start=1):
            user = ctx.guild.get_member(int(acc.user_id))
            username = user.name if user else f"مستخدم مغادر ({acc.user_id})"
            total_money = acc.wallet + acc.bank
            
            medal = "🥇" if index == 1 else "🥈" if index == 2 else "🥉" if index == 3 else f"`#{index}`"
            description += f"{medal} **{username}** — **{total_money:,} 🪙**\n"

        embed = discord.Embed(
            title="🏆 لوحة صدارة الأثرياء في السيرفر",
            description=description,
            color=0xffd700
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EconomyCog(bot))
          
