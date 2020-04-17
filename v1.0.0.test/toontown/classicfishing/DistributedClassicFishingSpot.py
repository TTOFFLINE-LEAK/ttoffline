from panda3d.core import *
import math
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *
from direct.distributed import DistributedObject
from direct.directnotify import DirectNotifyGlobal
from direct.actor import Actor
from direct.showutil import Rope
from direct.task.Task import Task
from toontown.effects import Ripples
from toontown.quest import Quests
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from toontown.toontowngui import TTDialog
import FishingCodes

class DistributedClassicFishingSpot(DistributedObject.DistributedObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedClassicFishingSpot')

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        self.lastAvId = 0
        self.lastFrame = 0
        self.avId = 0
        self.av = None
        self.placedAvatar = 0
        self.localToonFishing = 0
        self.nodePath = None
        self.collSphere = None
        self.collNode = None
        self.collNodePath = None
        self.protSphere = None
        self.protNode = None
        self.protNodePath = None
        self.track = None
        self.madeGui = 0
        self.castGui = None
        self.reelGui = None
        self.crankGui = None
        self.crankHeld = 0
        self.turnCrankTask = None
        self.itemGui = None
        self.failureGui = None
        self.brokeGui = None
        self.pole = None
        self.poleNode = []
        self.ptop = None
        self.bob = None
        self.bobBobTask = None
        self.splashSound = None
        self.ripples = None
        self.gotBobSpot = 0
        self.bobSpot = None
        self.nibbleStart = 0
        self.targetSpeed = None
        self.netTime = 0.0
        self.netDistance = 0.0
        self.line = None
        self.lineSphere = None
        self.pendingFish = 0
        self.crankTime = None
        return

    def disable(self):
        self.ignore(self.uniqueName('enterFishingSpotSphere'))
        self.setOccupied(0)
        self.avId = 0
        self.__hideBob()
        self.nodePath.detachNode()
        self.__unmakeGui()
        DistributedObject.DistributedObject.disable(self)

    def delete(self):
        DistributedObject.DistributedObject.delete(self)

    def generateInit(self):
        self.nodePath = NodePath(self.uniqueName('FishingSpot'))
        self.line = Rope.Rope(self.uniqueName('Line'))
        self.line.setColor(1, 1, 1, 0.4)
        self.line.setTransparency(1)
        self.lineSphere = BoundingSphere(Point3(-0.6, -2, -5), 5.5)
        self.collSphere = CollisionSphere(0, 0, 0, self.getSphereRadius())
        self.collSphere.setTangible(0)
        self.collNode = CollisionNode(self.uniqueName('FishingSpotSphere'))
        self.collNode.setCollideMask(ToontownGlobals.WallBitmask)
        self.collNode.addSolid(self.collSphere)
        self.collNodePath = self.nodePath.attachNewNode(self.collNode)
        self.protSphere = CollisionSphere(0, 0, 0, 1.5)
        self.protNode = CollisionNode(self.uniqueName('ProtectionSphere'))
        self.protNode.setCollideMask(ToontownGlobals.WallBitmask)
        self.protNode.addSolid(self.protSphere)
        self.protNodePath = NodePath(self.protNode)
        self.protNodePath.setScale(1, 1.5, 1.5)
        self.protNodePath.setPos(0, 7, 0)

    def generate(self):
        self.nodePath.reparentTo(self.getParentNodePath())
        self.accept(self.uniqueName('enterFishingSpotSphere'), self.__handleEnterSphere)

    def __handleEnterSphere(self, collEntry):
        if base.localAvatar.doId == self.lastAvId and globalClock.getFrameCount() <= self.lastFrame + 1:
            self.notify.info('Ignoring duplicate entry for avatar.')
            return
        else:
            if base.localAvatar.hp > 0 and base.cr.playGame.getPlace().fsm.getCurrentState().getName() != 'fishing':
                self.cr.playGame.getPlace().detectedFishingCollision()
                self.d_requestEnter()
            return

    def handleConfirm(self):
        status = self.confirm.doneStatus
        self.ignore('confirmDone')
        self.confirm.cleanup()
        del self.confirm
        if status == 'ok':
            base.localAvatar.enableAvatarControls()

    def d_requestEnter(self):
        self.sendUpdate('requestEnter', [])

    def rejectEnter(self):
        self.cr.playGame.getPlace().setState('walk')

    def d_requestExit(self):
        self.sendUpdate('requestExit', [])

    def d_doCast(self):
        self.sendUpdate('doCast', [])

    def d_doAutoReel(self):
        self.sendUpdate('doAutoReel', [])

    def d_doReel(self, speed, netTime, netDistance):
        self.sendUpdate('doReel', [speed, netTime, netDistance])

    def getSphereRadius(self):
        return 1.5

    def getParentNodePath(self):
        return render

    def setPosHpr(self, x, y, z, h, p, r):
        self.nodePath.setPosHpr(x, y, z, h, p, r)

    def setOccupied(self, avId):
        if self.track != None:
            if self.track.isPlaying():
                self.track.finish()
            self.track = None
        if self.av != None:
            if not self.av.isEmpty():
                self.av.setBlend(animBlend=False)
                self.av.setPlayRate(1.0, 'cast')
                self.__dropPole()
                self.av.loop('neutral')
                self.av.setParent(ToontownGlobals.SPRender)
                self.av.startSmooth()
            self.ignore(self.av.uniqueName('disable'))
            self.__hideBob()
            self.av.fishingSpot = None
            self.av = None
            self.placedAvatar = 0
        self.__hideLine()
        wasLocalToon = self.localToonFishing
        self.lastAvId = self.avId
        self.lastFrame = globalClock.getFrameCount()
        self.avId = avId
        self.localToonFishing = 0
        if self.avId == 0:
            self.collSphere.setTangible(0)
            self.protNodePath.detachNode()
        else:
            self.collSphere.setTangible(1)
            self.protNodePath.reparentTo(self.nodePath)
            self.__loadStuff()
            if self.avId == base.localAvatar.doId:
                base.cr.playGame.getPlace().setState('fishing')
                base.setCellsAvailable([
                 base.bottomCells[1],
                 base.bottomCells[2]], 0)
                self.localToonFishing = 1
            if self.cr.doId2do.has_key(self.avId):
                self.av = self.cr.doId2do[self.avId]
                self.placedAvatar = 0
                self.acceptOnce(self.av.uniqueName('disable'), self.__avatarGone)
                self.av.stopSmooth()
                self.av.wrtReparentTo(self.nodePath)
                self.av.fishingSpot = self
                self.av.setAnimState('neutral', 1.0)
                self.__setupNeutralBlend()
            else:
                self.notify.warning('Unknown avatar %d in fishing spot %d' % (self.avId, self.doId))
        if wasLocalToon and not self.localToonFishing:
            self.__hideGui()
            base.setCellsAvailable([
             base.bottomCells[1],
             base.bottomCells[2]], 1)
            place = base.cr.playGame.getPlace()
            if place:
                place.setState('walk')
        return

    def __avatarGone(self):
        self.setOccupied(0)

    def __setupNeutralBlend(self):
        self.av.stop()
        self.av.loop('neutral')
        self.av.setBlend(animBlend=True)
        self.av.pose('cast', 0)
        self.av.setControlEffect('neutral', 0.2)
        self.av.setControlEffect('cast', 0.8)

    def setTargetSpeed(self, speed):
        self.targetSpeed = speed
        if self.avId == base.localAvatar.doId:
            self.speedGauge.show()
            self.__updateSpeedGauge()

    def setMovie(self, mode, code, item, speed):
        if self.track != None:
            if self.track.isPlaying():
                self.track.finish()
            self.track = None
        if self.av == None:
            return
        else:
            self.__hideLine()
            if mode == FishingCodes.NoMovie:
                pass
            if mode == FishingCodes.EnterMovie:
                self.track = Parallel()
                self.av.stopLookAround()
                if self.localToonFishing:
                    self.track.append(LerpPosHprInterval(nodePath=camera, other=self.av, duration=1.5, pos=Point3(14, -7.4, 7.3), hpr=VBase3(45, -12, 0), blendType='easeInOut'))
                self.av.setBlend(animBlend=False)
                self.av.setPlayRate(1.0, 'walk')
                self.av.loop('walk')
                toonTrack = Sequence(LerpPosHprInterval(self.av, 1.5, Point3(0, 0, 0), Point3(0, 0, 0)), Func(self.__setupNeutralBlend), Func(self.__holdPole), Parallel(ActorInterval(self.av, 'cast', playRate=0.5, duration=27.0 / 12.0), ActorInterval(self.pole, 'cast', playRate=0.5, duration=27.0 / 12.0), LerpScaleInterval(self.pole, duration=2.0, scale=1.0, startScale=0.01)), Func(self.av.pose, 'cast', 88), Func(self.pole.pose, 'cast', 88))
                if self.localToonFishing:
                    toonTrack.append(Func(self.__showCastGui))
                self.track.append(toonTrack)
                self.track.start()
            elif mode == FishingCodes.ExitMovie:
                if self.localToonFishing:
                    self.__hideGui()
                self.av.stopLookAround()
                self.av.startLookAround()
                self.__placeAvatar()
                self.__hideLine()
                self.__hideBob()
                self.track = Sequence(Parallel(ActorInterval(self.av, 'cast', duration=1.0, startTime=1.0, endTime=0.0), ActorInterval(self.pole, 'cast', duration=1.0, startTime=1.0, endTime=0.0), LerpScaleInterval(self.pole, duration=0.5, scale=0.01, startScale=1.0)), Func(self.__dropPole))
                self.track.start()
            elif mode == FishingCodes.CastMovie:
                self.av.stopLookAround()
                self.av.startLookAround()
                self.__placeAvatar()
                self.__getBobSpot()
                self.track = Sequence(Parallel(ActorInterval(self.av, 'cast', duration=2.0, startTime=1.0), ActorInterval(self.pole, 'cast', duration=2.0, startTime=1.0), Sequence(Wait(1.3), Func(self.__showBobCast), Func(self.__showLineWaiting), LerpPosInterval(self.bob, 0.2, self.bobSpot), Func(self.__showBob), SoundInterval(self.splashSound))))
                if self.localToonFishing:
                    self.track.append(Func(self.__showReelGui))
                self.track.start()
            elif mode == FishingCodes.NibbleMovie:
                self.__placeAvatar()
                self.av.pose('cast', 71)
                self.pole.pose('cast', 71)
                self.__showLineWaiting()
                self.__nibbleBob()
            elif mode == FishingCodes.BeginReelMovie:
                self.av.stopLookAround()
                self.__placeAvatar()
                self.__hideBob()
                self.__showLineReelTaught()
                self.av.setPlayRate(speed, 'cast')
                self.pole.setPlayRate(speed, 'cast')
                self.track = Sequence(Parallel(ActorInterval(self.av, 'cast', duration=1.0 / speed, startTime=3.0 / speed, playRate=speed), ActorInterval(self.pole, 'cast', duration=1.0 / speed, startTime=3.0 / speed, playRate=speed)), Func(self.av.loop, 'cast', 1, None, 57, 65), Func(self.pole.loop, 'cast', 1, None, 96, 126))
                self.track.start()
            elif mode == FishingCodes.ContinueReelMovie:
                self.av.stopLookAround()
                self.__showLineReelTaught()
                if not self.placedAvatar:
                    self.__placeAvatar()
                    self.av.pose('cast', 88)
                    self.pole.pose('cast', 88)
                if speed < 0:
                    self.av.loop('cast', restart=0, fromFrame=65, toFrame=57)
                    self.pole.loop('cast', restart=0, fromFrame=126, toFrame=88)
                else:
                    self.av.loop('cast', restart=0, fromFrame=57, toFrame=65)
                    self.pole.loop('cast', restart=0, fromFrame=88, toFrame=126)
                self.av.setPlayRate(speed, 'cast')
                self.pole.setPlayRate(speed, 'cast')
            elif mode == FishingCodes.PullInMovie:
                self.av.startLookAround()
                self.__placeAvatar()
                self.__hideBob()
                self.av.setPlayRate(1, 'cast')
                self.pole.setPlayRate(1, 'cast')
                self.av.pose('cast', 94)
                self.pole.pose('cast', 94)
                if self.localToonFishing:
                    self.__showCastGui()
                    if code == FishingCodes.QuestItem:
                        self.__showQuestItem(item)
                    elif code == FishingCodes.FishItem:
                        self.__showFishItem(item)
                    elif code == FishingCodes.OverLimitFishItem:
                        self.__hideGui()
                        self.b_fishReleaseQuery(item)
                    else:
                        self.__showFailureReason(code)
            return

    def getStareAtNodeAndOffset(self):
        return (self.nodePath, Point3())

    def __loadStuff(self):
        if self.pole == None:
            self.pole = Actor.Actor()
            self.pole.loadModel('phase_4/models/props/fishing-pole-mod')
            self.pole.setBlend(frameBlend=config.GetBool('interpolate-animations', True))
            self.pole.loadAnims({'cast': 'phase_4/models/props/fishing-pole-chan'})
            self.pole.pose('cast', 0)
            self.ptop = self.pole.find('**/joint_attachBill')
        if self.bob == None:
            self.bob = loader.loadModel('phase_4/models/props/fishing_bob')
            self.ripples = Ripples.Ripples(self.nodePath)
            self.ripples.hide()
        if self.splashSound == None:
            self.splashSound = base.loader.loadSfx('phase_4/audio/sfx/TT_splash1.ogg')
        return

    def __placeAvatar(self):
        if not self.placedAvatar:
            self.placedAvatar = 1
            self.__holdPole()
            self.__setupNeutralBlend()
            self.av.setPosHpr(0, 0, 0, 0, 0, 0)

    def __holdPole(self):
        if self.poleNode != []:
            self.__dropPole()
        np = NodePath('pole-holder')
        hands = self.av.getRightHands()
        for h in hands:
            self.poleNode.append(np.instanceTo(h))

        self.pole.reparentTo(self.poleNode[0])

    def __dropPole(self):
        self.__hideBob()
        self.__hideLine()
        if self.pole != None:
            self.pole.clearMat()
            self.pole.detachNode()
        for pn in self.poleNode:
            pn.removeNode()

        self.poleNode = []
        return

    def __showLineWaiting(self):
        self.line.setup(4, ((None, (0, 0, 0)), (None, (0, -2, -4)), (self.bob, (0, -1, 0)), (self.bob, (0, 0, 0))))
        self.line.ropeNode.setBounds(self.lineSphere)
        self.line.reparentTo(self.ptop)
        return

    def __showLineReelTaught(self):
        self.__getBobSpot()
        self.line.setup(2, ((None, (0, 0, 0)), (self.nodePath, self.bobSpot)))
        self.line.ropeNode.setBounds(self.lineSphere)
        self.line.reparentTo(self.ptop)
        return

    def __showLineReelSlack(self):
        self.__getBobSpot()
        self.line.setup(3, ((None, (0, 0, 0)), (None, (0, -2, -4)), (self.nodePath, self.bobSpot)))
        self.line.ropeNode.setBounds(self.lineSphere)
        self.line.reparentTo(self.ptop)
        return

    def __hideLine(self):
        self.line.detachNode()

    def __showBobCast(self):
        self.__hideBob()
        self.bob.reparentTo(self.nodePath)
        self.av.update(0)
        self.bob.setPos(self.ptop, 0, 0, 0)

    def __showBob(self):
        self.__hideBob()
        self.__getBobSpot()
        self.bob.reparentTo(self.nodePath)
        self.bob.setPos(self.bobSpot)
        self.ripples.reparentTo(self.nodePath)
        self.ripples.setPos(self.bobSpot)
        self.ripples.play(0.75)
        self.bobBobTask = taskMgr.add(self.__doBobBob, self.taskName('bob'))

    def __nibbleBob(self):
        self.__hideBob()
        self.__getBobSpot()
        self.bob.reparentTo(self.nodePath)
        self.bob.setPos(self.bobSpot)
        self.ripples.reparentTo(self.nodePath)
        self.ripples.setPos(self.bobSpot)
        self.ripples.play()
        self.nibbleStart = globalClock.getFrameTime()
        self.bobBobTask = taskMgr.add(self.__doNibbleBob, self.taskName('bob'))

    def __hideBob(self):
        if self.bob != None:
            self.bob.detachNode()
        if self.bobBobTask != None:
            taskMgr.remove(self.bobBobTask)
            self.bobBobTask = None
        if self.ripples != None:
            self.ripples.stop()
            self.ripples.detachNode()
        return

    def __doBobBob(self, task):
        now = globalClock.getFrameTime()
        z = math.sin(now) * 0.5
        self.bob.setZ(self.bobSpot[2] + z)
        return Task.cont

    def __doNibbleBob(self, task):
        now = globalClock.getFrameTime()
        elapsed = now - self.nibbleStart
        if elapsed > FishingCodes.NibbleTime:
            self.__showBob()
            return Task.done
        x = (elapsed / FishingCodes.NibbleTime + 1.0) * 0.5
        y = math.sin(x * math.pi)
        amplitude = y * y * y * 0.2
        nibbleEffect = math.sin(now * 12) * amplitude
        z = math.sin(now) * 0.5 + nibbleEffect
        self.bob.setZ(self.bobSpot[2] + z)
        return Task.cont

    def __userExit(self):
        self.__hideGui()
        self.d_requestExit()

    def __userReel(self):
        self.__hideGui()
        self.d_doAutoReel()

    def __userCast(self):
        self.itemGui.detachNode()
        self.failureGui.detachNode()
        if self.av.getMoney() > 0:
            self.__hideCastButtons()
            self.jar['text'] = str(max(self.av.getMoney() - 1, 0))
            self.d_doCast()
        else:
            self.__showBroke()

    def __showCastGui(self):
        self.__hideGui()
        self.__makeGui()
        self.castButton.show()
        self.exitButton.show()
        self.castGui.reparentTo(aspect2d)
        self.castButton['state'] = DGG.NORMAL
        self.jar['text'] = str(self.av.getMoney())

    def __hideCastButtons(self):
        self.castButton.hide()
        self.exitButton.hide()

    def __showReelGui(self):
        self.__hideGui()
        self.__makeGui()
        self.reelGui.reparentTo(aspect2d)
        self.crankGui.show()
        self.speedGauge.hide()
        self.crankHandle.bind(DGG.B1PRESS, self.__clickCrank)
        self.crankHandle.bind(DGG.B1RELEASE, self.__releaseCrank)
        self.reelButton.hide()
        self.netTime = 0.0
        self.netDistance = 0.0
        self.targetSpeed = None
        return

    def __clickCrank(self, param):
        if self.crankHeld:
            self.__releaseCrank(param)
        self.reelButton.hide()
        self.crankHeld = 1
        self.d_doReel(1.0, self.netTime, self.netDistance)
        mpos = param.getMouse()
        angle = self.__getMouseAngleToCrank(mpos[0], mpos[1])
        self.crankR = self.crankHandle.getR() - angle
        self.crankAngle = angle
        self.crankDelta = 0
        self.crankTime = globalClock.getFrameTime()
        if self.turnCrankTask == None:
            self.turnCrankTask = taskMgr.add(self.__turnCrank, self.taskName('turnCrank'))
        return

    def __releaseCrank(self, unused):
        if not self.crankHeld:
            return
        else:
            self.crankHeld = 0
            self.__updateCrankSpeed(1)
            return

    def __turnCrank(self, task):
        if self.crankHeld and base.mouseWatcherNode.hasMouse():
            mx = base.mouseWatcherNode.getMouseX()
            my = base.mouseWatcherNode.getMouseY()
            angle = self.__getMouseAngleToCrank(mx, my)
            self.crankHandle.setR(self.crankR - angle)
            delta = angle - self.crankAngle
            if delta > 180:
                delta = delta - 360
            elif delta < -180:
                delta = delta + 360
            self.crankDelta += delta
            self.crankAngle = angle
        self.__updateCrankSpeed(0)
        if self.targetSpeed != None:
            self.__updateSpeedGauge()
        return Task.cont

    def __updateCrankSpeed(self, forceUpdate):
        now = globalClock.getFrameTime()
        elapsed = now - self.crankTime
        if elapsed != 0 and forceUpdate or elapsed >= FishingCodes.CalcCrankSpeed:
            degreesPerSecond = -(self.crankDelta / elapsed)
            speed = degreesPerSecond / FishingCodes.StandardCrankSpeed
            self.netTime += elapsed
            self.netDistance += speed * elapsed
            self.d_doReel(speed, self.netTime, self.netDistance)
            self.crankTime = now
            self.crankDelta = 0

    def __updateSpeedGauge(self):
        now = globalClock.getFrameTime()
        if self.crankTime == None:
            self.crankTime = now
        elapsed = now - self.crankTime
        if elapsed > 0:
            degreesPerSecond = -(self.crankDelta / elapsed)
            speed = degreesPerSecond / FishingCodes.StandardCrankSpeed
            totalTime = self.netTime + elapsed
            totalDistance = self.netDistance + speed * elapsed
        else:
            totalTime = self.netTime
            totalDistance = self.netDistance
        self.tooSlow.hide()
        self.tooFast.hide()
        if totalTime > 0:
            avgSpeed = totalDistance / totalTime
            pctDiff = 100.0 * (avgSpeed - self.targetSpeed) / self.targetSpeed
            self.speedGauge['value'] = pctDiff + 50.0
            if pctDiff >= FishingCodes.ManualReelMatch:
                self.tooFast.show()
            elif pctDiff <= -FishingCodes.ManualReelMatch:
                self.tooSlow.show()
        return

    def __getMouseAngleToCrank(self, x, y):
        p = self.crankGui.getRelativePoint(NodePath(), Point3(x, 0, y))
        angle = math.atan2(p[2], p[0]) * 180.0 / math.pi
        return angle

    def __showQuestItem(self, itemId):
        self.__makeGui()
        itemName = Quests.getItemName(itemId)
        self.itemLabel['text'] = itemName
        self.itemGui.reparentTo(aspect2d)

    def __showFishItem(self, itemId):
        self.__makeGui()
        itemName = FishingCodes.getFishName(itemId)
        itemValue = int(FishingCodes.FishValues[itemId] * self.targetSpeed)
        self.itemLabel['text'] = ('{0}\nValue: {1} jellybean{2}').format(itemName, itemValue, '' if itemValue == 1 else 's')
        self.jar['text'] = str(min(self.av.getMoney() + itemValue, self.av.getMaxMoney()))
        self.itemGui.reparentTo(aspect2d)

    def __showFailureReason(self, code):
        self.__makeGui()
        reason = ''
        if code == FishingCodes.TooSoon:
            reason = TTLocalizer.FishingFailureTooSoon
        elif code == FishingCodes.TooLate:
            reason = TTLocalizer.FishingFailureTooLate
        elif code == FishingCodes.AutoReel:
            reason = TTLocalizer.FishingFailureAutoReel
        elif code == FishingCodes.TooSlow:
            reason = TTLocalizer.FishingFailureTooSlow
        elif code == FishingCodes.TooFast:
            reason = TTLocalizer.FishingFailureTooFast
        self.failureLabel['text'] = reason
        self.failureGui.reparentTo(aspect2d)

    def __showBroke(self):
        self.__makeGui()
        self.brokeGui.reparentTo(aspect2d)
        self.castButton['state'] = DGG.DISABLED

    def __hideGui(self):
        if self.madeGui:
            if self.crankHeld:
                self.__releaseCrank(None)
            if self.turnCrankTask != None:
                taskMgr.remove(self.turnCrankTask)
                self.turnCrankTask = None
            self.castGui.detachNode()
            self.reelGui.detachNode()
            self.crankHandle.unbind(DGG.B1PRESS)
            self.crankHandle.unbind(DGG.B1RELEASE)
            self.itemGui.detachNode()
            self.failureGui.detachNode()
            self.brokeGui.detachNode()
        return

    def __makeGui(self):
        if self.madeGui:
            return
        else:
            buttonModels = loader.loadModel('phase_3.5/models/gui/inventory_gui')
            upButton = buttonModels.find('**/InventoryButtonUp')
            downButton = buttonModels.find('**/InventoryButtonDown')
            rolloverButton = buttonModels.find('**/InventoryButtonRollover')
            buttonModels.removeNode()
            crankModels = loader.loadModel('phase_4/models/gui/fishing_crank')
            crank = crankModels.find('**/fishing_crank')
            crankArrow = crankModels.find('**/fishing_crank_arrow')
            crankModels.removeNode()
            jarGui = loader.loadModel('phase_3.5/models/gui/jar_gui')
            jarImage = jarGui.find('**/Jar')
            jarGui.removeNode()
            self.castGui = NodePath('castGui')
            self.exitButton = DirectButton(parent=self.castGui, relief=None, text=TTLocalizer.FishingExit, text_fg=(1,
                                                                                                                    1,
                                                                                                                    0.6,
                                                                                                                    1), text_pos=(0,
                                                                                                                                  -0.23), text_scale=0.8, image=(upButton, downButton, rolloverButton), image_color=(1,
                                                                                                                                                                                                                     0,
                                                                                                                                                                                                                     0,
                                                                                                                                                                                                                     1), image_scale=(15,
                                                                                                                                                                                                                                      1,
                                                                                                                                                                                                                                      11), pos=(-0.2,
                                                                                                                                                                                                                                                0,
                                                                                                                                                                                                                                                -0.8), scale=0.12, command=self.__userExit)
            self.castButton = DirectButton(parent=self.castGui, relief=None, text=TTLocalizer.FishingCast, text_fg=(1,
                                                                                                                    1,
                                                                                                                    0.6,
                                                                                                                    1), text3_fg=(0.8,
                                                                                                                                  0.8,
                                                                                                                                  0.8,
                                                                                                                                  1), text_pos=(0,
                                                                                                                                                -0.23), text_scale=0.8, image=(upButton, downButton, rolloverButton), image_color=(1,
                                                                                                                                                                                                                                   0,
                                                                                                                                                                                                                                   0,
                                                                                                                                                                                                                                   1), image3_color=(0.8,
                                                                                                                                                                                                                                                     0.5,
                                                                                                                                                                                                                                                     0.5,
                                                                                                                                                                                                                                                     1), image_scale=(15,
                                                                                                                                                                                                                                                                      1,
                                                                                                                                                                                                                                                                      11), pos=(-0.2,
                                                                                                                                                                                                                                                                                0,
                                                                                                                                                                                                                                                                                -0.62), scale=0.12, command=self.__userCast)
            self.jar = DirectLabel(parent=self.castGui, relief=None, text=str(self.av.getMoney()), text_scale=0.2, text_fg=(0.95,
                                                                                                                            0.95,
                                                                                                                            0,
                                                                                                                            1), text_shadow=(0,
                                                                                                                                             0,
                                                                                                                                             0,
                                                                                                                                             1), text_pos=(0,
                                                                                                                                                           -0.1,
                                                                                                                                                           0), text_font=ToontownGlobals.getSignFont(), image=jarImage, pos=(-0.2,
                                                                                                                                                                                                                             0,
                                                                                                                                                                                                                             -0.35), scale=0.6)
            self.reelGui = NodePath('reelGui')
            self.reelButton = DirectButton(parent=self.reelGui, relief=None, text=TTLocalizer.FishingAutoReel, text_fg=(1,
                                                                                                                        1,
                                                                                                                        0.6,
                                                                                                                        1), text_pos=(0,
                                                                                                                                      -0.23), text_scale=0.8, image=(upButton, downButton, rolloverButton), image_color=(0,
                                                                                                                                                                                                                         0.69,
                                                                                                                                                                                                                         0,
                                                                                                                                                                                                                         1), image_scale=(24,
                                                                                                                                                                                                                                          1,
                                                                                                                                                                                                                                          11), pos=(1.0,
                                                                                                                                                                                                                                                    0,
                                                                                                                                                                                                                                                    -0.3), scale=0.1, command=self.__userReel)
            self.crankGui = self.reelGui.attachNewNode('crankGui')
            arrow1 = crankArrow.copyTo(self.crankGui)
            arrow1.setColor(1, 0, 0, 1)
            arrow1.setPos(0.25, 0, -0.25)
            arrow2 = crankArrow.copyTo(self.crankGui)
            arrow2.setColor(1, 0, 0, 1)
            arrow2.setPos(-0.25, 0, 0.25)
            arrow2.setR(180)
            self.crankGui.setPos(-0.2, 0, -0.69)
            self.crankGui.setScale(0.5)
            self.crankHandle = DirectFrame(parent=self.crankGui, state=DGG.NORMAL, relief=None, image=crank)
            self.speedGauge = DirectWaitBar(parent=self.crankGui, relief=DGG.SUNKEN, frameSize=(-0.8,
                                                                                                0.8,
                                                                                                -0.15,
                                                                                                0.15), borderWidth=(0.02,
                                                                                                                    0.02), scale=0.42, pos=(0,
                                                                                                                                            0,
                                                                                                                                            0.75), barColor=(0,
                                                                                                                                                             0.69,
                                                                                                                                                             0,
                                                                                                                                                             1))
            self.speedGauge.hide()
            self.tooSlow = DirectLabel(parent=self.speedGauge, relief=None, text=TTLocalizer.FishingCrankTooSlow, scale=0.2, pos=(-1,
                                                                                                                                  0,
                                                                                                                                  0.5))
            self.tooFast = DirectLabel(parent=self.speedGauge, relief=None, text=TTLocalizer.FishingCrankTooFast, scale=0.2, pos=(1,
                                                                                                                                  0,
                                                                                                                                  0.5))
            self.tooSlow.hide()
            self.tooFast.hide()
            self.itemGui = NodePath('itemGui')
            self.itemFrame = DirectFrame(parent=self.itemGui, relief=None, geom=DGG.getDefaultDialogGeom(), geom_color=ToontownGlobals.GlobalDialogColor, geom_scale=(1,
                                                                                                                                                                      1,
                                                                                                                                                                      0.5), text=TTLocalizer.FishingItemFound, text_pos=(0,
                                                                                                                                                                                                                         0.08), text_scale=0.08, pos=(0,
                                                                                                                                                                                                                                                      0,
                                                                                                                                                                                                                                                      0.59))
            self.itemLabel = DirectLabel(parent=self.itemFrame, text='', text_scale=0.06, pos=(0,
                                                                                               0,
                                                                                               -0.08))
            self.failureGui = NodePath('failureGui')
            self.failureFrame = DirectFrame(parent=self.failureGui, relief=None, geom=DGG.getDefaultDialogGeom(), geom_color=ToontownGlobals.GlobalDialogColor, geom_scale=(1.2,
                                                                                                                                                                            1,
                                                                                                                                                                            0.6), text=TTLocalizer.FishingFailure, text_pos=(0,
                                                                                                                                                                                                                             0.12), text_scale=0.08, pos=(0,
                                                                                                                                                                                                                                                          0,
                                                                                                                                                                                                                                                          0.59))
            self.failureLabel = DirectLabel(parent=self.failureFrame, text='', text_scale=0.06, text_wordwrap=16, pos=(0,
                                                                                                                       0,
                                                                                                                       -0.04))
            self.brokeGui = NodePath('brokeGui')
            self.brokeFrame = DirectFrame(parent=self.brokeGui, relief=None, geom=DGG.getDefaultDialogGeom(), geom_color=ToontownGlobals.GlobalDialogColor, geom_scale=(1.2,
                                                                                                                                                                        1,
                                                                                                                                                                        0.6), text=TTLocalizer.FishingBrokeHeader, text_pos=(0,
                                                                                                                                                                                                                             0.12), text_scale=0.08, pos=(0,
                                                                                                                                                                                                                                                          0,
                                                                                                                                                                                                                                                          0.59))
            self.brokeLabel = DirectLabel(parent=self.brokeFrame, relief=None, text=TTLocalizer.FishingBrokeClassic, text_scale=0.06, text_wordwrap=16, pos=(0,
                                                                                                                                                             0,
                                                                                                                                                             -0.04))
            self.madeGui = 1
            return

    def __unmakeGui(self):
        if not self.madeGui:
            return
        else:
            self.exitButton.destroy()
            self.castButton.destroy()
            self.jar.destroy()
            self.reelButton.destroy()
            self.crankHandle.destroy()
            self.speedGauge.destroy()
            self.itemFrame.destroy()
            self.failureFrame.destroy()
            self.brokeFrame.destroy()
            self.madeGui = 0
            return

    def __getBobSpot(self):
        if self.gotBobSpot:
            return
        else:
            startSpot = (0, 8, 5)
            ray = CollisionRay(startSpot[0], startSpot[1], startSpot[2], 0, 0, -1)
            rayNode = CollisionNode('BobRay')
            rayNode.setCollideMask(BitMask32.allOff())
            rayNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
            rayNode.addSolid(ray)
            rayNodePath = self.nodePath.attachNewNode(rayNode)
            cqueue = CollisionHandlerQueue()
            try:
                world = base.cr.playGame.getPlace().loader.geom
            except:
                world = None

            if world != None:
                trav = CollisionTraverser()
                trav.addCollider(rayNodePath, cqueue)
                trav.traverse(world)
            rayNodePath.removeNode()
            cqueue.sortEntries()
            if cqueue.getNumEntries() == 0:
                self.notify.warning("Couldn't find bob spot for %d" % self.doId)
                self.bobSpot = Point3(startSpot[0], startSpot[1], 0)
            else:
                entry = cqueue.getEntry(0)
                self.bobSpot = Point3(entry.getInteriorPoint(self.nodePath))
            self.gotBobSpot = 1
            return

    def b_fishReleaseQuery(self, fish):
        self.fishReleaseQuery(fish)
        self.d_fishReleaseQuery(fish)

    def fishReleaseQuery(self, fish):
        pass

    def d_fishReleaseQuery(self, fish):
        self.sendUpdate('fishReleaseQuery', [fish])

    def b_fishReleased(self, fish):
        self.fishReleased(fish)
        self.d_fishReleased(fish)

    def d_fishReleased(self, fish):
        self.sendUpdate('fishReleased', [fish])

    def fishReleased(self, fish):
        self.__showCastGui()