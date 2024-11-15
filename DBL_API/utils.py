from typing import Optional, Union

import os, json, sqlite3, shutil
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

from Types.DataTypes import (API_CONFIG,
                             Equipment, Trait, TraitRarity)
from Types.FlagTypes import ConfigType

from Scraping import Scraper
from Database.EquipUtils import downloadEquipData
from Database.TraitUtils import findTrait, parseTraits

class DBAPIConnection:
    def __init__(self, app_root:str) -> None:
        self.appRoot = app_root
        self.config = self.loadConfig(self.getConfigPath(ConfigType.API))
        self.scraper = Scraper(self.loadConfig(self.getConfigPath(ConfigType.SCRAPER)))
        self.__affirmDB()

    #region UTILS

    #region CLASS METHODS
    @classmethod
    def __joinpaths(root:str, addon:str) -> str: return os.path.join(root, addon)
    @classmethod
    def __getRoot(path:str) -> str: return os.path.realpath(path)
    #endregion

    #region RELPATH
    def getAssetPath(self, asset_rel_path:str) -> None: return self.__joinpaths(self.appRoot, f'{self.config.asset_rel_root}asset_rel_path')
    def getConfigPath(self, configType:ConfigType) -> str: return self.__joinpaths(self.appRoot, f'DBLAPI-CONFIG{os.sep}{configType.value}.json')
    #endregion

    #region CONFIG
    def loadConfig(self, configType:ConfigType, field:Optional[str] = None) -> Union[dict, str]:
        with open(self.getConfigPath(configType), 'r') as cFile: config = json.load(cFile)

        if field is None: return config
        else: return config[field]

    def updateConfig(self, configType:ConfigType, field:str, value) -> None:
        configPath = self.getConfigPath(configType)
        with open(configPath, 'r') as cFile:
            config = json.load(cFile)
        config[field] = value
        with open(configPath, 'w') as cFile:
            json.dump(config, cFile)

    #endregion

    #endregion

    #region SCRAPING
    def loadPageData(self, targetPage:str, id:Optional[str] = None) -> BeautifulSoup: return self.scraper.loadPageData(targetPage, id)

    def scrapeTraitData(self, traitID:int) -> dict:
        soup = self.scraper.loadPageData('TRAIT', traitID)
        rawData = soup.find('div', class_ = 'container text-center')
        return {'name': rawData.find('h2').text, 'desc': rawData.find('h5').text}
    
    #endregion

    #region DATABASE
    def getDBConn(self) -> sqlite3.Connection: return sqlite3.connect(self.dbPath)

    def __affirmDB(self) -> None:
        lUpdate = datetime.now() - datetime.strptime(self.config.db_last_updated, '%d/%m/%y')
        if lUpdate.days >= timedelta(days=7):
            self.__updateDBs()
            self.updateConfig(ConfigType.API, 'db_last_updated', datetime.strftime(datetime.now(), '%d/%m/%y'))

    def __updateDBs(self) -> None:
        self.__updateEquipDB()

    def __updateEquipDB(self) -> None:
        equipList = downloadEquipData()
        with open(self.getAssetPath('temp.txt'), 'w') as f:
            f.write(f'{equipList}')
        conn = self.getDBConn()
        cursor = conn.cursor()
        cursor.executemany('''
                           REPLACE INTO equip (id, name, rarity, img_path, is_ToP, conditions, effect1, effect2, effect3)
                           VALUES (?,?,?,?,?,?,?,?,?)
                            ''', [(e.id, e.name, e.rarity.value, e.img_path, e.is_ToP, e.conditions, e.effect1, e.effect2, e.effect3) for e in equipList])
        conn.commit()
        conn.close()

    def loadEquipDB(self) -> list[Equipment]:
        conn = self.getDBConn()
        cursor = conn.cursor()
        rawList = cursor.execute('SELECT * from equip').fetchall()
        return [Equipment(e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[8], e[9]) for e in rawList]

    def getDictedEquipData(self) -> list[dict]:
        eList = self.loadEquipData()
        return [ {  'id': e.id,
                    'name': e.name,
                    'rarity': e.rarity,
                    'rel_path': e.img_path,
                    'is_ToP': e.is_ToP,
                    'conditions': [{'id': t.id, 'name': t.name, 'rarity': t.rarity} for t in parseTraits(e.conditions)],
                    'effects': [e.effect1, e.effect2, e.effect3]
                } for e in eList]

    def equipImgConfirm(self, equipID:str, webSRC:str):
        equipImgPath = self.getAssetPath(f'equips{os.sep}{equipID}.png')
        if os.path.isfile(equipImgPath) == False:
            r = self.scraper.getImage(webSRC)
            with open(f'{equipImgPath}', 'wb') as out_file:
                shutil.copyfileobj(r.raw, out_file)
            del r

    def findTrait(self, traitID:int, traitRarity:Optional[TraitRarity] = None) -> Trait: return findTrait(self, traitID, traitRarity)

    #endregion

    #region PROPERTIES
    @property
    def appRoot(self) -> str: return self.__appRoot
    @appRoot.setter
    def appRoot(self, appRoot:str) -> None:
        if hasattr(self, '__appRoot'): raise Exception
        elif os.path.exists(appRoot) is False: raise Exception
        elif os.path.isfile is True: raise Exception
        else: self.__appRoot = appRoot

    @property
    def config(self) -> API_CONFIG: return self.__config
    @config.setter
    def config(self, config:dict) -> None:
        if hasattr(self, '__appRoot'): raise Exception
        else: self.__config = API_CONFIG(config['asset_rel_root'].replace('[os.sep]', os.sep), config['db_last_updated'])

    @property
    def dbPath(self) -> str: return self.__joinpaths(self.appRoot, f'static{os.sep}assets{os.sep}database.db')
    #endregion