from direct.actor import Actor
from otp.avatar import Avatar
import SuitDNA
from toontown.toonbase import ToontownGlobals
from panda3d.core import *
from otp.nametag.NametagGroup import NametagGroup
from toontown.battle import SuitBattleGlobals
from direct.task.Task import Task
from toontown.battle import BattleProps
from toontown.toonbase import TTLocalizer
from panda3d.core import VirtualFileMountHTTP, VirtualFileSystem, Filename, DSearchPath
from direct.showbase import AppRunnerGlobal
import string, os, time
aSize = 6.06
bSize = 5.29
cSize = 4.14
SuitDialogArray = []
SkelSuitDialogArray = []
AllSuits = (
 ('walk', 'walk'), ('run', 'walk'), ('neutral', 'neutral'), ('awalk', 'awalk'))
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
 ('glower', 'glower'),
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
m1 = (('pickpocket', 'pickpocket', 5),
 ('rubber-stamp', 'rubber-stamp', 5),
 ('shredder', 'shredder', 3.5),
 ('magic2', 'magic2', 5),
 ('glower', 'glower', 5))
m2 = (('effort', 'effort', 5),
 ('throw-paper', 'throw-paper', 5),
 ('throw-object', 'throw-object', 5),
 ('magic3', 'magic3', 5),
 ('pencil-sharpener', 'pencil-sharpener', 5),
 ('magic1', 'magic1', 5))
m3 = (('rubber-stamp', 'rubber-stamp', 5),
 ('speak', 'speak', 5),
 ('pickpocket', 'pickpocket', 5),
 ('finger-wag', 'fingerwag', 5),
 ('throw-paper', 'throw-paper', 5))
m4 = (('magic1', 'magic1', 5), ('magic2', 'magic2', 5), ('phone', 'phone', 5), ('magic3', 'magic3', 5))
m5 = (('magic1', 'magic1', 5), ('magic3', 'magic3', 5), ('throw-paper', 'throw-paper', 5), ('finger-wag', 'fingerwag', 5))
m6 = (('magic2', 'magic2', 5),
 ('effort', 'effort', 5),
 ('pencil-sharpener', 'pencil-sharpener', 5),
 ('magic3', 'magic3', 5),
 ('hold-eraser', 'hold-eraser', 5),
 ('throw-paper', 'throw-paper', 5))
m7 = (('pickpocket', 'pickpocket', 5), ('throw-paper', 'throw-paper', 3.5), ('glower', 'glower', 5))
m8 = (('finger-wag', 'fingerwag', 5),
 ('magic1', 'magic1', 5),
 ('magic3', 'magic3', 5),
 ('throw-object', 'throw-object', 5),
 ('throw-paper', 'throw-paper', 5))
if not config.GetBool('want-new-cogs', 0):
    ModelDict = {'a': ('/models/char/suitA-', 4), 'b': ('/models/char/suitB-', 4), 'c': ('/models/char/suitC-', 3.5)}
    TutorialModelDict = {'a': ('/models/char/suitA-', 4), 'b': ('/models/char/suitB-', 4), 
       'c': ('/models/char/suitC-', 3.5)}
else:
    ModelDict = {'a': ('/models/char/tt_a_ene_cga_', 4), 'b': ('/models/char/tt_a_ene_cgb_', 4), 
       'c': ('/models/char/tt_a_ene_cgc_', 3.5)}
    TutorialModelDict = {'a': ('/models/char/tt_a_ene_cga_', 4), 'b': ('/models/char/tt_a_ene_cgb_', 4), 
       'c': ('/models/char/tt_a_ene_cgc_', 3.5)}
HeadModelDict = {'a': ('/models/char/suitA-', 4), 'b': ('/models/char/suitB-', 4), 'c': ('/models/char/suitC-', 3.5)}

