# -*- coding: utf-8 -*-

import json
import uuid
from datetime import datetime

import discord
from discord.ext import commands

from models import db, BackupModel, BackupRestoreLogModel


class BackupCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    def collect_backup(self, guild):

        data = {

            "name": guild.name,

            "roles": [],

            "channels": []

        }


        # حفظ الرتب

        for role in guild.roles:

            if role.is_default():
                continue

            data["roles"].append({

                "name": role.name,

                "color": role.color.value,

                "permissions": role.permissions.value,

                "position": role.position

            })


        # حفظ القنوات

        for channel in guild.channels:


            item = {

                "name": channel.name,

                "type": str(channel.type),

                "position": channel.position

            }


            if hasattr(channel, "category") and channel.category:

                item["category"] = channel.category.name


            data["channels"].append(item)


        return data



    @commands.command(
        name="backup-create"
    )
    @commands.has_permissions(
        administrator=True
    )
    async def create_backup(
        self,
        ctx
    ):


        data = self.collect_backup(
            ctx.guild
        )


        backup_id = str(
            uuid.uuid4()
        )


        backup = BackupModel(

            guild_id=str(ctx.guild.id),

            backup_id=backup_id,

            name="Server Backup",

            created_by=str(ctx.author.id),

            data=json.dumps(data),

            size=len(
                json.dumps(data)
            ),

            status="completed"

        )


        db.session.add(
            backup
        )

        db.session.commit()



        await ctx.send(
            f"✅ تم إنشاء النسخة الاحتياطية\nID: `{backup_id}`"
        )



    @commands.command(
        name="backup-list"
    )
    @commands.has_permissions(
        administrator=True
    )
    async def backup_list(
        self,
        ctx
    ):


        backups = BackupModel.query.filter_by(
            guild_id=str(ctx.guild.id)
        ).all()


        if not backups:

            await ctx.send(
                "لا توجد نسخ احتياطية."
            )

            return



        embed = discord.Embed(
            title="💾 النسخ الاحتياطية",
            color=0x5865F2
        )


        for backup in backups:

            embed.add_field(

                name=backup.backup_id[:8],

                value=f"الحالة: {backup.status}",

                inline=False

            )


        await ctx.send(
            embed=embed
        )



    @commands.command(
        name="backup-delete"
    )
    @commands.has_permissions(
        administrator=True
    )
    async def delete_backup(
        self,
        ctx,
        backup_id
    ):


        backup = BackupModel.query.filter_by(
            backup_id=backup_id,
            guild_id=str(ctx.guild.id)
        ).first()


        if not backup:

            await ctx.send(
                "❌ النسخة غير موجودة"
            )

            return


        db.session.delete(
            backup
        )

        db.session.commit()


        await ctx.send(
            "✅ تم حذف النسخة الاحتياطية"
        )



async def setup(bot):

    await bot.add_cog(
        BackupCog(bot)
    )
