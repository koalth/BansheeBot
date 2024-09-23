import discord
from discord.ext import commands, tasks

from core import Cog, Context, ServerModel, CharacterModel

from py_markdown_table.markdown_table import markdown_table

from core.bot import BansheeBot


class Raid(Cog):
    """Commands related to the raid roster"""

    def __init__(self, bot: BansheeBot) -> None:
        self.is_roster_updating = False
        self.update_task = None
        self.check_refresh_status.start()
        super().__init__(bot)

    def cog_unload(self) -> None:
        self.check_refresh_status.cancel()

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
            raider_data.append(
                {
                    "Name": raider.name,
                    "Class": raider.class_name,
                    "Spec": raider.spec_name,
                    "Item Level": raider.item_level,
                }
            )

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
            last_crawled_at=profile.last_crawled_at,
        )

        await character.save()

        return await ctx.respond(
            f"`{character.name}`-`{character.realm}` has been registered!",
            ephemeral=True,
        )

    @discord.command(name="refresh", description="Start refreshing the raider roster")
    async def start_refresh(self, ctx: Context):
        pass

    @discord.command(name="status", description="Get the status of the roster refresh")
    async def get_status(self, ctx: Context):
        pass

    @tasks.loop(minutes=30)
    async def check_refresh_status(self):
        pass

    async def refresh_characters(self):
        pass

    async def refresh_character(self):
        pass

    # @tasks.loop(minutes=30)
    # async def check_refresh_status(self, ctx: Context):
    #     if not self.update_task or self.update_task.done():
    #         guild_id = ctx._get_guild_id()
    #         server = await ServerModel.get(discord_guild_id=guild_id)
    #         if server.roster_updating:
    #             self.update_task = self.bot.loop.create_task(self.refresh_roster(ctx))

    # async def refresh_roster(self, ctx: Context):
    #     guild_id = ctx._get_guild_id()
    #     server = await ServerModel.get(discord_guild_id=guild_id).prefetch_related(
    #         "raiders"
    #     )

    #     for raider in server.raiders:
    #         char = await CharacterModel.get(id=raider.id)
    #         profile = await ctx.getCharacter(char.name, char.realm, char.region)
    #         if profile is None:
    #             continue
    #         await CharacterModel.filter(id=raider.id).update(
    #             item_level=profile.item_level,
    #             spec_name=profile.spec_name,
    #             last_crawled_at=profile.last_crawled_at,
    #         )

    #     await ServerModel.filter(id=server.id).update(roster_updating=False)

    # @discord.command(name="refresh", description="Start the refresh process")
    # async def refresh(self, ctx: Context):
    #     guild_id = ctx._get_guild_id()
    #     server = await ServerModel.get(discord_guild_id=guild_id)
    #     if server.roster_updating:
    #         return await ctx.respond("Roster is already refreshing")

    #     await ServerModel.filter(id=server.id).update(roster_updating=True)


def setup(bot):
    bot.add_cog(Raid(bot))
