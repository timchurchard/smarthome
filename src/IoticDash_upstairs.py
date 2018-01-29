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

from IoticAgent import ThingRunner
from IoticAgent.Core.compat import Event


DUREX_DASH_MAC = '68:37:e9:c5:9f:ff'
SHEBA_DASH_MAC = 'fc:a6:67:a1:58:bb'

LIGHTS = ['upstairs_lamp', 'bedroom_lamp']


button_evt = Event()


class IoticDash(ThingRunner):

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


# dashbutton.py - https://gist.github.com/mr-pj/75297864abef5c8f2d5c134be2656023#file-dashbutton-py

from pydhcplib.dhcp_network import *

netopt = {'client_listen_port':"68", 'server_listen_port':"67", 'listen_address':"0.0.0.0"}

class Server(DhcpServer):
    def __init__(self, options, dashbuttons):
        DhcpServer.__init__(self, options["listen_address"],
                                options["client_listen_port"],
                                options["server_listen_port"])
        self.dashbuttons = dashbuttons

    def HandleDhcpRequest(self, packet):
        mac = self.hwaddr_to_str(packet.GetHardwareAddress())
        self.dashbuttons.press(mac)


    def hwaddr_to_str(self, hwaddr):
        result = []
        hexsym = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
        for iterator in range(6) :
            result += [str(hexsym[hwaddr[iterator]/16]+hexsym[hwaddr[iterator]%16])]
        return ':'.join(result)

class DashButtons():
    def __init__(self):
        self.buttons = {}

    def register(self, mac, function):
        self.buttons[mac] = function

    def press(self, mac):
        if mac in self.buttons:
            self.buttons[mac]()
            return True
        return False

# dashbutton.py - end


def button_press():
    print("Got Dash button press!")
    button_evt.set()


def main():
    dashbuttons = DashButtons()
    dashbuttons.register(DUREX_DASH_MAC, button_press)
    dashbuttons.register(SHEBA_DASH_MAC, button_press)
    server = Server(netopt, dashbuttons)

    runner = IoticDash('../cfg/ioticdash.ini')
    runner.run(background=True)

    while True:
        try:
            server.GetNextDhcpPacket()
        except KeyboardInterrupt:
            break

    runner.stop()


if __name__ == '__main__':
    main()

