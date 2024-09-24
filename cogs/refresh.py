import discord
from discord.ext import commands, tasks

from core import Cog, Context, ServerModel, CharacterModel, RaiderIOClient, Character

from core.bot import BansheeBot
import asyncio

from loguru import logger


class Refresh(Cog):
    """Commands and tasks relating to refreshing the raid roster"""

    def __init__(self, bot: BansheeBot):
        self.is_refreshing = False
        self.refresh_task = None
        self.check_refresh_status.start()
        super().__init__(bot)

    def cog_unload(self) -> None:
        self.check_refresh_status.cancel()

    @discord.command(
        name="refresh",
        description="Refresh the characters on the roster with the latest data from RaiderIO",
    )
    @commands.is_owner()
    @commands.guild_only()
    async def refresh(self, ctx: Context):
        if self.is_refreshing:
            return await ctx.respond("Roster is already refreshing")

        guild_id = ctx._get_guild_id()
        await ServerModel.filter(discord_guild_id=guild_id).update(roster_updating=True)
        self.refresh_task = self.bot.loop.create_task(self.refresh_roster(guild_id))
        return await ctx.respond(
            "Roster refresh is started in the background", ephemeral=True
        )

    @discord.command(
        name="status", description="Get the status of the current roster refresh"
    )
    @commands.is_owner()
    @commands.guild_only()
    async def status(self, ctx: Context):
        guild_id = ctx._get_guild_id()
        server = await ServerModel.get(discord_guild_id=guild_id)
        status = "in progress" if server.roster_updating else "not running"
        return await ctx.respond(
            f"Roster refresh status is currently {status}.", ephemeral=True
        )

    @tasks.loop(minutes=5)
    async def check_refresh_status(self):
        logger.debug("Checking refresh status")
        try:
            for guild in self.bot.guilds:
                server = await ServerModel.get(discord_guild_id=guild.id)
                if server.roster_updating and (
                    not self.refresh_task or self.refresh_task.done()
                ):
                    logger.info("Creating task to refresh roster")
                    self.refresh_task = self.bot.loop.create_task(
                        self.refresh_roster(guild.id)
                    )
        except Exception as err:
            logger.debug(f"Error during checking refresh status: {err}")

    @check_refresh_status.before_loop
    async def before_check_refresh_status(self):
        logger.info("Waiting for bot to check refresh status...")
        await self.bot.wait_until_ready()

    async def refresh_roster(self, guild_id: int):
        try:
            server = await ServerModel.get(discord_guild_id=guild_id).prefetch_related(
                "raiders"
            )
            for raider in server.raiders:
                await self.refresh_character(raider)
                await asyncio.sleep(1)

        except Exception as err:
            logger.error(f"An error has occurred during refresh: {err}")
        finally:
            await ServerModel.filter(discord_guild_id=guild_id).update(
                roster_updating=False
            )

    async def refresh_character(self, character: CharacterModel):
        try:
            client = RaiderIOClient()

            character_response = await client.getCharacterProfile(
                character.name, character.realm, character.region
            )

            profile = Character(
                name=character_response.name,
                realm=character_response.realm,
                region=character_response.region,
                char_class=character_response.character_class,
                item_level=character_response.gear.item_level_equipped,
                profile_url=character_response.profile_url,
                thumbnail_url=character_response.thumbnail_url,
                spec_name=character_response.active_spec_name,
                last_crawled_at=character_response.last_crawled_at,
            )

            char = await CharacterModel.get(id=character.id)
            await CharacterModel.filter(id=character.id).update(
                item_level=profile.item_level,
                spec_name=profile.spec_name,
                raiderio_last_crawled_at=profile.last_crawled_at,
            )

            logger.info(f"Character {char.name} refreshed")

            await char.save()
        except Exception as err:
            print(f"Error updating character {character.name}: {err}")


def setup(bot):
    bot.add_cog(Refresh(bot))
