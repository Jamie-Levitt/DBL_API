from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from Database.utils import checkForTable

from Types.DataTypes import Trait, TraitRarity
from Types.FlagTypes import DBTableType

if TYPE_CHECKING:
    from utils import DBAPIConnection

@checkForTable(DBTableType.TRAIT)
def __addTraitToDB(APIConn:DBAPIConnection, trait:Trait):
    conn = APIConn.getDBConn()
    cursor = conn.cursor()
    cursor.execute('''
                       REPLACE INTO trait (id, rarity, name, desc)
                       VALUES (?,?,?,?)
                        ''', (trait.id, trait.rarity.value, trait.name, trait.desc))
    conn.commit()
    conn.close()

@checkForTable(DBTableType.TRAIT)
def findTrait(APIConn:DBAPIConnection, traitID:int, traitRarity:Optional[TraitRarity] = None) -> Trait:
    r = APIConn.findInDB(traitID, 'trait')
    if r is not None: return Trait(r[0], TraitRarity(r[1]), r[2], r[3])
    else: 
        rawData = APIConn.scrapeTraitData(traitID)
        trait = Trait(traitID, traitRarity, rawData['name'], rawData['desc'])
        __addTraitToDB(trait)
        return trait

def parseTraits(traitStr:str) -> list[Trait]:
    splitList = traitStr.split(' || ')
    return [[findTrait(t) for t in subStr.split(' && ')] for subStr in splitList]