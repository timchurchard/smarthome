# /usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

from time import sleep
from threading import Lock
import nest
import sys

import logging

logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)s [%(name)s] {%(threadName)s} %(message)s',
                            level=logging.INFO)
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

from IoticAgent import ThingRunner


from Creds import Creds


# How often to poll the Nest API
LIVE_FREQ = 30


class IoticNest(ThingRunner):

    def __init__(self, config=None):
        super(IoticNest, self).__init__(config=config)
        #
        creds = Creds()
        client_id = creds.get('nest', 'id')
        client_secret = creds.get('nest', 'secret')
        access_token_cache_file = 'nest_test.cache.json'
        #
        self.__napi = nest.Nest(client_id=client_id, client_secret=client_secret, access_token_cache_file=access_token_cache_file)
        if self.__napi.authorization_required:
            print('Go to ' + self.__napi.authorize_url + ' to authorize, then enter PIN below')
            if sys.version_info[0] < 3:
                pin = raw_input("PIN: ")
            else:
                pin = input("PIN: ")
            self.__napi.request_token(pin)

    def on_startup(self):
        # Create Smarthome Nest Thing (Live, Private)
        self.__nest_private = self.client.create_thing("smartnest private")
        with self.__nest_private.get_meta() as meta:
            meta.set_label("Tim's House Smarthome Nest Private")
            meta.set_description("Nest Live Private Data")
            meta.set_location(52.526087, 0.391160)  # Southery White Bell Pub
        self.__live = self.__nest_private.create_feed('data')
        self.__ctrl = self.__nest_private.create_control('ctrl', self.__cb_ctrl)
        self.__nest_private.set_public(False)

    def on_shutdown(self):
        pass

    def __cb_ctrl(self, data):
        print("TODO: Got ctrl data", data)
        # The Nest object can also be used as a context manager
        # with nest.Nest(client_id=client_id, client_secret=client_secret, access_token_cache_file=access_token_cache_file) as napi:
        #    for device in napi.thermostats:
        #        device.temperature = 23

    def __get_thermo_state(self):
        share_data = {
                'device_name': 0,
                'state': 0,
                'temp': 0,
                'target': 0,
                'emergency': 0,
                'online': 0}

        for structure in self.__napi.structures:
            share_data['device_name'] = structure.name + ' '

            for device in structure.thermostats:
                share_data['device_name'] += device.name
                share_data['state'] = device.hvac_state
                share_data['temp'] = device.temperature
                share_data['target'] = device.target
                share_data['emergency'] = device.is_using_emergency_heat
                share_data['online'] = device.online
                break

        self.__live.share(share_data)

    def main(self):
        while True:
            self.__get_thermo_state()
            if self.wait_for_shutdown(LIVE_FREQ):
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
    runner = IoticNest('../../cfg/smartnest.ini')
    in_foreground(runner)

