#!/usr/bin/env python3
# Temp Reader

import requests
from datetime import datetime

class Temp:

    def __init__(self):
        self.__temp = 0
        self.__light = 0


    def get_temp(self):
        r = requests.get('http://10.0.1.20/')
        j = r.json()
        self.__temp = j['temp']
        self.__light = j['light']
        return datetime.utcnow(), self.__temp, self.__light

if __name__ == '__main__':
    t = Temp()
    print(t.get_temp())











