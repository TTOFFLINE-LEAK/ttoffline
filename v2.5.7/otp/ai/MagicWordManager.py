from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObject
from otp.ai.MagicWordGlobal import *
lastClickedNametag = None

class MagicWordManager(DistributedObject.DistributedObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('MagicWordManager')
    neverDisable = 1

    def generate(self):
        DistributedObject.DistributedObject.generate(self)
        self.accept('magicWord', self.handleMagicWord)

    def disable(self):
        self.ignore('magicWord')
        DistributedObject.DistributedObject.disable(self)

    def rejectWord(self, resp):
        self.sendMagicWordResponse(resp)

    def handleMagicWord(self, magicWord):
        if base.localAvatar.getIsTeleporting():
            self.sendMagicWordResponse('You cannot use magic words while teleporting!')
            return
        if not self.cr.wantMagicWords:
            return
        if magicWord.startswith('~~~~'):
            magicWord = magicWord[4:]
            self.sendUpdate('sendGlobalMagicWord', [magicWord, True, True])
            return
        if magicWord.startswith('~~~'):
            magicWord = magicWord[3:]
            self.sendUpdate('sendGlobalMagicWord', [magicWord, True, False])
            return
        if magicWord.startswith('~~'):
            if lastClickedNametag == None:
                target = base.localAvatar
            else:
                target = lastClickedNametag
            magicWord = magicWord[2:]
        if magicWord.startswith('~'):
            target = base.localAvatar
            magicWord = magicWord[1:]
        if hasattr(target, 'animFSM') and target.animFSM.getCurrentState().getName() in ('TeleportIn',
                                                                                         'TeleportOut',
                                                                                         'TeleportedOut'):
            self.sendMagicWordResponse('You cannot use magic words on people who are teleporting!')
            return
        targetId = target.doId
        if target == base.localAvatar:
            response = spellbook.process(base.localAvatar, target, magicWord)
            if response[1]:
                if response[0]:
                    self.sendMagicWordResponse(response[0])
                self.sendUpdate('sendMagicWord', [magicWord, targetId, False])
                return
        self.sendUpdate('sendMagicWord', [magicWord, targetId, True])
        return

    def sendMagicWordResponse(self, response):
        self.notify.info(response)
        base.localAvatar.setSystemMessage(0, 'Magic Mille: ' + str(response))