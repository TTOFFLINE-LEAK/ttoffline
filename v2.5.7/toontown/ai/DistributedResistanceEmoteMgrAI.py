from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from otp.otpbase.OTPLocalizer import EmoteFuncDict

class DistributedResistanceEmoteMgrAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedResistanceEmoteMgrAI')

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.air = air

    def addResistanceEmote(self):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if not av:
            return
        RESIST_INDEX = EmoteFuncDict['Resistance Salute']
        av.emoteAccess[RESIST_INDEX] = 1
        av.d_setEmoteAccess(av.emoteAccess)