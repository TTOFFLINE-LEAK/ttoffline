from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObjectAI
from otp.distributed.OtpDoGlobals import *
import json, os
colorsJsonDefaultValues = '{\n    "colors":\n    [\n        {\n            "name": "African Violet",\n            "value": [0.70, 0.52, 0.75, 1.0]\n        },\n        {\n            "name": "Lime Green",\n            "value": [0.50, 1.0, 0.00, 1.0]\n        }\n    ]\n}\n'
sosJsonDefaultValues = '{\n    "name" : ["Von", "Von II"],\n    "id": [1014, 1015],\n    "head": ["dss", "hss"],\n    "torso": ["ls", "ms"],\n    "legs": ["m", "m"],\n    "gender": ["m", "f"],\n    "head-color": [27, 7],\n    "arm-color": [27, 7],\n    "leg-color": [27, 7],\n    "glove-color": [27, 7],\n    "shirt-id": [0, 95],\n    "shirt-color": [0, 27],\n    "sleeve-id": [0, 95],\n    "sleeve-color": [0, 27],\n    "bottoms-id": [0, 6],\n    "bottoms-color": [0, 2],\n    "has-building": [0, 0],\n    "gag-track": [6, 1],\n    "gag-level": [0, 6],\n    "gag-damage": [255, 200],\n    "rating": [5, 5],\n    "zone": [-1, -1],\n    "type": [0, 0],\n    "hat": [[0, 0, 0], [0, 0, 0]],\n    "glasses": [[0, 0, 0], [0, 0, 0]],\n    "backpack": [[0, 0, 0], [0, 0, 0]],\n    "shoes": [[0, 0, 0], [0, 0, 0]]\n}\n'

class ModdingManagerAI(DistributedObjectAI.DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('ModdingManagerAI')

    def __init__(self, air):
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        self.colors = {}
        self.cards = {}
        self.generateColors()
        self.generateCards()

    def generateColors(self):
        if not os.path.exists('config/'):
            os.mkdir('config/')
        if not os.path.isfile('config/colors.json'):
            with open('config/colors.json', 'w') as (data):
                data.write(colorsJsonDefaultValues)
                data.close()
        with open('config/colors.json') as (data):
            colors = json.load(data)
        colors = json.dumps(colors)
        self.setColors(colors)

    def setColorsAiToUd(self, colors):
        self.sendUpdateToUD('setColorsAiToUd', [colors])

    def setColors(self, colors):
        self.colors = colors

    def getColors(self):
        return self.colors

    def generateCards(self):
        if not os.path.exists('config/'):
            os.mkdir('config/')
        if not os.path.isfile('config/sos.json'):
            with open('config/sos.json', 'w') as (data):
                data.write(sosJsonDefaultValues)
                data.close()
        with open('config/sos.json') as (data):
            sos = json.load(data)
        sos = json.dumps(sos)
        self.setCards(sos)

    def setCardsAiToUd(self, sos):
        self.sendUpdateToUD('setCardsAiToUd', [sos])

    def setCards(self, cards):
        self.cards = cards

    def getCards(self):
        return self.cards

    def d_setDefaultMaxToon(self, state):
        self.sendUpdate('setDefaultMaxToon', [state])

    def d_setDefaultZone(self, zone):
        self.sendUpdate('setDefaultZone', [zone])

    def sendUpdateToUD(self, field, args=[]):
        dg = self.dclass.aiFormatUpdate(field, OTP_DO_ID_MODDING_MANAGER, OTP_DO_ID_MODDING_MANAGER, self.doId, args)
        self.air.send(dg)