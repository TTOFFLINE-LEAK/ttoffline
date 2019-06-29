from DistributedNPCToonBase import *
from toontown.toonbase import TTLocalizer

class DistributedNPCKong(DistributedNPCToonBase):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedNPCKong')

    def handleCollisionSphereEnter(self, collEntry):
        self.sendUpdate('avatarEnter', [])

    def handleInteract(self, quoteId):
        try:
            quote = TTLocalizer.KongQuotes[quoteId]
        except IndexError:
            self.notify.warning('quote index %d out of range!')
            return

        self.setChatAbsolute(quote, CFSpeech | CFTimeout)