import discord
from discord.ext import commands, tasks

from core import Cog, Context, ServerModel, CharacterModel

from py_markdown_table.markdown_table import markdown_table

from loguru import logger


class Raid(Cog):
    """Commands related to the raid roster"""

    def get_requirement_emoji(
        self, item_level: int, item_level_requirement: int
    ) -> str:
        return " " if item_level >= item_level_requirement else "X"

    @discord.command(
        name="roster", description="Displays the roster of all registered characters"
    )
    @commands.is_owner()
    @commands.guild_only()
    async def roster(self, ctx: Context):
        guild_id = ctx._get_guild_id()
        server = await ServerModel.get(discord_guild_id=guild_id).prefetch_related(
            "raiders"
        )

        raider_data = []
        for raider in server.raiders:

            data = {
                "Name": raider.name,
                "Class/Spec": f"{raider.class_name}/{raider.spec_name}",
                "Item Level": raider.item_level,
            }

            if (
                server.raider_item_level_requirement is not None
                and server.raider_item_level_requirement > 0
            ):
                data.update(
                    {
                        "Requirements?": self.get_requirement_emoji(
                            raider.item_level, server.raider_item_level_requirement
                        )
                    }
                )

            raider_data.append(data)

        if len(raider_data) == 0:
            return await ctx.respond("There are no raiders to display.")

        table = (
            markdown_table(raider_data)
            .set_params(row_sep="always", padding_width=5, padding_weight="centerright")
            .get_markdown()
        )
        embed = discord.Embed(
            title="Raid Roster",
            color=discord.Color.dark_gold(),
        )

        embed.add_field(name="Raiders", value=table)

        embed.set_footer(text="Data from Raider.io")

        return await ctx.respond(embed=embed)

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


def setup(bot):
    bot.add_cog(Raid(bot))
