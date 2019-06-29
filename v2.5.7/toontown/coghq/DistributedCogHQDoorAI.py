from direct.directnotify import DirectNotifyGlobal
from toontown.building import DistributedDoorAI
from toontown.building import DoorTypes
from toontown.building import FADoorCodes
from toontown.coghq import CogDisguiseGlobals
from toontown.toonbase import ToontownGlobals

class DistributedCogHQDoorAI(DistributedDoorAI.DistributedDoorAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCogHQDoorAI')

    def __init__(self, air, blockNumber, doorType, destinationZone, doorIndex=0, lockValue=FADoorCodes.SB_DISGUISE_INCOMPLETE, swing=3):
        DistributedDoorAI.DistributedDoorAI.__init__(self, air, blockNumber, doorType, doorIndex, lockValue, swing)
        self.destinationZone = destinationZone

    def enter(self, avId):
        self.enqueueAvatarIdEnter(avId)
        self.sendUpdateToAvatarId(avId, 'setOtherZoneIdAndDoId', [self.destinationZone, self.otherDoor.getDoId()])

    def requestEnter(self):
        avId = self.air.getAvatarIdFromSender()
        dept = ToontownGlobals.cogHQZoneId2deptIndex(self.destinationZone)
        av = self.air.doId2do.get(avId)
        if av:
            if self.doorType == DoorTypes.EXT_COGHQ and self.isLockedDoor():
                parts = av.getCogParts()
                if CogDisguiseGlobals.isSuitComplete(parts, dept):
                    allowed = 1
                else:
                    allowed = 0
            else:
                allowed = 1
            if not allowed:
                self.sendReject(avId, self.isLockedDoor())
            else:
                self.enter(avId)

    def requestExit(self):
        avId = self.air.getAvatarIdFromSender()
        if self.avatarsWhoAreEntering.has_key(avId):
            del self.avatarsWhoAreEntering[avId]
        if not self.avatarsWhoAreExiting.has_key(avId):
            dept = ToontownGlobals.cogHQZoneId2deptIndex(self.destinationZone)
            self.avatarsWhoAreExiting[avId] = 1
            self.sendUpdate('avatarExit', [avId])
            self.openDoor(self.exitDoorFSM)
            if self.lockedDoor:
                av = self.air.doId2do[avId]
                if self.doorType == DoorTypes.EXT_COGHQ:
                    av.b_setCogIndex(-1)
                else:
                    av.b_setCogIndex(dept)