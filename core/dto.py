from typing import List, Optional
from dataclasses import dataclass


@dataclass
class Character:
    name: str
    realm: str
    region: str
    char_class: str
    spec_name: str
    item_level: int
    profile_url: str
    thumbnail_url: str
