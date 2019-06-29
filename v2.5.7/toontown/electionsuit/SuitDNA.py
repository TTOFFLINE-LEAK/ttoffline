import random
from panda3d.core import *
from direct.directnotify.DirectNotifyGlobal import *
from toontown.toonbase import TTLocalizer
import random
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from otp.avatar import AvatarDNA
notify = directNotify.newCategory('SuitDNA')
suitHeadTypes = ['f',
 'p',
 'ym',
 'mm',
 'ds',
 'hh',
 'cr',
 'tbc',
 'bf',
 'b',
 'dt',
 'ac',
 'bs',
 'sd',
 'le',
 'bw',
 'sc',
 'pp',
 'tw',
 'bc',
 'nc',
 'mb',
 'ls',
 'rb',
 'cc',
 'tm',
 'nd',
 'gh',
 'ms',
 'tf',
 'm',
 'mh',
 'm1',
 'm2',
 'm3',
 'm4',
 'm5',
 'm6',
 'm7',
 'm8',
 'cm',
 'sbf',
 'stm',
 'cm2',
 'mdr',
 'mtt']
suitATypes = ['ym',
 'hh',
 'tbc',
 'dt',
 'bs',
 'le',
 'bw',
 'pp',
 'nc',
 'rb',
 'nd',
 'tf',
 'm',
 'mh',
 'm3',
 'm4',
 'm5',
 'm8',
 'cm',
 'stm',
 'cm2',
 'mdr',
 'mtt']
suitBTypes = ['p',
 'ds',
 'b',
 'ac',
 'sd',
 'bc',
 'ls',
 'tm',
 'ms',
 'm2',
 'm6']
suitCTypes = ['f',
 'mm',
 'cr',
 'bf',
 'sc',
 'tw',
 'mb',
 'cc',
 'gh',
 'm1',
 'm7',
 'sbf']
suitDepts = ['c',
 'l',
 'm',
 's',
 'g']
suitDeptFullnames = {'c': TTLocalizer.Bossbot, 'l': TTLocalizer.Lawbot, 
   'm': TTLocalizer.Cashbot, 
   's': TTLocalizer.Sellbot, 
   'g': TTLocalizer.Hackerbot}
suitDeptFullnamesP = {'c': TTLocalizer.BossbotP, 'l': TTLocalizer.LawbotP, 
   'm': TTLocalizer.CashbotP, 
   's': TTLocalizer.SellbotP, 
   'g': TTLocalizer.HackerbotP}
corpPolyColor = VBase4(0.95, 0.75, 0.75, 1.0)
legalPolyColor = VBase4(0.75, 0.75, 0.95, 1.0)
moneyPolyColor = VBase4(0.65, 0.95, 0.85, 1.0)
salesPolyColor = VBase4(0.95, 0.75, 0.95, 1.0)
mafiaPolyColor = VBase4(0.957, 0.56, 0.518, 1.0)
suitsPerLevel = [1,
 1,
 1,
 1,
 1,
 1,
 1,
 1]
suitsPerDept = 8
goonTypes = ['pg', 'sg']

def getSuitBodyType(name):
    if name in suitATypes:
        return 'a'
    if name in suitBTypes:
        return 'b'
    if name in suitCTypes:
        return 'c'
    print 'Unknown body type for suit name: ', name


def getSuitDept(name):
    index = suitHeadTypes.index(name)
    if index < suitsPerDept:
        return suitDepts[0]
    if index < suitsPerDept * 2:
        return suitDepts[1]
    if index < suitsPerDept * 3:
        return suitDepts[2]
    if index < suitsPerDept * 4:
        return suitDepts[3]
    if index < suitsPerDept * 5:
        return suitDepts[4]
    print 'Unknown dept for suit name: ', name
    return
    return


def getDeptFullname(dept):
    return suitDeptFullnames[dept]


def getDeptFullnameP(dept):
    return suitDeptFullnamesP[dept]


