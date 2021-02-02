# -*- coding: utf-8 -*-
import time
import datetime
import requests
import pymysql
import ujson

from utils.logger import demo_logger

# detect new match result from hltv and return ONE matchId
class NewMatchDetector():
    def __init__(self):
        self.url = 'https://hltv-api.vercel.app/api/results'
        self.last_matchId = None
        self.result = {}

    @demo_logger('init lastmatch')
    def init_lastmatch(self):
        if not self.last_matchId: return
        result = self.get_new_result()
        last_matchId = result['matchId']

    @demo_logger('query hltv-api => all results')
    def get_new_result(self) -> dict:
        response = requests.get(self.url)
        return ujson.loads(response.content.decode('utf-8'))[0]

    @demo_logger('detecting new match results')
    def detect(self) -> str:
        self.init_lastmatch()
        while True:
            result = self.get_new_result()
            matchId = result['matchId']
            if matchId == self.last_matchId:
                print('Detect failed: old matchid')
                continue
            if self.query_if_new_match(matchId):
                self.insert_new_match(matchId)
                self.close_mysql()
                return matchId
            time.sleep(60)

