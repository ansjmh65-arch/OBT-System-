import os
import discord
from discord.ext import commands

# إعداد الصلاحيات الأساسية للبوت (Intents)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# تعريف البوت مع تحديد بادئة الأوامر (Prefix)
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"تم تسجيل الدخول بنجاح باسم: {bot.user} (ID: {bot.user.id})")
    print("البوت يعمل بكفاءة وجاهز تماماً!")

@bot.command(name="ping")
async def ping(ctx):
    """أمر تجريبي لفحص سرعة الاستجابة"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"Pong! 🏓 سرعة الاستجابة: {latency}ms")

# تشغيل البوت باستخدام متغير البيئة الآمن
if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("خطأ: لم يتم العثور على متغير البيئة DISCORD_TOKEN!")
    else:
        bot.run(TOKEN)
