import time
from panda3d.core import *
from direct.distributed.ClockDelta import *
from direct.fsm import FSM
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from direct.task.Task import Task
from otp.nametag.NametagConstants import *
from toontown.toonbase import TTLocalizer
from DistributedNPCToonBase import *
import NPCToons

class DistributedNPCRoaming(DistributedNPCToonBase, FSM.FSM):

    def __init__(self, cr):
        DistributedNPCToonBase.__init__(self, cr)
        self.isLocalToon = 0
        FSM.FSM.__init__(self, 'DistributedNPCRoaming')
        self.av = None
        self.nextCollision = 0
        self.moveSeq = None
        return

    def disable(self):
        self.ignoreAll()
        self.cleanMoveSeq()
        self.av = None
        if self.isLocalToon:
            base.localAvatar.posCamera(0, 0)
        DistributedNPCToonBase.disable(self)
        return

    def generate(self):
        DistributedNPCToonBase.generate(self)

    def announceGenerate(self):
        DistributedNPCToonBase.announceGenerate(self)

    def initToonState(self):
        self.setAnimState('neutral', 1, None, None)
        self.setPosHpr(266, -311, 31.387, 56, 0, 0)
        self.setShoes(1, 54, 0)
        return

    def getCollSphereRadius(self):
        return 1.0

    def setState(self, state, timestamp):
        timeStamp = ClockDelta.globalClockDelta.localElapsedTime(timestamp)
        self.request(state, [timeStamp])

    def setChatter(self, phraseId, avId, timestamp):
        self.cleanMoveSeq()
        curHpr = self.getHpr()
        if base.cr.doId2do.get(avId):
            self.headsUp(base.localAvatar)
            destHpr = self.getHpr()
            self.setHpr(curHpr)
            turnSequence = self.makeTurnToHeadingTrack(destHpr[0])
            self.moveSeq = Sequence(turnSequence, Func(self.lookAt, base.cr.doId2do.get(avId)), Func(self.setChatAbsolute, TTLocalizer.RiggyChatter[phraseId].replace('_avName_', base.cr.doId2do.get(avId).getName()), CFSpeech | CFTimeout))
        else:
            self.notify.warning(('Tried to talk to unknown avatar {0}!').format(avId))
            self.moveSeq = Sequence(Func(self.setChatAbsolute, TTLocalizer.RiggyChatter[phraseId].replace('_avName_', 'mate'), CFSpeech | CFTimeout))
        self.moveSeq.start()
        self.moveSeq.setT(globalClockDelta.localElapsedTime(timestamp))

    def makeTurnToHeadingTrack(self, heading):
        curHpr = self.getHpr()
        destHpr = self.getHpr()
        destHpr.setX(heading)
        if destHpr[0] - curHpr[0] > 180.0:
            destHpr.setX(destHpr[0] - 360)
        else:
            if destHpr[0] - curHpr[0] < -180.0:
                destHpr.setX(destHpr[0] + 360)
        turnSpeed = 180.0
        time = abs(destHpr[0] - curHpr[0]) / turnSpeed
        turnTracks = Parallel()
        if time > 0.2:
            turnTracks.append(Sequence(Func(self.loop, self.walkAnim), Wait(time), Func(self.loop, self.neutralAnim)))
        turnTracks.append(self.hprInterval(time, destHpr))
        return turnTracks

    def cleanMoveSeq(self):
        if self.moveSeq:
            self.moveSeq.finish()
            self.moveSeq = None
        return

    def enterIdle(self, timeStamp):
        self.setAnimState('neutral')
        self.startLookAround()

    def exitIdle(self):
        self.stopLookAround()

    def enterMoving(self, timeStamp):
        self.setAnimState('walk')

    def handleCollisionSphereEnter(self, collEntry):
        self.currentTime = time.time()
        if self.nextCollision > self.currentTime:
            self.nextCollision = self.currentTime + 2
        else:
            self.sendUpdate('avatarEnter', [])
            self.nextCollision = self.currentTime + 2

    def __handleUnexpectedExit(self):
        self.notify.warning('unexpected exit')
        self.av = None
        return

    def setupAvatars(self, av):
        self.ignoreAvatars()
        av.stopLookAround()
        av.lerpLookAt(Point3(-0.5, 4, 0), time=0.5)
        self.stopLookAround()
        self.lerpLookAt(Point3(av.getPos(self)), time=0.5)

    def setMovie(self, mode, npcId, avId, extraArgs, timestamp):
        pass