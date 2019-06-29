from direct.distributed.ClockDelta import *
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedQuizGameAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedQuizGameAI')

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.participants = []
        self.currentQuestion = None
        return

    def addParticipant(self):
        avId = self.air.getAvatarIdFromSender()
        self.participants.append(avId)
        self.notify.info(('Avatar {0} joined the quiz.').format(avId))
        self.acceptOnce(self.air.getAvatarExitEvent(avId), self.removeParticipantById, extraArgs=[avId])

    def removeParticipant(self):
        try:
            avId = self.air.getAvatarIdFromSender()
            self.participants.remove(avId)
            self.ignore(self.air.getAvatarExitEvent(avId))
            self.notify.info(('Avatar {0} left the quiz.').format(avId))
        except:
            self.notify.warning(("Avatar {0} tried to leave the Quiz, but wasn't in the Quiz in the first place!").format(self.air.getAvatarIdFromSender()))

    def removeParticipantById(self, avId):
        try:
            self.participants.remove(avId)
            self.notify.info(('Avatar {0} left the quiz.').format(avId))
        except:
            self.notify.warning(("Avatar {0} crashed while in the Quiz, but wasn't in the Quiz in the first place!").format(self.air.getAvatarIdFromSender()))