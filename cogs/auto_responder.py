import discord
from discord.ext import commands

class AutoResponderCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # قاعدة بيانات تخزين مؤقت للردود التلقائية الخاصة بالسيرفرات
        self.responses = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        guild_id = message.guild.id
        content = message.content.lower()

        # التحقق من وجود ردود مخصصة لهذا السيرفر
        if guild_id in self.responses:
            for trigger, reply in self.responses[guild_id].items():
                if trigger in content:
                    await message.channel.send(reply)
                    break

    # 1. إضافة رد تلقائي جديد (Add Auto Response)
    @commands.command(name="addresponse", aliases=["اضافة_رد"])
    @commands.has_permissions(administrator=True)
    async def add_response(self, ctx, trigger: str, *, reply: str):
        guild_id = ctx.guild.id
        
        if guild_id not in self.responses:
            self.responses[guild_id] = {}

        self.responses[guild_id][trigger.lower()] = reply

        embed = discord.Embed(
            title="🤖 تم إضافة الرد التلقائي بنجاح",
            description=f"**الكلمة المفتاحية:** `{trigger}`\n**رد البوت:** {reply}",
            color=0x23a55a
        )
        await ctx.send(embed=embed)

    # 2. حذف رد تلقائي (Remove Auto Response)
    @commands.command(name="deleteresponse", aliases=["حذف_رد"])
    @commands.has_permissions(administrator=True)
    async def delete_response(self, ctx, trigger: str):
        guild_id = ctx.guild.id
        trigger_lower = trigger.lower()

        if guild_id in self.responses and trigger_lower in self.responses[guild_id]:
            del self.responses[guild_id][trigger_lower]
            await ctx.send(f"✅ تم حذف الرد التلقائي للكلمة: `{trigger}` بنجاح.")
        else:
            await ctx.send(f"❌ لم يتم العثور على رد تلقائي مسجل لهذه الكلمة المفتاحية.")

    # 3. عرض قائمة الردود التلقائية (List Responses)
    @commands.command(name="responses", aliases=["الردود_التلقائية"])
    async def list_responses(self, ctx):
        guild_id = ctx.guild.id

        if guild_id not in self.responses or not self.responses[guild_id]:
            await ctx.send("❌ لا توجد أي ردود تلقائية مسجلة في هذا السيرفر حالياً.")
            return

        description = ""
        for index, (trigger, reply) in enumerate(self.responses[guild_id].items(), start=1):
            description += f"`#{index}` **الكلمة:** `{trigger}`\n**الرد:** {reply}\n\n"

        embed = discord.Embed(
            title="🤖 قائمة الردود التلقائية في السيرفر",
            description=description,
            color=0x5865F2
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AutoResponderCog(bot))
  
