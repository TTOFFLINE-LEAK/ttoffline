import json, os
from direct.directnotify import DirectNotifyGlobal

class Settings:
    notify = DirectNotifyGlobal.directNotify.newCategory('Settings')

    def __init__(self, fileName='settings.json'):
        self.fileName = fileName
        if os.path.dirname(self.fileName) and not os.path.exists(os.path.dirname(self.fileName)):
            os.makedirs(os.path.dirname(self.fileName))
        try:
            with open(self.fileName, 'r') as (f):
                self.settings = json.load(f)
        except:
            self.settings = {}

    def getOption(self, category, attribute, default):
        return self.settings.get(category, {}).get(attribute, default)

    def getBool(self, category, attribute, default=False):
        value = self.getOption(category, attribute, default)
        if isinstance(value, bool):
            return value
        return default

    def getFloat(self, category, attribute, default=1.0):
        value = self.getOption(category, attribute, default)
        if isinstance(value, float):
            return value
        return default

    def getList(self, category, attribute, default=[], expectedLength=2):
        value = self.getOption(category, attribute, default)
        if isinstance(value, list) and len(value) == expectedLength:
            return value
        return default

    def getInt(self, category, attribute, default=0):
        value = self.getOption(category, attribute, default)
        if isinstance(value, (int, long)):
            return int(value)
        return default

    def getString(self, category, attribute, default=''):
        value = self.getOption(category, attribute, default)
        if isinstance(value, basestring):
            return str(value)
        return default

    def doSavedSettingsExist(self):
        return os.path.exists(self.fileName)

    def writeSettings(self):
        with open(self.fileName, 'w+') as (f):
            json.dump(self.settings, f, indent=4)

    def updateSetting(self, category, attribute, value):
        if not self.settings.get(category):
            self.settings[category] = {}
        self.settings[category][attribute] = value
        self.writeSettings()