from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from otp.avatar import Avatar
import SuitDNA
from toontown.toonbase import ToontownGlobals
from panda3d.core import *
from toontown.battle import SuitBattleGlobals
from direct.task.Task import Task
from toontown.battle import BattleParticles
from toontown.battle import BattleProps
from toontown.toonbase import TTLocalizer
from libotp import *
from direct.showbase import AppRunnerGlobal
import SuitTimings, string, os
aSize = 6.06
bSize = 5.29
cSize = 4.14
SuitDialogArray = []
SkelSuitDialogArray = []
AllSuits = (('walk', 'walk'), ('run', 'walk'), ('neutral', 'neutral'))
AllSuitsMinigame = (('victory', 'victory'),
 ('flail', 'flailing'),
 ('tug-o-war', 'tug-o-war'),
 ('slip-backward', 'slip-backward'),
 ('slip-forward', 'slip-forward'))
AllSuitsTutorialBattle = (('lose', 'lose'), ('pie-small-react', 'pie-small'), ('squirt-small-react', 'squirt-small'))
AllSuitsBattle = (('drop-react', 'anvil-drop'),
 ('flatten', 'drop'),
 ('sidestep-left', 'sidestep-left'),
 ('sidestep-right', 'sidestep-right'),
 ('squirt-large-react', 'squirt-large'),
 ('landing', 'landing'),
 ('reach', 'walknreach'),
 ('rake-react', 'rake'),
 ('hypnotized', 'hypnotize'),
 ('soak', 'soak'))
SuitsCEOBattle = (('sit', 'sit'),
 ('sit-eat-in', 'sit-eat-in'),
 ('sit-eat-loop', 'sit-eat-loop'),
 ('sit-eat-out', 'sit-eat-out'),
 ('sit-angry', 'sit-angry'),
 ('sit-hungry-left', 'leftsit-hungry'),
 ('sit-hungry-right', 'rightsit-hungry'),
 ('sit-lose', 'sit-lose'),
 ('tray-walk', 'tray-walk'),
 ('tray-neutral', 'tray-neutral'),
 ('sit-lose', 'sit-lose'))
f = (('throw-paper', 'throw-paper', 3.5), ('phone', 'phone', 3.5), ('shredder', 'shredder', 3.5))
p = (('pencil-sharpener', 'pencil-sharpener', 5),
 ('pen-squirt', 'pen-squirt', 5),
 ('hold-eraser', 'hold-eraser', 5),
 ('finger-wag', 'finger-wag', 5),
 ('hold-pencil', 'hold-pencil', 5))
ym = (('throw-paper', 'throw-paper', 5),
 ('golf-club-swing', 'golf-club-swing', 5),
 ('magic3', 'magic3', 5),
 ('rubber-stamp', 'rubber-stamp', 5),
 ('smile', 'smile', 5))
mm = (('speak', 'speak', 5),
 ('effort', 'effort', 5),
 ('magic1', 'magic1', 5),
 ('pen-squirt', 'fountain-pen', 5),
 ('finger-wag', 'finger-wag', 5))
ds = (('magic1', 'magic1', 5),
 ('magic2', 'magic2', 5),
 ('throw-paper', 'throw-paper', 5),
 ('magic3', 'magic3', 5))
hh = (('pen-squirt', 'fountain-pen', 7),
 ('glower', 'glower', 5),
 ('throw-paper', 'throw-paper', 5),
 ('magic1', 'magic1', 5),
 ('roll-o-dex', 'roll-o-dex', 5))
cr = (('pickpocket', 'pickpocket', 5), ('throw-paper', 'throw-paper', 3.5), ('glower', 'glower', 5))
tbc = (('cigar-smoke', 'cigar-smoke', 8),
 ('glower', 'glower', 5),
 ('song-and-dance', 'song-and-dance', 8),
 ('golf-club-swing', 'golf-club-swing', 5))
cc = (('speak', 'speak', 5),
 ('glower', 'glower', 5),
 ('phone', 'phone', 3.5),
 ('finger-wag', 'finger-wag', 5))
tm = (('speak', 'speak', 5),
 ('throw-paper', 'throw-paper', 5),
 ('pickpocket', 'pickpocket', 5),
 ('roll-o-dex', 'roll-o-dex', 5),
 ('finger-wag', 'finger-wag', 5))
nd = (('pickpocket', 'pickpocket', 5),
 ('roll-o-dex', 'roll-o-dex', 5),
 ('magic3', 'magic3', 5),
 ('smile', 'smile', 5))
gh = (('speak', 'speak', 5), ('pen-squirt', 'fountain-pen', 5), ('rubber-stamp', 'rubber-stamp', 5))
ms = (('effort', 'effort', 5),
 ('throw-paper', 'throw-paper', 5),
 ('stomp', 'stomp', 5),
 ('quick-jump', 'jump', 6))
tf = (('phone', 'phone', 5),
 ('smile', 'smile', 5),
 ('throw-object', 'throw-object', 5),
 ('glower', 'glower', 5))
m = (('speak', 'speak', 5),
 ('magic2', 'magic2', 5),
 ('magic1', 'magic1', 5),
 ('golf-club-swing', 'golf-club-swing', 5))
mh = (('magic1', 'magic1', 5),
 ('smile', 'smile', 5),
 ('golf-club-swing', 'golf-club-swing', 5),
 ('song-and-dance', 'song-and-dance', 5))
sc = (('throw-paper', 'throw-paper', 3.5), ('watercooler', 'watercooler', 5), ('pickpocket', 'pickpocket', 5))
pp = (('throw-paper', 'throw-paper', 5), ('glower', 'glower', 5), ('finger-wag', 'fingerwag', 5))
tw = (('throw-paper', 'throw-paper', 3.5),
 ('glower', 'glower', 5),
 ('magic2', 'magic2', 5),
 ('finger-wag', 'finger-wag', 5))
bc = (('phone', 'phone', 5), ('hold-pencil', 'hold-pencil', 5))
nc = (('phone', 'phone', 5), ('throw-object', 'throw-object', 5))
mb = (('magic1', 'magic1', 5), ('throw-paper', 'throw-paper', 3.5))
ls = (('throw-paper', 'throw-paper', 5), ('throw-object', 'throw-object', 5), ('hold-pencil', 'hold-pencil', 5))
rb = (('glower', 'glower', 5), ('magic1', 'magic1', 5), ('golf-club-swing', 'golf-club-swing', 5))
bf = (('pickpocket', 'pickpocket', 5),
 ('rubber-stamp', 'rubber-stamp', 5),
 ('shredder', 'shredder', 3.5),
 ('watercooler', 'watercooler', 5))
b = (('effort', 'effort', 5),
 ('throw-paper', 'throw-paper', 5),
 ('throw-object', 'throw-object', 5),
 ('magic1', 'magic1', 5))
