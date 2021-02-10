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

    def get_localtime(self, utcTime: str):
        utc_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        ctime = datetime.datetime.strptime(utcTime, utc_format)
        localtime = ctime + datetime.timedelta(hours=8)
        return localtime.strftime("%Y-%m-%d %H:%M:%S")

    @demo_logger('init lastmatch')
    def init_lastmatch(self):
        if self.last_matchId: return
        result = self.get_new_result()
        self.last_matchId = result['matchId']

    # @demo_logger('query hltv-api => all results')
    def get_new_result(self) -> dict:
        response = requests.get(self.url)
        return ujson.loads(response.content.decode('utf-8'))[9]

    @demo_logger('detecting new match results')
    def detect(self) -> str:
        # self.init_lastmatch()
        while True:
            result = self.get_new_result()
            matchId = result['matchId']
            if matchId != self.last_matchId:
                self.last_matchId = matchId
                try:
                    result["time"] = self.get_localtime(result["time"])
                    if "bo" not in result["maps"]:
                        result["maps"] = "bo1"
                    return result
                except:
                    return {}
            time.sleep(60)

