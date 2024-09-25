from discord.ext import commands

from .bot import BansheeBot
from .context import Context
from .models import ServerModel, CharacterModel
from .api import RaiderIOClient
from .dto import Character
from .checks import is_raider, is_manager
from .services import *


class Cog(commands.Cog):

    def __init__(self, bot: BansheeBot) -> None:
        self.bot = bot
