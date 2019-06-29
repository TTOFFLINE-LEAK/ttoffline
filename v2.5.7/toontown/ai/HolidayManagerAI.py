from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.ClockDelta import *
from direct.task import Task
from otp.ai.MagicWordGlobal import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase.HolidayData import ONCELY_HOLIDAYS, WEEKLY_HOLIDAYS, YEARLY_HOLIDAYS
from toontown.parties import PartyGlobals
from toontown.effects.DistributedFireworkShowAI import DistributedFireworkShowAI
from toontown.effects import FireworkShows
from toontown.suit import SuitDNA
import random, time
from datetime import datetime, date

class HolidayManagerAI:
    notify = directNotify.newCategory('HolidayManagerAI')

    def __init__(self, air):
        self.air = air
        self.currentHolidays = []
        self.setup()

    def setup(self):
        holidays = config.GetString('active-holidays', '')
        if holidays != '':
            for holiday in holidays.split(','):
                holiday = int(holiday)
                self.currentHolidays.append(holiday)

            self.air.newsManager.setHolidayIdList([self.currentHolidays])
        if config.GetBool('want-hourly-fireworks', False) or self.isHolidayRunning(ToontownGlobals.JULY4_FIREWORKS) or self.isHolidayRunning(ToontownGlobals.NEWYEARS_FIREWORKS) or self.isHolidayRunning(ToontownGlobals.OCTOBER31_FIREWORKS) or self.isHolidayRunning(ToontownGlobals.NOVEMBER19_FIREWORKS) or self.isHolidayRunning(ToontownGlobals.FEBRUARY14_FIREWORKS) or self.isHolidayRunning(ToontownGlobals.JULY14_FIREWORKS) or self.isHolidayRunning(ToontownGlobals.COMBO_FIREWORKS):
            self.__startFireworksTick()
        self.oncelyHolidayTask()
        self.weeklyHolidayTask()
        self.yearlyHolidayTask()

    def __startFireworksTick(self):
        ts = time.time()
        nextHour = 3600 - ts % 3600
        taskMgr.doMethodLater(nextHour, self.__fireworksTick, 'hourly-fireworks')

    def __fireworksTick(self, task):
        task.delayTime = 3600
        showName = config.GetString('hourly-fireworks-type', 'july4')
        if self.isHolidayRunning(ToontownGlobals.JULY4_FIREWORKS):
            showType = ToontownGlobals.JULY4_FIREWORKS
        else:
            if self.isHolidayRunning(ToontownGlobals.NEWYEARS_FIREWORKS):
                showType = ToontownGlobals.NEWYEARS_FIREWORKS
            else:
                if self.isHolidayRunning(ToontownGlobals.JULY14_FIREWORKS) or self.isHolidayRunning(ToontownGlobals.OCTOBER31_FIREWORKS) or self.isHolidayRunning(ToontownGlobals.NOVEMBER19_FIREWORKS) or self.isHolidayRunning(ToontownGlobals.FEBRUARY14_FIREWORKS):
                    showType = PartyGlobals.FireworkShows.Summer
                else:
                    if self.isHolidayRunning(ToontownGlobals.COMBO_FIREWORKS):
                        shows = [
                         ToontownGlobals.JULY4_FIREWORKS, ToontownGlobals.NEWYEARS_FIREWORKS, PartyGlobals.FireworkShows.Summer]
                        showType = random.choice(shows)
                    else:
                        if showName == 'july4':
                            showType = ToontownGlobals.JULY4_FIREWORKS
                        else:
                            if showName == 'newyears':
                                showType = ToontownGlobals.NEWYEARS_FIREWORKS
                            else:
                                if showName == 'summer':
                                    showType = PartyGlobals.FireworkShows.Summer
                                else:
                                    if showName == 'random':
                                        shows = [
                                         ToontownGlobals.JULY4_FIREWORKS, ToontownGlobals.NEWYEARS_FIREWORKS, PartyGlobals.FireworkShows.Summer]
                                        showType = random.choice(shows)
                                    else:
                                        raise AttributeError('%s is an invalid firework type' % showName)
                                        return
        numShows = len(FireworkShows.shows.get(showType, []))
        showIndex = random.randint(0, numShows - 1)
        for hood in self.air.hoods:
            if hood.HOOD == ToontownGlobals.GolfZone:
                continue
            fireworksShow = DistributedFireworkShowAI(self.air)
            fireworksShow.generateWithRequired(hood.HOOD)
            fireworksShow.b_startShow(showType, showIndex, globalClockDelta.getRealNetworkTime())

        return task.again

    def isHolidayRunning(self, holidayId):
        if holidayId in self.currentHolidays:
            return True

    def getInvadingCog(self, holidayId):
        specialType = 0
        invadingCog = ToontownGlobals.SUIT_INVASION_HOLIDAYS.get(holidayId)
        if invadingCog == None:
            return
        if invadingCog == 'skelecog':
            invadingCog = random.choice(SuitDNA.suitHeadTypes)
            specialType = 1
        else:
            if invadingCog == 'sellbot':
                invadingCog = SuitDNA.getRandomSuitByDept('s')
            else:
                if invadingCog == 'cashbot':
                    invadingCog = SuitDNA.getRandomSuitByDept('m')
                else:
                    if invadingCog == 'lawbot':
                        invadingCog = SuitDNA.getRandomSuitByDept('l')
                    else:
                        if invadingCog == 'bossbot':
                            invadingCog = SuitDNA.getRandomSuitByDept('c')
                        else:
                            if invadingCog == 'hackerbot':
                                invadingCog = SuitDNA.getRandomSuitByDept('g')
        return (
         invadingCog, specialType)

    def yearlyHolidayTask(self, task=None):
        for holiday in YEARLY_HOLIDAYS:
            holidayId = holiday[0]
            now = datetime.now()
            startDate = datetime(now.year, *holiday[1])
            endDate = datetime(now.year, *holiday[2])
            if startDate < now < endDate and holidayId not in self.currentHolidays:
                self.appendHoliday(holidayId)
            elif endDate < now and holidayId in self.currentHolidays:
                self.removeHoliday(holidayId)

        ts = time.time()
        nextHour = 3600 - ts % 3600
        taskMgr.doMethodLater(3600 - ts % 3600, self.yearlyHolidayTask, 'yearlyHolidayTask')

    def weeklyHolidayTask(self, task=None):
        for holiday in WEEKLY_HOLIDAYS:
            holidayId = holiday[0]
            startDay = holiday[1]
            if startDay == date.today().weekday() and holidayId not in self.currentHolidays:
                self.appendHoliday(holidayId)
            elif holidayId in self.currentHolidays:
                self.removeHoliday(holidayId)

        ts = time.time()
        nextHour = 3600 - ts % 3600
        taskMgr.doMethodLater(nextHour, self.weeklyHolidayTask, 'weeklyHolidayTask')

    def oncelyHolidayTask(self, task=None):
        for holiday in ONCELY_HOLIDAYS:
            holidayId = holiday[0]
            now = datetime.now()
            startDate = datetime(now.year, *holiday[1])
            endDate = datetime(now.year, *holiday[2])
            if startDay == date.today().weekday() and holidayId not in self.currentHolidays:
                self.appendHoliday(holidayId)
                if holidayId in self.currentHolidays:
                    self.removeHoliday(holidayId)

        ts = time.time()
        nextHour = 3600 - ts % 3600
        taskMgr.doMethodLater(nextHour, self.oncelyHolidayTask, 'oncelyHolidayTask')

    def appendHoliday(self, holidayId):
        if holidayId not in self.currentHolidays:
            invadingCog = self.getInvadingCog(holidayId)
            if invadingCog:
                if hasattr(simbase.air, 'suitInvasionManager'):
                    invasionSuccess = simbase.air.suitInvasionManager.startMegaInvading(invadingCog[0], invadingCog[1])
                    if not invasionSuccess:
                        return False
                else:
                    return False
            self.currentHolidays.append(holidayId)
            self.air.newsManager.setHolidayIdList([self.currentHolidays])
            messenger.send('holidayStart-%d' % holidayId)
            return True

    def removeHoliday(self, holidayId):
        if holidayId in self.currentHolidays:
            invadingCog = self.getInvadingCog(holidayId)
            if invadingCog:
                if hasattr(simbase.air, 'suitInvasionManager'):
                    simbase.air.suitInvasionManager.stopInvasion()
            self.currentHolidays.remove(holidayId)
            self.air.newsManager.setHolidayIdList([self.currentHolidays])
            messenger.send('holidayEnd-%d' % holidayId)
            return True

    def getCurPhase(self, holidayId):
        return 1


@magicWord(category=CATEGORY_SYSADMIN, types=[int])
def startHoliday(holidayId):
    if holidayId == ToontownGlobals.ORANGES:
        return 'Sorry, that holiday does not exist.'
    if simbase.air.holidayManager.appendHoliday(holidayId):
        return 'Started Holiday %s' % holidayId
    return 'Holiday %s is already running or could not be started' % holidayId


@magicWord(category=CATEGORY_SYSADMIN, types=[int])
def endHoliday(holidayId):
    if holidayId == ToontownGlobals.ORANGES:
        return 'Sorry, that holiday does not exist.'
    if simbase.air.holidayManager.removeHoliday(holidayId):
        return 'Ended Holiday %s' % holidayId
    return 'Holiday %s already ended' % holidayId