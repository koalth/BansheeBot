from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Character:
    name: str
    realm: str
    region: str
    char_class: str
    spec_name: str
    item_level: float
    profile_url: str
    thumbnail_url: str
    last_crawled_at: datetime
