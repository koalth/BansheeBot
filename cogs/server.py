import discord
from discord.ext import commands
from discord import option

from core import (
    Cog,
    Context,
    ServerModel,
    is_manager,
    set_manager_role,
    set_item_level_requirement,
    set_raider_role,
    create_server,
    delete_server,
)

from loguru import logger


class Server(Cog):
    """Commands related to server settings"""

    @discord.command(name="setmanager", description="Set the manager role for the bot")
    @option("role", discord.Role, description="Enter the manager role")
    @commands.is_owner()
    async def set_manager(self, ctx: Context, role: discord.Role):
        guild_id = ctx._get_guild_id()

        await set_manager_role(guild_id, role.id)
        return await ctx.respond(f"Manager role has been set!", ephemeral=True)

    @discord.command(name="setraider", description="Set the raider role for the bot")
    @option("role", discord.Role, description="Enter the raider role")
    @commands.is_owner()
    async def set_raider_role(self, ctx: Context, role: discord.Role):
        guild_id = ctx._get_guild_id()

        await set_raider_role(guild_id, role.id)

        return await ctx.respond(f"Raider role has been set!", ephemeral=True)

    @discord.command(
        name="setitemlevelrequirement",
        description="Set the item level requirement for the raid. Put 0 to remove the requirement.",
    )
    @option("itemlevel", description="Item level requirement for the raid roster")
    @commands.is_owner()
    async def set_item_level_requirement(self, ctx: Context, itemlevel: int):
        guild_id = ctx._get_guild_id()
        await set_item_level_requirement(guild_id, itemlevel)
        return await ctx.respond(
            f"Item level requirement has been set to `{itemlevel}`", ephemeral=True
        )

    @discord.command(name="set")
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """Creates the Server model when bot joins the server"""
        await create_server(guild.id)
        logger.info(f"Server with guild id {guild.id} created")
        return

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        """Deletes the associated server model for this server"""
        await delete_server(guild.id)
        logger.info(f"Server with guild id {guild.id} deleted")
        return


def setup(bot):
    bot.add_cog(Server(bot))
