from direct.directnotify import DirectNotifyGlobal
import HoodDataAI
from toontown.toonbase import ToontownGlobals
from toontown.safezone import DistributedTrolleyAI
from toontown.classicchars import DistributedMickeyAI, DistributedVampireMickeyAI, DistributedDaisyAI
from toontown.election.DistributedElectionEventAI import DistributedElectionEventAI
from toontown.safezone import ButterflyGlobals, DistributedPumpkinCogAI, DistributedPresentAI
from direct.task import Task

class TTHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('SZHoodAI')

    def __init__(self, air, zoneId=None):
        hoodId = ToontownGlobals.ToontownCentral
        if zoneId == None:
            zoneId = hoodId
        self.cCharClass = DistributedMickeyAI.DistributedMickeyAI
        self.cCharClassAF = DistributedDaisyAI.DistributedDaisyAI
        self.cCharClassHW = DistributedVampireMickeyAI.DistributedVampireMickeyAI
        self.cCharConfigVar = 'want-mickey'
        self.spookyCog = None
        self.presents = []
        HoodDataAI.HoodDataAI.__init__(self, air, zoneId, hoodId)
        return

    def startup(self):
        self.notify.info('Creating zone... Toontown Central')
        HoodDataAI.HoodDataAI.startup(self)
        trolley = DistributedTrolleyAI.DistributedTrolleyAI(self.air)
        trolley.generateWithRequired(self.zoneId)
        self.addDistObj(trolley)
        self.trolley = trolley
        if self.air.holidayManager.isHolidayRunning(ToontownGlobals.HALLOWEEN):
            self.createPumpkinCog()
        else:
            self.acceptOnce(('holidayStart-{0}').format(ToontownGlobals.HALLOWEEN), self.createPumpkinCog)
        if self.air.holidayManager.isHolidayRunning(ToontownGlobals.WINTER_DECORATIONS):
            self.createPresents()
        else:
            self.acceptOnce(('holidayStart-{0}').format(ToontownGlobals.WINTER_DECORATIONS), self.createPresents)
        self.createButterflies(ButterflyGlobals.TTC)
        if self.air.config.GetBool('want-doomsday', False) or self.air.config.GetBool('want-election-buildup', False):
            self.spawnElection()
        if simbase.blinkTrolley:
            taskMgr.doMethodLater(0.5, self._deleteTrolley, 'deleteTrolley')
        messenger.send('TTHoodSpawned', [self])

    def shutdown(self):
        HoodDataAI.HoodDataAI.shutdown(self)
        messenger.send('TTHoodDestroyed', [self])

    def _deleteTrolley(self, task):
        self.trolley.requestDelete()
        taskMgr.doMethodLater(0.5, self._createTrolley, 'createTrolley')
        return Task.done

    def _createTrolley(self, task):
        trolley = DistributedTrolleyAI.DistributedTrolleyAI(self.air)
        trolley.generateWithRequired(self.zoneId)
        self.trolley = trolley
        taskMgr.doMethodLater(0.5, self._deleteTrolley, 'deleteTrolley')
        return Task.done

    def spawnElection(self):
        election = self.air.doFind('ElectionEvent')
        if election is None:
            election = DistributedElectionEventAI(self.air)
            election.generateWithRequired(self.zoneId)
        election.b_setState('Idle')
        if self.air.config.GetBool('want-hourly-doomsday', False):
            self.__startElectionTick()
        return

    def __startElectionTick(self):
        ts = time.time()
        nextHour = 3600 - ts % 3600
        taskMgr.doMethodLater(nextHour, self.__electionTick, 'election-hourly')

    def __electionTick(self, task):
        task.delayTime = 3600
        toons = self.air.doFindAll('DistributedToon')
        if not toons:
            return task.again
        election = self.air.doFind('ElectionEvent')
        if election:
            state = election.getState()
            if state[0] == 'Idle':
                taskMgr.doMethodLater(10, election.b_setState, 'election-start-delay', extraArgs=['Event'])
        if not election:
            election = DistributedElectionEventAI(self.air)
            election.generateWithRequired(self.zoneId)
            election.b_setState('Idle')
            taskMgr.doMethodLater(10, election.b_setState, 'election-start-delay', extraArgs=['Event'])
        return task.again

    def createClassicCharacter(self):
        if not self.air.config.GetBool('want-doomsday', False):
            HoodDataAI.HoodDataAI.createClassicCharacter(self)

    def createAFClassicCharacter(self):
        if not self.air.config.GetBool('want-doomsday', False):
            HoodDataAI.HoodDataAI.createAFClassicCharacter(self)

    def createPumpkinCog(self):
        spookyCog = DistributedPumpkinCogAI.DistributedPumpkinCogAI(self.air)
        spookyCog.generateWithRequired(self.zoneId)
        self.addDistObj(spookyCog)
        self.spookyCog = spookyCog
        self.acceptOnce(('holidayEnd-{0}').format(ToontownGlobals.HALLOWEEN), self.removePumpkinCog)

    def removePumpkinCog(self):
        self.spookyCog.delete()
        self.spookyCog = None
        self.acceptOnce(('holidayStart-{0}').format(ToontownGlobals.HALLOWEEN), self.createPumpkinCog)
        return

    def createPresents(self):
        presentDefs = [
         [
          79.688, 158.123, 2.483, -15.427, 0, 0, 1],
         [
          -128.618, -65.178, 0.484, -230.316, 0, 0, 1],
         [
          -62.478, -22.103, -1.975, 0, 0, 0, 2],
         [
          140.478, -84.103, 2.525, -80, 0, 0, 2],
         [
          10.371, -130.137, 3.025, -227, 0, 0, 3],
         [
          110.094, 26.642, 4.025, -55, 0, 0, 3]]
        for presentDef in presentDefs:
            present = DistributedPresentAI.DistributedPresentAI(self.air, presentDef[0], presentDef[1], presentDef[2], presentDef[3], presentDef[4], presentDef[5], presentDef[6])
            present.generateWithRequired(self.zoneId)
            self.addDistObj(present)
            self.presents.append(present)

        self.acceptOnce(('holidayEnd-{0}').format(ToontownGlobals.WINTER_DECORATIONS), self.removePresents)

    def removePresents(self):
        for present in self.presents:
            present.delete()

        self.presents = []
        self.acceptOnce(('holidayStart-{0}').format(ToontownGlobals.WINTER_DECORATIONS), self.createPresents)