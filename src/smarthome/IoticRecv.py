# /usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

import json
import logging

logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)s [%(name)s] {%(threadName)s} %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

from IoticAgent import RetryingThingRunner


class IoticRecv(RetryingThingRunner):

    def __init__(self, config, queue):
        super(IoticRecv, self).__init__(config=config)
        self.queue = queue
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
        # - IoticVolume - snd_ctrl
        self.__snd_ctrl = self.__recv.attach(('snd ctrl', 'ctrl'))
        self.__recv.follow(('snd ctrl', 'feed'), self.__snd_ctrl_cb)
        # - IoticTemp
        self.__recv.follow(('smart_temp', 'data'), self.__temp_cb)
        # - IoticLoop
        self.__recv.follow(('smartloop private', 'data'), self.__loop_cb)
        # - IoticNest
        self.__recv.follow(('smartnest private', 'data'), self.__nest_cb)
        # - IoticLamp - Energenie Living room Lamp
        self.__lamp_ctrl = self.__recv.attach(('lamp ctrl', 'ctrl'))
        self.__recv.follow(('lamp ctrl', 'feed'), self.__lamp_data_cb)
        # - IoticLights - Ikea & Philips Lights
        self.__lights_ctrl = self.__recv.attach(('lights', 'ctrl'))
        self.__recv.follow(('lights', 'data'), self.__lights_data_cb)

    def __lights_data_cb(self, data):
        print("lights data cb got data", data)
        self.queue.put(json.dumps({'from': 'lights_ctrl', 'data': data['data']}))

    def __lamp_data_cb(self, data):
        print("lamp data cb got data", data)
        self.queue.put(json.dumps({'from': 'lamp_ctrl', 'state': data['data']['state']}))

    def lamp_ctrl_on(self):
        self.__lamp_ctrl.ask({'cmd': 'on'})

    def lamp_ctrl_off(self):
        self.__lamp_ctrl.ask({'cmd': 'off'})

    def __snd_ctrl_cb(self, data):
        print("snd ctrl cb got data", data)
        self.queue.put(json.dumps({'from': 'snd_ctrl', 'level': data['data']['level'], 'state': data['data']['state']}))

    def snd_ctrl_vol_up(self):
        self.__snd_ctrl.ask({'cmd': 'up'})

    def snd_ctrl_vol_down(self):
        self.__snd_ctrl.ask({'cmd': 'down'})

    def lights_ctrl(self, lamp, cmd):
        self.__lights_ctrl.ask({'lamp': lamp, 'cmd': cmd})

    def __temp_cb(self, data):
        print("temp_cb got data", data)
        self.queue.put(json.dumps({'from': 'temp', 'temp': data['data']['temp'], 'light': data['data']['light']}))

    def __loop_cb(self, data):
        print("loop_cb got data", data)
        self.queue.put(json.dumps({'from': 'loop', 'usage': data['data']['usage']}))

    def __nest_cb(self, data):
        print("nest_cb got data", data)
        self.queue.put(json.dumps({'from': 'nest', 'data': data['data']}))

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
    from queue import Queue
    queue = Queue()
    runner = IoticRecv('../../cfg/smarthome.ini', queue)
    in_foreground(runner)