def getSuitDeptFullname(name):
    return suitDeptFullnames[getSuitDept(name)]


def getSuitType(name):
    index = suitHeadTypes.index(name)
    return index % suitsPerDept + 1


def getRandomSuitType(level, rng=random):
    return random.randint(max(level - 4, 1), min(level, 8))


def getRandomSuitByDept(dept):
    deptNumber = suitDepts.index(dept)
    return suitHeadTypes[(suitsPerDept * deptNumber + random.randint(0, 7))]


class SuitDNA(AvatarDNA.AvatarDNA):

    def __init__(self, str=None, type=None, dna=None, r=None, b=None, g=None):
        if str != None:
            self.makeFromNetString(str)
        else:
            if type != None:
                if type == 's':
                    self.newSuit()
            else:
                self.type = 'u'
        return

    def __str__(self):
        if self.type == 's':
            return 'type = %s\nbody = %s, dept = %s, name = %s' % ('suit',
             self.body,
             self.dept,
             self.name)
        if self.type == 'b':
            return 'type = boss cog\ndept = %s' % self.dept
        return 'type undefined'

    def makeNetString(self):
        dg = PyDatagram()
        dg.addFixedString(self.type, 1)
        if self.type == 's':
            dg.addFixedString(self.name, 3)
            dg.addFixedString(self.dept, 1)
        else:
            if self.type == 'b':
                dg.addFixedString(self.dept, 1)
            else:
                if self.type == 'u':
                    notify.error('undefined avatar')
                else:
                    notify.error('unknown avatar type: ', self.type)
        return dg.getMessage()

    def makeFromNetString(self, string):
        dg = PyDatagram(string)
        dgi = PyDatagramIterator(dg)
        self.type = dgi.getFixedString(1)
        if self.type == 's':
            self.name = dgi.getFixedString(3)
            self.dept = dgi.getFixedString(1)
            self.body = getSuitBodyType(self.name)
        else:
            if self.type == 'b':
                self.dept = dgi.getFixedString(1)
            else:
                notify.error('unknown avatar type: ', self.type)
        return

    def __defaultGoon(self):
        self.type = 'g'
        self.name = goonTypes[0]

    def __defaultSuit(self):
        self.type = 's'
        self.name = 'ds'
        self.dept = getSuitDept(self.name)
        self.body = getSuitBodyType(self.name)

    def newSuit(self, name=None):
        if name == None:
            self.__defaultSuit()
        else:
            self.type = 's'
            self.name = name
            self.dept = getSuitDept(self.name)
            self.body = getSuitBodyType(self.name)
        return

    def newBossCog(self, dept):
        self.type = 'b'
        self.dept = dept

    def newSuitRandom(self, level=None, dept=None):
        self.type = 's'
        if level == None:
            level = random.choice(range(1, len(suitsPerLevel)))
        else:
            if level < 0 or level > len(suitsPerLevel):
                notify.error('Invalid suit level: %d' % level)
        if dept == None:
            dept = random.choice(suitDepts)
        self.dept = dept
        index = suitDepts.index(dept)
        base = index * suitsPerDept
        offset = 0
        if level > 1:
            for i in range(1, level):
                offset = offset + suitsPerLevel[(i - 1)]

        bottom = base + offset
        top = bottom + suitsPerLevel[(level - 1)]
        self.name = suitHeadTypes[random.choice(range(bottom, top))]
        self.body = getSuitBodyType(self.name)
        return

    def newGoon(self, name=None):
        if type == None:
            self.__defaultGoon()
        else:
            self.type = 'g'
            if name in goonTypes:
                self.name = name
            else:
                notify.error('unknown goon type: ', name)
        return

    def getType(self):
        if self.type == 's':
            type = 'suit'
        else:
            if self.type == 'b':
                type = 'boss'
            else:
                notify.error('Invalid DNA type: ', self.type)
        return type