import discord
from discord.utils import get
from typing import Optional

from core import Cog, Context, ServerModel, CharacterModel


class Raid(Cog):
    """Commands related to the raid roster"""

    @discord.command(
        name="roster", description="Displays the roster of all registered characters"
    )
    async def roster(self, ctx: Context):
        pass

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
        pass


def setup(bot):
    bot.add_cog(Raid(bot))
