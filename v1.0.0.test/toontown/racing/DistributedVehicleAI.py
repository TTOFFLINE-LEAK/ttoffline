from otp.ai.AIBase import *
from toontown.toonbase.ToontownGlobals import *
from toontown.racing.KartDNA import *
from direct.distributed.ClockDelta import *
from direct.distributed import DistributedSmoothNodeAI
from direct.fsm import FSM
from direct.task import Task

class DistributedVehicleAI(DistributedSmoothNodeAI.DistributedSmoothNodeAI, FSM.FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedVehicleAI')

    def __init__(self, air, avId):
        self.ownerId = avId
        DistributedSmoothNodeAI.DistributedSmoothNodeAI.__init__(self, air)
        FSM.FSM.__init__(self, 'DistributedVehicleAI')
        self.driverId = 0
        self.kartDNA = [-1] * getNumFields()
        self.__initDNA()
        self.request('Off')
        self.controlled = False

    def generate(self):
        DistributedSmoothNodeAI.DistributedSmoothNodeAI.generate(self)

    def delete(self):
        DistributedSmoothNodeAI.DistributedSmoothNodeAI.delete(self)

    def __initDNA(self):
        owner = self.air.doId2do.get(self.ownerId)
        if owner:
            self.kartDNA[KartDNA.bodyType] = owner.getKartBodyType()
            self.kartDNA[KartDNA.bodyColor] = owner.getKartBodyColor()
            self.kartDNA[KartDNA.accColor] = owner.getKartAccessoryColor()
            self.kartDNA[KartDNA.ebType] = owner.getKartEngineBlockType()
            self.kartDNA[KartDNA.spType] = owner.getKartSpoilerType()
            self.kartDNA[KartDNA.fwwType] = owner.getKartFrontWheelWellType()
            self.kartDNA[KartDNA.bwwType] = owner.getKartBackWheelWellType()
            self.kartDNA[KartDNA.rimsType] = owner.getKartRimType()
            self.kartDNA[KartDNA.decalType] = owner.getKartDecalType()
        else:
            self.notify.warning('__initDNA - OWNER %s OF KART NOT FOUND!' % self.ownerId)

    def setControlled(self, controlled):
        self.controlled = controlled

    def d_setControlled(self, controlled):
        self.sendUpdate('setControlled', [controlled])

    def b_setControlled(self, controlled):
        self.d_setControlled(controlled)
        self.setControlled(controlled)

    def getControlled(self):
        return self.controlled

    def d_setState(self, state):
        self.sendUpdate('setState', [state])

    def requestControl(self):
        avId = self.air.getAvatarIdFromSender()
        if avId == self.ownerId:
            self.request('Controlled', avId)

    def requestParked(self):
        avId = self.air.getAvatarIdFromSender()
        if avId == self.ownerId:
            self.request('Parked')

    def start(self):
        self.request('Controlled')

    def enterOff(self):
        return

    def exitOff(self):
        return

    def enterParked(self):
        self.driverId = 0
        self.d_setState('P')
        return

    def exitParked(self):
        return

    def enterControlled(self):
        fieldList = [
         'setComponentL',
         'setComponentX',
         'setComponentY',
         'setComponentZ',
         'setComponentH',
         'setComponentP',
         'setComponentR',
         'setComponentT',
         'setSmStop',
         'setSmH',
         'setSmZ',
         'setSmXY',
         'setSmXZ',
         'setSmPos',
         'setSmHpr',
         'setSmXYH',
         'setSmXYZH',
         'setSmPosHpr',
         'setSmPosHprL',
         'clearSmoothing',
         'suggestResync',
         'returnResync']
        self.air.setAllowClientSend(self.ownerId, self, fieldNameList=fieldList)
        self.d_setState('C')

    def exitControlled(self):
        pass

    def __handleUnexpectedExit(self):
        self.notify.warning('toon: %d exited unexpectedly, resetting vehicle %d' % (self.driverId, self.doId))
        self.request('Parked')
        self.requestDelete()

    def requestExplosion(self, doId):
        avId = self.air.getAvatarIdFromSender()
        if avId != self.ownerId:
            return
        else:
            owner = self.air.doId2do.get(self.ownerId)
            if not owner or owner.getHp() < 10 or not owner.getCarActive():
                return
            do = self.air.doId2do.get(doId)
            if not do or do.__class__.__name__ != 'DistributedSuitAI' or not hasattr(do, 'sp') or not do.sp or not do.isWalking():
                return
            do.sp.removeSuit(do)
            do.sp = None
            owner.takeDamage(10)
            self.sendUpdate('explosion', [])
            return

    def d_setNonRace(self, state):
        self.sendUpdate('setNonRace', [state])

    def getBodyType(self):
        return self.kartDNA[KartDNA.bodyType]

    def getBodyColor(self):
        return self.kartDNA[KartDNA.bodyColor]

    def getAccessoryColor(self):
        return self.kartDNA[KartDNA.accColor]

    def getEngineBlockType(self):
        return self.kartDNA[KartDNA.ebType]

    def getSpoilerType(self):
        return self.kartDNA[KartDNA.spType]

    def getFrontWheelWellType(self):
        return self.kartDNA[KartDNA.fwwType]

    def getBackWheelWellType(self):
        return self.kartDNA[KartDNA.bwwType]

    def getRimType(self):
        return self.kartDNA[KartDNA.rimsType]

    def getDecalType(self):
        return self.kartDNA[KartDNA.decalType]

    def getOwner(self):
        return self.ownerId