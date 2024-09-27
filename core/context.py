from os import getenv
import dotenv

from typing import Optional

import discord
from discord import ApplicationContext, Color, Embed
from discord.utils import utcnow

from .dto import Character
from .api import RaiderIOClient

from loguru import logger


class Context(ApplicationContext):

    async def getCharacter(
        self, name: str, realm: str, region: str
    ) -> Optional[Character]:
        try:
            client = RaiderIOClient()

            character_response = await client.getCharacterProfile(name, realm, region)
            return Character(
                name=character_response.name,
                realm=character_response.realm,
                region=character_response.region,
                char_class=character_response.character_class,
                item_level=character_response.gear.item_level_equipped,
                profile_url=character_response.profile_url,
                thumbnail_url=character_response.thumbnail_url,
                spec_name=character_response.active_spec_name,
                last_crawled_at=character_response.last_crawled_at
            )
        except Exception as err:
            logger.error(f"Error getting character: {err}")
            return None

    def _get_guild(self) -> discord.Guild:
        guild = self.guild
        assert type(guild) is discord.Guild
        return guild

    def _get_guild_id(self) -> int:
        guild = self._get_guild()
        return guild.id

    def _has_role(self, role_id: int) -> bool:
        return self.author.get_role(role_id) is not None  # type: ignore

    async def success(self, title: str, description: str | None = None, **kwargs):
        embed = Embed(
            title=title,
            description=description,
            timestamp=utcnow(),
            color=Color.green(),
        )

        return await self.respond(embed=embed, **kwargs)

    async def exception(self, title: str, description: str | None = None, **kwargs):
        embed = Embed(
            title=title, description=description, timestamp=utcnow(), color=Color.red()
        )

        return await self.respond(embed=embed, **kwargs)

    async def info(self, title: str, description: str | None = None, **kwargs):
        embed = Embed(
            title=title, description=description, timestamp=utcnow(), color=Color.blue()
        )

        return await self.respond(embed=embed, **kwargs)
