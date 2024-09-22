import discord

from core import Cog, Context, ServerModel, CharacterModel

from py_markdown_table.markdown_table import markdown_table


class Raid(Cog):
    """Commands related to the raid roster"""

    @discord.command(
        name="roster", description="Displays the roster of all registered characters"
    )
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

    
        table = markdown_table(raider_data).set_params(row_sep='always', padding_width=5, padding_weight='centerright').get_markdown()
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
        )

        await character.save()

        return await ctx.respond(
            f"`{character.name}`-`{character.realm}` has been registered!"
        )


def setup(bot):
    bot.add_cog(Raid(bot))
