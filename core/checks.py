from discord.ext import commands

from .models import ServerModel
from .context import Context
from .services import get_manager_role_id, get_raider_role_id


class RoleNotSetError(commands.CheckFailure):
    pass


class NotRaiderError(commands.CheckFailure):
    pass


def is_raider():
    async def predicate(ctx: Context):
        guild_id = ctx._get_guild_id()
        server_raider_role_id = await get_raider_role_id(guild_id)

        if server_raider_role_id is None:
            raise RoleNotSetError()

        if not ctx._has_role(server_raider_role_id):
            raise NotRaiderError("You do not have the raider role")

        return True

    return commands.check(predicate)  # type: ignore


class NotManagerError(commands.CheckFailure):
    pass


def is_manager():
    async def predicate(ctx: Context):
        guild_id = ctx._get_guild_id()
        server_manager_role_id = await get_manager_role_id(guild_id)

        if server_manager_role_id is None:
            raise RoleNotSetError()

        if not ctx._has_role(server_manager_role_id):
            raise NotManagerError("You do not have the manager role")

        return True

    return commands.check(predicate)  # type: ignore
