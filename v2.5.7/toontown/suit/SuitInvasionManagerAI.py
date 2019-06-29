from random import random, randint, choice
from direct.directnotify import DirectNotifyGlobal
import SuitDNA
from otp.ai.MagicWordGlobal import *
from otp.ai.passlib.hash import pbkdf2_sha512
from toontown.toonbase import ToontownGlobals

class SuitInvasionManagerAI:
    notify = DirectNotifyGlobal.directNotify.newCategory('SuitInvasionManagerAI')

    def __init__(self, air):
        self.air = air
        self.invading = 0
        self.specialSuit = 0
        self.suitName = None
        self.numSuits = 0
        self.spawnedSuits = 0
        self.specialSuit = False
        self.undergoingMegaInvasion = False
        if config.GetBool('want-mega-invasions', False):
            self.randomInvasionProbability = config.GetFloat('mega-invasion-probability', 0.4)
            self.specialSuit = choice([0, 0, 0, 1, 2])
            self.megaInvasionCog = config.GetString('mega-invasion-cog-type', '')
            if not self.megaInvasionCog:
                raise AttributeError('No mega invasion cog specified, but mega invasions are on!')
            if self.megaInvasionCog not in SuitDNA.suitHeadTypes:
                raise AttributeError('Invalid cog type specified for mega invasion!')
            taskMgr.doMethodLater(randint(1800, 5400), self.__randomInvasionTick, 'random-invasion-tick')
        else:
            if config.GetBool('want-random-invasions', True):
                self.randomInvasionProbability = config.GetFloat('random-invasion-probability', 0.3)
                taskMgr.doMethodLater(randint(1800, 5400), self.__randomInvasionTick, 'random-invasion-tick')
        return

    def __randomInvasionTick(self, task=None):
        task.delayTime = randint(1800, 5400)
        if self.getInvading():
            self.notify.debug('Invasion tested but already running invasion!')
            return task.again
        if random() <= self.randomInvasionProbability:
            self.notify.debug('Invasion probability hit! Starting invasion.')
            if config.GetBool('want-mega-invasions', False) and random() <= self.randomInvasionProbability:
                suitName = self.megaInvasionCog
                numSuits = randint(2000, 15000)
            else:
                suitPool = SuitDNA.suitHeadTypes[:32]
                for suit in SuitDNA.rank9Cogs:
                    if suit in suitPool:
                        suitPool.remove(suit)

                suitName = choice(suitPool)
                numSuits = randint(1500, 5000)
                self.specialSuit = False
            self.startInvasion(suitName, numSuits, self.specialSuit)
        return task.again

    def getInvading(self):
        return self.invading

    def stopInvasion(self, task=None):
        if not self.getInvading():
            return False
        self.air.newsManager.sendUpdate('setInvasionStatus', [
         ToontownGlobals.SuitInvasionEnd, self.suitName,
         self.numSuits, self.specialSuit])
        if task is not None:
            task.remove()
        else:
            taskMgr.remove('invasion-timeout')
        self.undergoingMegaInvasion = False
        self.specialSuit = 0
        self.numSuits = 0
        self.spawnedSuits = 0
        self.invading = 0
        self.suitName = None
        self.__spAllCogsSupaFly()
        return

    def __checkInvasionOver(self):
        if self.spawnedSuits >= self.numSuits:
            self.stopInvasion()

    def getInvadingCog(self):
        if self.getInvading():
            self.spawnedSuits += 1
            self.__checkInvasionOver()
        return (self.suitName, self.specialSuit)

    def __spAllCogsSupaFly(self):
        for sp in self.air.suitPlanners.values():
            sp.flySuits()

    def startInvasion(self, suitName='f', numSuits=1000, specialSuit=0):
        if self.getInvading():
            return False
        self.invading = True
        self.spawnedSuits = 0
        self.suitName = suitName
        self.numSuits = numSuits
        self.specialSuit = specialSuit
        if self.numSuits < 0:
            self.numSuits = abs(self.numSuits)
        if self.numSuits > 4294967295L:
            self.numSuits = 4294967295L
        if self.specialSuit < 0:
            self.specialSuit = abs(self.specialSuit)
        if self.specialSuit > 255:
            self.specialSuit = 255
        self.air.newsManager.sendUpdate('setInvasionStatus', [
         ToontownGlobals.SuitInvasionBegin, self.suitName,
         self.numSuits, self.specialSuit])
        timePerCog = config.GetFloat('invasion-time-per-cog', 1.5)
        taskMgr.doMethodLater(timePerCog * numSuits, self.stopInvasion, 'invasion-timeout')
        self.__spAllCogsSupaFly()
        return True

    def startMegaInvading(self, suitName='f', specialSuit=0):
        if self.undergoingMegaInvasion:
            return False
        if self.getInvading():
            self.stopInvasion()
        self.undergoingMegaInvasion = True
        return self.startInvasion(suitName, 4294967295L, specialSuit)


@magicWord(types=[str, str, int, int, str], category=CATEGORY_OVERRIDE)
def invasion(cmd, name='f', num=1000, specialSuit=0, password='iNvasIOnS'):
    invMgr = simbase.air.suitInvasionManager
    if cmd == 'start':
        if invMgr.getInvading():
            return 'There is already an invasion on the current AI!'
        if name not in SuitDNA.suitHeadTypes:
            return 'This cog does not exist!'
        if name in SuitDNA.rank9Cogs:
            return 'This Cog can only be summoned with a Swagtory summon.'
        if name in SuitDNA.extraSuits:
            if name in SuitDNA.spawnableExtrasSpecial:
                return 'This Cog currently cannot invade Toontown.'
            if name in SuitDNA.spawnableExtras and name not in SuitDNA.spawnableExtrasWithPass:
                if name == 'bfs':
                    if pbkdf2_sha512.verify(password, MagicWordToPasswordHash.get('invasion')[0]):
                        pass
                    else:
                        return 'This Cog currently cannot invade Toontown.'
            elif name in SuitDNA.spawnableExtras and name in SuitDNA.spawnableExtrasWithPass and (pbkdf2_sha512.verify(password, MagicWordToPasswordHash.get('invasion')[1]) and name == 'sm' or pbkdf2_sha512.verify(password, MagicWordToPasswordHash.get('invasion')[2]) and name == 'cag'):
                pass
            else:
                return 'This Cog currently cannot invade Toontown.'
        invMgr.startInvasion(name, num, specialSuit)
    else:
        if cmd == 'stop':
            if not invMgr.getInvading():
                return 'There is no invasion on the current AI!'
            if invMgr.undergoingMegaInvasion:
                return 'The current invasion is a mega invasion, you must stop the holiday to stop the invasion.'
            invMgr.stopInvasion()
        else:
            return "You didn't enter a valid command! Commands are ~invasion start or stop."