dt = (('rubber-stamp', 'rubber-stamp', 5),
 ('throw-paper', 'throw-paper', 5),
 ('speak', 'speak', 5),
 ('finger-wag', 'fingerwag', 5),
 ('throw-paper', 'throw-paper', 5))
ac = (('throw-object', 'throw-object', 5),
 ('roll-o-dex', 'roll-o-dex', 5),
 ('stomp', 'stomp', 5),
 ('phone', 'phone', 5),
 ('throw-paper', 'throw-paper', 5))
bs = (('magic1', 'magic1', 5), ('throw-paper', 'throw-paper', 5), ('finger-wag', 'fingerwag', 5))
sd = (('magic2', 'magic2', 5),
 ('quick-jump', 'jump', 6),
 ('stomp', 'stomp', 5),
 ('magic3', 'magic3', 5),
 ('hold-pencil', 'hold-pencil', 5),
 ('throw-paper', 'throw-paper', 5))
le = (('speak', 'speak', 5),
 ('throw-object', 'throw-object', 5),
 ('glower', 'glower', 5),
 ('throw-paper', 'throw-paper', 5))
bw = (('finger-wag', 'fingerwag', 5),
 ('cigar-smoke', 'cigar-smoke', 8),
 ('gavel', 'gavel', 8),
 ('magic1', 'magic1', 5),
 ('throw-object', 'throw-object', 5),
 ('throw-paper', 'throw-paper', 5))
sf = (('cigar-smoke', 'cigar-smoke', 8),
 ('magic2', 'magic2', 5),
 ('magic1', 'magic1', 5),
 ('speak', 'speak', 5))
sm = (('magic1', 'magic1', 5),
 ('smile', 'smile', 5),
 ('golf-club-swing', 'golf-club-swing', 5))
mdr = (('magic1', 'magic1', 5),
 ('magic3', 'magic3', 5),
 ('magic2', 'magic2', 5),
 ('finger-wag', 'fingerwag', 5))
if not base.config.GetBool('want-new-cogs', 0):
    ModelDict = {'a': ('/models/char/suitA-', 4), 'b': ('/models/char/suitB-', 4), 'c': ('/models/char/suitC-', 3.5)}
    TutorialModelDict = {'a': ('/models/char/suitA-', 4), 'b': ('/models/char/suitB-', 4), 
       'c': ('/models/char/suitC-', 3.5)}
else:
    ModelDict = {'a': ('/models/char/tt_a_ene_cga_', 4), 'b': ('/models/char/tt_a_ene_cgb_', 4), 
       'c': ('/models/char/tt_a_ene_cgc_', 3.5)}
    TutorialModelDict = {'a': ('/models/char/tt_a_ene_cga_', 4), 'b': ('/models/char/tt_a_ene_cgb_', 4), 
       'c': ('/models/char/tt_a_ene_cgc_', 3.5)}
HeadModelDict = {'a': ('/models/char/suitA-', 4), 'b': ('/models/char/suitB-', 4), 'c': ('/models/char/suitC-', 3.5)}
extraSpecialHeads = ['mole_cog']

def loadTutorialSuit():
    loader.loadModel('phase_3.5/models/char/suitC-mod').node()
    loadDialog(1)


def loadSuits(level):
    loadSuitModelsAndAnims(level, flag=1)
    loadDialog(level)


def unloadSuits(level):
    loadSuitModelsAndAnims(level, flag=0)
    unloadDialog(level)


def loadSuitModelsAndAnims(level, flag=0):
    for key in ModelDict.keys():
        model, phase = ModelDict[key]
        if base.config.GetBool('want-new-cogs', 0):
            headModel, headPhase = HeadModelDict[key]
        else:
            headModel, headPhase = ModelDict[key]
        if flag:
            if base.config.GetBool('want-new-cogs', 0):
                filepath = 'phase_3.5' + model + 'zero'
                if cogExists(model + 'zero.bam'):
                    loader.loadModel(filepath).node()
            else:
                loader.loadModel('phase_3.5' + model + 'mod').node()
            loader.loadModel('phase_' + str(headPhase) + headModel + 'heads').node()
        else:
            if base.config.GetBool('want-new-cogs', 0):
                filepath = 'phase_3.5' + model + 'zero'
                if cogExists(model + 'zero.bam'):
                    loader.unloadModel(filepath)
            else:
                loader.unloadModel('phase_3.5' + model + 'mod')
            loader.unloadModel('phase_' + str(headPhase) + headModel + 'heads')


def cogExists(filePrefix):
    searchPath = DSearchPath()
    if AppRunnerGlobal.appRunner:
        searchPath.appendDirectory(Filename.expandFrom('$TT_3_5_ROOT/phase_3.5'))
    else:
        basePath = os.path.expandvars('$TTMODELS') or './ttmodels'
        searchPath.appendDirectory(Filename.fromOsSpecific(basePath + '/built/phase_3.5'))
    filePrefix = filePrefix.strip('/')
    pfile = Filename(filePrefix)
    found = vfs.resolveFilename(pfile, searchPath)
    if not found:
        return False
    return True


def loadSuitAnims(suit, flag=1):
    if suit in SuitDNA.suitHeadTypes:
        try:
            animList = eval(suit)
        except NameError:
            animList = ()

    else:
        print 'Invalid suit name: ', suit
        return -1
    for anim in animList:
        phase = 'phase_' + str(anim[2])
        filePrefix = ModelDict[bodyType][0]
        animName = filePrefix + anim[1]
        if flag:
            loader.loadModel(animName).node()
        else:
            loader.unloadModel(animName)


def loadDialog(level):
    global SuitDialogArray
    if len(SuitDialogArray) > 0:
        return
    loadPath = 'phase_3.5/audio/dial/'
    SuitDialogFiles = ['COG_VO_grunt',
     'COG_VO_murmur',
     'COG_VO_statement',
     'COG_VO_question']
    for file in SuitDialogFiles:
        SuitDialogArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    SuitDialogArray.append(SuitDialogArray[2])
    SuitDialogArray.append(SuitDialogArray[2])


def loadSkelDialog():
    global SkelSuitDialogArray
    if len(SkelSuitDialogArray) > 0:
        return
    grunt = loader.loadSfx('phase_5/audio/sfx/Skel_COG_VO_grunt.ogg')
    murmur = loader.loadSfx('phase_5/audio/sfx/Skel_COG_VO_murmur.ogg')
    statement = loader.loadSfx('phase_5/audio/sfx/Skel_COG_VO_statement.ogg')
    question = loader.loadSfx('phase_5/audio/sfx/Skel_COG_VO_question.ogg')
    SkelSuitDialogArray = [grunt,
     murmur,
     statement,
     question,
     statement,
     statement]


def unloadDialog(level):
    global SuitDialogArray
    SuitDialogArray = []


def unloadSkelDialog():
    global SkelSuitDialogArray
    SkelSuitDialogArray = []


