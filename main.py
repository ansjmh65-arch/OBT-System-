"""
OBT System - بوت عربي متكامل
Full-featured Arabic Discord bot with permission tiers, anti-raid, XP, economy, and games.
"""

import discord
from discord.ext import commands
import asyncio
import os
import sys
import logging
from database import Database

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('obt_system.log', encoding='utf-8')
    ]
)
logger = logging.getLogger('OBT')

# Bot intents — enable in Discord Developer Portal:
# Server Members Intent + Message Content Intent
intents = discord.Intents.default()
intents.members = True           # welcome/goodbye, auto-role, anti-raid tracking
intents.message_content = True   # prefix commands, XP tracking, protection, games


class OBTSystem(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=self.get_prefix,
            intents=intents,
            help_command=None,
            application_id=int(os.getenv('BOT_APP_ID', '0')) or None
        )
        self.db = Database()
        self.logger = logger

    async def get_prefix(self, message):
        if not message.guild:
            return '!'
        prefix = await self.db.get_prefix(message.guild.id)
        return prefix or '!'

    async def setup_hook(self):
        await self.db.init()

        cogs = [
            # Core systems
            'cogs.anti_raid',        # Load first — other cogs call raid_tracker
            'cogs.moderation',
            'cogs.logs',
            'cogs.protection',
            'cogs.tickets',
            'cogs.points',
            # New systems
            'cogs.leveling',
            'cogs.economy',
            'cogs.fun',
            # Existing systems
            'cogs.clans',
            'cogs.content_creators',
            'cogs.general',
            'cogs.interactions',
            'cogs.settings',
        ]

        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f'✅ تم تحميل: {cog}')
            except Exception as e:
                logger.error(f'❌ فشل تحميل {cog}: {e}')
                import traceback
                traceback.print_exc()

        # Sync slash commands
        try:
            synced = await self.tree.sync()
            logger.info(f'🔄 تمت مزامنة {len(synced)} أمر Slash')
        except Exception as e:
            logger.error(f'❌ فشل مزامنة الأوامر: {e}')

    async def on_ready(self):
        logger.info(f'🚀 OBT System جاهز | {self.user} ({self.user.id})')
        logger.info(f'📊 متصل بـ {len(self.guilds)} سيرفر')

        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name='🛡️ OBT System | /مساعدة'
            ),
            status=discord.Status.online
        )

    async def on_guild_join(self, guild):
        await self.db.ensure_guild(guild.id)
        logger.info(f'➕ انضم البوت إلى: {guild.name} ({guild.id})')

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title='❌ خطأ في الصلاحيات',
                description='ليس لديك صلاحية استخدام هذا الأمر.',
                color=0xFF0000
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                title='❌ البوت يفتقر للصلاحيات',
                description='البوت لا يملك الصلاحيات الكافية.',
                color=0xFF0000
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(
                title='❌ عضو غير موجود',
                description='لم يتم العثور على العضو المذكور.',
                color=0xFF0000
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title='❌ خطأ في الأمر',
                description='خطأ في الوسائط. تحقق من الصيغة الصحيحة.',
                color=0xFF0000
            )
            await ctx.send(embed=embed)
        else:
            logger.error(f'خطأ في أمر: {error}')


async def main():
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error('❌ لم يتم تعيين DISCORD_TOKEN في المتغيرات البيئية!')
        sys.exit(1)

    bot = OBTSystem()
    async with bot:
        await bot.start(token)


if __name__ == '__main__':
    asyncio.run(main())
