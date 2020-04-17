from collections import OrderedDict
from direct.distributed import DistributedObjectAI
from direct.distributed.ClockDelta import globalClockDelta
from direct.directnotify import DirectNotifyGlobal
from direct.task import Task
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
MAX_PROPS = 0
PROPS_LOCKED = 1
PROPS_LOCKED_ZONE = 2
PROPS_UNLOCKED = 3
PROPS_UNLOCKED_ZONE = 4
PROPS_SPAWNING_LOCKED = 5
PROPS_DELETED = 6
PROPS_DELETED_ZONE = 7
PROPS_SPAMMING = 8
PROPS_ERROR = 9

class DistributedPropGeneratorAI(DistributedObjectAI.DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPropGeneratorAI')

    def __init__(self, air, zoneId):
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        self.zoneId = zoneId
        self.propInfo = OrderedDict()
        self.context = 0
        self.locked = False
        self.recentAvatars = {}

    def announceGenerate(self):
        DistributedObjectAI.DistributedObjectAI.announceGenerate(self)
        taskMgr.doMethodLater(0.5, self.propCooldown, self.uniqueName('propCooldown'))

    def requestProps(self):
        if not self.propInfo:
            return
        avId = self.air.getAvatarIdFromSender()
        for prop in self.propInfo.values():
            self.sendUpdateToAvatarId(avId, 'loadProp', [prop])

        self.sendUpdateToAvatarId(avId, 'loadProps', [])

    def d_spawnProp(self, propName, x, y, z, h, p, r, sX, sY, sZ):
        spawnTime = globalClockDelta.getRealNetworkTime(bits=32)
        creatorAvId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(creatorAvId)
        if av:
            creatorName = av.getName()
        else:
            creatorName = TTLocalizer.WordPageNA
        editorAvId = 0
        editorName = TTLocalizer.WordPageNA
        lockedState = 0
        reparentProp = 0
        reparentState = 0
        if len(self.propInfo.keys()) >= ToontownGlobals.MaxPropCount:
            self.sendUpdateToAvatarId(creatorAvId, 'propMessage', [MAX_PROPS])
            return
        if self.locked:
            self.sendUpdateToAvatarId(creatorAvId, 'propMessage', [PROPS_SPAWNING_LOCKED])
            return
        if creatorAvId in self.recentAvatars:
            if self.recentAvatars.get(creatorAvId) >= 5:
                self.sendUpdateToAvatarId(creatorAvId, 'propMessage', [PROPS_SPAMMING])
                return
            self.recentAvatars[creatorAvId] += 1
        if creatorAvId not in self.recentAvatars:
            self.recentAvatars[creatorAvId] = 1
        self.addPropInfo(self.context, propName, x, y, z, h, p, r, sX, sY, sZ, 1, 1, 1, 1, spawnTime, creatorAvId, creatorName, editorAvId, editorName, lockedState, reparentProp, reparentState)
        self.sendUpdate('spawnProp', [(self.context, propName, x, y, z, h, p, r, sX, sY, sZ, 1, 1, 1, 1, spawnTime, creatorAvId, creatorName, editorAvId, editorName, lockedState, reparentProp, reparentState)])
        self.context += 1

    def d_dupeProp(self, propId):
        spawnTime = globalClockDelta.getRealNetworkTime(bits=32)
        creatorAvId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(creatorAvId)
        if av:
            creatorName = av.getName()
        else:
            creatorName = TTLocalizer.WordPageNA
        editorAvId = 0
        editorName = TTLocalizer.WordPageNA
        if len(self.propInfo.keys()) >= ToontownGlobals.MaxPropCount:
            self.sendUpdateToAvatarId(creatorAvId, 'propMessage', [MAX_PROPS])
            return
        if self.locked:
            self.sendUpdateToAvatarId(creatorAvId, 'propMessage', [PROPS_SPAWNING_LOCKED])
            return
        if creatorAvId in self.recentAvatars:
            if self.recentAvatars.get(creatorAvId) >= 5:
                self.sendUpdateToAvatarId(creatorAvId, 'propMessage', [PROPS_SPAMMING])
                return
            self.recentAvatars[creatorAvId] += 1
        if creatorAvId not in self.recentAvatars:
            self.recentAvatars[creatorAvId] = 1
        propInfo = self.propInfo.get(propId)
        if not propInfo:
            self.sendUpdateToAvatarId(creatorAvId, 'propMessage', [PROPS_ERROR])
        self.addPropInfo(self.context, propInfo[1], propInfo[2], propInfo[3], propInfo[4], propInfo[5], propInfo[6], propInfo[7], propInfo[8], propInfo[9], propInfo[10], propInfo[11], propInfo[12], propInfo[13], propInfo[14], spawnTime, creatorAvId, creatorName, editorAvId, editorName, propInfo[20], propInfo[21], propInfo[22])
        self.sendUpdate('spawnProp', [
         (self.context, propInfo[1], propInfo[2], propInfo[3], propInfo[4], propInfo[5],
          propInfo[6], propInfo[7], propInfo[8], propInfo[9], propInfo[10], propInfo[11],
          propInfo[12], propInfo[13], propInfo[14], spawnTime, creatorAvId, creatorName,
          editorAvId, editorName, propInfo[20], propInfo[21], propInfo[22])])
        self.context += 1

    def confirmUpdateProp(self, propData):
        propId = propData[0]
        if propId not in self.propInfo:
            self.notify.warning('Received update for non-existant prop %d!' % propId)
            return
        propDataList = list(propData)
        propDataList[15] = globalClockDelta.getRealNetworkTime(bits=32)
        propData = tuple(propDataList)
        self.propInfo[propId] = propData
        self.d_updateProp(propData)

    def d_updateProp(self, propData):
        self.sendUpdate('updateProp', [propData])

    def addPropInfo(self, propId, propName, x, y, z, h, p, r, sX, sY, sZ, csR, csG, csB, csA, spawnTime, creatorAvId, creatorName, editorAvId, editorName, lockedState, reparentProp, reparentState):
        info = (
         propId, propName, x, y, z, h, p, r, sX, sY, sZ, csR, csG, csB, csA, spawnTime, creatorAvId, creatorName, editorAvId, editorName, lockedState, reparentProp, reparentState)
        if propId not in self.propInfo:
            self.notify.info(('INFO {0} NOT IN PROPINFO ADDING IT').format(propName))
            self.propInfo[propId] = info

    def d_openNewPropWindow(self):
        avId = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(avId, 'openNewPropWindow', [])

    def confirmDeleteProp(self, propId):
        avId = self.air.getAvatarIdFromSender()
        if propId not in self.propInfo:
            self.notify.warning('Received update for non-existant prop %d!' % propId)
            return
        for otherProp in self.propInfo.values():
            if otherProp[21] == propId and otherProp[22]:
                self.confirmDeleteProp(otherProp[0])

        del self.propInfo[propId]
        self.sendUpdate('deleteProp', [propId])

    def confirmDeleteAllProps(self, state):
        avId = self.air.getAvatarIdFromSender()
        if not state:
            self.deleteProps()
            self.sendUpdateToAvatarId(avId, 'propMessage', [PROPS_DELETED_ZONE])
        elif state:
            for propGeneratorId in self.air.propGenerators.keys():
                propGenerator = self.air.propGenerators[propGeneratorId]
                propGenerator.deleteProps()

            self.sendUpdateToAvatarId(avId, 'propMessage', [PROPS_DELETED])

    def deleteProps(self):
        self.propInfo = OrderedDict()
        self.context = 0
        self.sendUpdate('deleteAllProps', [])

    def confirmLockProps(self, state):
        avId = self.air.getAvatarIdFromSender()
        if not state:
            self.lockProps(state, avId)
        elif state:
            if not self.air.propGeneratorsLocked:
                self.air.propGeneratorsLocked = True
                self.sendUpdateToAvatarId(avId, 'propMessage', [PROPS_LOCKED])
            else:
                if self.air.propGeneratorsLocked:
                    self.air.propGeneratorsLocked = False
                    self.sendUpdateToAvatarId(avId, 'propMessage', [PROPS_UNLOCKED])
                for propGeneratorId in self.air.propGenerators.keys():
                    propGenerator = self.air.propGenerators[propGeneratorId]
                    propGenerator.lockProps(state)

    def lockProps(self, state=None, avId=0):
        if state:
            self.locked = self.air.propGeneratorsLocked
            return
        if not self.locked:
            self.locked = True
            self.sendUpdateToAvatarId(avId, 'propMessage', [PROPS_LOCKED_ZONE])
        elif self.locked:
            self.locked = False
            self.sendUpdateToAvatarId(avId, 'propMessage', [PROPS_UNLOCKED_ZONE])

    def propCooldown(self, task):
        for avId in self.recentAvatars.keys():
            self.recentAvatars[avId] -= 1
            if self.recentAvatars.get(avId) <= 0:
                del self.recentAvatars[avId]

        return Task.again