from pymongo import MongoClient
from pymongo import errors
import traceback
import pymongo
from datetime import datetime


class MongoConnector:
    def __init__(
            self,
            address: str,
            port: int,
            dbName: str,
            errorLogger,
    ):
        self.client = MongoClient(address, port)
        self.collectionList = {
            'placeInfo': ('placeName', 'placeAddress'),
            'reviewInfo': ('placeName', 'placeAddress', 'userHash', 'reviewInfoVisitCount'),
            'userInfo': ('userHash'),
        }
        self.db = None
        self.makeDB(dbName)
        self.errorLogger = errorLogger

    def makeDB(self, dbName):
        try:
            self.db = self.client[dbName]
            # make collection
            for cName, idxName in self.collectionList.items():
                self.db[cName]
                self.makeIndex(self.db[cName], idxName)
        except:
            raise Exception(traceback.format_exc())

    # 콜렉션마다 인덱스 만들기
    def makeIndex(self, collection, idxNames):
        try:
            if type(idxNames) == str:
                collection.create_index(idxNames, unique=True)
            else:
                collection.create_index([(idxEntry, pymongo.ASCENDING) for idxEntry in idxNames], unique=True)
        except:
            raise Exception(traceback.format_exc())

    def batchWrite(self, data: list, collectionName: str):
        try:
            result = self.db[collectionName].insert_many(data, ordered=False)
            print('{now} : {result}'.format(now=datetime.now().strftime('[%H:%M:%S]'), result=len(result.inserted_ids)))
        except errors.BulkWriteError as e:
            self.errorLogger.logger.error(e)
