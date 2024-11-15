from enum import Flag

class ConfigType(Flag):
    API = "API"
    SCRAPER = "Scraper"
    DB = "Database"

class DBTableType(Flag):
    TRAIT = "TRAIT"
    EQUIP = "EQUIP"