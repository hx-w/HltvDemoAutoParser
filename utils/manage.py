# -*- coding: utf-8 -*-
import time
from queue import Queue
import threading

from utils.downloader import DownloadThread
from utils.detector import NewMatchDetector
from utils.parser import DemoParser

class AutoDownloader():
    def __init__(self):
        # store matchId: str
        self.match_detector = NewMatchDetector()

    def start(self):
        while True:
            matchId = self.match_detector.detect()
            downloader = DownloadThread(matchId)
            downloader.start()
            parser = DemoParser(downloader.matchId, downloader.demoId)
            parser.parse()
            time.sleep(30)

