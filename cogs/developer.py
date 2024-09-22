import discord
from discord.ext import commands

from core import Cog, Context, ServerModel


class Developer(Cog):
    """Commands related to developer commands"""

    @discord.command(
        name="init", description="Initializes the server model for the current server"
    )
    @commands.is_owner()
    @commands.guild_only()
    async def init(self, ctx: Context):
        guild_id = ctx.guild_id
        exists = await ServerModel.exists(discord_guild_id=guild_id)
        if exists:
            return

        db_guild = await ServerModel.create(discord_guild_id=guild_id)
        await db_guild.save()

        await ctx.respond("Server has been initialized", ephemeral=True)


def setup(bot):
    bot.add_cog(Developer(bot))
