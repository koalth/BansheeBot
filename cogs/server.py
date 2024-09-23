import discord
from discord.ext import commands

from core import Cog, Context, ServerModel

from loguru import logger

class Server(Cog):
    """Commands related to server settings"""

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """Creates the Server model when bot joins the server"""
        exists = await ServerModel.exists(discord_guild_id=guild.id)
        if exists:
            logger.debug("Guild already exists.")
            return

        db_guild = await ServerModel.create(discord_guild_id=guild.id)
        await db_guild.save()
        logger.info(f"Server with guild id {guild.id} created")
        return

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        """Deletes the associated server model for this server"""
        exists = await ServerModel.exists(discord_guild_id=guild.id)
        if not exists:
            logger.debug("Server does not exist.")
            return

        db_guild = await ServerModel.get(discord_guild_id=guild.id)
        await ServerModel.delete(db_guild)
        logger.info(f"Server with guild id {guild.id} deleted")
        return


def setup(bot):
    bot.add_cog(Server(bot))
