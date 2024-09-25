from tortoise import Tortoise, fields
from tortoise.models import Model


class ServerModel(Model):
    id = fields.IntField(primary_key=True)
    discord_guild_id = fields.IntField(unique=True)

    raider_role_id = fields.IntField(null=True)
    raider_item_level_requirement = fields.IntField(null=True)

    manager_role_id = fields.IntField(null=True)
    raider_role_id = fields.IntField(null=True)

    # fields to track roster updates
    roster_updating = fields.BooleanField(default=False)

    raiders: fields.ReverseRelation["CharacterModel"]

    class Meta:
        table = "servers"


class CharacterModel(Model):
    id = fields.IntField(primary_key=True)
    discord_user_id = fields.IntField()

    name = fields.TextField()
    realm = fields.TextField()
    region = fields.TextField()

    item_level = fields.IntField()
    class_name = fields.TextField()
    spec_name = fields.TextField()
    profile_url = fields.TextField()
    thumbnail_url = fields.TextField()

    raiderio_last_crawled_at = (
        fields.DatetimeField()
    )  # This is the last time RaiderIO API crawled for the character data

    added_on = fields.DatetimeField(
        auto_now_add=True
    )  # This is when the character was added to the database
    last_updated = fields.DatetimeField(
        auto_now=True
    )  # This is the last time the character was updated

    raid_roster: fields.ForeignKeyRelation[ServerModel] = fields.ForeignKeyField(
        "models.ServerModel", related_name="raiders"
    )

    class Meta:
        table = "characters"
