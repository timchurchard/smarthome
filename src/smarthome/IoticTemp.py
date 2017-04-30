#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Temp Reader

from __future__ import unicode_literals, print_function

import requests
from datetime import datetime
import _mysql

import logging

logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)s [%(name)s] {%(threadName)s} %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

from IoticAgent import ThingRunner

from Creds import Creds


TEMP_ADDR = 'http://10.0.1.20/'


class IoticTemp(ThingRunner):

    def __init__(self, config):
        super(IoticTemp, self).__init__(config=config)
        self.__creds = Creds()
        self.__temp = 0
        self.__light = 0

    def __get_temp(self):
        r = requests.get(TEMP_ADDR)
        j = r.json()
        self.__temp = j['temp']
        self.__light = j['light']
        return datetime.utcnow(), self.__temp, self.__light

    # Store data
    def __store_temp(self, data):
        db = _mysql.connect(host=self.__creds.get('db', 'host'),
                            user=self.__creds.get('db', 'user'),
                            passwd=self.__creds.get('db', 'pass'),
                            db=self.__creds.get('db', 'db'))
        db.query('insert into temp_raw(time, temp, light) values("%s", %f, %i)' % data)
        db.commit()
        db.close()

    def on_startup(self):
        # Create Temperature Thing
        self.__temp_thing = self.client.create_thing("smart_temp")
        with self.__temp_thing.get_meta() as meta:
            meta.set_label("Tim's House Hallway Temperature")
            meta.set_description("Arduino with TMP36 sensor")
            meta.set_location(52.526087, 0.391160)  # Southery White Bell Pub
        self.__temp_feed = self.__temp_thing.create_feed("data")
        self.__temp_thing.set_public(True)

    def main(self):
        while True:
            temp_time, temp, light = self.__get_temp()
            self.__store_temp((temp_time, temp, light))
            self.__temp_feed.share(time=temp_time, data={'temp': temp, 'light': light})
            if self.wait_for_shutdown(10):
                return

def in_foreground(runner):
    try:
        # blocks until finished
        runner.run()
    except KeyboardInterrupt:
        pass
    finally:
        runner.stop()

if __name__ == '__main__':
    runner = IoticTemp('../../cfg/smarttemp.ini')
    in_foreground(runner)

