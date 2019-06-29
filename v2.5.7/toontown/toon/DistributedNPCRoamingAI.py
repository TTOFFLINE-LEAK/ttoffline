import random
from panda3d.core import *
from direct.fsm import FSM
from direct.task import Task
from toontown.toonbase import TTLocalizer, ToontownGlobals
from DistributedNPCToonBaseAI import *
TALK_TIME_MIN = 7.0
TALK_TIME_MAX = 15.0

class DistributedNPCRoamingAI(DistributedNPCToonBaseAI, FSM.FSM):

    def __init__(self, air, npcId):
        FSM.FSM.__init__(self, 'DistributedNPCRoamingAI')
        DistributedNPCToonBaseAI.__init__(self, air, npcId)
        self.givesQuests = 0
        self.interestedIn = []
        self.accept(('toon-entered-{0}').format(ToontownGlobals.ToonFest), self.__handleToonEntered)
        self.accept(('toon-left-{0}').format(ToontownGlobals.ToonFest), self.__handleToonLeft)

    def delete(self):
        taskMgr.remove(self.uniqueName('saySomething'))
        self.ignoreAll()
        DistributedNPCToonBaseAI.delete(self)

    def announceGenerate(self):
        self.b_setState('Idle')

    def enterOff(self, timestamp):
        pass

    def enterMoving(self, timestamp):
        pass

    def enterIdle(self, timestamp):
        taskMgr.doMethodLater(random.randrange(TALK_TIME_MIN, TALK_TIME_MAX), self.saySomething, self.uniqueName('saySomething'))

    def saySomething(self, task):
        if len(self.interestedIn) != 0:
            phrase = random.randrange(len(TTLocalizer.RiggyChatter))
            avId = random.choice(self.interestedIn)
            self.d_setChatter(phrase, avId)
        task.delayTime = random.randrange(TALK_TIME_MIN, TALK_TIME_MAX)
        return Task.again

    def d_setChatter(self, phraseId, avId):
        timestamp = ClockDelta.globalClockDelta.getRealNetworkTime()
        self.sendUpdate('setChatter', [phraseId, avId, timestamp])

    def b_setState(self, state):
        self.d_setState(state)
        self.setState(state)

    def d_setState(self, state):
        timestamp = ClockDelta.globalClockDelta.getRealNetworkTime()
        self.sendUpdate('setState', [state, timestamp])

    def setState(self, state):
        timestamp = ClockDelta.globalClockDelta.getRealNetworkTime()
        self.request(state, [timestamp])

    def rejectAvatar(self, avId):
        self.notify.warning('rejectAvatar: should not be called by a roamer!')

    def d_setMovie(self, avId, flag, extraArgs=[]):
        self.notify.warning('setMovie: should not be called by a roamer!')

    def __handleToonEntered(self, av):
        avId = av.doId
        if not self.air.doId2do.has_key(avId):
            self.notify.warning('Avatar %s entered ToonFest but does not exist!' % avId)
            return
        if avId not in self.interestedIn:
            self.acceptOnce(self.air.getAvatarExitEvent(avId), self.__handleToonLeft, extraArgs=[av])
            self.interestedIn.append(avId)
            self.notify.warning(('Interested in {0}').format(avId))

    def __handleToonLeft(self, av):
        avId = av.doId
        self.ignore(self.air.getAvatarExitEvent(avId))
        if avId in self.interestedIn:
            self.interestedIn.remove(avId)
            self.notify.warning(('Not interested in {0}').format(avId))