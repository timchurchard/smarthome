# /usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

import sys, os
from threading import Thread
import logging

logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)s [%(name)s] {%(threadName)s} %(message)s',
                            level=logging.INFO)
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

from scapy.all import *

from IoticAgent import RetryingThingRunner
from IoticAgent.Core.compat import Event


DUREX_DASH_MAC = '68:37:e9:c5:9f:ff'
SHEBA_DASH_MAC = 'fc:a6:67:a1:58:bb'

LIGHTS = ['upstairs_lamp', 'bedroom_lamp']


button_evt = Event()


class IoticDash(RetryingThingRunner):

    def __init__(self, config=None):
        super(IoticDash, self).__init__(config=config)
        self.__on = True

    def on_startup(self):
        # Create snd_ctrl Thing
        self.__thing = self.client.create_thing("dash ctrl")
        with self.__thing.get_meta() as meta:
            meta.set_label("Tim's House RPI Dash button handler")
            meta.set_description("RPI Wifi sniffing for Dash")
            meta.set_location(52.526087, 0.391160)  # Southery White Bell Pub
        self.__thing.set_public(False)
        #
        self.__light_ctrl = self.__thing.attach(('lights', 'ctrl'))

    def main(self):
        global button_evt
        while True:
            if button_evt.is_set():
                for light in LIGHTS:
                    self.__light_ctrl.ask({'lamp': light, 'cmd': 'on' if self.__on else 'off'})
                self.__on = False if self.__on else True
                button_evt.clear()
            if self.wait_for_shutdown(2):
                return


def arp_display(pkt):
    global button_evt
    if pkt.haslayer(ARP): # Needed for Raspberry Pi
        if pkt[ARP].op == 1: #who-has (request)
            if pkt[ARP].hwsrc == DUREX_DASH_MAC:
                print("Pushed Durex!")
                button_evt.set()
            if pkt[ARP].hwsrc == SHEBA_DASH_MAC:
                print("Pushed Sheba!")
                button_evt.set()


def main():
    runner = IoticDash('../cfg/ioticdash.ini')
    runner.run(background=True)

    try:
        sniff(prn=arp_display, filter="arp", store=0, count=0)
    except:
        pass

    runner.stop()


if __name__ == '__main__':
    main()

