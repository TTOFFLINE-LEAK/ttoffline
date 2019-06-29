from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD

class CentralLoggerUD(DistributedObjectGlobalUD):
    notify = DirectNotifyGlobal.directNotify.newCategory('CentralLoggerUD')

    def sendMessage(self, category, eventString, targetDISLId, targetAvId):
        accId = self.air.getAccountIdFromSender()
        avId = self.air.getAvatarIdFromSender()
        self.air.writeServerEvent('central-logger-event', fromAccId=accId, fromAvId=avId, category=category, eventString=eventString, targetDISLId=targetDISLId, targetAvId=targetAvId)

    def logAIGarbage(self):
        pass