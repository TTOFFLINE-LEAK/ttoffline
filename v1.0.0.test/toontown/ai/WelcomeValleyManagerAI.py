from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from toontown.hood import ZoneUtil
from toontown.hood.GSHoodDataAI import GSHoodDataAI
from toontown.hood.TTHoodDataAI import TTHoodDataAI
from toontown.toonbase import ToontownGlobals

class WelcomeValleyManagerAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('WelcomeValleyManagerAI')

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)

    def requestZoneIdMessage(self, zoneId, context):
        avId = self.air.getAvatarIdFromSender()
        if zoneId == 0:
            zoneId = ToontownGlobals.WelcomeValleyBegin
        self.toonSetZone(avId, zoneId)
        self.sendUpdateToAvatarId(avId, 'requestZoneIdResponse', [zoneId, context])

    def toonSetZone(self, doId, zoneId):
        event = self.staticGetLogicalZoneChangeEvent(doId)
        inWelcomeValley = self.isAccepting(event)
        if not ZoneUtil.isDynamicZone(zoneId):
            if ZoneUtil.isWelcomeValley(zoneId) and not inWelcomeValley:
                self.air.districtStats.b_setNewAvatarCount(self.air.districtStats.getNewAvatarCount() + 1)
                self.accept(event, lambda newZoneId, _: self.toonSetZone(doId, newZoneId))
                self.accept(self.air.getAvatarExitEvent(doId), self.toonSetZone, extraArgs=[doId, 666])
            elif not ZoneUtil.isWelcomeValley(zoneId) and inWelcomeValley:
                self.air.districtStats.b_setNewAvatarCount(self.air.districtStats.getNewAvatarCount() - 1)
                self.ignore(event)
                self.ignore(self.air.getAvatarExitEvent(doId))

    def createWelcomeValleyHoods(self):
        self.air.createHood(TTHoodDataAI, 30000)
        self.air.createHood(GSHoodDataAI, 23000)