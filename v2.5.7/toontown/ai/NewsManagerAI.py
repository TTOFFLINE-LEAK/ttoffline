from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from toontown.toonbase import ToontownGlobals
from toontown.toonbase.HolidayData import ONCELY_HOLIDAYS, WEEKLY_HOLIDAYS, YEARLY_HOLIDAYS
from otp.ai.MagicWordGlobal import *

class NewsManagerAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('NewsManagerAI')

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.accept('avatarEntered', self.__announceIfInvasion)
        self.oncelyHolidays = ONCELY_HOLIDAYS
        self.weeklyHolidays = WEEKLY_HOLIDAYS
        self.yearlyHolidays = YEARLY_HOLIDAYS

    def __announceIfInvasion(self, avatar):
        if self.air.suitInvasionManager.getInvading():
            self.sendUpdateToAvatarId(avatar.getDoId(), 'setInvasionStatus', [
             ToontownGlobals.SuitInvasionBulletin, self.air.suitInvasionManager.suitName,
             self.air.suitInvasionManager.numSuits, self.air.suitInvasionManager.specialSuit])

    def setPopulation(self, todo0):
        pass

    def setBingoWin(self, todo0):
        pass

    def setBingoStart(self):
        self.sendUpdate('setBingoStart', [])

    def setBingoEnd(self):
        self.sendUpdate('setBingoEnd', [])

    def setCircuitRaceStart(self):
        self.sendUpdate('setCircuitRaceStart', [])

    def setCircuitRaceEnd(self):
        self.sendUpdate('setCircuitRaceEnd', [])

    def setTrolleyHolidayStart(self):
        self.sendUpdate('setTrolleyHolidayStart', [])

    def setTrolleyHolidayEnd(self):
        self.sendUpdate('setTrolleyHolidayEnd', [])

    def setTrolleyWeekendStart(self):
        self.sendUpdate('setTrolleyWeekendStart', [])

    def setTrolleyWeekendEnd(self):
        self.sendUpdate('setTrolleyWeekendEnd', [])

    def setRoamingTrialerWeekendStart(self):
        pass

    def setRoamingTrialerWeekendEnd(self):
        pass

    def setInvasionStatus(self, msgType, cogType, numRemaining, skeleton):
        self.sendUpdate('setInvasionStatus', args=[msgType, cogType, numRemaining, skeleton])

    def setHolidayIdList(self, holidays):
        self.sendUpdate('setHolidayIdList', holidays)

    def holidayNotify(self):
        pass

    def setWeeklyCalendarHolidays(self, weeklyHolidays):
        self.sendUpdate('setWeeklyCalendarHolidays', [weeklyHolidays])

    def getWeeklyCalendarHolidays(self):
        return self.weeklyHolidays

    def setYearlyCalendarHolidays(self, yearlyHolidays):
        self.sendUpdate('setYearlyCalendarHolidays', [yearlyHolidays])

    def getYearlyCalendarHolidays(self):
        return self.yearlyHolidays

    def setOncelyCalendarHolidays(self, oncelyHolidays):
        self.sendUpdate('setWeeklyCalendarHolidays', [oncelyHolidays])

    def getOncelyCalendarHolidays(self):
        return self.oncelyHolidays

    def setRelativelyCalendarHolidays(self, todo0):
        pass

    def getRelativelyCalendarHolidays(self):
        return []

    def setMultipleStartHolidays(self, todo0):
        pass

    def getMultipleStartHolidays(self):
        return []

    def sendSystemMessage(self, todo0, todo1):
        pass


@magicWord(category=CATEGORY_DEBUG)
def invasionstatus():
    if not simbase.air.suitInvasionManager.getInvading():
        return 'There is no invasion in progress!'
    simbase.air.newsManager.sendUpdateToAvatarId(spellbook.getInvoker().getDoId(), 'setInvasionStatus', [
     ToontownGlobals.SuitInvasionUpdate, simbase.air.suitInvasionManager.suitName,
     simbase.air.suitInvasionManager.numSuits, simbase.air.suitInvasionManager.specialSuit])