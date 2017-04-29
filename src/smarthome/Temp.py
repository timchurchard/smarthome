#!/usr/bin/env python3
# Temp Reader

import requests
from datetime import datetime
import _mysql

from Creds import Creds


TEMP_ADDR = 'http://10.0.1.20/'


class Temp:

    def __init__(self):
        self.__creds = Creds()
        self.__temp = 0
        self.__light = 0


    def get_temp(self):
        r = requests.get(TEMP_ADDR)
        j = r.json()
        self.__temp = j['temp']
        self.__light = j['light']
        return datetime.utcnow(), self.__temp, self.__light

    # Store data
    def store_temp(self):
        db = _mysql.connect(host=self.__creds.get('db', 'host'),
                            user=self.__creds.get('db', 'user'),
                            passwd=self.__creds.get('db', 'pass'),
                            db=self.__creds.get('db', 'db'))
        db.query('insert into temp_raw(time, temp, light) values("%s", %f, %i)' % self.get_temp())
        db.commit()
        db.close()

if __name__ == '__main__':
    t = Temp()
    #print(t.get_temp())
    t.store_temp()










