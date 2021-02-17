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
        self.top15teams = [
            "Astralis", "Natus Vincere", "Vitality", "BIG", "Liquid",
            "Virtus.pro", "Heroic", "mousesports", "FURIA", "fnatic",
            "G2", "OG", "Spirit", "Complexity", "Gambit", "Evil Geniuses",
            "FunPlus Phoenix", "NIP", "FaZe", "Cloud9", "MIBR"
        ]
        self.db = None

    def get_localtime(self, utcTime: str):
        utc_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        ctime = datetime.datetime.strptime(utcTime, utc_format)
        localtime = ctime + datetime.timedelta(hours=8)
        return localtime.strftime("%Y-%m-%d %H:%M:%S")

    @demo_logger('connecting mysql')
    def connect_mysql(self):
        self.db = pymysql.connect(
            "localhost",
            "demo_detector",
            "811021",
            "csgodemo"
        )

    def query_and_insert(self, matchId: str) -> bool:
        cursor = self.db.cursor()
        ext = cursor.execute(
            "SELECT 1 FROM demo_history WHERE matchId = '%s' limit 1" % (matchId)
        )
        if ext == 1: return True
        rctime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            """
            INSERT INTO demo_history
            (matchId, status, record_time)
            VALUES
            ('%s', 'MARKED', '%s')
            """ % (matchId, rctime)
        )
        self.db.commit()

    # @demo_logger('query hltv-api => all results')
    def get_new_result(self) -> dict:
        response = requests.get(self.url)
        all_ = ujson.loads(response.content.decode("utf-8"))
        for res in all_:
            if res['team1']['name'] not in self.top15teams or res['team2']['name'] not in self.top15teams:
                # print('not in top30: %s - %s' % (res['team1']['name'], res['team2']['name']))
                continue
            if self.query_and_insert(res["matchId"]):
                continue
            return res
        return {}

    @demo_logger('detecting new match results')
    def detect(self) -> str:
        while True:
            self.connect_mysql()
            result = self.get_new_result()

            try:
                result["time"] = self.get_localtime(result["time"])
                if "bo" not in result["maps"]:
                    result["maps"] = "bo1"
                if self.db != None:
                    self.db.close()
                return result
            except: pass
            if self.db != None:
                self.db.close()
            time.sleep(600)

