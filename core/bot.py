from os import environ, getenv
from dotenv import load_dotenv

import discord
from discord.ext import commands
from tortoise import Tortoise

from .context import Context
from .models import ServerModel, CharacterModel

load_dotenv()

from loguru import logger


class BansheeBot(commands.Bot):

    def __init__(self) -> None:
        super().__init__(
            intents=discord.Intents(
                guilds=True,
                messages=True,
                guild_messages=True,
                message_content=True,
                members=True,
            )
        )

    async def get_application_context(
        self, interaction: discord.Interaction
    ) -> Context:
        return Context(self, interaction)

    async def setup_tortoise(self) -> None:
        await Tortoise.init(
            db_url="sqlite://data/database.db", modules={"models": ["core.models"]}
        )
        await Tortoise.generate_schemas()

    async def setup_logger(self) -> None:
        logger.add("discord_{time}.log", rotation="1 day", enqueue=True)

    async def start(self, token: str, *, reconnect: bool = True) -> None:
        await self.setup_tortoise()
        await self.setup_logger()
        return await super().start(token, reconnect=reconnect)

    async def close(self) -> None:
        await Tortoise.close_connections()
        return await super().close()

    def run(self, debug: bool = False) -> None:
        default_cog_list = [
            "cogs.raid",
            "cogs.server",
            "cogs.developer",
            "cogs.refresh",
        ]
        for cog in default_cog_list:
            self.load_extension(cog)
            logger.info(f"{cog} loaded")

        token = getenv("DISCORD_TOKEN")
        if token is None:
            raise Exception("Token was not found")

        super().run(token)

    async def on_application_command_error(
        self, context: discord.ApplicationContext, error: Exception
    ) -> None:
        await context.respond(
            embed=discord.Embed(
                title=error.__class__.__name__,
                description=str(error),
                color=discord.Color.red(),
            ),
            ephemeral=True,
        )
