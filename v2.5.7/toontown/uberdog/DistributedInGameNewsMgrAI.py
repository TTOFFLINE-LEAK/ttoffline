from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectGlobalAI import DistributedObjectGlobalAI

class DistributedInGameNewsMgrAI(DistributedObjectGlobalAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedInGameNewsMgrAI')

    def __init__(self, air):
        DistributedObjectGlobalAI.__init__(self, air)
        self.latestIssueStr = ''

    def setLatestIssueStr(self, issueStr):
        self.latestIssueStr = issueStr

    def d_setLatestIssueStr(self, issueStr):
        self.sendUpdate('setLatestIssueStr', [issueStr])

    def b_setLatestIssueStr(self, issueStr):
        self.setLatestIssueStr(issueStr)
        self.d_setLatestIssueStr(issueStr)

    def getLatestIssueStr(self):
        return self.latestIssueStr

    def inGameNewsMgrAIStartingUp(self, todo0, todo1):
        pass

    def newIssueUDtoAI(self, todo0):
        pass