from discord.ext import commands

def is_guild_admin():
    async def predicate(ctx: commands.Context):
        return ctx.author.guild_permissions.administrator
    return commands.check(predicate)
  
