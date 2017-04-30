
import pyloopenergy

from .Creds import Creds


class Loop:

    def __init__(self):
        self.__creds = Creds()
        self.__loop = pyloopenergy.LoopEnergy(self.__creds.get('loop', 'serial'), self.__creds.get('loop', 'secret'))

    def get_usage(self):
        return self.__loop.electricity_useage

    def store_usage(self):
        pass

    def terminate(self):
        self.__loop.terminate()
