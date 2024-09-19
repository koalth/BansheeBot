import discord

from core import Cog, Context, ServerModel, CharacterModel


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

        raider_names = "\n".join([raider.name for raider in server.raiders])
        class_specs = "\n".join(
            [f"{raider.class_name}/{raider.spec_name}" for raider in server.raiders]
        )
        item_levels = "\n".join([str(raider.item_level) for raider in server.raiders])

        embed = discord.Embed(title="Raid Roster", color=discord.Color.dark_gold())

        embed.add_field(name="Raiders", value=raider_names, inline=True)
        embed.add_field(name="Class/Spec", value=class_specs, inline=True)
        embed.add_field(name="Item Level", value=item_levels, inline=True)

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
