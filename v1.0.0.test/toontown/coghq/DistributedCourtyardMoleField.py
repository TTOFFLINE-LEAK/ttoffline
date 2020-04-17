from panda3d.core import *
from otp.level.BasicEntities import DistributedNodePathEntity
from direct.directnotify import DirectNotifyGlobal
from toontown.coghq import MoleHill
from toontown.coghq import MoleFieldBase
from direct.distributed.ClockDelta import globalClockDelta
from direct.gui.DirectGui import DGG, DirectFrame, DirectLabel
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from direct.task import Task
import random
from toontown.minigame import Trajectory
from direct.interval.IntervalGlobal import *
from direct.distributed import DistributedObject

class DistributedCourtyardMoleField(DistributedObject.DistributedObject, MoleFieldBase.MoleFieldBase):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCourtyardMoleField')
    ScheduleTaskName = 'moleFieldScheduler'

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        self.moleHills = []
        self.numMolesWhacked = 0
        self.detectCount = 0
        self.cameraHold = None
        self.activeField = 1
        self.toonHitTracks = {}
        return

    def disable(self):
        for ival in self.toonHitTracks.values():
            ival.finish()

        self.toonHitTracks = {}
        DistributedObject.DistributedObject.disable(self)
        self.ignoreAll()

    def delete(self):
        self.soundBomb = None
        self.soundBomb2 = None
        self.soundCog = None
        DistributedObject.DistributedObject.delete(self)
        self.stopScheduleTask()
        for mole in self.moleHills:
            mole.destroy()

        self.moleHills = []
        return

    def announceGenerate(self):
        DistributedObject.DistributedObject.announceGenerate(self)
        self.loadModel()

    def loadModel(self):
        moleIndex = 0
        self.moleHills = []
        for index in xrange(len(ToontownGlobals.MoleHillPositions)):
            xPos = ToontownGlobals.MoleHillPositions[index][0]
            yPos = ToontownGlobals.MoleHillPositions[index][1]
            zPos = ToontownGlobals.MoleHillPositions[index][2]
            newMoleHill = MoleHill.MoleHill(xPos, yPos, zPos, self, moleIndex)
            newMoleHill.reparentTo(render)
            self.moleHills.append(newMoleHill)
            moleIndex += 1

        self.numMoles = len(self.moleHills)
        self.centerNode = render.attachNewNode('center')
        self.soundBomb = base.loader.loadSfx('phase_12/audio/sfx/Mole_Surprise.ogg')
        self.soundBomb2 = base.loader.loadSfx('phase_3.5/audio/dial/AV_pig_howl.ogg')
        self.soundCog = base.loader.loadSfx('phase_12/audio/sfx/Mole_Stomp.ogg')
        self.soundUp = base.loader.loadSfx('phase_4/audio/sfx/MG_Tag_C.ogg')
        self.soundDown = base.loader.loadSfx('phase_4/audio/sfx/MG_cannon_whizz.ogg')
        upInterval = SoundInterval(self.soundUp, loop=0)
        downInterval = SoundInterval(self.soundDown, loop=0)
        self.soundIUpDown = Sequence(upInterval, downInterval)

    def setGameStart(self, timestamp):
        self.activeField = 1
        self.scheduleMoles()
        self.notify.debug('%d setGameStart: Starting game' % self.doId)
        self.gameStartTime = globalClockDelta.networkToLocalTime(timestamp)
        for hill in self.moleHills:
            hill.setGameStartTime(self.gameStartTime)

        self.startScheduleTask()

    def local2GameTime(self, timestamp):
        return timestamp - self.gameStartTime

    def game2LocalTime(self, timestamp):
        return timestamp + self.gameStartTime

    def getCurrentGameTime(self):
        return self.local2GameTime(globalClock.getFrameTime())

    def startScheduleTask(self):
        taskMgr.add(self.scheduleTask, self.ScheduleTaskName)

    def stopScheduleTask(self):
        taskMgr.remove(self.ScheduleTaskName)

    def scheduleTask(self, task):
        curTime = self.getCurrentGameTime()
        while self.schedule and self.schedule[0][0] <= curTime and self.activeField:
            popupInfo = self.schedule[0]
            self.schedule = self.schedule[1:]
            startTime, moleIndex, curMoveUpTime, curStayUpTime, curMoveDownTime, moleType = popupInfo
            hill = self.moleHills[moleIndex]
            hill.doMolePop(startTime, curMoveUpTime, curStayUpTime, curMoveDownTime, moleType)

        if self.schedule:
            return task.cont
        else:
            return task.done

    def handleEnterMole(self, colEntry):
        surfaceNormal = colEntry.getSurfaceNormal(render)
        self.notify.debug('surfaceNormal=%s' % surfaceNormal)
        into = colEntry.getIntoNodePath()
        moleIndex = int(into.getName().split('-')[(-1)])
        self.notify.debug('hit mole %d' % moleIndex)
        moleHill = self.moleHills[moleIndex]
        moleHill.stashMoleCollision()
        popupNum = moleHill.getPopupNum()
        if moleHill.hillType == MoleFieldBase.HILL_MOLE:
            timestamp = globalClockDelta.getFrameNetworkTime()
            moleHill.setHillType(MoleFieldBase.HILL_WHACKED)
            self.sendUpdate('whackedBomb', [moleIndex, popupNum, timestamp])
            self.__showToonHitByBomb(localAvatar.doId, moleIndex, timestamp)
        elif moleHill.hillType == MoleFieldBase.HILL_BOMB:
            moleHill.setHillType(MoleFieldBase.HILL_COGWHACKED)
            self.soundCog.play()
            self.sendUpdate('whackedMole', [moleIndex, popupNum])

    def updateMole(self, moleIndex, status):
        if status == self.WHACKED:
            moleHill = self.moleHills[moleIndex]
            if not moleHill.hillType == MoleFieldBase.HILL_COGWHACKED:
                moleHill.setHillType(MoleFieldBase.HILL_COGWHACKED)
                self.soundCog.play()
            moleHill.doMoleDown()

    def reportToonHitByBomb(self, avId, moleIndex, timestamp):
        if avId != localAvatar.doId:
            self.__showToonHitByBomb(avId, moleIndex, timestamp)
            moleHill = self.moleHills[moleIndex]
            if not moleHill.hillType == MoleFieldBase.HILL_WHACKED:
                moleHill.setHillType(MoleFieldBase.HILL_WHACKED)
                self.soundCog.play()
            moleHill.doMoleDown()

    def __showToonHitByBomb(self, avId, moleIndex, timestamp=0):
        toon = base.cr.doId2do.get(avId)
        moleHill = self.moleHills[moleIndex]
        if toon == None:
            return
        else:
            rng = random.Random(timestamp)
            curPos = toon.getPos(render)
            oldTrack = self.toonHitTracks.get(avId)
            if oldTrack:
                if oldTrack.isPlaying():
                    oldTrack.finish()
            toon.setPos(curPos)
            toon.setZ(render.getZ())
            parentNode = render.attachNewNode('mazeFlyToonParent-' + `avId`)
            parentNode.setPos(toon.getPos(render))
            toon.reparentTo(parentNode)
            toon.setPos(0, 0, 0)
            startPos = parentNode.getPos()
            dropShadow = toon.dropShadow.copyTo(parentNode)
            dropShadow.setScale(toon.dropShadow.getScale(render))
            trajectory = Trajectory.Trajectory(0, Point3(0, 0, 0), Point3(0, 0, 50), gravMult=1.0)
            flyDur = trajectory.calcTimeOfImpactOnPlane(0.0)
            xPos = random.randint(-25, 25) + moleHill.getX()
            yPos = random.randint(-25, 25) + moleHill.getY()
            endPos = Point3(xPos, yPos, startPos[2])

            def flyFunc(t, trajectory, startPos=startPos, endPos=endPos, dur=flyDur, moveNode=parentNode, flyNode=toon):
                u = t / dur
                moveNode.setX(startPos[0] + u * (endPos[0] - startPos[0]))
                moveNode.setY(startPos[1] + u * (endPos[1] - startPos[1]))
                if flyNode and not flyNode.isEmpty():
                    flyNode.setPos(trajectory.getPos(t))

            def safeSetHpr(node, hpr):
                if node and not node.isEmpty():
                    node.setHpr(hpr)

            flyTrack = Sequence(LerpFunctionInterval(flyFunc, fromData=0.0, toData=flyDur, duration=flyDur, extraArgs=[trajectory]), name=toon.uniqueName('hitBySuit-fly'))
            if avId != localAvatar.doId:
                cameraTrack = Sequence()
            else:
                base.localAvatar.stopUpdateSmartCamera()
                self.camParentHold = camera.getParent()
                self.camParent = base.localAvatar.attachNewNode('iCamParent')
                self.camParent.setPos(self.camParentHold.getPos())
                self.camParent.setHpr(self.camParentHold.getHpr())
                camera.reparentTo(self.camParent)
                self.camParent.reparentTo(parentNode)
                startCamPos = camera.getPos()
                destCamPos = camera.getPos()
                zenith = trajectory.getPos(flyDur / 2.0)[2]
                destCamPos.setZ(zenith * 1.3)
                destCamPos.setY(destCamPos[1] * 0.3)

                def camTask(task, zenith=zenith, flyNode=toon, startCamPos=startCamPos, camOffset=destCamPos - startCamPos):
                    u = flyNode.getZ() / zenith
                    camera.lookAt(toon)
                    return Task.cont

                camTaskName = 'mazeToonFlyCam-' + `avId`
                taskMgr.add(camTask, camTaskName, priority=20)

                def cleanupCamTask(self=self, toon=toon, camTaskName=camTaskName, startCamPos=startCamPos):
                    taskMgr.remove(camTaskName)
                    self.camParent.reparentTo(toon)
                    camera.setPos(startCamPos)
                    camera.lookAt(toon)
                    camera.reparentTo(self.camParentHold)
                    base.localAvatar.startUpdateSmartCamera()

                cameraTrack = Sequence(Wait(flyDur), Func(cleanupCamTask), name='hitBySuit-cameraLerp')
            geomNode = toon.getGeomNode()
            startHpr = geomNode.getHpr()
            destHpr = Point3(startHpr)
            hRot = rng.randrange(1, 8)
            if rng.choice([0, 1]):
                hRot = -hRot
            destHpr.setX(destHpr[0] + hRot * 360)
            spinHTrack = Sequence(LerpHprInterval(geomNode, flyDur, destHpr, startHpr=startHpr), Func(safeSetHpr, geomNode, startHpr), name=toon.uniqueName('hitBySuit-spinH'))
            parent = geomNode.getParent()
            rotNode = parent.attachNewNode('rotNode')
            geomNode.reparentTo(rotNode)
            rotNode.setZ(toon.getHeight() / 2.0)
            oldGeomNodeZ = geomNode.getZ()
            geomNode.setZ(-toon.getHeight() / 2.0)
            startHpr = rotNode.getHpr()
            destHpr = Point3(startHpr)
            pRot = rng.randrange(1, 3)
            if rng.choice([0, 1]):
                pRot = -pRot
            destHpr.setY(destHpr[1] + pRot * 360)
            spinPTrack = Sequence(LerpHprInterval(rotNode, flyDur, destHpr, startHpr=startHpr), Func(safeSetHpr, rotNode, startHpr), name=toon.uniqueName('hitBySuit-spinP'))
            soundTrack = Sequence()

            def preFunc(self=self, avId=avId, toon=toon, dropShadow=dropShadow):
                forwardSpeed = toon.forwardSpeed
                rotateSpeed = toon.rotateSpeed
                if avId == localAvatar.doId:
                    toon.stopSmooth()
                    base.cr.playGame.getPlace().fsm.request('stopped')
                else:
                    toon.stopSmooth()
                if forwardSpeed or rotateSpeed:
                    toon.setSpeed(forwardSpeed, rotateSpeed)
                toon.dropShadow.hide()

            def postFunc(self=self, avId=avId, oldGeomNodeZ=oldGeomNodeZ, dropShadow=dropShadow, parentNode=parentNode):
                if avId == localAvatar.doId:
                    base.localAvatar.setPos(endPos)
                    if hasattr(self, 'orthoWalk'):
                        self.orthoWalk.start()
                dropShadow.removeNode()
                del dropShadow
                if toon and toon.dropShadow:
                    toon.dropShadow.show()
                geomNode = toon.getGeomNode()
                rotNode = geomNode.getParent()
                baseNode = rotNode.getParent()
                geomNode.reparentTo(baseNode)
                rotNode.removeNode()
                del rotNode
                geomNode.setZ(oldGeomNodeZ)
                toon.reparentTo(render)
                toon.setPos(endPos)
                parentNode.removeNode()
                del parentNode
                if avId == localAvatar.doId:
                    toon.startSmooth()
                    place = base.cr.playGame.getPlace()
                    if place and hasattr(place, 'fsm'):
                        place.fsm.request('walk')
                else:
                    toon.startSmooth()

            preFunc()
            hitTrack = Sequence(Func(toon.setPos, Point3(0.0, 0.0, 0.0)), Wait(0.25), Parallel(flyTrack, cameraTrack, self.soundIUpDown, spinHTrack, spinPTrack, soundTrack), Func(postFunc), name=toon.uniqueName('hitBySuit'))
            self.toonHitTracks[avId] = hitTrack
            hitTrack.start()
            posM = moleHill.getPos(render)
            posN = Point3(posM[0], posM[1], posM[2] + 4.0)
            self.soundBomb.play()
            self.soundBomb2.play()
            return

    def handleEnterHill(self):
        pass