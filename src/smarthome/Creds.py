
import json


# Path to `git secret reveal`d secret
CFG = '../../cfg/creds.json'
CFG2 = '../cfg/creds.json'


class Creds:

    def __init__(self):
        try:
            with open(CFG, 'r') as f:
                self.__json = json.loads(f.read())
        except FileNotFoundError:
            with open(CFG2, 'r') as f:
                self.__json = json.loads(f.read())

    def get(self, section, value):
        return self.__json[section][value]
