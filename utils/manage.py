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
            result = self.match_detector.detect()
            if result == {}: continue
            try:
                downloader = DownloadThread(result["matchId"])
                if downloader.start():
                    result["demoId"] = downloader.demoId
                    parser = DemoParser(result)
                    parser.parse()
            except: pass
            time.sleep(30)

