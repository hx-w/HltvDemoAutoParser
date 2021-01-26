# -*- coding: utf-8 -*-
import time
import threading
import requests
from bs4 import BeautifulSoup

# class for demo download
class DownloadThread(threading.Thread):
    def __init__(self, matchId: str):
        threading.Thread.__init__(self)
        self.matchId = matchId # format: in https://hltv-api.vercel.app/api/results
        self.demoId = 'Not Found' # format: /download/demo/<str>
        self.host = 'https://www.hltv.org'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
        }
        self.download_directory = 'static/demos/'
        self.tar_name = matchId.split('/')[-1] # team1-vs-team2-event
        self.file_backend = '.tar'

    def formatFloat(number: float) -> float:
        return '{:.2f}'.format(number)

    def getDemoId(self):
        url = f"{self.host}{self.matchId}"
        response = requests.get(url, self.headers)
        try:
            soup = BeautifulSoup(response.content.decode('utf-8'), 'lxml')
            links = list(filter(lambda x: 'download/demo' in x['href'], soup.findAll('a')))
            assert len(links) > 0, f'demoId not found for {self.matchId}'
            self.demoId = links[0]['href']
        except Exception as ept:
            print('[Error]', ept)

    def downloadDemo(self) -> bool:
        url = f"{self.host}{self.demoId}"
        response = requests.get(url, headers=self.headers, stream=True)
        try:
            file_size_bytes = float(response.headers['Content-Length']) / 1024 / 1024
            save_count_bytes = 0.0
            last_time = time.time()

            print(f'[Info] 开始下载：{self.tar_name}')
            with open(f'{self.download_directory}{self.tar_name}{self.file_backend}', 'wb') as demoFile:
                for chunk in response.iter_content(chunk_size=1024):
                    if not chunk: continue
                    save_count_bytes += len(chunk)
                    if time.time() - last_time > 60: # query proc every 60s
                        proc = save_count_bytes / file_size_bytes
                        print(f"[ProcQuery] <{self.tar_name}> {self.formatFloat(save_count_bytes / 1048576)}/{self.formatFloat(file_size_bytes) / 1048576}M ===== {self.formatFloat(proc * 100)}%")
                        last_time = time.time()
                    demoFile.write(chunk)
            print(f'[Info] 结束下载：{self.tar_name}')
            return True
        except Exception as ept:
            print('[Error]', ept)
            return False


    def run(self):
        self.getDemoId()
        if not self.downloadDemo():
            self.downloadDemo()
