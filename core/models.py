from tortoise import Tortoise, fields
from tortoise.models import Model


class ServerModel(Model):
    id = fields.IntField(primary_key=True)
    discord_guild_id = fields.IntField(unique=True)

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

    raid_roster: fields.ForeignKeyRelation[ServerModel] = fields.ForeignKeyField(
        "models.ServerModel", related_name="raiders"
    )

    class Meta:
        table = "characters"
