# -*- coding: utf-8 -*-
import time
from queue import Queue
import threading

from utils.downloader import DownloadThread
from utils.detector import NewMatchDetector

class AutoDownloader():
    def __init__(self, qmaxsize=3):
        # store matchId: str
        self.taskQ = Queue(maxsize=qmaxsize)
        self.match_detector = NewMatchDetector()

    def consumer(self): # download demo
        while True:
            matchId = self.taskQ.get() # block=True
            downloader = DownloadThread(matchId)
            downloader.start()
            downloader.join() # until download finish
            time.sleep(1)

    def producer(self): # put new matchId in taskQ
        while True:
            new_matchId = self.match_detector.detect() # block when no new match
            self.taskQ.put(new_matchId) # block if queue full
            time.sleep(1)

    def start(self):
        t_pro = threading.Thread(target=self.producer)
        t_con = threading.Thread(target=self.consumer)
        t_pro.start()
        t_con.start()

