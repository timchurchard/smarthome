
import json


# Path to `git secret reveal`d secret
CFG = '../cfg/creds.json'


class Creds:

    def __init__(self):
        with open(CFG, 'r') as f:
            self.__json = json.loads(f.read())


    def get(self, section, value):
        return self.__json[section][value]
