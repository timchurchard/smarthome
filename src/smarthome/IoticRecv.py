# /usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

from time import sleep
from threading import Lock
import sys
import logging

logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)s [%(name)s] {%(threadName)s} %(message)s',
                            level=logging.INFO)
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

from IoticAgent import ThingRunner



class IoticRecv(ThingRunner):

    def __init__(self, config=None):
        super(IoticRecv, self).__init__(config=config)
        #
        self.__recv = None

    def on_startup(self):
        # Create Smarthome Receiver Thing
        self.__recv = self.client.create_thing("smarthome")
        with self.__recv.get_meta() as meta:
            meta.set_label("Tim's House Smarthome Receiver")
            meta.set_description("Iotic behind control UI")
            meta.set_location(52.526087, 0.391160)  # Southery White Bell Pub

        # Setup subscriptions
        self.__snd_ctrl = self.__recv.attach(('snd ctrl', 'ctrl'))
        self.__recv.follow(('snd ctrl', 'feed'), self.__snd_ctrl_cb)

    def __snd_ctrl_cb(self, data):
        print("snd ctrl cb got data", data)

    def snd_ctrl_vol_up(self):
        self.__snd_ctrl.ask({'cmd': 'up'})

    def snd_ctrl_vol_down(self):
        self.__snd_ctrl.ask({'cmd': 'down'})

    def main(self):
        while True:
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
    runner = IoticRecv('../../cfg/smarthome.ini')
    in_foreground(runner)
