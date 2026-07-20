import discord
from discord.ext import commands
from models import db, Clan

class ClanCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 1. أمر إنشاء كلان جديد (Create Clan)
    @commands.command(name="createclan", aliases=["انشاء_كلان"])
    async def create_clan(self, ctx, tag: str, *, name: str):
        # التحقق مما إذا كان الكلان موجوداً مسبقاً بنفس الاسم أو الـ Tag في السيرفر
        existing_clan = Clan.query.filter_by(guild_id=str(ctx.guild.id)).filter(
            (Clan.name == name) | (Clan.tag == tag)
        ).first()

        if existing_clan:
            await ctx.send("❌ عذراً، اسم الكلان أو الشعار (Tag) مستخدم بالفعل في هذا السيرفر.")
            return

        # إنشاء الكلان الجديد في قاعدة البيانات
        new_clan = Clan(
            guild_id=str(ctx.guild.id),
            name=name,
            tag=tag.upper(),
            owner_id=str(ctx.author.id),
            level=1,
            points=0
        )
        db.session.add(new_clan)
        db.session.commit()

        embed = discord.Embed(
            title="🛡️ تأسيس كلان جديد بنجاح",
            description=f"مبارك لك يا {ctx.author.mention}!\nتم تأسيس الكلان **[{tag.upper()}] {name}** بنجاح.",
            color=0x5865F2
        )
        await ctx.send(embed=embed)

    # 2. عرض معلومات الكلان (Clan Info)
    @commands.command(name="clan", aliases=["كلان"])
    async def clan_info(self, ctx, *, name: str = None):
        if not name:
            await ctx.send("❌ يرجى كتابة اسم الكلان الذي تريد البحث عنه. مثال: `!clan Dragons`")
            return

        clan = Clan.query.filter_by(guild_id=str(ctx.guild.id), name=name).first()
        if not clan:
            await ctx.send("❌ لم يتم العثور على كلان بهذا الاسم في السيرفر.")
            return

        owner = ctx.guild.get_member(int(clan.owner_id))
        owner_name = owner.name if owner else f"مستخدم مغادر ({clan.owner_id})"

        embed = discord.Embed(
            title=f"🛡️ معلومات الكلان: [{clan.tag}] {clan.name}",
            color=0xffd700
        )
        embed.add_field(name="قائد الكلان", value=owner_name, inline=True)
        embed.add_field(name="مستوى الكلان", value=str(clan.level), inline=True)
        embed.add_field(name="نقاط الكلان", value=f"{clan.points:,} نقطة", inline=True)
        embed.set_footer(text=f"تاريخ التأسيس: {clan.created_at.strftime('%Y-%m-%d')}")

        await ctx.send(embed=embed)

    # 3. لوحة صدارة الكلانات (Clans Leaderboard)
    @commands.command(name="clanboard", aliases=["ترتيب_الكلانات"])
    async def clan_leaderboard(self, ctx):
        top_clans = Clan.query.filter_by(guild_id=str(ctx.guild.id)).order_by(Clan.points.desc()).limit(10).all()

        if not top_clans:
            await ctx.send("❌ لا توجد أي كلانات مسجلة حتى الآن في هذا السيرفر.")
            return

        description = ""
        for index, clan in enumerate(top_clans, start=1):
            medal = "🥇" if index == 1 else "🥈" if index == 2 else "🥉" if index == 3 else f"`#{index}`"
            description += f"{medal} **[{clan.tag}] {clan.name}** — المستوى: **{clan.level}** ( النقاط: {clan.points:,} )\n"

        embed = discord.Embed(
            title="🏆 لوحة صدارة الكلانات في السيرفر",
            description=description,
            color=0xffd700
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ClanCog(bot))
