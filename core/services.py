from discord.ext import commands

from .models import ServerModel
from .context import Context


def is_raider():
    async def predicate(ctx: Context):
        guild_id = ctx._get_guild_id()
        server = await ServerModel.get(discord_guild_id=guild_id)
        assert server.raider_role_id

        has_raider_role = ctx.author.get_role(server.raider_role_id) is not None  # type: ignore

        if has_raider_role:
            return True

        return False

    return commands.check(predicate)  # type: ignore


def is_manager():
    async def predicate(ctx: Context):
        guild_id = ctx._get_guild_id()
        server = await ServerModel.get(discord_guild_id=guild_id)
        assert server.manager_role_id

        has_manager_role = ctx.author.get_role(server.manager_role_id) is not None  # type: ignore

        if has_manager_role:
            return True

        return False

    return commands.check(predicate)  # type: ignore
