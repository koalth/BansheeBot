from discord.ext import commands

from .bot import BansheeBot
from .context import Context
from .models import ServerModel, CharacterModel


class Cog(commands.Cog):

    def __init__(self, bot: BansheeBot) -> None:
        self.bot = bot
