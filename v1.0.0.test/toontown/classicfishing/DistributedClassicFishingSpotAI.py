import random
from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.task.Task import Task
from toontown.toonbase import TTLocalizer
import FishingCodes

class DistributedClassicFishingSpotAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedClassicFishingSpotAI')

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.avId = None
        self.pondDoId = None
        self.posHpr = [None, None, None, None, None, None]
        self.cast = False
        self.currentFish = None
        self.nibbleFinished = False
        self.targetSpeed = None
        self.crankedBefore = False
        self.totalDistance = 0
        self.totalTime = 0
        return

    def generate(self):
        DistributedObjectAI.generate(self)
        pond = self.air.doId2do.get(self.pondDoId)
        if pond is None:
            self.notify.error(("Pond {0} didn't generate for Fishing Spot {1} in zone {2}!").format(self.pondDoId, self.doId, self.zoneId))
        pond.addSpot(self)
        return

    def setPondDoId(self, pondDoId):
        self.pondDoId = pondDoId

    def getPondDoId(self):
        return self.pondDoId

    def setPosHpr(self, x, y, z, h, p, r):
        self.posHpr = [
         x, y, z, h, p, r]

    def getPosHpr(self):
        return self.posHpr

    def setOccupied(self, avId):
        self.avId = avId

    def d_setOccupied(self, avId):
        self.sendUpdate('setOccupied', [avId])

    def b_setOccupied(self, avId):
        self.setOccupied(avId)
        self.d_setOccupied(avId)

    def setTargetSpeed(self, speed):
        self.targetSpeed = speed

    def d_setTargetSpeed(self, speed):
        self.sendUpdate('setTargetSpeed', [speed])

    def b_setTargetSpeed(self, speed):
        self.setTargetSpeed(speed)
        self.d_setTargetSpeed(speed)

    def doCast(self):
        taskMgr.remove('timeOut%d' % self.doId)
        taskMgr.doMethodLater(45, DistributedClassicFishingSpotAI.removeFromPierWithAnim, 'timeOut%d' % self.doId, [self])
        av = self.air.doId2do[self.avId]
        av.takeMoney(1, False)
        self.crankedBefore = False
        self.totalDistance = 0
        self.totalTime = 0
        self.cast = True
        self.currentFish = None
        self.nibbleFinished = False
        self.targetSpeed = None
        self.d_setMovie(FishingCodes.CastMovie, 0, 0, 0)
        taskMgr.doMethodLater(random.randrange(FishingCodes.NibbleMinWait, FishingCodes.NibbleMaxWait), self.makeNibble, 'makeNibble%d' % self.doId)
        return

    def doAutoReel(self):
        pass

    def doReel(self, speed, netTime, netDistance):
        taskMgr.remove('timeOut%d' % self.doId)
        taskMgr.doMethodLater(45, DistributedClassicFishingSpotAI.removeFromPierWithAnim, 'timeOut%d' % self.doId, [self])
        if self.nibbleFinished:
            return
        else:
            if self.currentFish == None:
                self.uncast()
                self.d_setMovie(FishingCodes.PullInMovie, FishingCodes.TooSoon, 0, 0)
            elif self.crankedBefore == False:
                self.crankedBefore = True
                self.d_setMovie(FishingCodes.BeginReelMovie, 0, 0, speed)
                taskMgr.remove('nibbleDone%d' % self.doId)
                taskMgr.doMethodLater(FishingCodes.PostNibbleWait, self.nibbleDone, 'nibbleDone%d' % self.doId)
            else:
                self.d_setMovie(FishingCodes.ContinueReelMovie, 0, 0, speed)
            self.totalTime += netTime
            self.totalDistance += netDistance
            return

    def fishReleaseQuery(self, fish):
        pass

    def fishReleased(self, fish):
        pass

    def uncast(self):
        self.cast = False
        taskMgr.remove('makeNibble%d' % self.doId)
        taskMgr.remove('nibbleDone%d' % self.doId)

    def requestEnter(self):
        avId = self.air.getAvatarIdFromSender()
        if self.avId != None:
            if self.avId == avId:
                self.air.writeServerEvent('suspicious', avId=avId, issue='Toon requested to enter a pier twice!')
            self.sendUpdateToAvatarId(avId, 'rejectEnter', [])
            return
        else:
            self.acceptOnce(self.air.getAvatarExitEvent(avId), self.removeFromPier)
            self.b_setOccupied(avId)
            self.d_setMovie(FishingCodes.EnterMovie, 0, 0, 0)
            taskMgr.remove('cancelAnimation%d' % self.doId)
            taskMgr.doMethodLater(2, DistributedClassicFishingSpotAI.cancelAnimation, 'cancelAnimation%d' % self.doId, [self])
            taskMgr.remove('timeOut%d' % self.doId)
            taskMgr.doMethodLater(45, DistributedClassicFishingSpotAI.removeFromPierWithAnim, 'timeOut%d' % self.doId, [self])
            self.lastFish = [None, None, None]
            self.cast = False
            return

    def requestExit(self):
        avId = self.air.getAvatarIdFromSender()
        if self.avId != avId:
            self.air.writeServerEvent('suspicious', avId=avId, issue="Toon requested to exit a pier they're not on!")
            return
        self.ignore(self.air.getAvatarExitEvent(avId))
        self.removeFromPierWithAnim()

    def setMovie(self, mode, code, item, speed):
        pass

    def makeNibble(self, task):
        numFish = len(TTLocalizer.ClassicFishNames)
        self.currentFish = random.randrange(0, numFish)
        self.b_setTargetSpeed(round(random.uniform(1.0, 3.0), 3))
        self.notify.debug(('A {0} with speed {1} bit our line.').format(TTLocalizer.ClassicFishNames[self.currentFish][0], self.targetSpeed))
        self.d_setMovie(FishingCodes.NibbleMovie, 0, 0, 0)
        taskMgr.doMethodLater(FishingCodes.NibbleTime, self.nibbleDone, 'nibbleDone%d' % self.doId)
        return Task.done

    def nibbleDone(self, task):
        self.uncast()
        avgSpeed = 0
        if self.totalTime:
            avgSpeed = self.totalDistance / self.totalTime
        if avgSpeed == 0:
            self.d_setMovie(FishingCodes.PullInMovie, FishingCodes.TooLate, 0, 0)
            return Task.done
        else:
            pctDiff = 100.0 * (avgSpeed - self.targetSpeed) / self.targetSpeed
            self.notify.debug(('pctDiff: {0}, avgSpeed: {1}').format(pctDiff, avgSpeed))
            if pctDiff >= FishingCodes.ManualReelMatch:
                self.d_setMovie(FishingCodes.PullInMovie, FishingCodes.TooFast, 0, 0)
            elif pctDiff <= -FishingCodes.ManualReelMatch:
                self.d_setMovie(FishingCodes.PullInMovie, FishingCodes.TooSlow, 0, 0)
            else:
                av = self.air.doId2do.get(self.avId)
                if av is None:
                    self.notify.warning(('Invalid avatar {0} tried to catch an item!').format(self.avId))
                    return
                questItem = self.air.questManager.toonFished(av, self.zoneId)
                if questItem:
                    self.d_setMovie(FishingCodes.PullInMovie, FishingCodes.QuestItem, questItem, 0)
                else:
                    self.d_setMovie(FishingCodes.PullInMovie, FishingCodes.FishItem, self.currentFish, 0)
                    av.addMoney(int(FishingCodes.FishValues[self.currentFish] * self.targetSpeed))
            self.nibbleFinished = True
            return Task.done

    def d_setMovie(self, mode, code, item, speed):
        self.sendUpdate('setMovie', [mode, code, item, speed])

    def cancelAnimation(self):
        self.d_setMovie(FishingCodes.NoMovie, 0, 0, 0)

    def removeFromPierWithAnim(self):
        taskMgr.remove('cancelAnimation%d' % self.doId)
        self.d_setMovie(FishingCodes.ExitMovie, 0, 0, 0)
        taskMgr.doMethodLater(1, DistributedClassicFishingSpotAI.removeFromPier, 'remove%d' % self.doId, [self])

    def removeFromPier(self):
        self.uncast()
        taskMgr.remove('timeOut%d' % self.doId)
        self.cancelAnimation()
        self.d_setOccupied(0)
        self.avId = None
        return