def attachSuitHead(node, suitName):
    suitIndex = SuitDNA.suitHeadTypes.index(suitName)
    suitDNA = SuitDNA.SuitDNA()
    suitDNA.newSuit(suitName)
    suit = Suit()
    suit.setDNA(suitDNA)
    headParts = suit.getHeadParts()
    head = node.attachNewNode('head')
    for part in headParts:
        copyPart = part.copyTo(head)
        copyPart.setDepthTest(1)
        copyPart.setDepthWrite(1)

    suit.delete()
    suit = None
    p1 = Point3()
    p2 = Point3()
    head.calcTightBounds(p1, p2)
    d = p2 - p1
    biggest = max(d[0], d[2])
    column = suitIndex % SuitDNA.suitsPerDept
    s = (0.2 + column / 100.0) / biggest
    pos = -0.14 + (SuitDNA.suitsPerDept - column - 1) / 135.0
    head.setPosHprScale(0, 0, pos, 180, 0, 0, s, s, s)
    return head


class Suit(Avatar.Avatar):
    healthColors = (
     Vec4(0, 1, 0, 1),
     Vec4(1, 1, 0, 1),
     Vec4(1, 0.5, 0, 1),
     Vec4(1, 0, 0, 1),
     Vec4(0.3, 0.3, 0.3, 1))
    healthGlowColors = (Vec4(0.25, 1, 0.25, 0.5),
     Vec4(1, 1, 0.25, 0.5),
     Vec4(1, 0.5, 0.25, 0.5),
     Vec4(1, 0.25, 0.25, 0.5),
     Vec4(0.3, 0.3, 0.3, 0))
    medallionColors = {'c': Vec4(0.863, 0.776, 0.769, 1.0), 's': Vec4(0.843, 0.745, 0.745, 1.0), 
       'l': Vec4(0.749, 0.776, 0.824, 1.0), 
       'm': Vec4(0.749, 0.769, 0.749, 1.0)}

    def __init__(self, isToon=False):
        try:
            self.Suit_initialized
            return
        except:
            self.Suit_initialized = 1

        Avatar.Avatar.__init__(self)
        self.setFont(ToontownGlobals.getSuitFont())
        self.setPlayerType(NametagGroup.CCSuit)
        self.setPickable(1)
        self.leftHand = None
        self.rightHand = None
        self.shadowJoint = None
        self.nametagJoint = None
        self.headParts = []
        self.healthBar = None
        self.healthCondition = 0
        self.isToon = isToon
        self.isDisguised = 0
        self.isSkeleton = 0
        self.isVirtual = 0
        self.isWaiter = 0
        self.isRental = 0
        self.isSkeleRevive = 0
        self.isCustomCog = 0
        self.particles = []
        self.prop = None
        self.propInSound = None
        self.propOutSound = None
        return

    def delete(self):
        try:
            self.Suit_deleted
        except:
            self.Suit_deleted = 1
            if self.leftHand:
                self.leftHand.removeNode()
                self.leftHand = None
            if self.rightHand:
                self.rightHand.removeNode()
                self.rightHand = None
            if self.shadowJoint:
                self.shadowJoint.removeNode()
                self.shadowJoint = None
            if self.nametagJoint:
                self.nametagJoint.removeNode()
                self.nametagJoint = None
            for part in self.headParts:
                part.removeNode()

            for particle in self.particles:
                particle.cleanup()

            self.headParts = []
            self.removeHealthBar()
            Avatar.Avatar.delete(self)

        return

    def setHeight(self, height):
        Avatar.Avatar.setHeight(self, height)
        self.nametag3d.setPos(0, 0, height + 1.0)

    def getRadius(self):
        return 2

    def setDNAString(self, dnaString):
        self.dna = SuitDNA.SuitDNA()
        self.dna.makeFromNetString(dnaString)
        self.setDNA(self.dna)

    def setDNA(self, dna):
        if self.style:
            pass
        else:
            self.style = dna
            self.generateSuit()
            self.initializeDropShadow()
            self.initializeNametag3d()

    def generateSuit(self):
        dna = self.style
        self.headParts = []
        self.headColor = None
        self.headTexture = None
        self.loseActor = None
        self.isSkeleton = 0
        if dna.name == 'f':
            self.scale = 4.0 / cSize
            self.handColor = SuitDNA.corpPolyColor
            self.generateBody()
            self.generateHead('flunky')
            self.generateHead('glasses')
            self.setHeight(4.88)
        elif dna.name == 'p':
            self.scale = 3.35 / bSize
            self.handColor = SuitDNA.corpPolyColor
            self.generateBody()
            self.generateHead('pencilpusher')
            self.setHeight(5.0)
        elif dna.name == 'ym':
            self.scale = 4.125 / aSize
            self.handColor = SuitDNA.corpPolyColor
            self.generateBody()
            self.generateHead('yesman')
            self.setHeight(5.28)
        elif dna.name == 'mm':
            self.scale = 2.5 / cSize
            self.handColor = SuitDNA.corpPolyColor
            self.generateBody()
            self.generateHead('micromanager')
            self.setHeight(3.25)
        elif dna.name == 'ds':
            self.scale = 4.5 / bSize
            self.handColor = SuitDNA.corpPolyColor
            self.generateBody()
            self.generateHead('beancounter')
            self.setHeight(6.08)
        elif dna.name == 'hh':
            self.scale = 6.5 / aSize
            self.handColor = SuitDNA.corpPolyColor
            self.generateBody()
            self.generateHead('headhunter')
            self.setHeight(7.45)
        elif dna.name == 'cr':
            self.scale = 6.75 / cSize
            self.handColor = VBase4(0.85, 0.55, 0.55, 1.0)
            self.generateBody()
            self.headTexture = 'corporate-raider.jpg'
            self.generateHead('flunky')
            self.setHeight(8.23)
        elif dna.name == 'tbc':
            self.scale = 7.0 / aSize
            self.handColor = VBase4(0.75, 0.95, 0.75, 1.0)
            self.generateBody()
            self.generateHead('bigcheese')
            self.setHeight(9.34)
        elif dna.name == 'bf':
            self.scale = 4.0 / cSize
            self.handColor = SuitDNA.legalPolyColor
            self.generateBody()
            self.headTexture = 'bottom-feeder.jpg'
            self.generateHead('tightwad')
            self.setHeight(4.81)
        elif dna.name == 'b':
            self.scale = 4.375 / bSize
            self.handColor = VBase4(0.95, 0.95, 1.0, 1.0)
            self.generateBody()
            self.headTexture = 'blood-sucker.jpg'
            self.generateHead('movershaker')
            self.setHeight(6.17)
        elif dna.name == 'dt':
            self.scale = 4.25 / aSize
            self.handColor = SuitDNA.legalPolyColor
            self.generateBody()
            self.headTexture = 'double-talker.jpg'
            self.generateHead('twoface')
            self.setHeight(5.63)
        elif dna.name == 'ac':
            self.scale = 4.35 / bSize
            self.handColor = SuitDNA.legalPolyColor
            self.generateBody()
            self.generateHead('ambulancechaser')
            self.setHeight(6.39)
        elif dna.name == 'bs':
            self.scale = 4.5 / aSize
            self.handColor = SuitDNA.legalPolyColor
            self.generateBody()
            self.generateHead('backstabber')
            self.setHeight(6.71)
        elif dna.name == 'sd':
            self.scale = 5.65 / bSize
            self.handColor = VBase4(0.5, 0.8, 0.75, 1.0)
            self.generateBody()
            self.headTexture = 'spin-doctor.jpg'
            self.generateHead('telemarketer')
            self.setHeight(7.9)
        elif dna.name == 'le':
            self.scale = 7.125 / aSize
            self.handColor = VBase4(0.25, 0.25, 0.5, 1.0)
            self.generateBody()
            self.generateHead('legaleagle')
            self.setHeight(8.27)
        elif dna.name == 'bw':
            self.scale = 7.0 / aSize
            self.handColor = SuitDNA.legalPolyColor
            self.generateBody()
            self.generateHead('bigwig')
            self.setHeight(8.69)
        elif dna.name == 'sc':
            self.scale = 3.6 / cSize
            self.handColor = SuitDNA.moneyPolyColor
            self.generateBody()
            self.generateHead('coldcaller')
            self.setHeight(4.77)
        elif dna.name == 'pp':
            self.scale = 3.55 / aSize
            self.handColor = VBase4(1.0, 0.5, 0.6, 1.0)
            self.generateBody()
            self.generateHead('pennypincher')
            self.setHeight(5.26)
        elif dna.name == 'tw':
            self.scale = 4.5 / cSize
            self.handColor = SuitDNA.moneyPolyColor
            self.generateBody()
            self.generateHead('tightwad')
            self.setHeight(5.41)
        elif dna.name == 'bc':
            self.scale = 4.4 / bSize
            self.handColor = SuitDNA.moneyPolyColor
            self.generateBody()
            self.generateHead('beancounter')
            self.setHeight(5.95)
        elif dna.name == 'nc':
            self.scale = 5.25 / aSize
            self.handColor = SuitDNA.moneyPolyColor
            self.generateBody()
            self.generateHead('numbercruncher')
            self.setHeight(7.22)
        elif dna.name == 'mb':
            self.scale = 5.3 / cSize
            self.handColor = SuitDNA.moneyPolyColor
            self.generateBody()
            self.generateHead('moneybags')
            self.setHeight(6.97)
        elif dna.name == 'ls':
            self.scale = 6.5 / bSize
            self.handColor = VBase4(0.5, 0.85, 0.75, 1.0)
            self.generateBody()
            self.generateHead('loanshark')
            self.setHeight(8.58)
        elif dna.name == 'rb':
            self.scale = 7.0 / aSize
            self.handColor = SuitDNA.moneyPolyColor
            self.generateBody()
            self.headTexture = 'robber-baron.jpg'
            self.generateHead('yesman')
            self.setHeight(8.95)
        elif dna.name == 'cc':
            self.scale = 3.5 / cSize
            self.handColor = VBase4(0.55, 0.65, 1.0, 1.0)
            self.headColor = VBase4(0.25, 0.35, 1.0, 1.0)
            self.generateBody()
            self.generateHead('coldcaller')
            self.setHeight(4.63)
        elif dna.name == 'tm':
            self.scale = 3.75 / bSize
            self.handColor = SuitDNA.salesPolyColor
            self.generateBody()
            self.generateHead('telemarketer')
            self.setHeight(5.24)
        elif dna.name == 'nd':
            self.scale = 4.35 / aSize
            self.handColor = SuitDNA.salesPolyColor
            self.generateBody()
            self.headTexture = 'name-dropper.jpg'
            self.generateHead('numbercruncher')
            self.setHeight(5.98)
        elif dna.name == 'gh':
            self.scale = 4.75 / cSize
            self.handColor = SuitDNA.salesPolyColor
            self.generateBody()
            self.generateHead('gladhander')
            self.setHeight(6.4)
        elif dna.name == 'ms':
            self.scale = 4.75 / bSize
            self.handColor = SuitDNA.salesPolyColor
            self.generateBody()
            self.generateHead('movershaker')
            self.setHeight(6.7)
        elif dna.name == 'tf':
            self.scale = 5.25 / aSize
            self.handColor = SuitDNA.salesPolyColor
            self.generateBody()
            self.generateHead('twoface')
            self.setHeight(6.95)
        elif dna.name == 'm':
            self.scale = 5.75 / aSize
            self.handColor = SuitDNA.salesPolyColor
            self.generateBody()
            self.headTexture = 'mingler.jpg'
            self.generateHead('twoface')
            self.setHeight(7.61)
        elif dna.name == 'mh':
            self.scale = 7.0 / aSize
            self.handColor = SuitDNA.salesPolyColor
            self.generateBody()
            self.generateHead('yesman')
            self.setHeight(8.95)
        elif dna.name == 'sf':
            self.scale = 5.75 / aSize
            self.handColor = SuitDNA.salesPolyColor
            self.generateBody()
            self.headTexture = 'mingler.jpg'
            self.generateHead('twoface')
            self.setHeight(7.61)
            self.makeSkeleton()
            self.makeCustomCog(dna.name)
        elif dna.name == 'sm':
            self.scale = 7.0 / aSize
            self.handColor = SuitDNA.salesPolyColor
            self.generateBody()
            self.generateHead('yesman', 'phase_14.5/models/char/stormish-head')
            self.generateHead('warpighelm', 'phase_14.5/models/char/stormish-head')
            self.setHeight(9.2)
            self.makeCustomCog(dna.name)
        elif dna.name == 'mdr':
            self.scale = 8.125 / aSize
            self.handColor = VBase4(1, 0, 0, 0.5)
            self.generateBody()
            self.generateHead('mole_cog', 'phase_12/models/bossbotHQ/mole_cog')
            self.setHeight(9.5)
        self.setName(SuitBattleGlobals.SuitAttributes[dna.name]['name'])
        self.getGeomNode().setScale(self.scale)
        self.generateHealthBar()
        self.generateCorporateMedallion()
        self.setBlend(frameBlend=base.settings.getBool('game', 'smooth-animations', False))
        return

    def generateBody(self):
        animDict = self.generateAnimDict()
        filePrefix, bodyPhase = ModelDict[self.style.body]
        if base.config.GetBool('want-new-cogs', 0):
            if cogExists(filePrefix + 'zero.bam'):
                self.loadModel('phase_3.5' + filePrefix + 'zero')
            else:
                self.loadModel('phase_3.5' + filePrefix + 'mod')
        else:
            self.loadModel('phase_3.5' + filePrefix + 'mod')
        self.loadAnims(animDict)
        self.setSuitClothes()

    def generateAnimDict(self):
        animDict = {}
        filePrefix, bodyPhase = ModelDict[self.style.body]
        for anim in AllSuits:
            animDict[anim[0]] = 'phase_' + str(bodyPhase) + filePrefix + anim[1]

        for anim in AllSuitsMinigame:
            animDict[anim[0]] = 'phase_4' + filePrefix + anim[1]

        for anim in AllSuitsTutorialBattle:
            filePrefix, bodyPhase = TutorialModelDict[self.style.body]
            animDict[anim[0]] = 'phase_' + str(bodyPhase) + filePrefix + anim[1]

        for anim in AllSuitsBattle:
            animDict[anim[0]] = 'phase_5' + filePrefix + anim[1]

        if not base.config.GetBool('want-new-cogs', 0):
            if self.style.body == 'a':
                animDict['neutral'] = 'phase_4/models/char/suitA-neutral'
                for anim in SuitsCEOBattle:
                    animDict[anim[0]] = 'phase_12/models/char/suitA-' + anim[1]

            elif self.style.body == 'b':
                animDict['neutral'] = 'phase_4/models/char/suitB-neutral'
                for anim in SuitsCEOBattle:
                    animDict[anim[0]] = 'phase_12/models/char/suitB-' + anim[1]

            elif self.style.body == 'c':
                animDict['neutral'] = 'phase_3.5/models/char/suitC-neutral'
                for anim in SuitsCEOBattle:
                    animDict[anim[0]] = 'phase_12/models/char/suitC-' + anim[1]

        if self.isToon:
            style2Types = {'a': SuitDNA.suitATypes, 'b': SuitDNA.suitBTypes, 
               'c': SuitDNA.suitCTypes}
            fellowSuits = style2Types.get(self.style.body)
            for suit in fellowSuits:
                try:
                    animList = globals()[suit]
                except KeyError:
                    animList = ()

                for anim in animList:
                    phase = 'phase_' + str(anim[2])
                    animDict[anim[0]] = phase + filePrefix + anim[1]

        else:
            try:
                animList = eval(self.style.name)
            except NameError:
                animList = ()

            for anim in animList:
                phase = 'phase_' + str(anim[2])
                animDict[anim[0]] = phase + filePrefix + anim[1]

        return animDict

    def initializeBodyCollisions(self, collIdStr):
        Avatar.Avatar.initializeBodyCollisions(self, collIdStr)
        if not self.ghostMode:
            self.collNode.setCollideMask(self.collNode.getIntoCollideMask() | ToontownGlobals.PieBitmask)

    def setSuitClothes(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        dept = self.style.dept
        phase = 3.5

        def __doItTheOldWay__():
            if self.style.name in SuitDNA.extraSuitsClothes.keys():
                clothingPaths = SuitDNA.extraSuitsClothes.get(self.style.name)
                torsoTex = loader.loadTexture(clothingPaths[0])
                legTex = loader.loadTexture(clothingPaths[1])
                armTex = loader.loadTexture(clothingPaths[2])
            else:
                torsoTex = loader.loadTexture('phase_%s/maps/%s_blazer.jpg' % (phase, dept))
                legTex = loader.loadTexture('phase_%s/maps/%s_leg.jpg' % (phase, dept))
                armTex = loader.loadTexture('phase_%s/maps/%s_sleeve.jpg' % (phase, dept))
            torsoTex.setMinfilter(Texture.FTLinearMipmapLinear)
            torsoTex.setMagfilter(Texture.FTLinear)
            legTex.setMinfilter(Texture.FTLinearMipmapLinear)
            legTex.setMagfilter(Texture.FTLinear)
            armTex.setMinfilter(Texture.FTLinearMipmapLinear)
            armTex.setMagfilter(Texture.FTLinear)
            modelRoot.find('**/torso').setTexture(torsoTex, 1)
            modelRoot.find('**/arms').setTexture(armTex, 1)
            modelRoot.find('**/legs').setTexture(legTex, 1)
            modelRoot.find('**/hands').setColor(self.handColor)
            self.leftHand = self.find('**/joint_Lhold')
            self.rightHand = self.find('**/joint_Rhold')
            self.shadowJoint = self.find('**/joint_shadow')
            self.nametagJoint = self.find('**/joint_nameTag')

        if base.config.GetBool('want-new-cogs', 0):
            if dept == 'c':
                texType = 'bossbot'
            elif dept == 'm':
                texType = 'cashbot'
            elif dept == 'l':
                texType = 'lawbot'
            elif dept == 's':
                texType = 'sellbot'
            if self.find('**/body').isEmpty():
                __doItTheOldWay__()
            else:
                filepath = 'phase_3.5/maps/tt_t_ene_' + texType + '.jpg'
                if cogExists('/maps/tt_t_ene_' + texType + '.jpg'):
                    bodyTex = loader.loadTexture(filepath)
                    self.find('**/body').setTexture(bodyTex, 1)
                self.leftHand = self.find('**/def_joint_left_hold')
                self.rightHand = self.find('**/def_joint_right_hold')
                self.shadowJoint = self.find('**/def_shadow')
                self.nametagJoint = self.find('**/def_nameTag')
        else:
            __doItTheOldWay__()

    def generateHead(self, headType, modelOverride=None):
        if base.config.GetBool('want-new-cogs', 0):
            filePrefix, phase = HeadModelDict[self.style.body]
        else:
            filePrefix, phase = ModelDict[self.style.body]
        if modelOverride:
            headModel = loader.loadModel(modelOverride)
        else:
            headModel = loader.loadModel('phase_' + str(phase) + filePrefix + 'heads')
        headReferences = headModel.findAllMatches('**/' + headType)
        for i in xrange(0, headReferences.getNumPaths()):
            if base.config.GetBool('want-new-cogs', 0):
                headPart = self.instance(headReferences.getPath(i), 'modelRoot', 'to_head')
                if not headPart:
                    headPart = self.instance(headReferences.getPath(i), 'modelRoot', 'joint_head')
            else:
                headPart = self.instance(headReferences.getPath(i), 'modelRoot', 'joint_head')
            if self.headTexture:
                headTex = loader.loadTexture('phase_' + str(phase) + '/maps/' + self.headTexture)
                headTex.setMinfilter(Texture.FTLinearMipmapLinear)
                headTex.setMagfilter(Texture.FTLinear)
                headPart.setTexture(headTex, 1)
            if self.headColor:
                headPart.setColor(self.headColor)
            if headType in extraSpecialHeads:
                self.handleSpecialHead(headType, headPart)
            self.headParts.append(headPart)

        headModel.removeNode()

    def handleSpecialHead(self, headType, headPart):
        if headType == 'mole_cog':
            headPart.setH(180)
            headPart.setZ(-0.5)
            headPart.setScale(0.69)

    def generateCorporateTie(self, modelPath=None):
        if not modelPath:
            modelPath = self
        dept = self.style.dept
        tie = modelPath.find('**/tie')
        if tie.isEmpty():
            self.notify.warning('skelecog has no tie model!!!')
            return
        if dept == 'c':
            tieTex = loader.loadTexture('phase_5/maps/cog_robot_tie_boss.jpg')
        elif dept == 's':
            tieTex = loader.loadTexture('phase_5/maps/cog_robot_tie_sales.jpg')
        elif dept == 'l':
            tieTex = loader.loadTexture('phase_5/maps/cog_robot_tie_legal.jpg')
        elif dept == 'm':
            tieTex = loader.loadTexture('phase_5/maps/cog_robot_tie_money.jpg')
        tieTex.setMinfilter(Texture.FTLinearMipmapLinear)
        tieTex.setMagfilter(Texture.FTLinear)
        tie.setTexture(tieTex, 1)

    def generateCorporateMedallion(self):
        icons = loader.loadModel('phase_3/models/gui/cog_icons')
        dept = self.style.dept
        if base.config.GetBool('want-new-cogs', 0):
            chestNull = self.find('**/def_joint_attachMeter')
            if chestNull.isEmpty():
                chestNull = self.find('**/joint_attachMeter')
        else:
            chestNull = self.find('**/joint_attachMeter')
        if dept == 'c':
            self.corpMedallion = icons.find('**/CorpIcon').copyTo(chestNull)
        elif dept == 's':
            self.corpMedallion = icons.find('**/SalesIcon').copyTo(chestNull)
        elif dept == 'l':
            self.corpMedallion = icons.find('**/LegalIcon').copyTo(chestNull)
        elif dept == 'm':
            self.corpMedallion = icons.find('**/MoneyIcon').copyTo(chestNull)
        self.corpMedallion.setPosHprScale(0.02, 0.05, 0.04, 180.0, 0.0, 0.0, 0.51, 0.51, 0.51)
        self.corpMedallion.setColor(self.medallionColors[dept])
        icons.removeNode()

    def generateHealthBar(self):
        self.removeHealthBar()
        model = loader.loadModel('phase_3.5/models/gui/matching_game_gui')
        button = model.find('**/minnieCircle')
        button.setScale(3.0)
        button.setH(180.0)
        button.setColor(self.healthColors[0])
        if base.config.GetBool('want-new-cogs', 0):
            chestNull = self.find('**/def_joint_attachMeter')
            if chestNull.isEmpty():
                chestNull = self.find('**/joint_attachMeter')
        else:
            chestNull = self.find('**/joint_attachMeter')
        button.reparentTo(chestNull)
        self.healthBar = button
        glow = BattleProps.globalPropPool.getProp('glow')
        glow.reparentTo(self.healthBar)
        glow.setScale(0.28)
        glow.setPos(-0.005, 0.01, 0.015)
        glow.setColor(self.healthGlowColors[0])
        button.flattenLight()
        self.healthBarGlow = glow
        self.healthBar.hide()
        self.healthCondition = 0

    def reseatHealthBarForSkele(self):
        self.healthBar.setPos(0.0, 0.1, 0.0)

    def updateHealthBar(self, hp, forceUpdate=0, hpIsAbsolute=False):
        if hpIsAbsolute:
            self.currHP = min(hp, self.maxHP)
        else:
            if hp > self.currHP:
                hp = self.currHP
            self.currHP -= hp
        health = float(self.currHP) / float(self.maxHP)
        if health > 0.95:
            condition = 0
        elif health > 0.7:
            condition = 1
        elif health > 0.3:
            condition = 2
        elif health > 0.05:
            condition = 3
        elif health > 0.0:
            condition = 4
        else:
            condition = 5
        if self.healthCondition != condition or forceUpdate:
            if condition == 4:
                taskMgr.remove(self.uniqueName('blink-task'))
                blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.75), Task(self.__blinkGray), Task.pause(0.1))
                taskMgr.add(blinkTask, self.uniqueName('blink-task'))
            elif condition == 5:
                if self.healthCondition == 4:
                    taskMgr.remove(self.uniqueName('blink-task'))
                blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.25), Task(self.__blinkGray), Task.pause(0.1))
                taskMgr.add(blinkTask, self.uniqueName('blink-task'))
            else:
                self.healthBar.setColor(self.healthColors[condition], 1)
                self.healthBarGlow.setColor(self.healthGlowColors[condition], 1)
                taskMgr.remove(self.uniqueName('blink-task'))
            self.healthCondition = condition

    def uniqueName(self, name):
        return name + ('-{0}').format(id(self))

    def __blinkRed(self, task):
        self.healthBar.setColor(self.healthColors[3], 1)
        self.healthBarGlow.setColor(self.healthGlowColors[3], 1)
        if self.healthCondition == 5:
            self.healthBar.setScale(1.17)
        return Task.done

    def __blinkGray(self, task):
        if not self.healthBar:
            return
        self.healthBar.setColor(self.healthColors[4], 1)
        self.healthBarGlow.setColor(self.healthGlowColors[4], 1)
        if self.healthCondition == 5:
            self.healthBar.setScale(1.0)
        return Task.done

    def removeHealthBar(self):
        if self.healthBar:
            self.healthBar.removeNode()
            self.healthBar = None
        if self.healthCondition == 4 or self.healthCondition == 5:
            taskMgr.remove(self.uniqueName('blink-task'))
        self.healthCondition = 0
        return

    def getLoseActor(self):
        if base.config.GetBool('want-new-cogs', 0):
            if self.find('**/body'):
                return self
        if self.loseActor == None:
            if self.isSkeleton:
                loseModel = 'phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-lose-mod'
                filePrefix, phase = TutorialModelDict[self.style.body]
                loseAnim = 'phase_' + str(phase) + filePrefix + 'lose'
                self.loseActor = Actor.Actor(loseModel, {'lose': loseAnim})
                if self.isCustomCog:
                    self.handleCustomCogLoseActor(True)
                self.generateCorporateTie(self.loseActor)
            else:
                filePrefix, phase = TutorialModelDict[self.style.body]
                loseModel = 'phase_' + str(phase) + filePrefix + 'lose-mod'
                loseAnim = 'phase_' + str(phase) + filePrefix + 'lose'
                self.loseActor = Actor.Actor(loseModel, {'lose': loseAnim})
                loseNeck = self.loseActor.find('**/joint_head')
                for part in self.headParts:
                    part.instanceTo(loseNeck)

                if self.isWaiter:
                    self.makeWaiter(self.loseActor)
                elif self.isRental:
                    self.makeRentalSuit(self.style.dept, self.loseActor)
                elif self.isCustomCog:
                    self.handleCustomCogLoseActor(False)
                else:
                    self.setSuitClothes(self.loseActor)
        if self.isVirtual:
            actorNode = self.loseActor.find('**/__Actor_modelRoot')
            actorCollection = actorNode.findAllMatches('*')
            parts = ()
            for thingIndex in range(0, actorCollection.getNumPaths()):
                thing = actorCollection[thingIndex]
                if thing.getName() not in ('joint_attachMeter', 'joint_nameTag', 'def_nameTag'):
                    thing.setColorScale(1.0, 0.0, 0.0, 1.0)
                    thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                    thing.setDepthWrite(False)
                    thing.setBin('fixed', 1)

            self.loseActor.find('**/joint_shadow').hide()
        self.loseActor.setScale(self.scale)
        self.loseActor.setPos(self.getPos())
        self.loseActor.setHpr(self.getHpr())
        shadowJoint = self.loseActor.find('**/joint_shadow')
        dropShadow = loader.loadModel('phase_3/models/props/drop_shadow')
        dropShadow.setScale(0.45)
        dropShadow.setColor(0.0, 0.0, 0.0, 0.5)
        dropShadow.reparentTo(shadowJoint)
        self.loseActor.setBlend(frameBlend=base.settings.getBool('game', 'smooth-animations', False))
        return self.loseActor

    def cleanupLoseActor(self):
        self.notify.debug('cleanupLoseActor()')
        if self.loseActor != None:
            self.notify.debug('cleanupLoseActor() - got one')
            self.loseActor.cleanup()
        self.loseActor = None
        return

    def handleCustomCogLoseActor(self, isSkeleton):
        if self.style.name == 'sf':
            self.loseActor.getGeomNode().setColor(1, 0.29, 0.6, 1)
            cigar = self.find('**/' + self.style.name + '_cigar')
            if cigar:
                cigar.reparentTo(self.loseActor.find('**/joint_head'))
            if self.particles:
                self.particles[0].disable()
                self.particles[0].cleanup()
                self.particles = []
        elif self.style.name == 'sm' and isSkeleton:
            self.loseActor.getGeomNode().setColor(0.45, 0.65, 1, 1)
            self.loseActor.find('**/tie').setColorScale(0.45, 0.65, 1, 1)
            helmet = self.find('**/' + self.style.name + '_helmet')
            if helmet:
                helmet.reparentTo(self.loseActor.find('**/joint_head'))

    def makeSkeleton(self):
        model = 'phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-zero'
        anims = self.generateAnimDict()
        anim = self.getCurrentAnim()
        self.removePart('modelRoot')
        self.loadModel(model)
        self.loadAnims(anims)
        if self.isCustomCog:
            self.handleCustomCogSkeleton()
        self.getGeomNode().setScale(self.scale * 1.0173)
        self.generateHealthBar()
        self.generateCorporateTie()
        self.setHeight(self.height)
        parts = self.findAllMatches('**/pPlane*')
        for partNum in xrange(0, parts.getNumPaths()):
            bb = parts.getPath(partNum)
            bb.setTwoSided(1)

        self.setName(TTLocalizer.Skeleton)
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': self._name, 'dept': self.getStyleDept(), 
           'level': self.getActualLevel()}
        self.setDisplayName(nameInfo)
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagNull = self.find('**/joint_nameTag')
        self.loop(anim)
        self.isSkeleton = 1
        self.setBlend(frameBlend=base.settings.getBool('game', 'smooth-animations', False))

    def handleCustomCogSkeleton(self):
        if self.style.name == 'sm':
            self.getGeomNode().setColor(0.45, 0.65, 1, 1)
            self.find('**/tie').setColorScale(0.45, 0.65, 1, 1)
            helmet = loader.loadModel('phase_14.5/models/char/stormish-head').find('**/warpighelm')
            helmet.setName(self.style.name + '_helmet')
            helmet.reparentTo(self.find('**/to_head'))
            helmet.setScale(0.5)
            helmet.setPos(0, 0.25, 0.5)
            helmet.setColor(1, 1, 1, 1)

    def makeVirtual(self):
        actorNode = self.find('**/__Actor_modelRoot')
        actorCollection = actorNode.findAllMatches('*')
        for thingIndex in range(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            if thing.getName() not in ('joint_attachMeter', 'joint_nameTag', 'def_nameTag'):
                thing.setColorScale(1.0, 0.0, 0.0, 1.0)
                thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                thing.setDepthWrite(False)
                thing.setBin('fixed', 1)

        self.find('**/joint_shadow').hide()
        self.isVirtual = True

    def getVirtual(self):
        return self.isVirtual

    def makeWaiter(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isWaiter = 1
        dept = self.style.dept
        torsoTex = loader.loadTexture('phase_3.5/maps/waiter_%s_blazer.jpg' % dept)
        torsoTex.setMinfilter(Texture.FTLinearMipmapLinear)
        torsoTex.setMagfilter(Texture.FTLinear)
        legTex = loader.loadTexture('phase_3.5/maps/waiter_leg.jpg')
        legTex.setMinfilter(Texture.FTLinearMipmapLinear)
        legTex.setMagfilter(Texture.FTLinear)
        armTex = loader.loadTexture('phase_3.5/maps/waiter_sleeve.jpg')
        armTex.setMinfilter(Texture.FTLinearMipmapLinear)
        armTex.setMagfilter(Texture.FTLinear)
        modelRoot.find('**/torso').setTexture(torsoTex, 1)
        modelRoot.find('**/arms').setTexture(armTex, 1)
        modelRoot.find('**/legs').setTexture(legTex, 1)

    def makeRentalSuit(self, suitType, modelRoot=None):
        if not modelRoot:
            modelRoot = self.getGeomNode()
        suitName = ToontownGlobals.Dept2Dept.get(suitType).lower()
        if suitName:
            torsoTex = loader.loadTexture('phase_3.5/maps/tt_t_ene_%sRental_blazer.jpg' % suitName)
            legTex = loader.loadTexture('phase_3.5/maps/tt_t_ene_%sRental_leg.jpg' % suitName)
            armTex = loader.loadTexture('phase_3.5/maps/tt_t_ene_%sRental_sleeve.jpg' % suitName)
            handTex = loader.loadTexture('phase_3.5/maps/tt_t_ene_Rental_hand.jpg')
        else:
            self.notify.warning('No rental suit for cog type %s' % suitType)
            return
        self.isRental = 1
        modelRoot.find('**/torso').setTexture(torsoTex, 1)
        modelRoot.find('**/arms').setTexture(armTex, 1)
        modelRoot.find('**/legs').setTexture(legTex, 1)
        modelRoot.find('**/hands').setTexture(handTex, 1)

    def makeSkeleRevive(self):
        self.isSkeleRevive = 1

    def makeCustomCog(self, suitName):
        if suitName == 'sf':
            self.getGeomNode().setColor(1, 0.29, 0.6, 1)
            cigar = loader.loadModel('phase_5/models/props/cigar')
            cigar.setName(suitName + '_cigar')
            cigar.reparentTo(self.find('**/to_head'))
            cigar.setPosHprScale(-0.4, 1, 0.15, 26.57, 0, 254.05, 8, 8, 8)
            base.enableParticles()
            smoke = BattleParticles.loadParticleFile('cigar.ptf')
            smoke.start(cigar)
            smoke.setPosHprScale(0.02, 0.01, 0.01, 0.0, 0.0, 110.0, 0.02, 0.02, 0.02)
            self.particles.append(smoke)
        self.isCustomCog = 1

    def getHeadParts(self):
        return self.headParts

    def getRightHand(self):
        return self.rightHand

    def getLeftHand(self):
        return self.leftHand

    def getShadowJoint(self):
        return self.shadowJoint

    def getNametagJoints(self):
        return []

    def getDialogueArray(self):
        if self.isSkeleton:
            loadSkelDialog()
            return SkelSuitDialogArray
        else:
            return SuitDialogArray

    def getStyleDept(self):
        if hasattr(self, 'dna') and self.dna:
            return SuitDNA.getDeptFullname(self.dna.dept)
        else:
            self.notify.error('called getStyleDept() before dna was set!')
            return 'unknown'

    def getActualLevel(self):
        if hasattr(self, 'dna'):
            if hasattr(self, 'level'):
                lv = SuitBattleGlobals.getActualFromRelativeLevel(self.getStyleName(), self.level)
                return ToontownGlobals.SuitLevels[lv]
            lv = SuitBattleGlobals.getActualFromRelativeLevel(self.getStyleName(), SuitDNA.suitDepts.index(SuitDNA.getSuitDept(self.dna.name)))
            return ToontownGlobals.SuitLevels[lv]
        else:
            self.notify.warning('called getActualLevel with no DNA, returning 1 for level')
            return 1

    def getStyleName(self):
        if hasattr(self, 'dna') and self.dna:
            return self.dna.name
        else:
            self.notify.error('called getStyleName() before dna was set!')
            return 'unknown'

    def attachPropeller(self):
        if self.prop == None:
            self.prop = BattleProps.globalPropPool.getProp('propeller')
        if self.propInSound == None:
            self.propInSound = base.loader.loadSfx('phase_5/audio/sfx/ENC_propeller_in.ogg')
        if self.propOutSound == None:
            self.propOutSound = base.loader.loadSfx('phase_5/audio/sfx/ENC_propeller_out.ogg')
        if base.config.GetBool('want-new-cogs', 0):
            head = self.find('**/to_head')
            if head.isEmpty():
                head = self.find('**/joint_head')
        else:
            head = self.find('**/joint_head')
        self.prop.reparentTo(head)
        return

    def detachPropeller(self):
        if self.prop:
            self.prop.cleanup()
            self.prop.removeNode()
            self.prop = None
        if self.propInSound:
            self.propInSound = None
        if self.propOutSound:
            self.propOutSound = None
        return

    def beginSupaFlyMove(self, pos, moveIn, trackName):
        skyPos = Point3(pos)
        if moveIn:
            skyPos.setZ(pos.getZ() + SuitTimings.fromSky * ToontownGlobals.SuitWalkSpeed)
        else:
            skyPos.setZ(pos.getZ() + SuitTimings.toSky * ToontownGlobals.SuitWalkSpeed)
        groundF = 28
        dur = self.getDuration('landing')
        fr = self.getFrameRate('landing')
        animTimeInAir = groundF / fr
        impactLength = dur - animTimeInAir
        timeTillLanding = SuitTimings.fromSky - impactLength
        waitTime = timeTillLanding - animTimeInAir
        if self.prop == None:
            self.prop = BattleProps.globalPropPool.getProp('propeller')
        propDur = self.prop.getDuration('propeller')
        lastSpinFrame = 8
        fr = self.prop.getFrameRate('propeller')
        spinTime = lastSpinFrame / fr
        openTime = (lastSpinFrame + 1) / fr
        if moveIn:
            lerpPosTrack = Sequence(self.posInterval(timeTillLanding, pos, startPos=skyPos), Wait(impactLength))
            shadowScale = self.dropShadow.getScale()
            shadowTrack = Sequence(Func(self.dropShadow.reparentTo, render), Func(self.dropShadow.setPos, pos), self.dropShadow.scaleInterval(timeTillLanding, self.scale, startScale=Vec3(0.01, 0.01, 1.0)), Func(self.dropShadow.reparentTo, self.getShadowJoint()), Func(self.dropShadow.setPos, 0, 0, 0), Func(self.dropShadow.setScale, shadowScale))
            fadeInTrack = Sequence(Func(self.setTransparency, 1), self.colorScaleInterval(1, colorScale=VBase4(1, 1, 1, 1), startColorScale=VBase4(1, 1, 1, 0)), Func(self.clearColorScale), Func(self.clearTransparency))
            animTrack = Sequence(Func(self.pose, 'landing', 0), Wait(waitTime), ActorInterval(self, 'landing', duration=dur), Func(self.loop, 'walk'))
            self.attachPropeller()
            propTrack = Parallel(SoundInterval(self.propInSound, duration=waitTime + dur, node=self), Sequence(ActorInterval(self.prop, 'propeller', constrainedLoop=1, duration=waitTime + spinTime, startTime=0.0, endTime=spinTime), ActorInterval(self.prop, 'propeller', duration=propDur - openTime, startTime=openTime), Func(self.detachPropeller)))
            return Parallel(lerpPosTrack, shadowTrack, fadeInTrack, animTrack, propTrack, name=trackName)
        else:
            lerpPosTrack = Sequence(Wait(impactLength), LerpPosInterval(self, timeTillLanding, skyPos, startPos=pos))
            shadowTrack = Sequence(Func(self.dropShadow.reparentTo, render), Func(self.dropShadow.setPos, pos), self.dropShadow.scaleInterval(timeTillLanding, Vec3(0.01, 0.01, 1.0), startScale=self.scale), Func(self.dropShadow.reparentTo, self.getShadowJoint()), Func(self.dropShadow.setPos, 0, 0, 0))
            fadeOutTrack = Sequence(Func(self.setTransparency, 1), self.colorScaleInterval(1, colorScale=VBase4(1, 1, 1, 0), startColorScale=VBase4(1, 1, 1, 1)), Func(self.clearColorScale), Func(self.clearTransparency), Func(self.reparentTo, hidden))
            actInt = ActorInterval(self, 'landing', loop=0, startTime=dur, endTime=0.0)
            self.attachPropeller()
            self.prop.hide()
            propTrack = Parallel(SoundInterval(self.propOutSound, duration=waitTime + dur, node=self), Sequence(Func(self.prop.show), ActorInterval(self.prop, 'propeller', endTime=openTime, startTime=propDur), ActorInterval(self.prop, 'propeller', constrainedLoop=1, duration=propDur - openTime, startTime=spinTime, endTime=0.0), Func(self.detachPropeller)))
            return Parallel(ParallelEndTogether(lerpPosTrack, shadowTrack, fadeOutTrack), actInt, propTrack, name=trackName)
            return