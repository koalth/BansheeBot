import discord

from typing import List, Optional

from core import CharacterModel

from py_markdown_table.markdown_table import markdown_table


class RosterEmbed:

    def __init__(self, raiders: List[CharacterModel]):
        self.raiders = raiders

    def _get_requirement_emoji(
        self, item_level: int, item_level_requirement: int
    ) -> str:
        return " " if item_level >= item_level_requirement else "X"

    def _defaults(self) -> discord.Embed:
        embed = discord.Embed(color=discord.Color.dark_gold())
        embed.set_footer(text="Data from Raider.IO")

        return embed

    def _get_names_field(self, embed: discord.Embed) -> discord.Embed:
        names = "\n".join([raider.name for raider in self.raiders])
        embed.add_field(name="Names", value=names, inline=True)
        return embed

    def _get_item_levels_field(self, embed: discord.Embed) -> discord.Embed:
        item_levels = "\n".join([str(raider.item_level) for raider in self.raiders])
        embed.add_field(name="Item Levels", value=item_levels, inline=True)
        return embed

    def _get_meets_requirement_field(
        self, embed: discord.Embed, item_level_requirement: int
    ) -> discord.Embed:
        meets_requirements = "\n".join(
            [
                self._get_requirement_emoji(raider.item_level, item_level_requirement)
                for raider in self.raiders
            ]
        )
        embed.add_field(
            name="Meets Requirement?", value=meets_requirements, inline=True
        )
        return embed

    def _get_class_spec_field(self, embed: discord.Embed) -> discord.Embed:
        class_specs = "\n".join(
            [f"{raider.class_name}/{raider.spec_name}" for raider in self.raiders]
        )
        embed.add_field(name="Class/Spec", value=class_specs, inline=True)
        return embed

    def raid_roster(self, item_level_requirement: int) -> discord.Embed:
        embed = self._defaults()

        embed = self._get_names_field(embed)
        embed = self._get_item_levels_field(embed)
        embed = self._get_meets_requirement_field(embed, item_level_requirement)

        return embed

    def detailed_roster(self) -> discord.Embed:
        embed = self._defaults()

        embed = self._get_names_field(embed)
        embed = self._get_class_spec_field(embed)
        return embed
