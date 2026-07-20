import os
from threading import Thread
import discord
from discord.ext import commands
from flask import Flask

# جلب التوكن من بيئة النظام بشكل سري لكي لا يكتشفه GitHub
TOKEN = os.getenv("DISCORD_TOKEN")

app = Flask(__name__)


@app.route("/")
def home():
  return "<h3>Bot & Dashboard are Running! 🚀</h3>"


def run_flask():
  app.run(host="0.0.0.0", port5000, debug=False, use_reloader=False)


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
  print(f"تم تسجيل الدخول بنجاح باسم: {bot.user.name}")


@bot.command(name="ping")
async def ping(ctx):
  latency = round(bot.latency * 1000)
  await ctx.send(f"Pong! 🏓 سرعة الاستجابة: `{latency}ms`")


if __name__ == "__main__":
  flask_thread = Thread(target=run_flask)
  flask_thread.daemon = True
  flask_thread.start()

  if not TOKEN:
    print(
        "خطأ: لم يتم العثور على التوكن. تأكد من إضافته كمتغير بيئة في نظامك."
    )
  else:
    bot.run(TOKEN)
