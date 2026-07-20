import discord
from discord.ext import commands
from models import db, ContentCreator

class ContentCreatorsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 1. أمر تسجيل قناة صانع محتوى (Register Creator)
    @commands.command(name="registercreator", aliases=["تسجيل_صانع_محتوى"])
    async def register_creator(self, ctx, platform: str, *, channel_url: str):
        valid_platforms = ["youtube", "twitch", "tiktok"]
        platform_lower = platform.lower()

        if platform_lower not in valid_platforms:
            await ctx.send(f"❌ منصة غير صالحة. المنصات المدعومة هي: `youtube`, `twitch`, `tiktok`")
            return

        # التحقق مما إذا كان المستخدم مسجلاً مسبقاً بنفس المنصة
        existing = ContentCreator.query.filter_by(
            guild_id=str(ctx.guild.id), 
            user_id=str(ctx.author.id), 
            platform=platform_lower
        ).first()

        if existing:
            await ctx.send("❌ أنت مسجل مسبقاً كصانع محتوى على هذه المنصة في السيرفر.")
            return

        # تسجيل صانع المحتوى الجديد في قاعدة البيانات
        new_creator = ContentCreator(
            guild_id=str(ctx.guild.id),
            user_id=str(ctx.author.id),
            platform=platform_lower,
            channel_url=channel_url,
            is_verified=False
        )
        db.session.add(new_creator)
        db.session.commit()

        embed = discord.Embed(
            title="🎬 تسجيل طلب صانع محتوى",
            description=f"مرحباً بك يا {ctx.author.mention}!\nتم استلام طلبك لمنصة **{platform_lower.capitalize()}** بنجاح. سيتم مراجعته والتحقق منه قريباً من قبل الإدارة.",
            color=0x5865F2
        )
        await ctx.send(embed=embed)

    # 2. أمر اعتماد صانع المحتوى من قبل الإدارة (Verify Creator)
    @commands.command(name="verifycreator", aliases=["اعتماد_صانع_محتوى"])
    @commands.has_permissions(administrator=True)
    async def verify_creator(self, ctx, member: discord.Member, platform: str):
        creator = ContentCreator.query.filter_by(
            guild_id=str(ctx.guild.id), 
            user_id=str(member.id), 
            platform=platform.lower()
        ).first()

        if not creator:
            await ctx.send("❌ لم يتم العثور على طلب تسجيل لهذا العضو على هذه المنصة.")
            return

        creator.is_verified = True
        db.session.commit()

        embed = discord.Embed(
            title="✅ تم اعتماد صانع المحتوى",
            description=f"مبارك لـ {member.mention}! تم اعتماد حسابه كصانع محتوى رسمي بنجاح.",
            color=0x23a55a
        )
        await ctx.send(embed=embed)

    # 3. عرض قائمة صناع المحتوى المعتمدين في السيرفر (Creators List)
    @commands.command(name="creators", aliases=["صناع_المحتوى"])
    async def list_creators(self, ctx):
        creators = ContentCreator.query.filter_by(guild_id=str(ctx.guild.id), is_verified=True).all()

        if not creators:
            await ctx.send("❌ لا يوجد صناع محتوى معتمدون حالياً في هذا السيرفر.")
            return

        description = ""
        for index, cr in enumerate(creators, start=1):
            user = ctx.guild.get_member(int(cr.user_id))
            username = user.name if user else f"مستخدم مغادر ({cr.user_id})"
            description += f"`#{index}` **{username}** — المنصة: `{cr.platform.capitalize()}`\n[رابط القناة]({cr.channel_url})\n\n"

        embed = discord.Embed(
            title="🌟 قائمة صناع المحتوى المعتمدين",
            description=description,
            color=0xffd700
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ContentCreatorsCog(bot))
  
