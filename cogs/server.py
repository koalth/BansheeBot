import discord
from discord.ext import commands

from core import Cog, Context, ServerModel


class Server(Cog):
    """Commands related to server settings"""

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        pass

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        pass


def setup(bot):
    bot.add_cog(Server(bot))
