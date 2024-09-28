import discord
from discord.ext import commands, tasks

from core import (
    Cog,
    Context,
    ServerModel,
    CharacterModel,
    is_raider,
    is_manager,
    create_character,
    delete_character,
    character_exists,
    server_has_raiders,
    get_raiders,
    get_item_level_requirement,
)
from views import RosterEmbed

from py_markdown_table.markdown_table import markdown_table

from loguru import logger


class Raid(Cog):
    """Commands related to the raid roster"""

    @discord.command(
        name="register",
        description="Register your World of Warcraft character to be tracked for raid",
    )
    @discord.option(name="name", description="Name of your World of Warcraft character")
    @discord.option(
        name="realm", description="Realm of the World of Warcraft character"
    )
    @commands.guild_only()
    @commands.check_any(commands.is_owner(), is_manager(), is_raider())  # type: ignore
    async def register(self, ctx: Context, name: str, realm: str, region: str = "us"):

        # check if character already exists
        exists = await character_exists(name, realm)
        if exists:
            logger.debug(f"Character already exists")
            return await ctx.respond(
                f"`{name}` has already been registered",
                ephemeral=True,
            )

        guild_id = ctx._get_guild_id()
        profile = await ctx.getCharacter(name, realm, region)

        if profile is None:
            logger.debug(f"Character profile was none")
            return await ctx.respond(f"Character was not found")

        await create_character(profile, guild_id, ctx.author.id)

        return await ctx.respond(
            f"`{profile.name}`-`{profile.realm}` has been registered!",
            ephemeral=True,
        )

    @discord.command(
        name="remove", description="Remove a character from the raid roster"
    )
    @commands.guild_only()
    @commands.check_any(commands.is_owner(), is_manager())  # type: ignore
    async def remove_character(self, ctx: Context, name: str, realm: str):

        if not await character_exists(name, realm):
            return await ctx.respond(
                f"Character does not exist",
                ephemeral=True,
            )

        await delete_character(name, realm, ctx._get_guild_id())
        return await ctx.respond("Character has been deleted", ephemeral=True)

    # roster_group = discord.SlashCommandGroup(
    #     name="roster", description="Commands related to roster"
    # )

    @discord.command(name="roster", description="Display the raid roster")
    @commands.check_any(commands.is_owner(), is_manager())  # type: ignore
    async def raid_roster(self, ctx: Context):
        guild_id = ctx._get_guild_id()

        if not await server_has_raiders(guild_id):
            return await ctx.respond("There are no raiders.", ephemeral=True)

        raiders = await get_raiders(guild_id)

        roster_embed = RosterEmbed(raiders)  # type: ignore

        item_level_req = await get_item_level_requirement(guild_id)

        roster_embed = roster_embed.raid_roster(item_level_req)

        return await ctx.respond(embed=roster_embed)

    # @roster_group.command(
    #     name="details", description="Show the roster with more details"
    # )
    # @commands.check_any(commands.is_owner(), is_manager())  # type: ignore
    # async def roster_detail(self, ctx: Context):
    #     return await ctx.respond(
    #         "Hello I am the roster with more details. You need to be a raider to use this"
    #     )


def setup(bot):
    bot.add_cog(Raid(bot))
