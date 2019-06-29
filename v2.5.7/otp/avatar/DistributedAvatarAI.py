from otp.ai.MagicWordGlobal import *
from otp.otpbase import OTPGlobals
from direct.fsm import ClassicFSM
from direct.fsm import State
from direct.distributed import DistributedNodeAI
from direct.task import Task
from toontown.toonbase import ToontownGlobals

class DistributedAvatarAI(DistributedNodeAI.DistributedNodeAI):

    def __init__(self, air):
        DistributedNodeAI.DistributedNodeAI.__init__(self, air)
        self.hp = 0
        self.maxHp = 0

    def b_setName(self, name):
        self.setName(name)
        self.d_setName(name)

    def d_setName(self, name):
        self.sendUpdate('setName', [name])

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def b_setMaxHp(self, maxHp):
        self.d_setMaxHp(maxHp)
        self.setMaxHp(maxHp)

    def d_setMaxHp(self, maxHp):
        self.sendUpdate('setMaxHp', [maxHp])

    def setMaxHp(self, maxHp):
        self.maxHp = maxHp

    def getMaxHp(self):
        return self.maxHp

    def b_setHp(self, hp):
        self.d_setHp(hp)
        self.setHp(hp)

    def d_setHp(self, hp):
        self.sendUpdate('setHp', [hp])

    def setHp(self, hp):
        self.hp = hp

    def getHp(self):
        return self.hp

    def b_setLocationName(self, locationName):
        self.d_setLocationName(locationName)
        self.setLocationName(locationName)

    def d_setLocationName(self, locationName):
        pass

    def setLocationName(self, locationName):
        self.locationName = locationName

    def getLocationName(self):
        return self.locationName

    def b_setActivity(self, activity):
        self.d_setActivity(activity)
        self.setActivity(activity)

    def d_setActivity(self, activity):
        pass

    def d_setLoop(self, loop, start, end, partName):
        self.sendUpdate('setLoop', [loop, start, end, partName])

    def d_setPose(self, anim, frame, partName):
        self.sendUpdate('setPose', [anim, frame, partName])

    def d_setPingPong(self, anim, start, end, partName):
        self.sendUpdate('setPingPong', [anim, start, end, partName])

    def d_setLeftHand(self, prop):
        self.sendUpdate('setLeftHand', [prop])

    def d_setRightHand(self, prop):
        self.sendUpdate('setRightHand', [prop])

    def d_spawnProp(self, prop):
        self.sendUpdate('spawnProp', [prop])

    def setActivity(self, activity):
        self.activity = activity

    def getActivity(self):
        return self.activity

    def toonUp(self, num):
        if self.hp >= self.maxHp:
            return
        self.hp = min(self.hp + num, self.maxHp)
        self.b_setHp(self.hp)

    def getRadius(self):
        return OTPGlobals.AvatarDefaultRadius

    def checkAvOnShard(self, avId):
        senderId = self.air.getAvatarIdFromSender()
        onShard = False
        if simbase.air.doId2do.get(avId):
            onShard = True
        self.sendUpdateToAvatarId(senderId, 'confirmAvOnShard', [avId, onShard])


@magicWord(category=CATEGORY_OVERRIDE, types=[str, int, int, str])
def loop(anim, start=-1, end=-1, part=''):
    target = spellbook.getTarget()
    target.d_setLoop(anim, start, end, partName=part)


@magicWord(category=CATEGORY_OVERRIDE, types=[str, int, str])
def pose(anim, frame, part=''):
    target = spellbook.getTarget()
    target.d_setPose(anim, frame, partName=part)


@magicWord(category=CATEGORY_OVERRIDE, types=[str, int, int, str])
def pingpong(anim, start=-1, end=-1, part=''):
    target = spellbook.getTarget()
    target.d_setPingPong(anim, start, end, partName=part)


@magicWord(category=CATEGORY_OVERRIDE, types=[str])
def rightHand(prop=''):
    target = spellbook.getTarget()
    target.d_setRightHand(prop)


@magicWord(category=CATEGORY_OVERRIDE, types=[str])
def leftHand(prop=''):
    target = spellbook.getTarget()
    target.d_setLeftHand(prop)


@magicWord(category=CATEGORY_SYSADMIN, types=[str])
def spawnProp(prop=''):
    if not config.GetBool('want-spawn-prop', False):
        return '~spawnProp is disabled'
    toon = spellbook.getInvoker()
    zone = toon.zoneId
    target = spellbook.getTarget()
    target.d_spawnProp(prop)