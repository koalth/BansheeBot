import discord
from discord.ext import commands, tasks

from core import Cog, Context, ServerModel, CharacterModel, is_raider, is_manager
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
    @discord.option(
        name="region",
        description="Region of the World of Warcraft character",
        choices=["us"],
    )
    @commands.guild_only()
    async def register(self, ctx: Context, name: str, realm: str, region: str):

        # check if character already exists
        exists = await CharacterModel.exists(name=name, realm=realm)

        if exists:
            logger.debug(f"Character already exists")
            return await ctx.respond(f"`{name}` has already been registered")

        guild_id = ctx._get_guild_id()
        profile = await ctx.getCharacter(name, realm, region)

        if profile is None:
            logger.debug(f"Character profile was none")
            return await ctx.respond(f"Character was not found")

        server = await ServerModel.get(discord_guild_id=guild_id)

        character = CharacterModel(
            discord_user_id=ctx.author.id,
            name=profile.name,
            realm=profile.realm,
            region=profile.region,
            item_level=profile.item_level,
            class_name=profile.char_class,
            spec_name=profile.spec_name,
            profile_url=profile.profile_url,
            thumbnail_url=profile.thumbnail_url,
            raid_roster_id=server.id,
            raiderio_last_crawled_at=profile.last_crawled_at,
        )

        await character.save()
        logger.info(f"Character {character.name} saved")
        return await ctx.respond(
            f"`{character.name}`-`{character.realm}` has been registered!",
            ephemeral=True,
        )

    @discord.command(
        name="itemlevel",
        description="Set the item level requirement for raid roster. Enter 0 to have no requirement",
    )
    @commands.guild_only()
    @commands.is_owner()
    async def set_item_level_requirement(self, ctx: Context, item_level: int):
        guild_id = ctx._get_guild_id()

        if item_level == 0:
            await ServerModel.filter(discord_guild_id=guild_id).update(
                raider_item_level_requirement=None
            )
        else:
            await ServerModel.filter(discord_guild_id=guild_id).update(
                raider_item_level_requirement=item_level
            )

        return await ctx.respond(
            f"Item level requirement has been set to `{item_level}`!", ephemeral=True
        )

    @discord.command(
        name="remove", description="Remove a character from the raid roster"
    )
    @commands.guild_only()
    @commands.is_owner()
    async def remove_character(self, ctx: Context, name: str, realm: str):
        exists = await CharacterModel.exists(name=name, realm=realm)

        # TODO will need to add the guild_id too to make sure we can't delete a character from another server

        if not exists:
            return await ctx.respond(f"Character does not exist")

        db_char = await CharacterModel.get(name=name, realm=realm)
        await CharacterModel.delete(db_char)
        return await ctx.respond("Character has been deleted", ephemeral=True)

    roster_group = discord.SlashCommandGroup(
        name="roster", description="Commands related to roster"
    )

    @roster_group.command(name="raid", description="Display the raid roster")
    @is_manager()
    async def raid_roster(self, ctx: Context):
        guild_id = ctx._get_guild_id()
        server = await ServerModel.get(discord_guild_id=guild_id).prefetch_related(
            "raiders"
        )

        if len(server.raiders) == 0:
            return await ctx.respond("There are no raiders.", ephemeral=True)

        roster_embed = RosterEmbed(server.raiders)  # type: ignore

        if server.raider_item_level_requirement:
            roster_embed = roster_embed.raid_roster(
                server.raider_item_level_requirement
            )
        else:
            return await ctx.respond(
                "There is no set item level requirements", ephemeral=True
            )

        return await ctx.respond(embed=roster_embed)

    @roster_group.command(
        name="details", description="Show the roster with more details"
    )
    async def roster_detail(self, ctx: Context):
        return await ctx.respond(
            "Hello I am the roster with more details. You need to be a raider to use this"
        )


def setup(bot):
    bot.add_cog(Raid(bot))
