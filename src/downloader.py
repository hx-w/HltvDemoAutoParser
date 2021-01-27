# -*- coding: utf-8 -*-
import time
import os, shutil
import threading
import requests
from bs4 import BeautifulSoup

from src.logger import demo_logger

# class for demo download
class DownloadThread(threading.Thread):
    def __init__(self, matchId: str):
        threading.Thread.__init__(self)
        self.matchId = matchId # format: in https://hltv-api.vercel.app/api/results
        self.demoId = 'Not Found' # format: /download/demo/<str>
        self.host = 'https://www.hltv.org'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
            'Referer': f'{self.host}{self.matchId}',
        }
        self.download_directory = 'static/demos/'
        self.tar_name = matchId.split('/')[-2] # number
        self.file_backend = '.rar'
        self.try_times = 3

    def formatFloat(self, number: float) -> float:
        return '{:.2f}'.format(number)

    @demo_logger('search demoId from matchId')
    def getDemoId(self):
        url = f"{self.host}{self.matchId}"
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.content.decode('utf-8'), 'lxml')
        links = list(filter(lambda x: 'download/demo' in x['href'], soup.findAll('a')))
        assert len(links) > 0, f'demoId not found from {self.matchId}'
        self.demoId = links[0]['href']

    @demo_logger('download demo file (.rar)')
    def downloadDemo(self, try_time: int) -> bool:
        url = f"{self.host}{self.demoId}"
        response = requests.get(url, headers=self.headers, stream=True)
        assert response.status_code == requests.codes.ok, f"<{try_time + 1} try> Download Network Issue ({response.status_code}) | {self.tar_name}"
        file_size_bytes = float(response.headers['Content-Length'])
        save_count_bytes = 0.0
        last_time = time.time()
        with open(f'{self.download_directory}{self.tar_name}{self.file_backend}', 'wb') as demoFile:
            for chunk in response.iter_content(chunk_size=1024):
                if not chunk: continue
                save_count_bytes += len(chunk)
                if time.time() - last_time > 5: # query proc every 60s
                    proc = save_count_bytes / file_size_bytes
                    print(f"[Proc] <{self.tar_name}> {self.formatFloat(save_count_bytes / 1048576)}/{self.formatFloat(file_size_bytes / 1048576)}M ===== {self.formatFloat(proc * 100)}%")
                    last_time = time.time()
                demoFile.write(chunk)
        return True

    @demo_logger('unrar demo file')
    def unrar(self):
        dir_path = os.path.join(self.download_directory, self.tar_name)
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path, ignore_errors=True)
        os.mkdir(dir_path)
        os.system(f'unrar x {dir_path}{self.file_backend} {dir_path}')
        os.remove(f'{dir_path}{self.file_backend}')

    def run(self):
        self.getDemoId()
        for try_time in range(self.try_times):
            if self.downloadDemo(try_time):
                break
        self.unrar()
        