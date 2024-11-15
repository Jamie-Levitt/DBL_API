from typing import Optional, TYPE_CHECKING

import requests
from bs4 import BeautifulSoup

from Types.DataTypes import SCRAPER_CONFIG, page_root, prDict
    
class Scraper:
    def __init__(self, config:dict):
        self.config = config

    def __findPagePath(self, target_page:page_root) -> str: return f'{self.config.rootURL}{self.config.page_roots[target_page.value]}'
    def __findWebAssetPath(self, target_asset:str) -> str: return f'{self.config.rootURL}/assets/{target_asset}'

    @classmethod
    def scrape(targetPage:str) -> BeautifulSoup:
        page = requests.get(targetPage)
        return BeautifulSoup(page.content, "html.parser")
    
    def loadPageData(self, targetPage:str, id:Optional[str] = None) -> BeautifulSoup:
        if id is not None: return self.scrape(f'{self.__findPagePath(targetPage)}/{id}')
        else: return self.scrape(self.__findPagePath(targetPage))
    
    def getImage(self, targetAsset:str):
        return requests.get(f'{self.__findWebAssetPath(targetAsset)}', stream=True)
    
    #region PROPERTIES
    @property
    def config(self) -> SCRAPER_CONFIG: return self.__config
    @config.setter
    def config(self, cf:dict) -> None:
        self.__config = SCRAPER_CONFIG(cf['rootURL'], prDict([(page_root(key), val) for key, val in cf['page_roots']]))
    #endregion