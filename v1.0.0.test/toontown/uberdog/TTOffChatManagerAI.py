from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectGlobalAI import DistributedObjectGlobalAI
from otp.distributed import OtpDoGlobals

class TTOffChatManagerAI(DistributedObjectGlobalAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('TTOffChatManagerAI')

    def announceGenerate(self):
        DistributedObjectGlobalAI.announceGenerate(self)
        self.sendUpdateToUD('addChatManager', [self.doId])

    def sendUpdateToUD(self, field, args=[]):
        dg = self.dclass.aiFormatUpdate(field, OtpDoGlobals.OTP_DO_ID_CHAT_MANAGER, OtpDoGlobals.OTP_DO_ID_CHAT_MANAGER, self.doId, args)
        self.air.send(dg)

    def receiveGlobalMessageUd2Ai(self, avName, message):
        self.sendUpdate('receiveGlobalMessage', [avName, message])