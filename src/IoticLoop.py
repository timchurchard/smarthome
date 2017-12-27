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

from IoticAgent import RetryingThingRunner

import pyloopenergy

from smarthome.Creds import Creds


class IoticLoop(RetryingThingRunner):

    def __init__(self, config=None):
        super(IoticLoop, self).__init__(config=config)
        #
        self.__creds = Creds()
        self.__loop = pyloopenergy.LoopEnergy(self.__creds.get('loop', 'serial'), self.__creds.get('loop', 'secret'))
        #
        self.__loop_private = None  # Thing
        self.__live = None          # Private Feed
        self.__loop_public = None   # Thing
        self.__delayed = None       # Public Feed

    def get_usage(self):
        return self.__loop.electricity_useage

    def store_usage(self):
        pass

    def get_hourly(self):
        pass

    def store_hourly(self):
        pass

    def on_startup(self):
        # Create Smarthome Loop Thing (Live, Private)
        self.__loop_private = self.client.create_thing("smartloop private")
        with self.__loop_private.get_meta() as meta:
            meta.set_label("Tim's House Smarthome Loop Private")
            meta.set_description("Loop Energy Live Private Data")
            meta.set_location(52.526087, 0.391160)  # Southery White Bell Pub
        self.__live = self.__loop_private.create_feed('data')
        self.__loop_private.set_public(False)
        # Create Smarthome Loop Thing (Delayed, Public)
        self.__loop_public = self.client.create_thing("smartloop public")
        with self.__loop_public.get_meta() as meta:
            meta.set_label("Tim's House Smarthome Loop Energy")
            meta.set_description("Loop Energy Data Hourly 28-day delayed")
            meta.set_location(52.526087, 0.391160)  # Southery White Bell Pub
        self.__delayed = self.__loop_public.create_feed('data')
        # TODO: self.__loop_public.set_public(True)
        self.__loop_public.set_public(False)

    def on_shutdown(self):
        self.__loop.terminate()

    def __elec_trace(self):
        self.__live.share({'usage': self.get_usage()})

    def main(self):
        self.__loop.subscribe_elecricity(self.__elec_trace)
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
    runner = IoticLoop('../cfg/smartloop.ini')
    in_foreground(runner)