def loadTutorialSuit():
    loader.loadModel('phase_3.5/models/char/suitC-mod')
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
        if config.GetBool('want-new-cogs', 0):
            headModel, headPhase = HeadModelDict[key]
        else:
            headModel, headPhase = ModelDict[key]
        if flag:
            if config.GetBool('want-new-cogs', 0):
                filepath = 'phase_3.5' + model + 'zero'
                if cogExists(model + 'zero'):
                    loader.loadModel(filepath)
            else:
                loader.loadModel('phase_3.5' + model + 'mod')
            loader.loadModel('phase_' + str(headPhase) + headModel + 'heads')
        else:
            if config.GetBool('want-new-cogs', 0):
                filepath = 'phase_3.5' + model + 'zero'
                if cogExists(model + 'zero'):
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
            animList = locals()[suit]
        except KeyError:
            animList = ()

    else:
        print 'Invalid suit name: ', suit
        return -1
    for anim in animList:
        phase = 'phase_' + str(anim[2])
        filePrefix = ModelDict[bodyType][0]
        animName = filePrefix + anim[1]
        if flag:
            loader.loadModel(animName)
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

    SuitDialogArray.append(SuitDialogArray[0])
    SuitDialogArray.append(SuitDialogArray[1])


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
       'm': Vec4(0.749, 0.769, 0.749, 1.0), 
       'g': Vec4(0.957, 0.76, 0.718, 1.0)}

    def __init__(self):
        try:
            self.Suit_initialized
            return
        except:
            self.Suit_initialized = 1

        Avatar.Avatar.__init__(self)
        self.setFont(ToontownGlobals.getSuitFont())
        self.setSpeechFont(ToontownGlobals.getSuitFont())
        self.setPlayerType(NametagGroup.CCSuit)
        self.setPickable(1)
        self.setBlend(frameBlend=config.GetBool('interpolate-animations', True))
        self.leftHand = None
        self.rightHand = None
        self.shadowJoint = None
        self.nametagJoint = None
        self.headParts = []
        self.healthBar = None
        self.healthCondition = 0
        self.isDisguised = 0
        self.isWaiter = 0
        self.isRental = 0
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
        self.isVirtual = 0
        scale = SuitBattleGlobals.SuitSizes[dna.name]
        if dna.name == 'f':
            self.scale = scale / cSize
            self.handColor = SuitDNA.corpPolyColor
            self.generateBody()
            self.generateHead('flunky')
            self.generateHead('glasses')
            self.setHeight(4.88)
        else:
            if dna.name == 'p':
                self.scale = scale / bSize
                self.handColor = SuitDNA.corpPolyColor
                self.generateBody()
                self.generateHead('pencilpusher')
                self.setHeight(5.0)
            else:
                if dna.name == 'ym':
                    self.scale = scale / aSize
                    self.handColor = SuitDNA.corpPolyColor
                    self.generateBody()
                    self.generateHead('yesman')
                    self.setHeight(5.28)
                else:
                    if dna.name == 'mm':
                        self.scale = scale / cSize
                        self.handColor = SuitDNA.corpPolyColor
                        self.generateBody()
                        self.generateHead('micromanager')
                        self.setHeight(3.25)
                    else:
                        if dna.name == 'ds':
                            self.scale = scale / bSize
                            self.handColor = SuitDNA.corpPolyColor
                            self.generateBody()
                            self.generateHead('beancounter')
                            self.setHeight(6.08)
                        else:
                            if dna.name == 'hh':
                                self.scale = scale / aSize
                                self.handColor = SuitDNA.corpPolyColor
                                self.generateBody()
                                self.generateHead('headhunter')
                                self.setHeight(7.45)
                            else:
                                if dna.name == 'cr':
                                    self.scale = scale / cSize
                                    self.handColor = VBase4(0.85, 0.55, 0.55, 1.0)
                                    self.generateBody()
                                    self.headTexture = 'corporate-raider.jpg'
                                    self.generateHead('flunky')
                                    self.setHeight(8.23)
                                else:
                                    if dna.name == 'tbc':
                                        self.scale = scale / aSize
                                        self.handColor = VBase4(0.75, 0.95, 0.75, 1.0)
                                        self.generateBody()
                                        self.generateHead('bigcheese')
                                        self.setHeight(9.34)
                                    else:
                                        if dna.name == 'bf':
                                            self.scale = scale / cSize
                                            self.handColor = SuitDNA.legalPolyColor
                                            self.generateBody()
                                            self.headTexture = 'bottom-feeder.jpg'
                                            self.generateHead('tightwad')
                                            self.setHeight(4.81)
                                        else:
                                            if dna.name == 'b':
                                                self.scale = scale / bSize
                                                self.handColor = VBase4(0.95, 0.95, 1.0, 1.0)
                                                self.generateBody()
                                                self.headTexture = 'blood-sucker.jpg'
                                                self.generateHead('movershaker')
                                                self.setHeight(6.17)
                                            else:
                                                if dna.name == 'dt':
                                                    self.scale = scale / aSize
                                                    self.handColor = SuitDNA.legalPolyColor
                                                    self.generateBody()
                                                    self.headTexture = 'double-talker.jpg'
                                                    self.generateHead('twoface')
                                                    self.setHeight(5.63)
                                                else:
                                                    if dna.name == 'ac':
                                                        self.scale = scale / bSize
                                                        self.handColor = SuitDNA.legalPolyColor
                                                        self.generateBody()
                                                        self.generateHead('ambulancechaser')
                                                        self.setHeight(6.39)
                                                    else:
                                                        if dna.name == 'bs':
                                                            self.scale = scale / aSize
                                                            self.handColor = SuitDNA.legalPolyColor
                                                            self.generateBody()
                                                            self.generateHead('backstabber')
                                                            self.setHeight(6.71)
                                                        else:
                                                            if dna.name == 'sd':
                                                                self.scale = scale / bSize
                                                                self.handColor = VBase4(0.5, 0.8, 0.75, 1.0)
                                                                self.generateBody()
                                                                self.headTexture = 'spin-doctor.jpg'
                                                                self.generateHead('telemarketer')
                                                                self.setHeight(7.9)
                                                            else:
                                                                if dna.name == 'le':
                                                                    self.scale = scale / aSize
                                                                    self.handColor = VBase4(0.25, 0.25, 0.5, 1.0)
                                                                    self.generateBody()
                                                                    self.generateHead('legaleagle')
                                                                    self.setHeight(8.27)
                                                                else:
                                                                    if dna.name == 'bw':
                                                                        self.scale = scale / aSize
                                                                        self.handColor = SuitDNA.legalPolyColor
                                                                        self.generateBody()
                                                                        self.generateHead('bigwig')
                                                                        self.setHeight(8.69)
                                                                    else:
                                                                        if dna.name == 'sc':
                                                                            self.scale = scale / cSize
                                                                            self.handColor = SuitDNA.moneyPolyColor
                                                                            self.generateBody()
                                                                            self.generateHead('coldcaller')
                                                                            self.setHeight(4.77)
                                                                        else:
                                                                            if dna.name == 'pp':
                                                                                self.scale = scale / aSize
                                                                                self.handColor = VBase4(1.0, 0.5, 0.6, 1.0)
                                                                                self.generateBody()
                                                                                self.generateHead('pennypincher')
                                                                                self.setHeight(5.26)
                                                                            else:
                                                                                if dna.name == 'tw':
                                                                                    self.scale = scale / cSize
                                                                                    self.handColor = SuitDNA.moneyPolyColor
                                                                                    self.generateBody()
                                                                                    self.generateHead('tightwad')
                                                                                    self.setHeight(5.41)
                                                                                else:
                                                                                    if dna.name == 'bc':
                                                                                        self.scale = scale / bSize
                                                                                        self.handColor = SuitDNA.moneyPolyColor
                                                                                        self.generateBody()
                                                                                        self.generateHead('beancounter')
                                                                                        self.setHeight(5.95)
                                                                                    else:
                                                                                        if dna.name == 'nc':
                                                                                            self.scale = scale / aSize
                                                                                            self.handColor = SuitDNA.moneyPolyColor
                                                                                            self.generateBody()
                                                                                            self.generateHead('numbercruncher')
                                                                                            self.setHeight(7.22)
                                                                                        else:
                                                                                            if dna.name == 'mb':
                                                                                                self.scale = scale / cSize
                                                                                                self.handColor = SuitDNA.moneyPolyColor
                                                                                                self.generateBody()
                                                                                                self.generateHead('moneybags')
                                                                                                self.setHeight(6.97)
                                                                                            else:
                                                                                                if dna.name == 'ls':
                                                                                                    self.scale = scale / bSize
                                                                                                    self.handColor = VBase4(0.5, 0.85, 0.75, 1.0)
                                                                                                    self.generateBody()
                                                                                                    self.generateHead('loanshark')
                                                                                                    self.setHeight(8.58)
                                                                                                else:
                                                                                                    if dna.name == 'rb':
                                                                                                        self.scale = scale / aSize
                                                                                                        self.handColor = SuitDNA.moneyPolyColor
                                                                                                        self.generateBody()
                                                                                                        self.headTexture = 'robber-baron.jpg'
                                                                                                        self.generateHead('yesman')
                                                                                                        self.setHeight(8.95)
                                                                                                    else:
                                                                                                        if dna.name == 'cc':
                                                                                                            self.scale = scale / cSize
                                                                                                            self.handColor = VBase4(0.55, 0.65, 1.0, 1.0)
                                                                                                            self.headColor = VBase4(0.25, 0.35, 1.0, 1.0)
                                                                                                            self.generateBody()
                                                                                                            self.generateHead('coldcaller')
                                                                                                            self.setHeight(4.63)
                                                                                                        else:
                                                                                                            if dna.name == 'tm':
                                                                                                                self.scale = scale / bSize
                                                                                                                self.handColor = SuitDNA.salesPolyColor
                                                                                                                self.generateBody()
                                                                                                                self.generateHead('telemarketer')
                                                                                                                self.setHeight(5.24)
                                                                                                            else:
                                                                                                                if dna.name == 'nd':
                                                                                                                    self.scale = scale / aSize
                                                                                                                    self.handColor = SuitDNA.salesPolyColor
                                                                                                                    self.generateBody()
                                                                                                                    self.headTexture = 'name-dropper.jpg'
                                                                                                                    self.generateHead('numbercruncher')
                                                                                                                    self.setHeight(5.98)
                                                                                                                else:
                                                                                                                    if dna.name == 'gh':
                                                                                                                        self.scale = scale / cSize
                                                                                                                        self.handColor = SuitDNA.salesPolyColor
                                                                                                                        self.generateBody()
                                                                                                                        self.generateHead('gladhander')
                                                                                                                        self.setHeight(6.4)
                                                                                                                    else:
                                                                                                                        if dna.name == 'ms':
                                                                                                                            self.scale = scale / bSize
                                                                                                                            self.handColor = SuitDNA.salesPolyColor
                                                                                                                            self.generateBody()
                                                                                                                            self.generateHead('movershaker')
                                                                                                                            self.setHeight(6.7)
                                                                                                                        else:
                                                                                                                            if dna.name == 'tf':
                                                                                                                                self.scale = scale / aSize
                                                                                                                                self.handColor = SuitDNA.salesPolyColor
                                                                                                                                self.generateBody()
                                                                                                                                self.generateHead('twoface')
                                                                                                                                self.setHeight(6.95)
                                                                                                                            else:
                                                                                                                                if dna.name == 'm':
                                                                                                                                    self.scale = scale / aSize
                                                                                                                                    self.handColor = SuitDNA.salesPolyColor
                                                                                                                                    self.generateBody()
                                                                                                                                    self.headTexture = 'mingler.jpg'
                                                                                                                                    self.generateHead('twoface')
                                                                                                                                    self.setHeight(7.61)
                                                                                                                                else:
                                                                                                                                    if dna.name == 'mh':
                                                                                                                                        self.scale = scale / aSize
                                                                                                                                        self.handColor = SuitDNA.salesPolyColor
                                                                                                                                        self.generateBody()
                                                                                                                                        self.generateHead('yesman')
                                                                                                                                        self.setHeight(8.95)
                                                                                                                                    else:
                                                                                                                                        if dna.name == 'm1':
                                                                                                                                            self.scale = scale / cSize
                                                                                                                                            self.handColor = SuitDNA.mafiaPolyColor
                                                                                                                                            self.generateBody()
                                                                                                                                            self.headTexture = 'soldier.jpg'
                                                                                                                                            self.generateHead('flunky')
                                                                                                                                            self.setHeight(4.81)
                                                                                                                                        else:
                                                                                                                                            if dna.name == 'm2':
                                                                                                                                                self.scale = scale / bSize
                                                                                                                                                self.handColor = VBase4(0.95, 0.95, 1.0, 1.0)
                                                                                                                                                self.generateBody()
                                                                                                                                                self.headTexture = 'capo.jpg'
                                                                                                                                                self.generateHead('movershaker')
                                                                                                                                                self.setHeight(6.17)
                                                                                                                                            else:
                                                                                                                                                if dna.name == 'm3':
                                                                                                                                                    self.scale = scale / aSize
                                                                                                                                                    self.handColor = SuitDNA.mafiaPolyColor
                                                                                                                                                    self.generateBody()
                                                                                                                                                    self.generateHead('greyhat')
                                                                                                                                                    self.setHeight(5.63)
                                                                                                                                                else:
                                                                                                                                                    if dna.name == 'm4':
                                                                                                                                                        self.scale = scale / aSize
                                                                                                                                                        self.handColor = SuitDNA.mafiaPolyColor
                                                                                                                                                        self.generateBody()
                                                                                                                                                        self.headTexture = 'cugine.jpg'
                                                                                                                                                        self.generateHead('numbercruncher')
                                                                                                                                                        self.setHeight(6.39)
                                                                                                                                                    else:
                                                                                                                                                        if dna.name == 'm5':
                                                                                                                                                            self.scale = scale / aSize
                                                                                                                                                            self.handColor = SuitDNA.mafiaPolyColor
                                                                                                                                                            self.generateBody()
                                                                                                                                                            self.headTexture = 'enforcer.jpg'
                                                                                                                                                            self.generateHead('yesman')
                                                                                                                                                            self.setHeight(6.71)
                                                                                                                                                        else:
                                                                                                                                                            if dna.name == 'm6':
                                                                                                                                                                self.scale = scale / bSize
                                                                                                                                                                self.handColor = SuitDNA.mafiaPolyColor
                                                                                                                                                                self.headColor = VBase4(1.0, 0.65, 0.75, 1.0)
                                                                                                                                                                self.generateBody()
                                                                                                                                                                self.headTexture = 'sharpseer.jpg'
                                                                                                                                                                self.generateHead('telemarketer')
                                                                                                                                                                self.setHeight(7.9)
                                                                                                                                                            else:
                                                                                                                                                                if dna.name == 'm7':
                                                                                                                                                                    self.scale = scale / cSize
                                                                                                                                                                    self.handColor = SuitDNA.mafiaPolyColor
                                                                                                                                                                    self.generateBody()
                                                                                                                                                                    self.headTexture = 'mademan.jpg'
                                                                                                                                                                    self.generateHead('flunky')
                                                                                                                                                                    self.setHeight(8.27)
                                                                                                                                                                else:
                                                                                                                                                                    if dna.name == 'm8':
                                                                                                                                                                        self.scale = scale / aSize
                                                                                                                                                                        self.handColor = SuitDNA.mafiaPolyColor
                                                                                                                                                                        self.generateBody()
                                                                                                                                                                        self.headTexture = 'don.jpg'
                                                                                                                                                                        self.generateHead('pennypincher')
                                                                                                                                                                        self.setHeight(8.69)
                                                                                                                                                                    else:
                                                                                                                                                                        if dna.name == 'cm':
                                                                                                                                                                            self.scale = scale / aSize
                                                                                                                                                                            self.handColor = VBase4(0.95, 0.95, 1.0, 1.0)
                                                                                                                                                                            self.generateBody()
                                                                                                                                                                            self.generateHead('chairman')
                                                                                                                                                                            self.setHeight(8.69)
                                                                                                                                                                        else:
                                                                                                                                                                            if dna.name == 'sbf':
                                                                                                                                                                                self.scale = scale / aSize
                                                                                                                                                                                self.handColor = VBase4(0.95, 0.95, 1, 1.0)
                                                                                                                                                                                self.generateBody()
                                                                                                                                                                                self.headTexture = 'steel-bottom-feeder.jpg'
                                                                                                                                                                                self.generateHead('tightwad')
                                                                                                                                                                                self.setHeight(8.69)
                                                                                                                                                                            else:
                                                                                                                                                                                if dna.name == 'stm':
                                                                                                                                                                                    self.scale = scale / aSize
                                                                                                                                                                                    self.handColor = VBase4(0.95, 0.95, 1, 1.0)
                                                                                                                                                                                    self.generateBody()
                                                                                                                                                                                    self.headTexture = 'steel-telemarketer.jpg'
                                                                                                                                                                                    self.generateHead('telemarketer')
                                                                                                                                                                                    self.setHeight(8.69)
                                                                                                                                                                                else:
                                                                                                                                                                                    if dna.name == 'cm2':
                                                                                                                                                                                        self.scale = scale / aSize
                                                                                                                                                                                        self.handColor = VBase4(0.95, 0.95, 1.0, 1.0)
                                                                                                                                                                                        self.generateBody()
                                                                                                                                                                                        self.generateHead('ChairmanHead_egg')
                                                                                                                                                                                        self.setHeight(8.69)
                                                                                                                                                                                    else:
                                                                                                                                                                                        if dna.name == 'mdr':
                                                                                                                                                                                            self.scale = scale / aSize
                                                                                                                                                                                            self.handColor = VBase4(1, 0, 0, 1.0)
                                                                                                                                                                                            self.generateBody()
                                                                                                                                                                                            self.generateHead('mole_cog')
                                                                                                                                                                                            self.setHeight(8.69)
                                                                                                                                                                                        else:
                                                                                                                                                                                            if dna.name == 'mtt':
                                                                                                                                                                                                self.scale = scale / aSize
                                                                                                                                                                                                self.handColor = SuitDNA.salesPolyColor
                                                                                                                                                                                                self.generateBody()
                                                                                                                                                                                                self.generateHead('mettaton')
                                                                                                                                                                                                self.setHeight(8.69)
        self.setName(SuitBattleGlobals.SuitAttributes[dna.name]['name'])
        self.getGeomNode().setScale(self.scale)
        self.generateHealthBar()
        self.generateCorporateMedallion()
        return

    def generateBody(self):
        animDict = self.generateAnimDict()
        filePrefix, bodyPhase = ModelDict[self.style.body]
        if config.GetBool('want-new-cogs', 0):
            if cogExists(filePrefix + 'zero'):
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

        if not config.GetBool('want-new-cogs', 0):
            if self.style.body == 'a':
                animDict['awalk'] = 'phase_4/models/char/suitA-awalk'
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

        try:
            animList = locals()[self.style.name]
        except KeyError:
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
            halloween = base.cr.newsManager.isHolidayRunning(ToontownGlobals.TRICK_OR_TREAT) or base.cr.newsManager.isHolidayRunning(ToontownGlobals.HALLOWEEN_PROPS) or base.cr.newsManager.isHolidayRunning(ToontownGlobals.HALLOWEEN)
            if self.style.name == 'cm':
                torsoTex = loader.loadTexture('phase_14/maps/chairman_blazer.jpg')
            else:
                if self.style.name == 'cm2':
                    torsoTex = loader.loadTexture('phase_14/maps/chairman2_blazer.jpg')
                else:
                    if self.style.name == 'sbf':
                        torsoTex = loader.loadTexture('phase_14/maps/steel_blazer.jpg')
                    else:
                        if self.style.name == 'stm':
                            torsoTex = loader.loadTexture('phase_14/maps/steel_blazer.jpg')
                        else:
                            if self.style.name == 'mdr':
                                torsoTex = loader.loadTexture('phase_3.5/maps/c_blazer.jpg')
                            else:
                                if self.style.name == 'mtt':
                                    torsoTex = loader.loadTexture('phase_14/maps/mtt_blazer.jpg')
                                else:
                                    if halloween:
                                        if self.style.name == 'b':
                                            torsoTex = loader.loadTexture('phase_3.5/maps/hw_blazer.jpg')
                                        elif self.style.name == 'ac':
                                            torsoTex = loader.loadTexture('phase_3.5/maps/hw2_blazer.jpg')
                                        else:
                                            torsoTex = loader.loadTexture('phase_%s/maps/%s_blazer.jpg' % (phase, dept))
                                    else:
                                        torsoTex = loader.loadTexture('phase_%s/maps/%s_blazer.jpg' % (phase, dept))
            torsoTex.setMinfilter(Texture.FTLinearMipmapLinear)
            torsoTex.setMagfilter(Texture.FTLinear)
            if self.style.name == 'cm':
                legTex = loader.loadTexture('phase_14/maps/chairman_leg.jpg')
            else:
                if self.style.name == 'cm2':
                    legTex = loader.loadTexture('phase_14/maps/chairman2_leg.jpg')
                else:
                    if self.style.name == 'sbf':
                        legTex = loader.loadTexture('phase_14/maps/steel_leg.jpg')
                    else:
                        if self.style.name == 'stm':
                            legTex = loader.loadTexture('phase_14/maps/steel_leg.jpg')
                        else:
                            if self.style.name == 'mdr':
                                legTex = loader.loadTexture('phase_3.5/maps/c_leg.jpg')
                            else:
                                if self.style.name == 'mtt':
                                    legTex = loader.loadTexture('phase_14/maps/mtt_leg.jpg')
                                else:
                                    if halloween:
                                        if self.style.name == 'b':
                                            legTex = loader.loadTexture('phase_3.5/maps/hw_leg.jpg')
                                        elif self.style.name == 'ac':
                                            legTex = loader.loadTexture('phase_3.5/maps/hw2_leg.jpg')
                                        else:
                                            legTex = loader.loadTexture('phase_%s/maps/%s_leg.jpg' % (phase, dept))
                                    else:
                                        legTex = loader.loadTexture('phase_%s/maps/%s_leg.jpg' % (phase, dept))
            legTex.setMinfilter(Texture.FTLinearMipmapLinear)
            legTex.setMagfilter(Texture.FTLinear)
            if self.style.name == 'cm':
                armTex = loader.loadTexture('phase_14/maps/chairman_sleeve.jpg')
            else:
                if self.style.name == 'cm2':
                    armTex = loader.loadTexture('phase_14/maps/chairman2_sleeve.jpg')
                else:
                    if self.style.name == 'sbf':
                        armTex = loader.loadTexture('phase_14/maps/steel_sleeve.jpg')
                    else:
                        if self.style.name == 'stm':
                            armTex = loader.loadTexture('phase_14/maps/steel_sleeve.jpg')
                        else:
                            if self.style.name == 'mdr':
                                armTex = loader.loadTexture('phase_3.5/maps/c_sleeve.jpg')
                            else:
                                if self.style.name == 'mtt':
                                    armTex = loader.loadTexture('phase_14/maps/mtt_sleeve.jpg')
                                else:
                                    if halloween:
                                        if self.style.name == 'b':
                                            armTex = loader.loadTexture('phase_3.5/maps/hw_sleeve.jpg')
                                        elif self.style.name == 'ac':
                                            armTex = loader.loadTexture('phase_3.5/maps/hw2_sleeve.jpg')
                                        else:
                                            armTex = loader.loadTexture('phase_%s/maps/%s_sleeve.jpg' % (phase, dept))
                                    else:
                                        armTex = loader.loadTexture('phase_%s/maps/%s_sleeve.jpg' % (phase, dept))
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

        if config.GetBool('want-new-cogs', 0):
            if dept == 'c':
                texType = 'bossbot'
            else:
                if dept == 'm':
                    texType = 'cashbot'
                else:
                    if dept == 'l':
                        texType = 'lawbot'
                    else:
                        if dept == 's':
                            texType = 'sellbot'
                        else:
                            if dept == 'g':
                                texType = 'hackerbot'
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

    def makeWaiter(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isWaiter = 1
        torsoTex = loader.loadTexture('phase_3.5/maps/waiter_m_blazer.jpg')
        torsoTex.setMinfilter(Texture.FTLinearMipmapLinear)
        torsoTex.setMagfilter(Texture.FTLinear)
        legTex = loader.loadTexture('phase_3.5/maps/waiter_m_leg.jpg')
        legTex.setMinfilter(Texture.FTLinearMipmapLinear)
        legTex.setMagfilter(Texture.FTLinear)
        armTex = loader.loadTexture('phase_3.5/maps/waiter_m_sleeve.jpg')
        armTex.setMinfilter(Texture.FTLinearMipmapLinear)
        armTex.setMagfilter(Texture.FTLinear)
        modelRoot.find('**/torso').setTexture(torsoTex, 1)
        modelRoot.find('**/arms').setTexture(armTex, 1)
        modelRoot.find('**/legs').setTexture(legTex, 1)

    def makeRentalSuit(self, suitType, modelRoot=None):
        if not modelRoot:
            modelRoot = self.getGeomNode()
        if suitType == 's':
            torsoTex = loader.loadTexture('phase_3.5/maps/tt_t_ene_sellbotRental_blazer.jpg')
            legTex = loader.loadTexture('phase_3.5/maps/tt_t_ene_sellbotRental_leg.jpg')
            armTex = loader.loadTexture('phase_3.5/maps/tt_t_ene_sellbotRental_sleeve.jpg')
            handTex = loader.loadTexture('phase_3.5/maps/tt_t_ene_sellbotRental_hand.jpg')
        else:
            self.notify.warning('No rental suit for cog type %s' % suitType)
            return
        self.isRental = 1
        modelRoot.find('**/torso').setTexture(torsoTex, 1)
        modelRoot.find('**/arms').setTexture(armTex, 1)
        modelRoot.find('**/legs').setTexture(legTex, 1)
        modelRoot.find('**/hands').setTexture(handTex, 1)

    def generateHead(self, headType):
        if config.GetBool('want-new-cogs', 0):
            filePrefix, phase = HeadModelDict[self.style.body]
        else:
            filePrefix, phase = ModelDict[self.style.body]
        if headType == 'greyhat':
            headModel = loader.loadModel('phase_14/models/char/greyhat')
        else:
            if headType == 'ChairmanHead_egg':
                headModel = loader.loadModel('phase_14/models/char/director-head')
            else:
                if headType == 'mole_cog':
                    headModel = loader.loadModel('phase_12/models/bossbotHQ/mole_cog')
                else:
                    if headType == 'mettaton':
                        headModel = loader.loadModel('phase_14/models/char/mettaton-head')
                    else:
                        if headType == 'chairman':
                            headModel = loader.loadModel('phase_3.5/models/char/suitC-' + 'heads')
                        else:
                            if self.style.name == 'stm':
                                headModel = loader.loadModel('phase_4/models/char/suitB-heads')
                            else:
                                headModel = loader.loadModel('phase_' + str(phase) + filePrefix + 'heads')
        headReferences = headModel.findAllMatches('**/' + headType)
        for i in range(0, headReferences.getNumPaths()):
            if config.GetBool('want-new-cogs', 0):
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
            if headType == 'greyhat':
                headPart.setZ(1)
                headPart.setScale(1.5)
            if headType == 'ChairmanHead_egg':
                headPart.setH(180)
                headPart.setZ(-0.2)
                headPart.setY(-0.2)
                headPart.setScale(0.3)
            if self.style.name == 'stm':
                headPart.setZ(-0.2)
                headPart.setScale(1.1)
            if headType == 'mole_cog':
                headPart.setH(180)
                headPart.setZ(-0.5)
                headPart.setScale(0.69)
            self.headParts.append(headPart)

        headModel.removeNode()

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
        else:
            if dept == 's':
                tieTex = loader.loadTexture('phase_5/maps/cog_robot_tie_sales.jpg')
            else:
                if dept == 'l':
                    tieTex = loader.loadTexture('phase_5/maps/cog_robot_tie_legal.jpg')
                else:
                    if dept == 'm':
                        tieTex = loader.loadTexture('phase_5/maps/cog_robot_tie_money.jpg')
                    else:
                        if dept == 'g':
                            tieTex = loader.loadTexture('phase_5/maps/cog_robot_tie_mafia.jpg')
        tieTex.setMinfilter(Texture.FTLinearMipmapLinear)
        tieTex.setMagfilter(Texture.FTLinear)
        tie.setTexture(tieTex, 1)

    def generateCorporateMedallion(self):
        icons = loader.loadModel('phase_3/models/gui/cog_icons')
        dept = self.style.dept
        if not dept and self.style.name == 'cm':
            dept = 'g'
        if not dept and self.style.name == 'cm2':
            dept = 'g'
        if not dept and self.style.name == 'sbf':
            dept = 'l'
        if not dept and self.style.name == 'stm':
            dept = 's'
        if not dept and self.style.name == 'mdr':
            dept = 'c'
        if not dept and self.style.name == 'mtt':
            dept = 's'
        if config.GetBool('want-new-cogs', 0):
            chestNull = self.find('**/def_joint_attachMeter')
            if chestNull.isEmpty():
                chestNull = self.find('**/joint_attachMeter')
        else:
            chestNull = self.find('**/joint_attachMeter')
        if dept == 'c':
            self.corpMedallion = icons.find('**/CorpIcon').copyTo(chestNull)
        else:
            if dept == 's':
                self.corpMedallion = icons.find('**/SalesIcon').copyTo(chestNull)
            else:
                if dept == 'l':
                    self.corpMedallion = icons.find('**/LegalIcon').copyTo(chestNull)
                else:
                    if dept == 'm':
                        self.corpMedallion = icons.find('**/MoneyIcon').copyTo(chestNull)
                    else:
                        if dept == 'g':
                            self.corpMedallion = icons.find('**/HackerIcon').copyTo(chestNull)
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
        if config.GetBool('want-new-cogs', 0):
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

    def updateHealthBar(self, hp, forceUpdate=0):
        if hp > self.currHP:
            hp = self.currHP
        self.currHP -= hp
        health = float(self.currHP) / float(self.maxHP)
        if health > 0.95:
            condition = 0
        else:
            if health > 0.7:
                condition = 1
            else:
                if health > 0.3:
                    condition = 2
                else:
                    if health > 0.05:
                        condition = 3
                    else:
                        if health > 0.0:
                            condition = 4
                        else:
                            condition = 5
        if self.healthCondition != condition or forceUpdate:
            if condition == 4:
                blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.75), Task(self.__blinkGray), Task.pause(0.1))
                taskMgr.add(blinkTask, self.uniqueName('blink-task'))
            else:
                if condition == 5:
                    if self.healthCondition == 4:
                        taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.25), Task(self.__blinkGray), Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                else:
                    self.healthBar.setColor(self.healthColors[condition], 1)
                    self.healthBarGlow.setColor(self.healthGlowColors[condition], 1)
            self.healthCondition = condition

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
        if config.GetBool('want-new-cogs', 0):
            if self.find('**/body'):
                return self
        if self.loseActor == None:
            if not self.isSkeleton:
                filePrefix, phase = TutorialModelDict[self.style.body]
                loseModel = 'phase_' + str(phase) + filePrefix + 'lose-mod'
                loseAnim = 'phase_' + str(phase) + filePrefix + 'lose'
                self.loseActor = Actor.Actor(loseModel, {'lose': loseAnim})
                loseNeck = self.loseActor.find('**/joint_head')
                for part in self.headParts:
                    part.instanceTo(loseNeck)

                if self.isWaiter:
                    self.makeWaiter(self.loseActor)
                else:
                    self.setSuitClothes(self.loseActor)
            else:
                loseModel = 'phase_5/models/char/cog' + self.style.body.upper() + '_robot-lose-mod'
                filePrefix, phase = TutorialModelDict[self.style.body]
                loseAnim = 'phase_' + str(phase) + filePrefix + 'lose'
                self.loseActor = Actor.Actor(loseModel, {'lose': loseAnim})
                self.generateCorporateTie(self.loseActor)
                if self.isVirtual:
                    actorNode = self.loseActor.find('**/__Actor_modelRoot')
                    actorCollection = actorNode.findAllMatches('*')
                    parts = ()
                    for thingIndex in range(0, actorCollection.getNumPaths()):
                        thing = actorCollection[thingIndex]
                        if thing.getName() not in ('joint_attachMeter', 'joint_nameTag',
                                                   'def_nameTag'):
                            thing.setColorScale(1.0, 0.0, 0.0, 1.0)
                            thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                            thing.setDepthWrite(False)
                            thing.setBin('fixed', 1)

        self.loseActor.setScale(self.scale)
        self.loseActor.setPos(self.getPos())
        self.loseActor.setHpr(self.getH(), 0, 0)
        self.loseActor.setBlend(frameBlend=config.GetBool('interpolate-animations', True))
        self.collTube = CollisionTube(0, 0, 0.5, 0, 0, 4, 2)
        self.collNode = CollisionNode('loseActor')
        self.collNode.addSolid(self.collTube)
        self.collNodePath = self.loseActor.attachNewNode(self.collNode)
        shadowJoint = self.loseActor.find('**/joint_shadow')
        dropShadow = loader.loadModel('phase_3/models/props/drop_shadow')
        dropShadow.setScale(0.45)
        dropShadow.setColor(0.0, 0.0, 0.0, 0.5)
        dropShadow.reparentTo(shadowJoint)
        return self.loseActor

    def cleanupLoseActor(self):
        self.notify.debug('cleanupLoseActor()')
        if self.loseActor != None:
            self.notify.debug('cleanupLoseActor() - got one')
            self.loseActor.cleanup()
        self.loseActor = None
        return

    def makeSkeleton(self):
        model = 'phase_5/models/char/cog' + self.style.body.upper() + '_robot-zero'
        anims = self.generateAnimDict()
        anim = self.getCurrentAnim()
        modelRoot = self.getGeomNode()
        modelRoot.find('**/torso').removeNode()
        modelRoot.find('**/arms').removeNode()
        modelRoot.find('**/hands').removeNode()
        modelRoot.find('**/legs').removeNode()
        modelRoot.find('**/').removeNode()
        modelRoot.find('**/joint_head').removeNode()
        self.loadModel(model)
        self.loadAnims(anims)
        self.getGeomNode().setScale(self.scale * 1.0173)
        self.generateHealthBar()
        self.generateCorporateMedallion()
        self.generateCorporateTie()
        self.setHeight(self.height)
        parts = self.findAllMatches('**/pPlane*')
        for partNum in range(0, parts.getNumPaths()):
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

    def makeVirtual(self):
        actorNode = self.find('**/__Actor_modelRoot')
        actorCollection = actorNode.findAllMatches('*')
        parts = ()
        for thingIndex in range(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            if thing.getName() not in ('joint_attachMeter', 'joint_nameTag', 'def_nameTag'):
                thing.setColorScale(1.0, 0.0, 0.0, 1.0)
                thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                thing.setDepthWrite(False)
                thing.setBin('fixed', 1)

        self.isVirtual = 1

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
        loadDialog(1)
        return SuitDialogArray