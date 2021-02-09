# -*- coding: utf-8 -*-

import os, shutil
from datetime import datetime
from utils.logger import demo_logger

class DemoParser():
    @demo_logger('Init Demo Parser(py)')
    def __init__(self, matchId: str, demoId: str):
        matchId_list = matchId.split('/')
        demoId_list = demoId.split('/')
        self.parser_matchName = matchId_list[-1]
        self.parser_matchId = matchId_list[-2]
        self.parser_demoId = demoId_list[-1]
        self.parser_matchTime = datetime.now().strftime("%y-%m-%d")

        self.parser_path = 'utils/go-demoparser/parser.go'
        self.demo_dir = os.path.join('static/demos', self.parser_matchId)
    
    @demo_logger('Parse demo(go)')
    def parse(self):
        # get all demos for single match
        for demofile in os.listdir(self.demo_dir):
            if not demofile.endswith('.dem'):
                print('Demo parsing faild: <%s>' % (demofile))
                continue
            demopath = os.path.join(self.demo_dir, demofile)
            os.system(f'go run {self.parser_path} -filepath {demopath} -matchtime {self.parser_matchTime} -matchid {self.parser_matchId} -demoid {self.parser_demoId} -matchname {self.parser_matchName}')
            # delete
            os.remove(demopath)
        # remove empty dir
        shutil.rmtree(self.demo_dir)
        os.system(f"scp -i ~/.ssh/csgowiki_nopass.pem static/info/{self.parser_matchId}_*.json root@www.csgowiki.top:/home/csgowiki/csgowiki_docker/demoparser/static/")
