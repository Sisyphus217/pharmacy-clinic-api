import asyncio
from motor.motor_asyncio import AsyncIOMotorClient



class SettingsDB():
    def __init__(self, url='mongodb://localhost:27017', db_name='hospital_db') -> None:

        self.CLIENT = AsyncIOMotorClient(url) 

        self.DB = self.CLIENT[db_name]

        self.COLLECTION_MED = self.DB["medication"]
        self.COLLECTION_BEN = self.DB["beneficiary"]

     
        
if __name__ == "__main__":
    pass