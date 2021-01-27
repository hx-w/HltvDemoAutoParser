# -*- coding: utf-8 -*-
import datetime

def demo_logger(purpose: str):
    def decorator(func):
        def warpper(*args, **kwargs):
            currTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print('[Info]', '%s (Start) [%s]' % (purpose, currTime))
            try:
                return func(*args, **kwargs)
            except Exception as ept:
                print('[Error]', '%s | %s [%s]' % (ept, func.__name__, currTime))
        return warpper
    return decorator
