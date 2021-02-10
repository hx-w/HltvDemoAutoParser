# -*- coding: utf-8 -*-

import os, shutil, ujson
from posix import listdir
from utils.logger import demo_logger

class DemoParser():
    @demo_logger('Init Demo Parser(py)')
    def __init__(self, result: dict):
        self.result = result
        matchId_list = self.result["matchId"].split('/')
        demoId_list = self.result["demoId"].split('/')
        self.parser_matchName_str = matchId_list[-1]
        self.parser_matchId_int = matchId_list[-2]
        self.parser_demoId_int = demoId_list[-1]

        self.parser_path = 'utils/go-demoparser/parser.go'
        self.demo_dir = os.path.join('static/demos', self.parser_matchId_int)
        self.info_dir = os.path.join('static/info/')
    
    @demo_logger('Parse demo(go)')
    def parse(self):
        # get all demos for single match
        for demofile in os.listdir(self.demo_dir):
            if not demofile.endswith('.dem'):
                print('Demo parsing faild: <%s>' % (demofile))
                continue
            demopath = os.path.join(self.demo_dir, demofile)
            jsonfile = demofile[:-3] + 'json'
            os.system(f'go run {self.parser_path} -filepath {demopath} -topath {jsonfile} -matchtime "{self.result["time"]}" -matchid {self.parser_matchId_int} -demoid {self.parser_demoId_int} -matchname {self.parser_matchName_str}')
            # delete
            os.remove(demopath)
            fr = open(self.info_dir + jsonfile, 'r')
            try:
                json_ = ujson.load(fr)
                fr.close()
                res = {
                    "match_info": self.result,
                    "utility_info": json_[1:]
                }
                fo = open(self.info_dir + jsonfile, 'w')
                ujson.dump(res, fo)
                fo.close()
            except Exception as ept:
                print('[ERROR]', ept)
            # post

        # remove empty dir
        shutil.rmtree(self.demo_dir)
        # os.system(f"scp -i ~/.ssh/csgowiki_nopass.pem static/info/{self.parser_matchId_int}_*.json root@www.csgowiki.top:/home/csgowiki/csgowiki_docker/demoparser/static/")

