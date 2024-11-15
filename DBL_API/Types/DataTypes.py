from typing import NamedTuple

from enum import IntEnum, Flag

#region API-Typing
class API_CONFIG(NamedTuple):
    asset_rel_root: str
    db_last_updated: str

class DB_CONFIG(NamedTuple):
    TRAIT: dict
    EQUIP: dict
    CHARS: dict

class page_root(Flag):
    ROOT = 'ROOT'
    TRAIT = 'TRAIT'
    CHARS_ROOT = 'CHARS_ROOT'
    CHAR = 'CHAR'
    EQUIPS_ROOT = 'EQUIPS_ROOT'
    EQUIP = 'EQUIP'

    @classmethod
    def is_pr(cls, col) -> bool:
        if isinstance(col, cls): col = col.value
        if not col in cls.__members__: return False
        else: return True

class prDict(dict):
    def __setitem__(self, key:page_root, val:str):
        if page_root.is_pr(key): super().__setitem__(page_root(key), val)
        else: raise KeyError(f'KEY [{key}] is not of type page_root')

    def __getitem__(self, key:page_root):
        if isinstance(key, str): return super().__getitem__(key.value)

class SCRAPER_CONFIG(NamedTuple):
    rootURL: str
    page_roots: prDict
#endregion

#region DBL-Items
class TraitRarity(IntEnum):
    standard = 0
    bronze = 1
    silver = 2
    gold = 3
    ultra = 4

class Trait(NamedTuple):
    id: int
    rarity: TraitRarity
    name: str
    desc: str

class EquipRarity(IntEnum):
    iron = 0
    bronze = 1
    silver = 2
    gold = 3
    unique = 4
    platinum = 5
    event = 6

    awakenedBronze = 10
    awakenedSilver = 20
    awakenedGold = 30
    awakenedUnique = 40

class Equipment(NamedTuple):
    id: int
    name: str
    rarity: EquipRarity
    img_path: str
    is_ToP: bool
    conditions: str
    effect1: str
    effect2: str
    effect3: str

#endregion
