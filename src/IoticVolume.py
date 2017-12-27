# /usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

from time import sleep
from threading import Lock
import sys, os
import logging

logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)s [%(name)s] {%(threadName)s} %(message)s',
                            level=logging.INFO)
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

from IoticAgent import RetryingThingRunner


MAX = 80
MIN = 0
DEFAULT = 25


class IoticVolume(RetryingThingRunner):

    def __init__(self, config=None):
        super(IoticVolume, self).__init__(config=config)
        #
        self.__level = 0
        self.__reset()

    def __reset(self):
        for x in range(0, int(MAX/2)):
            self.__down()
        for x in range(0, DEFAULT):
            self.__up()

    def __up(self):
        os.system("irsend SEND_ONCE ir_vol.conf KEY_VOLUMEUP")
        self.__level += 1

    def __down(self):
        os.system("irsend SEND_ONCE ir_vol.conf KEY_VOLUMEDOWN")
        if self.__level > 0:
            self.__level -= 1

    def on_startup(self):
        # Create snd_ctrl Thing
        self.__thing = self.client.create_thing("snd ctrl")
        with self.__thing.get_meta() as meta:
            meta.set_label("Tim's House RPI Volume Control")
            meta.set_description("RPI3 with IR GPIO board")
            meta.set_location(52.526087, 0.391160)  # Southery White Bell Pub
        self.__feed = self.__thing.create_feed("feed")
        self.__ctrl = self.__thing.create_control("ctrl", self.__ctrl_cb)
        self.__thing.set_public(False)

    def __ctrl_cb(self, data):
        if 'data' in data and 'cmd' in data['data']:
            if data['data']['cmd'] == 'reset':
                self.__reset()
            elif data['data']['cmd'] == 'up':
                self.__up()
            elif data['data']['cmd'] == 'down':
                self.__down()
            else:
                return
            self.__feed.share({'state': data['data']['cmd'], 'level': self.__level})

    def main(self):
        while True:
            if self.wait_for_shutdown(30):
                return
            try:
                self.__feed.share({'state': 'update', 'level': self.__level})
            except:
                pass

def in_foreground(runner):
    try:
        # blocks until finished
        runner.run()
    except KeyboardInterrupt:
        pass
    finally:
        runner.stop()

if __name__ == '__main__':
    runner = IoticVolume('../cfg/ioticvolume.ini')
    in_foreground(runner)
