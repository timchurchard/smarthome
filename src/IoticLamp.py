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

from gpiozero import Energenie

from IoticAgent import RetryingThingRunner


LAMP = 1


class IoticLamp(RetryingThingRunner):

    def __init__(self, config=None):
        super(IoticLamp, self).__init__(config=config)
        #
        self.__lamp = Energenie(LAMP)

    def __lamp_on(self):
        self.__lamp.on()

    def __lamp_off(self):
        self.__lamp.off()

    def on_startup(self):
        # Create snd_ctrl Thing
        self.__thing = self.client.create_thing("lamp ctrl")
        with self.__thing.get_meta() as meta:
            meta.set_label("Tim's House RPI Energenie Lamp Control")
            meta.set_description("RPI with Energenie GPIO board")
            meta.set_location(52.526087, 0.391160)  # Southery White Bell Pub
        self.__feed = self.__thing.create_feed("feed")
        self.__ctrl = self.__thing.create_control("ctrl", self.__ctrl_cb)
        self.__thing.set_public(False)

    def __ctrl_cb(self, data):
        if 'data' in data and 'cmd' in data['data']:
            if data['data']['cmd'] == 'on':
                print("__ctrl_cb: Turning lamp on")
                self.__lamp_on()
            elif data['data']['cmd'] == 'off':
                print("__ctrl_cb: Turning lamp off")
                self.__lamp_off()
            else:
                print("__ctrl_cb: Unknown data", data['data'])
                return
            self.__feed.share({'state': self.__lamp.is_active})

    def main(self):
        while True:
            if self.wait_for_shutdown(30):
                self.__lamp.close()
                return
            self.__feed.share({'state': self.__lamp.is_active})

def in_foreground(runner):
    try:
        # blocks until finished
        runner.run()
    except KeyboardInterrupt:
        pass
    finally:
        runner.stop()

if __name__ == '__main__':
    runner = IoticLamp('../cfg/smartlamp.ini')
    in_foreground(runner)

