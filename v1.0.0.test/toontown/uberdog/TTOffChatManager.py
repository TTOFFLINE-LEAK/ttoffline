from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal
from otp.otpbase import OTPGlobals
from libotp import WhisperPopup

class TTOffChatManager(DistributedObjectGlobal):
    notify = DirectNotifyGlobal.directNotify.newCategory('TTOffChatManager')

    def sendChatMessage(self, message):
        toon = base.cr.doId2do.get(base.localAvatar.doId)
        if not toon:
            return
        if not toon.getMuted():
            self.sendUpdate('chatMessage', [message[:OTPGlobals.MaxChatLength]])

    def sendWhisperMessage(self, message, receiverAvId):
        toon = base.cr.doId2do.get(base.localAvatar.doId)
        if not toon:
            return
        if not toon.getMuted():
            self.sendUpdate('whisperMessage', [message[:OTPGlobals.MaxChatLength], receiverAvId])

    def sendGlobalMessage(self, message):
        toon = base.cr.doId2do.get(base.localAvatar.doId)
        if not toon:
            return
        if not toon.getMuted():
            self.sendUpdate('globalMessage', [message[:OTPGlobals.MaxChatLength]])

    def receiveGlobalMessage(self, avName, message):
        messenger.send('addChatHistory', [avName.split('\n')[0], None, None, 'darkGreen', message.strip(),
         WhisperPopup.WTGlobal])
        if base.globalChatWhispers and hasattr(base, 'localAvatar'):
            base.localAvatar.setSystemMessage(0, avName.split('\n')[0] + ': ' + message.strip(), WhisperPopup.WTGlobal)
        return