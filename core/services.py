from loguru import logger

from typing import Optional

from .models import ServerModel, CharacterModel
from .dto import Character


# Server
async def set_manager_role(guild_id: int, role_id: int) -> None:
    logger.info(f"Setting manager role {role_id}")
    await ServerModel.filter(discord_guild_id=guild_id).update(manager_role_id=role_id)


async def set_raider_role(guild_id: int, role_id: int) -> None:
    logger.info(f"Setting raider role {role_id}")
    await ServerModel.filter(discord_guild_id=guild_id).update(raider_role_id=role_id)


async def server_exists(guild_id: int) -> bool:
    return await ServerModel.exists(discord_guild_id=guild_id)


async def create_server(guild_id: int):
    if server_exists(guild_id):
        logger.debug(f"Server {guild_id} already exists, cannot create.")
        return

    db_guild = await ServerModel.create(discord_guild_id=guild_id)
    await db_guild.save()
    logger.info(f"Server {guild_id} has been created")


async def delete_server(guild_id: int):
    if not server_exists(guild_id):
        logger.debug(f"Server {guild_id} does not exists, cannot delete.")
        return

    db_guild = await ServerModel.get(discord_guild_id=guild_id)
    await ServerModel.delete(db_guild)
    logger.info(f"Server {guild_id} has been deleted")


async def get_server(guild_id: int) -> ServerModel:
    return await ServerModel.get(discord_guild_id=guild_id)


async def get_server_with_raiders(guild_id: int) -> ServerModel:
    return await ServerModel.get(discord_guild_id=guild_id).prefetch_related("raiders")


async def set_item_level_requirement(guild_id: int, item_level_requirement: int):
    logger.info(f"Setting item level requirement to {item_level_requirement}")
    await ServerModel.filter(discord_guild_id=guild_id).update(
        raider_item_level_requirement=item_level_requirement
    )


async def get_item_level_requirement(guild_id: int) -> Optional[int]:
    server = await get_server(guild_id)
    return server.raider_item_level_requirement


async def server_has_raiders(guild_id: int) -> bool:
    server = await ServerModel.get(discord_guild_id=guild_id).prefetch_related(
        "raiders"
    )

    return len(server.raiders) > 0


async def get_raiders(guild_id: int):
    server = await ServerModel.get(discord_guild_id=guild_id).prefetch_related(
        "raiders"
    )

    return server.raiders


async def get_manager_role_id(guild_id: int) -> Optional[int]:
    server = await get_server(guild_id)
    return server.manager_role_id if server.manager_role_id is not None else None


async def get_raider_role_id(guild_id: int) -> Optional[int]:
    server = await get_server(guild_id)
    return server.raider_role_id if server.raider_role_id is not None else None


# Character
async def character_exists(name: str, realm: str) -> bool:
    return await CharacterModel.exists(name=name, realm=realm)


async def create_character(
    character: Character, guild_id: int, author_id: int
) -> Character:

    server = await get_server(guild_id)

    db_character = CharacterModel(
        discord_user_id=author_id,
        name=character.name,
        realm=character.realm,
        region=character.region,
        item_level=character.item_level,
        class_name=character.char_class,
        spec_name=character.spec_name,
        profile_url=character.profile_url,
        thumbnail_url=character.thumbnail_url,
        raid_roster_id=server.id,
        raiderio_last_crawled_at=character.last_crawled_at,
    )

    await db_character.save()
    logger.info(f"Character {character.name}-{character.realm} has been created")

    return character


async def delete_character(name: str, realm: str, guild_id: int):
    server = await ServerModel.get(discord_guild_id=guild_id)

    if not (
        await CharacterModel.exists(name=name, realm=realm, raid_roster_id=server.id)
    ):
        logger.debug(f"Character {name}-{realm} was not found, cannot delete.")
        return

    db_char = await CharacterModel.get(name=name, realm=realm, raid_roster_id=server.id)
    await CharacterModel.delete(db_char)
    logger.info(f"Character {name}-{realm} was successfully deleted")
