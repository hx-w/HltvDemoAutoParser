# -*- coding: utf-8 -*-
import time
import datetime
import requests
import pymysql
import ujson

from src.logger import demo_logger

# detect new match result from hltv and return ONE matchId
class NewMatchDetector():
    def __init__(self):
        self.url = 'https://hltv-api.vercel.app/api/results'
        self.db_host = 'localhost'
        self.db_user = 'demo_detector'
        self.db_name = 'csgodemo'
        self.db_password = '811021'
        self.db_tablename = 'demo_history'
        self.db = None
        self.results = []

    @demo_logger('<database> connect mysql')
    def connect_mysql(self):
        self.db = pymysql.connect(
            host = self.db_host,
            user = self.db_user,
            db = self.db_name,
            passwd = self.db_password
        )

    @demo_logger('<database> close mysql')
    def close_mysql(self):
        self.db.close()

    @demo_logger('query hltv-api => all results')
    def get_all_results(self) -> list:
        response = requests.get(self.url)
        self.results = ujson.loads(response.content.decode('utf-8'))

    @demo_logger('<database> query match exist')
    def query_if_new_match(self, matchId: str) -> bool:
        cursor = self.db.cursor()
        ifExists = cursor.execute(
            "SELECT 1 FROM %s WHERE matchId = '%s' limit 1" % (self.db_tablename, matchId)
        )
        return ifExists != 1

    @demo_logger('<database> insert match')
    def insert_new_match(self, matchId: str):
        currTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = self.db.cursor()
        cursor.execute(
            """
            INSERT INTO %s
            (matchId, status, record_time)
            VALUES
            ('%s', 'DOWNLOADING', '%s')
            """ % (self.db_tablename, matchId, currTime)
        )
        self.db.commit()

    def detect(self) -> str:
        self.connect_mysql()
        while True:
            self.get_all_results()
            for each_ in self.results:
                matchId = each_['matchId']
                if self.query_if_new_match(matchId):
                    self.insert_new_match(matchId)
                    self.close_mysql()
                    return matchId
            time.sleep(60)
