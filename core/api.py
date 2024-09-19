from __future__ import annotations

from typing import List, Optional, Dict, TypeVar
from typing_extensions import TypedDict
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from aiolimiter import AsyncLimiter
import aiohttp
import urllib.parse

from loguru import logger


class MyBaseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class ItemResponse(MyBaseModel):
    item_id: int
    item_level: int
    enchant: Optional[int] = None
    icon: str
    name: str
    item_quality: int
    is_legendary: bool
    is_azerite_armor: bool
    gems: List[int]
    tier: Optional[str] = None
    bonuses: List[int]


class ItemsResponse(TypedDict):
    head: Optional[ItemResponse]
    neck: Optional[ItemResponse]
    shoulder: Optional[ItemResponse]
    back: Optional[ItemResponse]
    chest: Optional[ItemResponse]
    waist: Optional[ItemResponse]
    wrist: Optional[ItemResponse]
    hands: Optional[ItemResponse]
    legs: Optional[ItemResponse]
    feet: Optional[ItemResponse]
    finger1: Optional[ItemResponse]
    finger2: Optional[ItemResponse]
    trinket1: Optional[ItemResponse]
    trinket2: Optional[ItemResponse]
    mainhand: Optional[ItemResponse]
    # offhand: Optional[ItemResponse]


class GearResponse(MyBaseModel):
    updated_at: str
    item_level_equipped: int
    item_level_total: int
    items: ItemsResponse


class GuildResponse(MyBaseModel):
    name: str
    realm: str
    region: str
    faction: Optional[str] = None
    last_crawled_at: Optional[datetime] = None
    profile_url: Optional[str] = None


class CharacterResponse(MyBaseModel):
    name: str
    race: str
    character_class: str = Field(alias="class")
    active_spec_name: str
    active_spec_role: str
    gender: str
    faction: str
    achievement_points: int
    honorable_kills: int
    thumbnail_url: str
    region: str
    realm: str
    last_crawled_at: datetime
    profile_url: str
    profile_banner: str
    gear: GearResponse


ModelType = TypeVar("ModelType", bound=BaseModel)


class RaiderIOClient:

    client: aiohttp.ClientSession
    limiter: AsyncLimiter

    api_url: str = "https://raider.io/api/v1"
    rate_limit: int = 100
    timeout: int
    retries: int
    backoff_factor: int

    def __init__(self) -> None:
        self.client = aiohttp.ClientSession(base_url=self.api_url)
        self.limiter = AsyncLimiter(self.rate_limit)

    def _create_url(
        self, endpoint: str, params: Optional[Dict[str, str]] = None
    ) -> str:
        if params is not None:
            endpoint = f"{endpoint}?{urllib.parse.urlencode(params)}"

        return endpoint

    async def _fetch_response(
        self, endpoint: str, model_cls: type[ModelType]
    ) -> ModelType:
        async with self.client.get(endpoint) as response:
            assert response.status == 200
            data = await response.json()
            return model_cls(**data)

    async def _get(
        self,
        endpoint: str,
        model_cls: type[ModelType],
        params: Optional[Dict[str, str]] = None,
    ) -> Optional[ModelType]:
        try:
            async with self.limiter:
                endpoint = self._create_url(endpoint, params)
                return await self._fetch_response(endpoint, model_cls)
        except Exception as err:
            logger.error(
                f"There was an error requesting endpoint {endpoint} with params: {params}. Error: {err}"
            )
            return None

    async def getCharacterProfile(
        self, name: str, realm: str, region: str
    ) -> CharacterResponse:
        params = {"region": region, "realm": realm, "name": name, "fields": "gear"}

        response = await self._get("character/profile", CharacterResponse, params)

        if response is None:
            logger.error("Response was none")
            raise Exception("Response was none")

        return response
