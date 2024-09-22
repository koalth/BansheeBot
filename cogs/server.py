import discord
from discord.ext import commands

from core import Cog, Context, ServerModel


class Server(Cog):
    """Commands related to server settings"""
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """Creates the Server model when bot joins the server"""
        exists = await ServerModel.exists(discord_guild_id=guild.id)
        if exists:
            return

        db_guild = await ServerModel.create(discord_guild_id=guild.id)
        await db_guild.save()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        """Deletes the associated server model for this server"""
        exists = await ServerModel.exists(discord_guild_id=guild.id)
        if not exists:
            return

        db_guild = await ServerModel.get(discord_guild_id=guild.id)
        await ServerModel.delete(db_guild)


def setup(bot):
    bot.add_cog(Server(bot))
