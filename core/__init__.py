from discord.ext import commands

from .bot import BansheeBot
from .context import Context
from .models import ServerModel, CharacterModel
from .api import RaiderIOClient
from .dto import Character
from .services import is_raider, is_manager


class Cog(commands.Cog):

    def __init__(self, bot: BansheeBot) -> None:
        self.bot = bot
