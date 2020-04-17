import datetime, time
from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from toontown.toonbase import ToontownGlobals

class NewsManagerAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('NewsManagerAI')

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.weeklyCalendarHolidays = []
        self.yearlyCalendarHolidays = []
        self.oncelyCalendarHolidays = []
        self.relativelyCalendarHolidays = []
        self.multipleStartHolidays = []

    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)
        self.setupWeeklyCalendarHolidays()
        self.setupYearlyCalendarHolidays()
        self.air.holidayManager.setup()
        taskMgr.add(self.__weeklyCalendarHolidayTask, self.uniqueName('weekly-calendar-holiday-task'))
        self.accept('avatarEntered', self.handleAvatarEntered)

    def delete(self):
        DistributedObjectAI.delete(self)
        taskMgr.remove(self.uniqueName('silly-saturday-task'))
        taskMgr.remove(self.uniqueName('start-silly-saturday-bingo'))
        taskMgr.remove(self.uniqueName('start-silly-saturday-circuit'))
        taskMgr.remove(self.uniqueName('start-weekly-calendar-holiday'))

    def handleAvatarEntered(self, av):
        if self.air.suitInvasionManager.getInvading():
            self.sendUpdateToAvatarId(av.getDoId(), 'setInvasionStatus', [ToontownGlobals.SuitInvasionBulletin,
             self.air.suitInvasionManager.invadingCog[0],
             self.air.suitInvasionManager.numSuits,
             self.air.suitInvasionManager.invadingCog[1]])
        if self.air.holidayManager.isHolidayRunning(ToontownGlobals.SILLY_SATURDAY_BINGO) or self.air.holidayManager.isHolidayRunning(ToontownGlobals.SILLY_SATURDAY_CIRCUIT) or self.air.holidayManager.isHolidayRunning(ToontownGlobals.SILLY_SATURDAY_TROLLEY) or self.air.holidayManager.isHolidayRunning(ToontownGlobals.ROAMING_TRIALER_WEEKEND):
            self.sendUpdateToAvatarId(av.getDoId(), 'holidayNotify', [])

    def setupWeeklyCalendarHolidays(self):
        weeklyCalendarHolidays = self.getWeeklyCalendarHolidays()[:]
        weeklyEvents = [
         [
          ToontownGlobals.CIRCUIT_RACING, 0],
         [
          ToontownGlobals.FISH_BINGO_NIGHT, 2],
         [
          ToontownGlobals.SILLY_SATURDAY_BINGO, 5]]
        for weeklyEvent in weeklyEvents:
            if weeklyEvent not in weeklyCalendarHolidays:
                weeklyCalendarHolidays.append(weeklyEvent)

        self.b_setWeeklyCalendarHolidays(weeklyCalendarHolidays)

    def setupYearlyCalendarHolidays(self):
        yearlyCalendarHolidays = self.getYearlyCalendarHolidays()[:]
        yearlyEvents = [
         [
          ToontownGlobals.VALENTINES_DAY, [2, 9, 0, 0], [2, 16, 23, 59]],
         [
          ToontownGlobals.IDES_OF_MARCH, [3, 14, 0, 0], [3, 20, 23, 59]],
         [
          ToontownGlobals.APRIL_FOOLS_COSTUMES, [3, 29, 0, 0], [4, 11, 23, 59]],
         [
          ToontownGlobals.JULY4_FIREWORKS, [6, 30, 0, 0], [7, 15, 23, 59]],
         [
          ToontownGlobals.HALLOWEEN_PROPS, [10, 25, 0, 0], [11, 1, 23, 59]],
         [
          ToontownGlobals.TRICK_OR_TREAT, [10, 25, 0, 0], [11, 1, 23, 59]],
         [
          ToontownGlobals.BLACK_CAT_DAY, [10, 31, 0, 0], [10, 31, 23, 59]],
         [
          ToontownGlobals.WINTER_DECORATIONS, [12, 14, 0, 0], [1, 4, 23, 59]],
         [
          ToontownGlobals.WINTER_CAROLING, [12, 16, 0, 0], [1, 4, 23, 59]],
         [
          ToontownGlobals.NEWYEARS_FIREWORKS, [12, 31, 0, 0], [1, 6, 23, 59]]]
        for yearlyEvent in yearlyEvents:
            if yearlyEvent not in yearlyCalendarHolidays:
                yearlyCalendarHolidays.append(yearlyEvent)

        self.b_setYearlyCalendarHolidays(yearlyCalendarHolidays)

    def __weeklyCalendarHolidayTask(self, task):
        holidaysToStart = []
        holidaysToEnd = []
        weeklyCalendarHolidays = self.getWeeklyCalendarHolidays()[:]
        currentWeekday = self.air.toontownTimeManager.getCurServerDateTime().now(tz=self.air.toontownTimeManager.serverTimeZone).weekday()
        for weeklyCalendarHoliday in weeklyCalendarHolidays:
            if weeklyCalendarHoliday[0] == ToontownGlobals.SILLY_SATURDAY_BINGO:
                if currentWeekday == weeklyCalendarHoliday[1]:
                    currentHour = self.air.toontownTimeManager.getCurServerDateTime().now(tz=self.air.toontownTimeManager.serverTimeZone).hour
                    if not currentHour // 2 % 12 % 2:
                        if not self.air.holidayManager.isHolidayRunning(ToontownGlobals.SILLY_SATURDAY_BINGO):
                            if self.air.holidayManager.isHolidayRunning(ToontownGlobals.SILLY_SATURDAY_CIRCUIT):
                                self.air.holidayManager.endHoliday(ToontownGlobals.SILLY_SATURDAY_CIRCUIT)
                                taskMgr.doMethodLater(5, self.air.holidayManager.startHoliday, self.uniqueName('start-silly-saturday-bingo'), extraArgs=[
                                 ToontownGlobals.SILLY_SATURDAY_BINGO], appendTask=True)
                            else:
                                self.air.holidayManager.startHoliday(ToontownGlobals.SILLY_SATURDAY_BINGO)
                    elif not self.air.holidayManager.isHolidayRunning(ToontownGlobals.SILLY_SATURDAY_CIRCUIT):
                        if self.air.holidayManager.isHolidayRunning(ToontownGlobals.SILLY_SATURDAY_BINGO):
                            self.air.holidayManager.endHoliday(ToontownGlobals.SILLY_SATURDAY_BINGO)
                            taskMgr.doMethodLater(5, self.air.holidayManager.startHoliday, self.uniqueName('start-silly-saturday-circuit'), extraArgs=[
                             ToontownGlobals.SILLY_SATURDAY_CIRCUIT], appendTask=True)
                        else:
                            self.air.holidayManager.startHoliday(ToontownGlobals.SILLY_SATURDAY_CIRCUIT)
                    currentEpoch = time.mktime(datetime.datetime.now(tz=self.air.toontownTimeManager.serverTimeZone).timetuple()) + datetime.datetime.now(tz=self.air.toontownTimeManager.serverTimeZone).microsecond * 1e-06
                    task.delayTime = 3600.0 - currentEpoch % 3600.0
                    return task.again
                if self.air.holidayManager.isHolidayRunning(ToontownGlobals.SILLY_SATURDAY_BINGO):
                    self.air.holidayManager.endHoliday(ToontownGlobals.SILLY_SATURDAY_BINGO)
                if self.air.holidayManager.isHolidayRunning(ToontownGlobals.SILLY_SATURDAY_CIRCUIT):
                    self.air.holidayManager.endHoliday(ToontownGlobals.SILLY_SATURDAY_CIRCUIT)
            elif currentWeekday == weeklyCalendarHoliday[1]:
                if not self.air.holidayManager.isHolidayRunning(weeklyCalendarHoliday[0]):
                    holidaysToStart.append(weeklyCalendarHoliday[0])
            elif self.air.holidayManager.isHolidayRunning(weeklyCalendarHoliday[0]):
                holidaysToEnd.append(weeklyCalendarHoliday[0])

        for holidayToEnd in holidaysToEnd:
            if self.air.holidayManager.isHolidayRunning(holidayToEnd):
                self.air.holidayManager.endHoliday(holidayToEnd)

        for holidayToStart in holidaysToStart:
            if not self.air.holidayManager.isHolidayRunning(holidayToStart):
                if holidaysToEnd:
                    taskMgr.doMethodLater(5, self.air.holidayManager.startHoliday, self.uniqueName('start-weekly-calendar-holiday'), extraArgs=[holidayToStart], appendTask=True)
                else:
                    self.air.holidayManager.startHoliday(holidayToStart)

        tomorrow = self.air.toontownTimeManager.getCurServerDateTime().now(tz=self.air.toontownTimeManager.serverTimeZone) + datetime.timedelta(1)
        midnight = datetime.datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day, hour=0, minute=0, second=0, tzinfo=self.air.toontownTimeManager.serverTimeZone)
        secondsUntilMidnight = (midnight - self.air.toontownTimeManager.getCurServerDateTime().now(tz=self.air.toontownTimeManager.serverTimeZone)).seconds
        task.delayTime = secondsUntilMidnight
        return task.again

    def setWeeklyCalendarHolidays(self, weeklyCalendarHolidays):
        self.weeklyCalendarHolidays = weeklyCalendarHolidays

    def d_setWeeklyCalendarHolidays(self, weeklyCalendarHolidays):
        self.sendUpdate('setWeeklyCalendarHolidays', [weeklyCalendarHolidays])

    def b_setWeeklyCalendarHolidays(self, weeklyCalendarHolidays):
        self.setWeeklyCalendarHolidays(weeklyCalendarHolidays)
        self.d_setWeeklyCalendarHolidays(weeklyCalendarHolidays)

    def getWeeklyCalendarHolidays(self):
        return self.weeklyCalendarHolidays

    def setYearlyCalendarHolidays(self, yearlyCalendarHolidays):
        self.yearlyCalendarHolidays = yearlyCalendarHolidays

    def d_setYearlyCalendarHolidays(self, yearlyCalendarHolidays):
        self.sendUpdate('setYearlyCalendarHolidays', [yearlyCalendarHolidays])

    def b_setYearlyCalendarHolidays(self, yearlyCalendarHolidays):
        self.setYearlyCalendarHolidays(yearlyCalendarHolidays)
        self.d_setYearlyCalendarHolidays(yearlyCalendarHolidays)

    def getYearlyCalendarHolidays(self):
        return self.yearlyCalendarHolidays

    def setOncelyCalendarHolidays(self, oncelyCalendarHolidays):
        self.oncelyCalendarHolidays = oncelyCalendarHolidays

    def d_setOncelyCalendarHolidays(self, oncelyCalendarHolidays):
        self.sendUpdate('setOncelyCalendarHolidays', [oncelyCalendarHolidays])

    def b_setOncelyCalendarHolidays(self, oncelyCalendarHolidays):
        self.setOncelyCalendarHolidays(oncelyCalendarHolidays)
        self.d_setOncelyCalendarHolidays(oncelyCalendarHolidays)

    def getOncelyCalendarHolidays(self):
        return self.oncelyCalendarHolidays

    def setRelativelyCalendarHolidays(self, relativelyCalendarHolidays):
        self.relativelyCalendarHolidays = relativelyCalendarHolidays

    def d_setRelativelyCalendarHolidays(self, relativelyCalendarHolidays):
        self.sendUpdate('setRelativelyCalendarHolidays', [relativelyCalendarHolidays])

    def b_setRelativelyCalendarHolidays(self, relativelyCalendarHolidays):
        self.setRelativelyCalendarHolidays(relativelyCalendarHolidays)
        self.d_setRelativelyCalendarHolidays(relativelyCalendarHolidays)

    def getRelativelyCalendarHolidays(self):
        return self.relativelyCalendarHolidays

    def setMultipleStartHolidays(self, multipleStartHolidays):
        self.multipleStartHolidays = multipleStartHolidays

    def d_setMultipleStartHolidays(self, multipleStartHolidays):
        self.sendUpdate('setMultipleStartHolidays', [multipleStartHolidays])

    def b_setMultipleStartHolidays(self, multipleStartHolidays):
        self.setMultipleStartHolidays(multipleStartHolidays)
        self.d_setMultipleStartHolidays(multipleStartHolidays)

    def getMultipleStartHolidays(self):
        return self.multipleStartHolidays

    def d_setInvasionStatus(self, msgType, cogType, numRemaining, skeleton):
        self.sendUpdate('setInvasionStatus', [msgType, cogType, numRemaining, skeleton])

    def d_setHolidayIdList(self, holidayIdList):
        self.sendUpdate('setHolidayIdList', [holidayIdList])

    def d_setBingoStart(self):
        self.sendUpdate('setBingoStart')

    def d_setBingoEnd(self):
        self.sendUpdate('setBingoEnd')

    def d_setCircuitRaceStart(self):
        self.sendUpdate('setCircuitRaceStart')

    def d_setCircuitRaceEnd(self):
        self.sendUpdate('setCircuitRaceEnd')

    def d_setExpMultiplier(self, mult):
        self.sendUpdate('setExpMultiplier', [mult])