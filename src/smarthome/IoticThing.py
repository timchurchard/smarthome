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

from .Temp import Temp


class IoticThing(ThingRunner):

    def __init__(self, config=None):
        super(IoticThing, self).__init__(config=config)
        #
        self.__temp = Temp()

    def on_startup(self):
        # Create Temperature Thing
        self.__temp_thing = self.client.create_thing("smart_temp")
        with self.__temp_thing.get_meta() as meta:
            meta.set_label("Tim's House Hallway Temperature")
            meta.set_description("Arduino with TMP36 sensor")
            meta.set_location(52.526087, 0.391160)  # Southery White Bell Pub
        self.__temp_feed = self.__temp_thing.create_feed("data")
        self.__temp_thing.set_public(True)

    def main():

        while True:

            temp_time, temp, light = self.__temp.get_temp()

            if self.wait_for_shutdown(10):
                return

