from discord.ext import commands

from .models import ServerModel
from .context import Context


class RoleNotSetError(commands.CheckFailure):
    pass


class NotRaiderError(commands.CheckFailure):
    pass


def is_raider():
    async def predicate(ctx: Context):
        guild_id = ctx._get_guild_id()
        server = await ServerModel.get(discord_guild_id=guild_id)

        if server.raider_role_id is None:
            raise RoleNotSetError()

        has_raider_role = ctx.author.get_role(server.raider_role_id) is not None  # type: ignore

        if not has_raider_role:
            raise NotRaiderError("You do not have the raider role")

        return True

    return commands.check(predicate)  # type: ignore


class NotManagerError(commands.CheckFailure):
    pass


def is_manager():
    async def predicate(ctx: Context):
        guild_id = ctx._get_guild_id()
        server = await ServerModel.get(discord_guild_id=guild_id)

        if server.raider_role_id is None:
            raise RoleNotSetError()

        has_manager_role = ctx.author.get_role(server.manager_role_id) is not None  # type: ignore

        if not has_manager_role:
            raise NotManagerError("You do not have the manager role")

        return True

    return commands.check(predicate)  # type: ignore
