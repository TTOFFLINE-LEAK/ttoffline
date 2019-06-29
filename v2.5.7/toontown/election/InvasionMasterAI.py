import random

class InvasionMasterAI:
    UNREACHABLE_TIMEOUT = 5.0

    def __init__(self, invasion):
        self.invasion = invasion
        self._unreachables = {}

    def getAttackableToons(self):
        result = []
        for toon in self.invasion.toons:
            if toon.ghostMode:
                continue
            unreachableTimestamp = self._unreachables.get(toon.doId)
            if unreachableTimestamp and unreachableTimestamp > globalClock.getFrameTime():
                continue
            result.append(toon)

        return result

    def requestOrders(self, brain):
        attackables = self.getAttackableToons()
        if attackables:
            toonId = random.choice(attackables).doId
            brain.demand('Attack', toonId)
        else:
            if self.invasion.sadToons:
                brain.demand('Attack', random.choice(self.invasion.sadToons).doId)
            else:
                brain.demand('AskAgain')

    def toonUnreachable(self, toonId):
        self._unreachables[toonId] = globalClock.getFrameTime() + self.UNREACHABLE_TIMEOUT