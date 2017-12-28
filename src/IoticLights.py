# /usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

from time import sleep
from copy import copy

from qhue import Bridge

import logging
logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)s [%(name)s] {%(threadName)s} %(message)s',
                            level=logging.INFO)
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

from pytradfri import Gateway
from pytradfri.api.libcoap_api import APIFactory
from pytradfri.error import PytradfriError, RequestTimeout
from pytradfri.util import load_json, save_json

from IoticAgent import RetryingThingRunner

from smarthome.Creds import Creds


LIGHTS = {
    'front_lamp': {
        'type': 'ikea',
        'ids': [65538]
    },
    'liv_main': {
        'type': 'ikea',
        'ids': [65539]
    },
    'kitchen_lamp': {
        'type': 'ikea',
        'ids': [65540, 65541, 65542]
    },
    'upstairs_lamp': {
        'type': 'philips',
        'uniqueid': '00:17:88:01:02:b2:10:26-0b'
    },
    'bedroom_lamp': {
        'type': 'philips',
        'uniqueid': '00:17:88:01:02:b0:10:65-0b'
    }
}
TMPL_STATE = {
    'reachable': False,
    'on': False,
    'bri': 0
}


class IoticLights(RetryingThingRunner):

    def __init__(self, config=None):
        super(IoticLights, self).__init__(config=config)
        #
        self.__creds = Creds()
        #
        self.__thing = None
        self.__feed = None
        self.__ctrl = None
        #
        self.__state = {}
        for id in LIGHTS:
            self.__state[id] = copy(TMPL_STATE)
        #
        hueip = self.__creds.get('lights', 'hue_ip')
        huekey = self.__creds.get('lights', 'hue_key')
        self.__hue = Bridge(hueip, huekey)
        #
        self.__ikea_api, self.__ikea_lights = self.__get_ikea_lights()

    def __ctrl_cb(self, data):
        lamp = None
        cmd = None
        is_philips = False
        if 'data' in data and 'lamp' in data['data'] and 'cmd' in data['data']:
            if data['data']['lamp'] in LIGHTS:
                lamp = data['data']['lamp']
                if LIGHTS[lamp]['type'] == 'philips':
                    is_philips = True
            if data['data']['cmd'] in ['on', 'off']:
                cmd = True if data['data']['cmd'] == 'on' else False
        else:
            print("__ctrl_cb: Unknown data (need lamp & cmd)", data['data'])
            return

        if lamp is not None and cmd is not None:
            print("__ctrl_cb: Turning lamp (%s) to state (%s)" % (lamp, cmd))
            try:
                self.__ctrl_lamp(is_philips, lamp, cmd)
            except:
                logger.error("__ctrl_lamp failed", exc_info=True)
            self.__feed.share(self.__state)
        else:
            print("__ctrl_cb: Unknown data", data['data'])

    def __ctrl_lamp(self, is_philips, lamp, on):
        if is_philips:
            for id, data in self.__hue.lights().items():
                if data['uniqueid'] == LIGHTS[lamp]['uniqueid']:
                    try:
                        bri=254 if on else 0
                        self.__hue.lights[id].state(on=on, bri=bri)
                    except:
                        logger.error("Philips Hue API Failure", exc_info=True)
                    self.__update_philips_state()
        else:
            if self.__ikea_lights is None:
                self.__ikea_api, self.__ikea_lights = self.__get_ikea_lights()
            if self.__ikea_lights is not None:
                for uid in LIGHTS[lamp]['ids']:
                    for light in self.__ikea_lights:
                        if light.id == uid:
                            cmd = light.light_control.set_state(on)
                            self.__ikea_api(cmd)
                self.__update_ikea_state()


    def __update_philips_state(self):
        try:
            for id, data in self.__hue.lights().items():
                for lid, ldata in LIGHTS.items():
                    if LIGHTS[lid]['type'] != 'philips':
                        continue
                    if LIGHTS[lid]['uniqueid'] == data['uniqueid']:
                        self.__state[lid]['state'] = {
                            'reachable': data['state']['reachable'],
                            'on': data['state']['on'],
                            'bri': data['state']['bri']
                        }
        except:
            logger.error("Fail to update philips light state", exc_info=True)

    def __get_ikea_conn(self):
        confpath = "pytradfri.cfg.json"
        #
        ikea_ip = self.__creds.get('lights', 'ikea_ip')
        ikea_key = self.__creds.get('lights', 'ikea_key')
        #
        conf = load_json(confpath)
        try:
            identity = conf[ikea_ip].get('id')
            psk = conf[ikea_ip].get('psk')
            api_factory = APIFactory(host=ikea_ip, psk_id=identity, psk=psk)
        except:
            api_factory = APIFactory(host=ikea_ip, psk_id=identity)
            try:
                psk = api_factory.generate_psk(ikea_key)
                print('Generated PSK: ', psk)

                identity = "IoticLights.py.ikea"
                conf[ikea_ip] = {'id': identity,
                                 'psk': psk}
                save_json(confpath, conf)
            except AttributeError:
                logger.error("Failed to save generated PSK")

        return api_factory

    def __get_ikea_lights(self):
        conn = self.__get_ikea_conn()

        api = lights = None
        try:
            api = conn.request
            gw = Gateway()

            devices_command = gw.get_devices()
            devices_commands = api(devices_command)
            devices = api(devices_commands)

            lights = [dev for dev in devices if dev.has_light_control]
        except RequestTimeout:
            logger.error("Failed to get ikea lights")

        return api, lights

    def __update_ikea_state(self):
        # Note: Need to destroy connection else get stale status
        self.__ikea_lights = None
        #
        if self.__ikea_lights is None:
            self.__ikea_api, self.__ikea_lights = self.__get_ikea_lights()
        if self.__ikea_lights is not None:
            for light in self.__ikea_lights:
                for lid, data in LIGHTS.items():
                    if LIGHTS[lid]['type'] != 'ikea':
                        continue
                    if light.id in LIGHTS[lid]['ids']:
                        # Note: For groups of lights only the 'last' one counts
                        self.__state[lid]['state'] = {
                            'reachable': True,  # TODO
                            'on': light.light_control.lights[0].state,
                            'bri': light.light_control.lights[0].dimmer
                        }

    def on_startup(self):
        # Create Smarthome Lights Thing (Private)
        self.__thing = self.client.create_thing("lights")
        with self.__thing.get_meta() as meta:
            meta.set_label("Tim's House Smarthome Lights Private")
            meta.set_description("Lights")
            meta.set_location(52.526087, 0.391160)  # Southery White Bell Pub
        self.__feed = self.__thing.create_feed('data')
        self.__ctrl = self.__thing.create_control("ctrl", self.__ctrl_cb)
        self.__thing.set_public(False)
        # Get light state
        self.__update_philips_state()
        self.__update_ikea_state()

    def main(self):
        while True:
            if self.wait_for_shutdown(30):
                return
            self.__update_philips_state()
            self.__update_ikea_state()
            self.__feed.share(self.__state)


def in_foreground(runner):
    try:
        # blocks until finished
        runner.run()
    except KeyboardInterrupt:
        pass
    finally:
        runner.stop()

if __name__ == '__main__':
    runner = IoticLights('../cfg/ioticlights.ini')
    in_foreground(runner)

