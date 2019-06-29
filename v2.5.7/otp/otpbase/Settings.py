import json, os

class Settings:

    def __init__(self, fileName='settings.json'):
        self.fileName = fileName
        if self.fileName.startswith('config/'):
            if not os.path.exists('config/'):
                os.mkdir('config/')
        try:
            with open(self.fileName, 'r') as (file):
                self.settings = json.load(file)
        except:
            self.settings = {}

    def updateSetting(self, type, attribute, value):
        with open(self.fileName, 'w+') as (file):
            if not self.settings.get(type):
                self.settings[type] = {}
            self.settings[type][attribute] = value
            json.dump(self.settings, file, indent=4)

    def getOption(self, type, attribute, default):
        return self.settings.get(type, {}).get(attribute, default)

    def getString(self, type, attribute, default=''):
        value = self.getOption(type, attribute, default)
        if isinstance(value, basestring):
            return value
        return default

    def getInt(self, type, attribute, default=0):
        value = self.getOption(type, attribute, default)
        if isinstance(value, (int, long)):
            return int(value)
        return default

    def getBool(self, type, attribute, default=False):
        value = self.getOption(type, attribute, default)
        if isinstance(value, bool):
            return value
        return default

    def getList(self, type, attribute, default=[], expectedLength=2):
        value = self.getOption(type, attribute, default)
        if isinstance(value, list) and len(value) == expectedLength:
            return value
        return default