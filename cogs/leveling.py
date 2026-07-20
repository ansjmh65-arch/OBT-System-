import discord
from discord.ext import commands
import math
from models import db, LevelUser

class LevelingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # دالة مساعدة لحساب أو جلب بيانات المستخدم في قاعدة البيانات
    def get_user_level(self, guild_id, user_id):
        user_data = LevelUser.query.filter_by(guild_id=str(guild_id), user_id=str(user_id)).first()
        if not user_data:
            user_data = LevelUser(guild_id=str(guild_id), user_id=str(user_id), xp=0, level=0)
            db.session.add(user_data)
            db.session.commit()
        return user_data

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        guild_id = message.guild.id
        user_id = message.author.id

        # منح خبرة عشوائية لكل رسالة يتم إرسالها (بين 15 إلى 25 نقطة خبرة)
        import random
        gained_xp = random.randint(15, 25)

        user_data = self.get_user_level(guild_id, user_id)
        user_data.xp += gained_xp

        # المعادلة الرياضية لحساب المستوى المطلوب: XP المطلوب = المستوى الحالي * 100 + 50
        next_level_xp = (user_data.level + 1) * 100 + 50

        if user_data.xp >= next_level_xp:
            user_data.level += 1
            db.session.commit()

            # إرسال رسالة تهنئة بالترقية في نفس الروم
            embed = discord.Embed(
                title="🎉 ترقية جديدة في المستوى!",
                description=f"مبارك لك يا {message.author.mention}! لقد صعدت إلى المستوى **{user_data.level}** 🚀",
                color=0x23a55a
            )
            await message.channel.send(embed=embed)
        else:
            db.session.commit()

    # 1. أمر الرانك (Rank)
    @commands.command(name="rank", aliases=["level", "مستوى"])
    async def rank(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        user_data = self.get_user_level(ctx.guild.id, target.id)

        next_level_xp = (user_data.level + 1) * 100 + 50

        embed = discord.Embed(
            title=f"⭐ بطاقة المستوى لـ {target.name}",
            color=0x5865F2
        )
        embed.add_field(name="المستوى الحالي", value=str(user_data.level), inline=True)
        embed.add_field(name="نقاط الخبرة (XP)", value=f"{user_data.xp:,} / {next_level_xp:,}", inline=True)
        embed.set_thumbnail(url=target.display_avatar.url)

        await ctx.send(embed=embed)

    # 2. لوحة صدارة المستويات (Leaderboard / Top Levels)
    @commands.command(name="levels", aliases=["top-levels", "مستويات"])
    async def levels_leaderboard(self, ctx):
        top_users = LevelUser.query.filter_by(guild_id=str(ctx.guild.id)).order_by(LevelUser.level.desc(), LevelUser.xp.desc()).limit(10).all()

        if not top_users:
            await ctx.send("❌ لا توجد بيانات مستويات مسجلة بعد في هذا السيرفر.")
            return

        description = ""
        for index, acc in enumerate(top_users, start=1):
            user = ctx.guild.get_member(int(acc.user_id))
            username = user.name if user else f"مستخدم مغادر ({acc.user_id})"
            
            medal = "🥇" if index == 1 else "🥈" if index == 2 else "🥉" if index == 3 else f"`#{index}`"
            description += f"{medal} **{username}** — المستوى: **{acc.level}** (XP: {acc.xp:,})\n"

        embed = discord.Embed(
            title="🏆 لوحة صدارة المستويات في السيرفر",
            description=description,
            color=0xffd700
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(LevelingCog(bot))
      
