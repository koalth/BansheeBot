import discord
from discord.ext import commands, tasks

from core import Cog, Context, ServerModel, CharacterModel

from py_markdown_table.markdown_table import markdown_table

from core.bot import BansheeBot


class Raid(Cog):
    """Commands related to the raid roster"""

    def get_requirement_emoji(
        self, item_level: int, item_level_requirement: int
    ) -> str:
        return "✅" if item_level >= item_level_requirement else "❌"

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
                "Class": raider.class_name,
                "Spec": raider.spec_name,
                "Item Level": raider.item_level,
            }

            if (
                server.raider_item_level_requirement is not None
                and server.raider_item_level_requirement > 0
            ):
                data.update(
                    {
                        "Meets Requirments?": self.get_requirement_emoji(
                            raider.item_level, server.raider_item_level_requirement
                        )
                    }
                )

            raider_data.append(data)

        if len(raider_data) is 0:
            return await ctx.respond("There are no raiders to display.")

        table = (
            markdown_table(raider_data)
            .set_params(row_sep="always", padding_width=5, padding_weight="centerright")
            .get_markdown()
        )
        embed = discord.Embed(title="Raid Roster", color=discord.Color.dark_gold())
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
            return await ctx.respond(f"`{name}` has already been registered")

        guild_id = ctx._get_guild_id()
        profile = await ctx.getCharacter(name, realm, region)

        if profile is None:
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

        return await ctx.respond(
            f"`{character.name}`-`{character.realm}` has been registered!",
            ephemeral=True,
        )

    @discord.command(
        name="itemlevel",
        description="Set the item level requirement for raid roster. Enter 0 to have no requirement",
    )
    async def set_item_level_requirement(self, item_level: int):
        pass


def setup(bot):
    bot.add_cog(Raid(bot))
