# -*- coding: utf-8 -*-
import time, sys
import os, shutil
import requests
from bs4 import BeautifulSoup

from utils.logger import demo_logger

# class for demo download
class DownloadThread():
    def __init__(self, matchId: str):
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
        # self.matchTime = matchTime

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
        # get matchtime
        # if self.matchTime: return
        # time_link = soup.findAll(name="div", attrs={"class": "date", "data-time-format": "do 'of' MMMM y"})
        # self.matchTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time_link[0]["data-unix"][:-3])))

    @demo_logger('download demo file (.rar)')
    def downloadDemo(self, try_time: int) -> bool:
        url = f"{self.host}{self.demoId}"
        response = requests.get(url, headers=self.headers, stream=True)
        assert response.status_code == requests.codes.ok, f"<{try_time + 1} try> Download Network Issue ({response.status_code}) | {self.tar_name}"
        file_size_bytes = float(response.headers['Content-Length'])

        rar_path = f"{self.download_directory}{self.tar_name}{self.file_backend}"
        if os.path.exists(rar_path):
            temp_size = os.path.getsize(rar_path)
        else:
            temp_size = 0
        print(f"download(bytes)  {temp_size}/{file_size_bytes}")
        with open(rar_path, 'ab') as demoFile:
            for chunk in response.iter_content(chunk_size=1024):
                if not chunk: continue
                temp_size += len(chunk)
                demoFile.write(chunk)
                demoFile.flush()
                done = int(50 * temp_size / file_size_bytes)
                sys.stdout.write("\r[%s%s] %d%%" % ('█' * done, ' ' * (50 - done), 100 * temp_size / file_size_bytes))
                sys.stdout.flush()
        print()
        return True

    @demo_logger('unrar demo file')
    def unrar(self):
        dir_path = os.path.join(self.download_directory, self.tar_name)
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path, ignore_errors=True)
        os.mkdir(dir_path)
        os.system(f'unrar x {dir_path}{self.file_backend} {dir_path}')
        os.remove(f'{dir_path}{self.file_backend}')

    def start(self):
        self.getDemoId()
        success = False
        for try_time in range(self.try_times):
            if success := self.downloadDemo(try_time):
                break
        if success:
            self.unrar()
        return success
        
