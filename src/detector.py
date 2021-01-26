# -*- coding: utf-8 -*-
import time
import requests
import pymysql
import ujson

# detect new match result from hltv and return ONE matchId
class NewMatchDetector():
    def __init__(self):
        self.url = 'https://hltv-api.vercel.app/api/results'
        self.db_host = 'localhost'
        self.db_user = 'demo_detector'
        self.db_name = 'csgodemo'
        self.db_password = 'mypassword'
        pass

    def get_all_results(self) -> list:
        try:
            response = requests.get(self.url)
            results = ujson.loads(response.content.decode('utf-8'))
            return results
        except Exception as ept:
            print('[Error]', ept)
            return []

    def query_if_new_match(self, matchId: str) -> bool:
        return False

    def insert_new_match(self, matchId: str):
        pass

    def detect(self) -> str:
        while True:
            allResults = self.get_all_results()
            for each_ in allResults:
                matchId = each_['matchId']
                if self.query_if_new_match(matchId):
                    self.insert_new_match(matchId)
                    return matchId
            time.sleep(60)
