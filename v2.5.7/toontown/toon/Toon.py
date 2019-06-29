from otp.avatar import Avatar
from otp.avatar.Avatar import teleportNotify
import ToonDNA
from direct.task.Task import Task
from toontown.suit import SuitDNA
from toontown.suit import GoonDeath
from direct.actor import Actor
from ToonHead import *
from panda3d.core import *
from panda3d.direct import *
from direct.interval.IntervalGlobal import *
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import ToontownGlobals
from otp.otpbase import OTPLocalizer
from toontown.toonbase import TTLocalizer
import random
from toontown.effects import Wake
import TTEmote
from otp.avatar import Emote
import Motion
from toontown.hood import ZoneUtil
from toontown.battle import SuitBattleGlobals
from otp.otpbase import OTPGlobals
from toontown.effects import DustCloud
from otp.otpbase.PythonUtil import Functor
from toontown.distributed import DelayDelete
from otp.nametag.NametagConstants import *
from toontown.battle import BattleParticles
from toontown.toon import LaughingManGlobals
from toontown.toon import GhostHeadGlobals
from toontown.battle import BattleProps
from toontown.suit import SuitTimings
import AccessoryGlobals, types, time

def teleportDebug(requestStatus, msg, onlyIfToAv=True):
    if teleportNotify.getDebug():
        teleport = 'teleport'
        if requestStatus.has_key('how') and requestStatus['how'][:len(teleport)] == teleport:
            if not onlyIfToAv or requestStatus.has_key('avId') and requestStatus['avId'] > 0:
                teleportNotify.debug(msg)


SLEEP_STRING = TTLocalizer.ToonSleepString
DogDialogueArray = []
CatDialogueArray = []
HorseDialogueArray = []
RabbitDialogueArray = []
MouseDialogueArray = []
DuckDialogueArray = []
MonkeyDialogueArray = []
BearDialogueArray = []
PigDialogueArray = []
ScroogeDialogueArray = []
GyroDialogueArray = []
SuitDialogueArray = []
SkeletonDialogueArray = []
BossDialogueArray = []
MickeyDialogueArray = []
MinnieDialogueArray = []
GoofyDialogueArray = []
DonaldDialogueArray = []
DaisyDialogueArray = []
ChipDialogueArray = []
DaleDialogueArray = []
DoodleDialogueArray = []
LegsAnimDict = {}
TorsoAnimDict = {}
HeadAnimDict = {}
Preloaded = []
Phase3AnimList = (('neutral', 'neutral'), ('run', 'run'))
Phase3_5AnimList = (('walk', 'walk'),
 (
  'teleport', 'teleport'),
 (
  'book', 'book'),
 (
  'jump', 'jump'),
 (
  'running-jump', 'running-jump'),
 (
  'jump-squat', 'jump-zstart'),
 (
  'jump-idle', 'jump-zhang'),
 (
  'jump-land', 'jump-zend'),
 (
  'running-jump-squat', 'leap_zstart'),
 (
  'running-jump-idle', 'leap_zhang'),
 (
  'running-jump-land', 'leap_zend'),
 (
  'pushbutton', 'press-button'),
 (
  'throw', 'pie-throw'),
 (
  'victory', 'victory-dance'),
 (
  'sidestep-left', 'sidestep-left'),
 (
  'conked', 'conked'),
 (
  'cringe', 'cringe'),
 (
  'wave', 'wave'),
 (
  'shrug', 'shrug'),
 (
  'angry', 'angry'),
 (
  'tutorial-neutral', 'tutorial-neutral'),
 (
  'left-point', 'left-point'),
 (
  'right-point', 'right-point'),
 (
  'right-point-start', 'right-point-start'),
 (
  'give-props', 'give-props'),
 (
  'give-props-start', 'give-props-start'),
 (
  'right-hand', 'right-hand'),
 (
  'right-hand-start', 'right-hand-start'),
 (
  'duck', 'duck'),
 (
  'sidestep-right', 'jump-back-right'))
Phase4AnimList = (('sit', 'sit'),
 (
  'sit-start', 'intoSit'),
 (
  'swim', 'swim'),
 (
  'tug-o-war', 'tug-o-war'),
 (
  'sad-walk', 'losewalk'),
 (
  'sad-neutral', 'sad-neutral'),
 (
  'up', 'up'),
 (
  'down', 'down'),
 (
  'left', 'left'),
 (
  'right', 'right'),
 (
  'applause', 'applause'),
 (
  'confused', 'confused'),
 (
  'bow', 'bow'),
 (
  'curtsy', 'curtsy'),
 (
  'bored', 'bored'),
 (
  'think', 'think'),
 (
  'battlecast', 'fish'),
 (
  'cast', 'cast'),
 (
  'castlong', 'castlong'),
 (
  'fish-end', 'fishEND'),
 (
  'fish-neutral', 'fishneutral'),
 (
  'fish-again', 'fishAGAIN'),
 (
  'reel', 'reel'),
 (
  'reel-H', 'reelH'),
 (
  'reel-neutral', 'reelneutral'),
 (
  'periscope', 'periscope'),
 (
  'pole', 'pole'),
 (
  'pole-neutral', 'poleneutral'),
 (
  'slip-forward', 'slip-forward'),
 (
  'slip-backward', 'slip-backward'),
 (
  'catch-neutral', 'gameneutral'),
 (
  'catch-run', 'gamerun'),
 (
  'catch-eatneutral', 'eat_neutral'),
 (
  'catch-eatnrun', 'eatnrun'),
 (
  'catch-intro-throw', 'gameThrow'),
 (
  'swing', 'swing'),
 (
  'pet-start', 'petin'),
 (
  'pet-loop', 'petloop'),
 (
  'pet-end', 'petend'),
 (
  'scientistJealous', 'scientistJealous'),
 (
  'scientistEmcee', 'scientistEmcee'),
 (
  'scientistWork', 'scientistWork'),
 (
  'scientistGame', 'scientistGame'),
 (
  'riggyNeutral', 'riggyNeutral'),
 (
  'riggyWalk', 'riggyWalk'),
 (
  'taunt', 'taunt'))
Phase5AnimList = (('water-gun', 'water-gun'),
 (
  'hold-bottle', 'hold-bottle'),
 (
  'firehose', 'firehose'),
 (
  'spit', 'spit'),
 (
  'tickle', 'tickle'),
 (
  'smooch', 'smooch'),
 (
  'happy-dance', 'happy-dance'),
 (
  'sprinkle-dust', 'sprinkle-dust'),
 (
  'juggle', 'juggle'),
 (
  'climb', 'climb'),
 (
  'sound', 'shout'),
 (
  'toss', 'toss'),
 (
  'hold-magnet', 'hold-magnet'),
 (
  'hypnotize', 'hypnotize'),
 (
  'struggle', 'struggle'),
 (
  'lose', 'lose'),
 (
  'melt', 'melt'))
Phase5_5AnimList = (('takePhone', 'takePhone'),
 (
  'phoneNeutral', 'phoneNeutral'),
 (
  'phoneBack', 'phoneBack'),
 (
  'bank', 'jellybeanJar'),
 (
  'callPet', 'callPet'),
 (
  'feedPet', 'feedPet'),
 (
  'start-dig', 'into_dig'),
 (
  'loop-dig', 'loop_dig'),
 (
  'water', 'water'))
Phase6AnimList = (('headdown-putt', 'headdown-putt'),
 (
  'into-putt', 'into-putt'),
 (
  'loop-putt', 'loop-putt'),
 (
  'rotateL-putt', 'rotateL-putt'),
 (
  'rotateR-putt', 'rotateR-putt'),
 (
  'swing-putt', 'swing-putt'),
 (
  'look-putt', 'look-putt'),
 (
  'lookloop-putt', 'lookloop-putt'),
 (
  'bad-putt', 'bad-putt'),
 (
  'badloop-putt', 'badloop-putt'),
 (
  'good-putt', 'good-putt'))
Phase9AnimList = (('push', 'push'),)
Phase10AnimList = (('leverReach', 'leverReach'), ('leverPull', 'leverPull'), ('leverNeutral', 'leverNeutral'))
Phase12AnimList = ()
if not config.GetBool('want-new-anims', 1):
    LegDict = {'s': '/models/char/dogSS_Shorts-legs-', 'm': '/models/char/dogMM_Shorts-legs-', 'l': '/models/char/dogLL_Shorts-legs-'}
    TorsoDict = {'s': '/models/char/dogSS_Naked-torso-', 'm': '/models/char/dogMM_Naked-torso-', 
       'l': '/models/char/dogLL_Naked-torso-', 
       'ss': '/models/char/dogSS_Shorts-torso-', 
       'ms': '/models/char/dogMM_Shorts-torso-', 
       'ls': '/models/char/dogLL_Shorts-torso-', 
       'sd': '/models/char/dogSS_Skirt-torso-', 
       'md': '/models/char/dogMM_Skirt-torso-', 
       'ld': '/models/char/dogLL_Skirt-torso-'}
else:
    LegDict = {'s': '/models/char/tt_a_chr_dgs_shorts_legs_', 'm': '/models/char/tt_a_chr_dgm_shorts_legs_', 
       'l': '/models/char/tt_a_chr_dgl_shorts_legs_'}
    TorsoDict = {'ss': '/models/char/tt_a_chr_dgs_shorts_torso_', 'ms': '/models/char/tt_a_chr_dgm_shorts_torso_', 
       'ls': '/models/char/tt_a_chr_dgl_shorts_torso_', 
       'sd': '/models/char/tt_a_chr_dgs_skirt_torso_', 
       'md': '/models/char/tt_a_chr_dgm_skirt_torso_', 
       'ld': '/models/char/tt_a_chr_dgl_skirt_torso_', 
       's': '/models/char/tt_a_chr_dgs_nude_torso_', 
       'm': '/models/char/tt_a_chr_dgm_nude_torso_', 
       'l': '/models/char/tt_a_chr_dgl_nude_torso_'}

def loadModels():
    global Preloaded
    preloadAvatars = config.GetBool('preload-avatars', 0)
    if preloadAvatars:

        def loadTex(path):
            tex = loader.loadTexture('/' + path)
            tex.setMinfilter(Texture.FTLinearMipmapLinear)
            tex.setMagfilter(Texture.FTLinear)
            Preloaded.append(tex)

        for shirt in ToonDNA.Shirts:
            loadTex(shirt)

        for sleeve in ToonDNA.Sleeves:
            loadTex(sleeve)

        for short in ToonDNA.BoyShorts:
            loadTex(short)

        for bottom in ToonDNA.GirlBottoms:
            loadTex(bottom[0])

        for key in LegDict.keys():
            fileRoot = LegDict[key]
            model = loader.loadModel('/phase_3' + fileRoot + '1000')
            Preloaded.append(model)
            model = loader.loadModel('/phase_3' + fileRoot + '500')
            Preloaded.append(model)
            model = loader.loadModel('/phase_3' + fileRoot + '250')
            Preloaded.append(model)

        for key in TorsoDict.keys():
            fileRoot = TorsoDict[key]
            if key == 's' or key == 'm' or key == 'l':
                model = loader.loadModel('/phase_14' + fileRoot + '1000')
                Preloaded.append(model)
                if len(key) > 1:
                    model = loader.loadModel('/phase_14' + fileRoot + '500')
                    Preloaded.append(model)
                    model = loader.loadModel('/phase_14' + fileRoot + '250')
                    Preloaded.append(model)
            else:
                model = loader.loadModel('/phase_3' + fileRoot + '1000')
                Preloaded.append(model)
                if len(key) > 1:
                    model = loader.loadModel('/phase_3' + fileRoot + '500')
                    Preloaded.append(model)
                    model = loader.loadModel('/phase_3' + fileRoot + '250')
                    Preloaded.append(model)

        for key in HeadDict.keys():
            fileRoot = HeadDict[key]
            if key[0] == 'g':
                model = loader.loadModel('/phase_3' + fileRoot.strip('_'))
                Preloaded.append(model)
            else:
                model = loader.loadModel('/phase_3' + fileRoot + '1000')
                Preloaded.append(model)
                model = loader.loadModel('/phase_3' + fileRoot + '500')
                Preloaded.append(model)
                model = loader.loadModel('/phase_3' + fileRoot + '250')
                Preloaded.append(model)


def loadBasicAnims():
    loadPhaseAnims()


def unloadBasicAnims():
    loadPhaseAnims(0)


def loadTutorialBattleAnims():
    loadPhaseAnims('phase_3.5')


def unloadTutorialBattleAnims():
    loadPhaseAnims('phase_3.5', 0)


def loadMinigameAnims():
    loadPhaseAnims('phase_4')


def unloadMinigameAnims():
    loadPhaseAnims('phase_4', 0)


def loadBattleAnims():
    loadPhaseAnims('phase_5')


def unloadBattleAnims():
    loadPhaseAnims('phase_5', 0)


def loadSellbotHQAnims():
    loadPhaseAnims('phase_9')


def unloadSellbotHQAnims():
    loadPhaseAnims('phase_9', 0)


def loadCashbotHQAnims():
    loadPhaseAnims('phase_10')


def unloadCashbotHQAnims():
    loadPhaseAnims('phase_10', 0)


def loadBossbotHQAnims():
    loadPhaseAnims('phase_12')


def unloadBossbotHQAnims():
    loadPhaseAnims('phase_12', 0)


def loadPhaseAnims(phaseStr='phase_3', loadFlag=1):
    if phaseStr == 'phase_3':
        animList = Phase3AnimList
    else:
        if phaseStr == 'phase_3.5':
            animList = Phase3_5AnimList
        else:
            if phaseStr == 'phase_4':
                animList = Phase4AnimList
            else:
                if phaseStr == 'phase_5':
                    animList = Phase5AnimList
                else:
                    if phaseStr == 'phase_5.5':
                        animList = Phase5_5AnimList
                    else:
                        if phaseStr == 'phase_6':
                            animList = Phase6AnimList
                        else:
                            if phaseStr == 'phase_9':
                                animList = Phase9AnimList
                            else:
                                if phaseStr == 'phase_10':
                                    animList = Phase10AnimList
                                else:
                                    if phaseStr == 'phase_12':
                                        animList = Phase12AnimList
                                    else:
                                        self.notify.error('Unknown phase string %s' % phaseStr)
    for key in LegDict.keys():
        for anim in animList:
            if loadFlag:
                pass
            elif LegsAnimDict[key].has_key(anim[0]):
                if base.localAvatar.style.legs == key:
                    base.localAvatar.unloadAnims([anim[0]], 'legs', None)

    for key in TorsoDict.keys():
        for anim in animList:
            if loadFlag:
                pass
            elif TorsoAnimDict[key].has_key(anim[0]):
                if base.localAvatar.style.torso == key:
                    base.localAvatar.unloadAnims([anim[0]], 'torso', None)

    for key in HeadDict.keys():
        if key.find('d') >= 0 or key.find('g') >= 0:
            for anim in animList:
                if loadFlag:
                    pass
                elif HeadAnimDict[key].has_key(anim[0]):
                    if base.localAvatar.style.head == key:
                        base.localAvatar.unloadAnims([anim[0]], 'head', None)

    return


def compileGlobalAnimList():
    phaseList = [
     Phase3AnimList,
     Phase3_5AnimList,
     Phase4AnimList,
     Phase5AnimList,
     Phase5_5AnimList,
     Phase6AnimList,
     Phase9AnimList,
     Phase10AnimList,
     Phase12AnimList]
    phaseStrList = ['phase_3',
     'phase_3.5',
     'phase_4',
     'phase_5',
     'phase_5.5',
     'phase_6',
     'phase_9',
     'phase_10',
     'phase_12']
    for animList in phaseList:
        phaseStr = phaseStrList[phaseList.index(animList)]
        for key in LegDict.keys():
            LegsAnimDict.setdefault(key, {})
            for anim in animList:
                file = phaseStr + LegDict[key] + anim[1]
                LegsAnimDict[key][anim[0]] = file

        for key in TorsoDict.keys():
            TorsoAnimDict.setdefault(key, {})
            for anim in animList:
                file = phaseStr + TorsoDict[key] + anim[1]
                TorsoAnimDict[key][anim[0]] = file

        for key in HeadDict.keys():
            if key.find('d') >= 0 or key.find('g') >= 0:
                HeadAnimDict.setdefault(key, {})
                for anim in animList:
                    file = phaseStr + HeadDict[key] + anim[1]
                    HeadAnimDict[key][anim[0]] = file


def loadDialog():
    global BearDialogueArray
    global BossDialogueArray
    global CatDialogueArray
    global ChipDialogueArray
    global DaisyDialogueArray
    global DaleDialogueArray
    global DogDialogueArray
    global DonaldDialogueArray
    global DoodleDialogueArray
    global DuckDialogueArray
    global GoofyDialogueArray
    global GyroDialogueArray
    global HorseDialogueArray
    global MickeyDialogueArray
    global MinnieDialogueArray
    global MonkeyDialogueArray
    global MouseDialogueArray
    global PigDialogueArray
    global RabbitDialogueArray
    global ScroogeDialogueArray
    global SkeletonDialogueArray
    global SuitDialogueArray
    loadPath = 'phase_3.5/audio/dial/'
    DogDialogueFiles = ('AV_dog_short', 'AV_dog_med', 'AV_dog_long', 'AV_dog_question',
                        'AV_dog_exclaim', 'AV_dog_howl')
    for file in DogDialogueFiles:
        DogDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    catDialogueFiles = ('AV_cat_short', 'AV_cat_med', 'AV_cat_long', 'AV_cat_question',
                        'AV_cat_exclaim', 'AV_cat_howl')
    for file in catDialogueFiles:
        CatDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    horseDialogueFiles = ('AV_horse_short', 'AV_horse_med', 'AV_horse_long', 'AV_horse_question',
                          'AV_horse_exclaim', 'AV_horse_howl')
    for file in horseDialogueFiles:
        HorseDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    rabbitDialogueFiles = ('AV_rabbit_short', 'AV_rabbit_med', 'AV_rabbit_long', 'AV_rabbit_question',
                           'AV_rabbit_exclaim', 'AV_rabbit_howl')
    for file in rabbitDialogueFiles:
        RabbitDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    mouseDialogueFiles = ('AV_mouse_short', 'AV_mouse_med', 'AV_mouse_long', 'AV_mouse_question',
                          'AV_mouse_exclaim', 'AV_mouse_howl')
    for file in mouseDialogueFiles:
        MouseDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    duckDialogueFiles = ('AV_duck_short', 'AV_duck_med', 'AV_duck_long', 'AV_duck_question',
                         'AV_duck_exclaim', 'AV_duck_howl')
    for file in duckDialogueFiles:
        DuckDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    monkeyDialogueFiles = ('AV_monkey_short', 'AV_monkey_med', 'AV_monkey_long', 'AV_monkey_question',
                           'AV_monkey_exclaim', 'AV_monkey_howl')
    for file in monkeyDialogueFiles:
        MonkeyDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    bearDialogueFiles = ('AV_bear_short', 'AV_bear_med', 'AV_bear_long', 'AV_bear_question',
                         'AV_bear_exclaim', 'AV_bear_howl')
    for file in bearDialogueFiles:
        BearDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    pigDialogueFiles = ('AV_pig_short', 'AV_pig_med', 'AV_pig_long', 'AV_pig_question',
                        'AV_pig_exclaim', 'AV_pig_howl')
    for file in pigDialogueFiles:
        PigDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    scroogeDialogueFiles = ('AV_duck_short', 'AV_duck_med', 'AV_duck_long', 'AV_duck_question',
                            'AV_duck_exclaim', 'AV_duck_howl')
    for file in scroogeDialogueFiles:
        ScroogeDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    gyroDialogueFiles = ('AV_duck_short', 'AV_duck_med', 'AV_duck_long', 'AV_duck_question',
                         'AV_duck_exclaim', 'AV_duck_howl')
    for file in gyroDialogueFiles:
        GyroDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    if config.GetBool('want-old-question', False):
        suitDialogueFiles = ('COG_VO_grunt', 'COG_VO_murmur', 'COG_VO_statement', 'COG_VO_question_retro',
                             'COG_VO_statement', 'COG_VO_murmur')
    else:
        suitDialogueFiles = ('COG_VO_grunt', 'COG_VO_murmur', 'COG_VO_statement', 'COG_VO_question',
                             'COG_VO_statement', 'COG_VO_murmur')
    for file in suitDialogueFiles:
        SuitDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    skeletonDialogueFiles = ('Skel_COG_VO_grunt', 'Skel_COG_VO_murmur', 'Skel_COG_VO_statement',
                             'Skel_COG_VO_question', 'Skel_COG_VO_statement', 'Skel_COG_VO_murmur')
    for file in skeletonDialogueFiles:
        SkeletonDialogueArray.append(base.loader.loadSfx('phase_5/audio/sfx/' + file + '.ogg'))

    BossDialogueArray.append(base.loader.loadSfx('phase_9/audio/sfx/Boss_COG_VO_grunt.ogg'))
    BossDialogueArray.append(base.loader.loadSfx('phase_9/audio/sfx/Boss_COG_VO_murmur.ogg'))
    BossDialogueArray.append(base.loader.loadSfx('phase_9/audio/sfx/Boss_COG_VO_statement.ogg'))
    BossDialogueArray.append(base.loader.loadSfx('phase_9/audio/sfx/Boss_COG_VO_question.ogg'))
    BossDialogueArray.append(base.loader.loadSfx('phase_9/audio/sfx/Boss_COG_VO_statement.ogg'))
    BossDialogueArray.append(base.loader.loadSfx('phase_9/audio/sfx/Boss_COG_VO_murmur.ogg'))
    MickeyDialogueArray.append(base.loader.loadSfx('phase_3/audio/dial/mickey.ogg'))
    MickeyDialogueArray.append(base.loader.loadSfx('phase_3/audio/dial/mickey.ogg'))
    MickeyDialogueArray.append(base.loader.loadSfx('phase_3/audio/dial/mickey.ogg'))
    MickeyDialogueArray.append(base.loader.loadSfx('phase_3/audio/dial/mickey.ogg'))
    MickeyDialogueArray.append(base.loader.loadSfx('phase_3/audio/dial/mickey.ogg'))
    MickeyDialogueArray.append(base.loader.loadSfx('phase_3/audio/dial/mickey.ogg'))
    MinnieDialogueArray.append(base.loader.loadSfx('phase_3/audio/dial/minnie.ogg'))
    MinnieDialogueArray.append(base.loader.loadSfx('phase_3/audio/dial/minnie.ogg'))
    MinnieDialogueArray.append(base.loader.loadSfx('phase_3/audio/dial/minnie.ogg'))
    MinnieDialogueArray.append(base.loader.loadSfx('phase_3/audio/dial/minnie.ogg'))
    MinnieDialogueArray.append(base.loader.loadSfx('phase_3/audio/dial/minnie.ogg'))
    MinnieDialogueArray.append(base.loader.loadSfx('phase_3/audio/dial/minnie.ogg'))
    DaisyDialogueArray.append(base.loader.loadSfx('phase_4/audio/dial/daisy.ogg'))
    DaisyDialogueArray.append(base.loader.loadSfx('phase_4/audio/dial/daisy.ogg'))
    DaisyDialogueArray.append(base.loader.loadSfx('phase_4/audio/dial/daisy.ogg'))
    DaisyDialogueArray.append(base.loader.loadSfx('phase_4/audio/dial/daisy.ogg'))
    DaisyDialogueArray.append(base.loader.loadSfx('phase_4/audio/dial/daisy.ogg'))
    DaisyDialogueArray.append(base.loader.loadSfx('phase_4/audio/dial/daisy.ogg'))
    GoofyDialogueArray.append(base.loader.loadSfx('phase_6/audio/dial/goofy.ogg'))
    GoofyDialogueArray.append(base.loader.loadSfx('phase_6/audio/dial/goofy.ogg'))
    GoofyDialogueArray.append(base.loader.loadSfx('phase_6/audio/dial/goofy.ogg'))
    GoofyDialogueArray.append(base.loader.loadSfx('phase_6/audio/dial/goofy.ogg'))
    GoofyDialogueArray.append(base.loader.loadSfx('phase_6/audio/dial/goofy.ogg'))
    GoofyDialogueArray.append(base.loader.loadSfx('phase_6/audio/dial/goofy.ogg'))
    DonaldDialogueArray.append(base.loader.loadSfx('phase_6/audio/dial/donald.ogg'))
    DonaldDialogueArray.append(base.loader.loadSfx('phase_6/audio/dial/donald.ogg'))
    DonaldDialogueArray.append(base.loader.loadSfx('phase_6/audio/dial/donald.ogg'))
    DonaldDialogueArray.append(base.loader.loadSfx('phase_6/audio/dial/donald.ogg'))
    DonaldDialogueArray.append(base.loader.loadSfx('phase_6/audio/dial/donald.ogg'))
    DonaldDialogueArray.append(base.loader.loadSfx('phase_6/audio/dial/donald.ogg'))
    ChipDialogueArray.append(base.loader.loadSfx('phase_6/audio/dial/chip.ogg'))
    ChipDialogueArray.append(base.loader.loadSfx('phase_6/audio/dial/chip.ogg'))
    ChipDialogueArray.append(base.loader.loadSfx('phase_6/audio/dial/chip.ogg'))
    ChipDialogueArray.append(base.loader.loadSfx('phase_6/audio/dial/chip.ogg'))
    ChipDialogueArray.append(base.loader.loadSfx('phase_6/audio/dial/chip.ogg'))
    ChipDialogueArray.append(base.loader.loadSfx('phase_6/audio/dial/chip.ogg'))
    DaleDialogueArray.append(base.loader.loadSfx('phase_6/audio/dial/dale.ogg'))
    DaleDialogueArray.append(base.loader.loadSfx('phase_6/audio/dial/dale.ogg'))
    DaleDialogueArray.append(base.loader.loadSfx('phase_6/audio/dial/dale.ogg'))
    DaleDialogueArray.append(base.loader.loadSfx('phase_6/audio/dial/dale.ogg'))
    DaleDialogueArray.append(base.loader.loadSfx('phase_6/audio/dial/dale.ogg'))
    DaleDialogueArray.append(base.loader.loadSfx('phase_6/audio/dial/dale.ogg'))
    DoodleDialogueArray.append(base.loader.loadSfx('phase_5/audio/sfx/speak_v1.ogg'))
    DoodleDialogueArray.append(base.loader.loadSfx('phase_5/audio/sfx/speak_v1.ogg'))
    DoodleDialogueArray.append(base.loader.loadSfx('phase_5/audio/sfx/speak_v1.ogg'))
    DoodleDialogueArray.append(base.loader.loadSfx('phase_5/audio/sfx/speak_v1.ogg'))
    DoodleDialogueArray.append(base.loader.loadSfx('phase_5/audio/sfx/speak_v1.ogg'))
    DoodleDialogueArray.append(base.loader.loadSfx('phase_5/audio/sfx/speak_v1.ogg'))


def unloadDialog():
    global BearDialogueArray
    global BossDialogueArray
    global CatDialogueArray
    global ChipDialogueArray
    global DaisyDialogueArray
    global DaleDialogueArray
    global DogDialogueArray
    global DonaldDialogueArray
    global DoodleDialogueArray
    global DuckDialogueArray
    global GoofyDialogueArray
    global GyroDialogueArray
    global HorseDialogueArray
    global MickeyDialogueArray
    global MinnieDialogueArray
    global MonkeyDialogueArray
    global MouseDialogueArray
    global PigDialogueArray
    global RabbitDialogueArray
    global SkeletonDialogueArray
    global SuitDialogueArray
    DogDialogueArray = []
    CatDialogueArray = []
    HorseDialogueArray = []
    RabbitDialogueArray = []
    MouseDialogueArray = []
    DuckDialogueArray = []
    MonkeyDialogueArray = []
    BearDialogueArray = []
    PigDialogueArray = []
    GyroDialogueArray = []
    SuitDialogueArray = []
    SkeletonDialogueArray = []
    BossDialogueArray = []
    MickeyDialogueArray = []
    MinnieDialogueArray = []
    GoofyDialogueArray = []
    DonaldDialogueArray = []
    DaisyDialogueArray = []
    ChipDialogueArray = []
    DaleDialogueArray = []
    DoodleDialogueArray = []


class Toon(Avatar.Avatar, ToonHead):
    notify = DirectNotifyGlobal.directNotify.newCategory('Toon')
    afkTimeout = config.GetInt('afk-timeout', 600)

    def __init__(self):
        try:
            self.Toon_initialized
            return
        except:
            self.Toon_initialized = 1

        Avatar.Avatar.__init__(self)
        ToonHead.__init__(self)
        self.cameraFollow = 0
        self.yesmanTeaser = 0
        self.forwardSpeed = 0.0
        self.rotateSpeed = 0.0
        self.avatarType = 'toon'
        self.motion = Motion.Motion(self)
        self.standWalkRunReverse = None
        self.playingAnim = None
        self.soundTeleport = None
        self.cheesyEffect = ToontownGlobals.CENormal
        self.effectTrack = None
        self.emoteTrack = None
        self.emote = None
        self.stunTrack = None
        self.__bookActors = []
        self.__holeActors = []
        self.rollodex = None
        self.holeClipPath = None
        self.wake = None
        self.lastWakeTime = 0
        self.forceJumpIdle = False
        self.numPies = 0
        self.pieType = 0
        self.pieThrowType = ToontownGlobals.PieThrowArc
        self.pieModel = None
        self.__pieModelType = None
        self.pieScale = 1.0
        self.hatNodes = []
        self.glassesNodes = []
        self.backpackNodes = []
        self.hat = (0, 0, 0)
        self.glasses = (0, 0, 0)
        self.backpack = (0, 0, 0)
        self.shoes = (0, 0, 0)
        self.isStunned = 0
        self.isDisguised = 0
        self.isCog = False
        self.isTransformed = 0
        self.isBecomePet = 0
        self.isGoon = 0
        self.isBossCog = 0
        self.animeChair = None
        self.forceRate = False
        self.rate = 1
        self.bossCogSeq = None
        self.defaultColorScale = None
        self.jar = None
        self.setTag('pieCode', str(ToontownGlobals.PieCodeToon))
        self.setFont(ToontownGlobals.getToonFont())
        self.setSpeechFont(ToontownGlobals.getToonFont())
        self.soundChatBubble = base.loader.loadSfx('phase_3/audio/sfx/GUI_balloon_popup.ogg')
        self.neutralAnim = 'neutral'
        self.runAnim = 'run'
        self.walkAnim = 'walk'
        self.animFSM = ClassicFSM('Toon', [State('off', self.enterOff, self.exitOff),
         State('neutral', self.enterNeutral, self.exitNeutral),
         State('victory', self.enterVictory, self.exitVictory),
         State('Happy', self.enterHappy, self.exitHappy),
         State('Sad', self.enterSad, self.exitSad),
         State('SlowCatching', self.enterSlowCatching, self.exitSlowCatching),
         State('Catching', self.enterCatching, self.exitCatching),
         State('CatchEating', self.enterCatchEating, self.exitCatchEating),
         State('Sleep', self.enterSleep, self.exitSleep),
         State('walk', self.enterWalk, self.exitWalk),
         State('jumpSquat', self.enterJumpSquat, self.exitJumpSquat),
         State('jump', self.enterJump, self.exitJump),
         State('jumpAirborne', self.enterJumpAirborne, self.exitJumpAirborne),
         State('jumpLand', self.enterJumpLand, self.exitJumpLand),
         State('run', self.enterRun, self.exitRun),
         State('swim', self.enterSwim, self.exitSwim),
         State('swimhold', self.enterSwimHold, self.exitSwimHold),
         State('dive', self.enterDive, self.exitDive),
         State('cringe', self.enterCringe, self.exitCringe),
         State('OpenBook', self.enterOpenBook, self.exitOpenBook, ['ReadBook', 'CloseBook']),
         State('ReadBook', self.enterReadBook, self.exitReadBook),
         State('CloseBook', self.enterCloseBook, self.exitCloseBook),
         State('TeleportOut', self.enterTeleportOut, self.exitTeleportOut),
         State('Died', self.enterDied, self.exitDied),
         State('PlaygroundDied', self.enterPlaygroundDied, self.exitPlaygroundDied),
         State('FourBossDied', self.enterFourBossDied, self.exitFourBossDied),
         State('TeleportedOut', self.enterTeleportedOut, self.exitTeleportedOut),
         State('TeleportIn', self.enterTeleportIn, self.exitTeleportIn),
         State('Emote', self.enterEmote, self.exitEmote),
         State('SitStart', self.enterSitStart, self.exitSitStart),
         State('Sit', self.enterSit, self.exitSit),
         State('Push', self.enterPush, self.exitPush),
         State('Squish', self.enterSquish, self.exitSquish),
         State('FallDown', self.enterFallDown, self.exitFallDown),
         State('GolfPuttLoop', self.enterGolfPuttLoop, self.exitGolfPuttLoop),
         State('GolfRotateLeft', self.enterGolfRotateLeft, self.exitGolfRotateLeft),
         State('GolfRotateRight', self.enterGolfRotateRight, self.exitGolfRotateRight),
         State('GolfPuttSwing', self.enterGolfPuttSwing, self.exitGolfPuttSwing),
         State('GolfGoodPutt', self.enterGolfGoodPutt, self.exitGolfGoodPutt),
         State('GolfBadPutt', self.enterGolfBadPutt, self.exitGolfBadPutt),
         State('Flattened', self.enterFlattened, self.exitFlattened),
         State('CogThiefRunning', self.enterCogThiefRunning, self.exitCogThiefRunning),
         State('ScientistJealous', self.enterScientistJealous, self.exitScientistJealous),
         State('ScientistEmcee', self.enterScientistEmcee, self.exitScientistEmcee),
         State('ScientistWork', self.enterScientistWork, self.exitScientistWork),
         State('ScientistLessWork', self.enterScientistLessWork, self.exitScientistLessWork),
         State('ScientistPlay', self.enterScientistPlay, self.enterScientistPlay)], 'off', 'off')
        animStateList = self.animFSM.getStates()
        self.animFSM.enterInitialState()
        self.isAprilFools = time.localtime().tm_mon == 4 and time.localtime().tm_mday == 1
        self.fullToon = True
        self.suit = None
        self.ebicJumpVariable = Sequence()
        self.magicScale = 1
        return

    def stopAnimations(self):
        if hasattr(self, 'animFSM'):
            if not self.animFSM.isInternalStateInFlux():
                self.animFSM.request('off')
            else:
                self.notify.warning('animFSM in flux, state=%s, not requesting off' % self.animFSM.getCurrentState().getName())
        else:
            self.notify.warning('animFSM has been deleted')
        if self.effectTrack != None:
            self.effectTrack.finish()
            self.effectTrack = None
        if self.emoteTrack != None:
            self.emoteTrack.finish()
            self.emoteTrack = None
        if self.stunTrack != None:
            self.stunTrack.finish()
            self.stunTrack = None
        if self.wake:
            self.wake.stop()
            self.wake.destroy()
            self.wake = None
        if self.bossCogSeq:
            self.bossCogSeq.finish()
            self.bossCogSeq = None
        if self.magicRainbow:
            self.magicRainbow.finish()
            self.magicRainbow = None
        if self.ebicJumpVariable:
            self.ebicJumpVariable.finish()
            self.ebicJumpVariable = None
        self.cleanupPieModel()
        return

    def delete(self):
        try:
            self.Toon_deleted
        except:
            self.Toon_deleted = 1
            self.stopAnimations()
            self.rightHands = None
            self.rightHand = None
            self.leftHands = None
            self.leftHand = None
            self.headParts = None
            self.torsoParts = None
            self.hipsParts = None
            self.legsParts = None
            del self.animFSM
            for bookActor in self.__bookActors:
                bookActor.cleanup()

            del self.__bookActors
            for holeActor in self.__holeActors:
                holeActor.cleanup()

            del self.__holeActors
            self.soundTeleport = None
            self.motion.delete()
            self.motion = None
            if self.rollodex:
                self.rollodex.removeNode()
                self.rollodex = None
            Avatar.Avatar.delete(self)
            ToonHead.delete(self)

        return

    def updateToonDNA(self, newDNA, fForce=0, tPose=False):
        self.style.gender = newDNA.getGender()
        oldDNA = self.style
        if fForce or newDNA.head != oldDNA.head:
            self.swapToonHead(newDNA.head)
            if not tPose:
                self.loop('neutral')
        if fForce or newDNA.torso != oldDNA.torso:
            self.swapToonTorso(newDNA.torso, genClothes=0)
            if not tPose:
                self.loop('neutral')
        if fForce or newDNA.legs != oldDNA.legs:
            self.swapToonLegs(newDNA.legs)
            if not tPose:
                self.loop('neutral')
        self.swapToonColor(newDNA)
        self.__swapToonClothes(newDNA)
        self.runAnim = 'run'
        if self.style.getAnimal() == 'riggy' and self.style.torso.startswith('l') and self.style.legs == 'l':
            self.neutralAnim = 'riggyNeutral'
            self.walkAnim = 'riggyWalk'
        else:
            self.neutralAnim = 'neutral'
            self.walkAnim = 'walk'

    def setDNAString(self, dnaString):
        newDNA = ToonDNA.ToonDNA()
        newDNA.makeFromNetString(dnaString)
        self.setDNA(newDNA)

    def setDNA(self, dna):
        if hasattr(self, 'isDisguised'):
            if self.isDisguised:
                return
        if self.style:
            self.updateToonDNA(dna)
        else:
            self.style = dna
            self.generateToon()
            self.initializeDropShadow()
            self.initializeNametag3d()
        self.neutralAnim = 'neutral' if not (self.style.getAnimal() == 'riggy' and self.style.torso.startswith('l') and self.style.legs == 'l') else 'riggyNeutral'
        self.runAnim = 'run'
        self.walkAnim = 'walk' if not (self.style.getAnimal() == 'riggy' and self.style.torso.startswith('l') and self.style.legs == 'l') else 'riggyWalk'

    def parentToonParts(self):
        if self.hasLOD():
            for lodName in self.getLODNames():
                if config.GetBool('want-new-anims', 1):
                    if not self.getPart('torso', lodName).find('**/def_head').isEmpty():
                        self.attach('head', 'torso', 'def_head', lodName)
                    else:
                        self.attach('head', 'torso', 'joint_head', lodName)
                else:
                    self.attach('head', 'torso', 'joint_head', lodName)
                self.attach('torso', 'legs', 'joint_hips', lodName)

        else:
            self.attach('head', 'torso', 'joint_head')
            self.attach('torso', 'legs', 'joint_hips')

    def unparentToonParts(self):
        if self.hasLOD():
            for lodName in self.getLODNames():
                self.getPart('head', lodName).reparentTo(self.getLOD(lodName))
                self.getPart('torso', lodName).reparentTo(self.getLOD(lodName))
                self.getPart('legs', lodName).reparentTo(self.getLOD(lodName))

        else:
            self.getPart('head').reparentTo(self.getGeomNode())
            self.getPart('torso').reparentTo(self.getGeomNode())
            self.getPart('legs').reparentTo(self.getGeomNode())

    def setLODs(self):
        self.setLODNode()
        levelOneIn = config.GetInt('lod1-in', 20)
        levelOneOut = config.GetInt('lod1-out', 0)
        levelTwoIn = config.GetInt('lod2-in', 80)
        levelTwoOut = config.GetInt('lod2-out', 20)
        levelThreeIn = config.GetInt('lod3-in', 280)
        levelThreeOut = config.GetInt('lod3-out', 80)
        self.addLOD(1000, levelOneIn, levelOneOut)
        self.addLOD(500, levelTwoIn, levelTwoOut)
        self.addLOD(250, levelThreeIn, levelThreeOut)
        if config.GetBool('always-max-lod', False):
            self.useLOD(1000)

    def generateToon(self):
        self.setLODs()
        self.generateToonLegs()
        self.generateToonHead()
        self.generateToonTorso()
        self.generateToonColor()
        self.parentToonParts()
        self.rescaleToon()
        self.resetHeight()
        self.setupToonNodes()
        self.setBlend(frameBlend=config.GetBool('interpolate-animations', True))

    def setupToonNodes(self):
        rightHand = NodePath('rightHand')
        self.rightHand = None
        self.rightHands = []
        leftHand = NodePath('leftHand')
        self.leftHands = []
        self.leftHand = None
        for lodName in self.getLODNames():
            hand = self.getPart('torso', lodName).find('**/joint_Rhold')
            if config.GetBool('want-new-anims', 1):
                if not self.getPart('torso', lodName).find('**/def_joint_right_hold').isEmpty():
                    hand = self.getPart('torso', lodName).find('**/def_joint_right_hold')
            else:
                hand = self.getPart('torso', lodName).find('**/joint_Rhold')
            self.rightHands.append(hand)
            rightHand = rightHand.instanceTo(hand)
            if config.GetBool('want-new-anims', 1):
                if not self.getPart('torso', lodName).find('**/def_joint_left_hold').isEmpty():
                    hand = self.getPart('torso', lodName).find('**/def_joint_left_hold')
            else:
                hand = self.getPart('torso', lodName).find('**/joint_Lhold')
            self.leftHands.append(hand)
            leftHand = leftHand.instanceTo(hand)
            if self.rightHand == None:
                self.rightHand = rightHand
            if self.leftHand == None:
                self.leftHand = leftHand

        self.headParts = self.findAllMatches('**/__Actor_head')
        self.legsParts = self.findAllMatches('**/__Actor_legs')
        self.hipsParts = self.legsParts.findAllMatches('**/joint_hips')
        self.torsoParts = self.hipsParts.findAllMatches('**/__Actor_torso')
        return

    def initializeBodyCollisions(self, collIdStr):
        Avatar.Avatar.initializeBodyCollisions(self, collIdStr)
        if not self.ghostMode:
            self.collNode.setCollideMask(self.collNode.getIntoCollideMask() | ToontownGlobals.PieBitmask)

    def getBookActors(self):
        if self.__bookActors:
            return self.__bookActors
        bookActor = Actor.Actor('phase_3.5/models/props/book-mod', {'book': 'phase_3.5/models/props/book-chan'})
        bookActor2 = Actor.Actor(other=bookActor)
        bookActor3 = Actor.Actor(other=bookActor)
        bookActor.setBlend(frameBlend=config.GetBool('interpolate-animations', True))
        bookActor2.setBlend(frameBlend=config.GetBool('interpolate-animations', True))
        bookActor3.setBlend(frameBlend=config.GetBool('interpolate-animations', True))
        self.__bookActors = [bookActor, bookActor2, bookActor3]
        hands = self.getRightHands()
        for bookActor, hand in zip(self.__bookActors, hands):
            bookActor.reparentTo(hand)
            bookActor.hide()

        return self.__bookActors

    def getHoleActors(self):
        if self.__holeActors:
            return self.__holeActors
        holeActor = Actor.Actor('phase_3.5/models/props/portal-mod', {'hole': 'phase_3.5/models/props/portal-chan'})
        if config.GetBool('want-retro-mode', False):
            holeActor.setTexture(loader.loadTexture('phase_3/maps/avatar_palette_2tmla_1_retro.jpg', 'phase_3/maps/avatar_palette_2tmla_1_retro_a.rgb'), 1)
        holeActor2 = Actor.Actor(other=holeActor)
        holeActor3 = Actor.Actor(other=holeActor)
        holeActor.setBlend(frameBlend=config.GetBool('interpolate-animations', True))
        holeActor2.setBlend(frameBlend=config.GetBool('interpolate-animations', True))
        holeActor3.setBlend(frameBlend=config.GetBool('interpolate-animations', True))
        self.__holeActors = [holeActor, holeActor2, holeActor3]
        for ha in self.__holeActors:
            if hasattr(self, 'uniqueName'):
                holeName = self.uniqueName('toon-portal')
            else:
                holeName = 'toon-portal'
            ha.setName(holeName)

        return self.__holeActors

    def rescaleToon(self):
        animalStyle = self.style.getAnimal()
        bodyScale = ToontownGlobals.toonBodyScales[animalStyle]
        headScale = ToontownGlobals.toonHeadScales[animalStyle]
        self.setAvatarScale(bodyScale)
        for lod in self.getLODNames():
            self.getPart('head', lod).setScale(headScale)

    def getBodyScale(self):
        animalStyle = self.style.getAnimal()
        bodyScale = ToontownGlobals.toonBodyScales[animalStyle]
        return bodyScale

    def resetHeight(self):
        if hasattr(self, 'style') and self.style:
            animal = self.style.getAnimal()
            bodyScale = ToontownGlobals.toonBodyScales[animal]
            headScale = ToontownGlobals.toonHeadScales[animal][2]
            shoulderHeight = ToontownGlobals.legHeightDict[self.style.legs] * bodyScale + ToontownGlobals.torsoHeightDict[self.style.torso] * bodyScale
            height = shoulderHeight + ToontownGlobals.headHeightDict[self.style.head] * headScale
            self.shoulderHeight = shoulderHeight
            if self.cheesyEffect == ToontownGlobals.CEBigToon or self.cheesyEffect == ToontownGlobals.CEBigWhite:
                height *= ToontownGlobals.BigToonScale
            else:
                if self.cheesyEffect == ToontownGlobals.CESmallToon:
                    height *= ToontownGlobals.SmallToonScale
            if self.animeChair:
                height = 10
            self.setHeight(height * self.magicScale)

    def generateToonLegs(self, copy=1):
        legStyle = self.style.legs
        filePrefix = LegDict.get(legStyle)
        if filePrefix is None:
            self.notify.error('unknown leg style: %s' % legStyle)
        self.loadModel('phase_3' + filePrefix + '1000', 'legs', '1000', copy)
        self.loadModel('phase_3' + filePrefix + '500', 'legs', '500', copy)
        self.loadModel('phase_3' + filePrefix + '250', 'legs', '250', copy)
        if not copy:
            self.showPart('legs', '1000')
            self.showPart('legs', '500')
            self.showPart('legs', '250')
        self.loadAnims(LegsAnimDict[legStyle], 'legs', '1000')
        self.loadAnims(LegsAnimDict[legStyle], 'legs', '500')
        self.loadAnims(LegsAnimDict[legStyle], 'legs', '250')
        self.findAllMatches('**/boots_short').stash()
        self.findAllMatches('**/boots_long').stash()
        self.findAllMatches('**/shoes').stash()
        return

    def swapToonLegs(self, legStyle, copy=1):
        self.unparentToonParts()
        self.removePart('legs', '1000')
        self.removePart('legs', '500')
        self.removePart('legs', '250')
        if 'legs' in self._Actor__commonBundleHandles:
            del self._Actor__commonBundleHandles['legs']
        self.style.legs = legStyle
        self.generateToonLegs(copy)
        self.generateToonColor()
        self.parentToonParts()
        self.rescaleToon()
        self.resetHeight()
        del self.shadowJoint
        self.initializeDropShadow()
        self.initializeNametag3d()
        self.setBlend(frameBlend=config.GetBool('interpolate-animations', True))

    def generateToonTorso(self, copy=1, genClothes=1):
        torsoStyle = self.style.torso
        filePrefix = TorsoDict.get(torsoStyle)
        if filePrefix is None:
            self.notify.error('unknown torso style: %s' % torsoStyle)
        if len(torsoStyle) == 1:
            self.loadModel('phase_14' + filePrefix + '1000', 'torso', '1000', copy)
            self.loadModel('phase_14' + filePrefix + '1000', 'torso', '500', copy)
            self.loadModel('phase_14' + filePrefix + '1000', 'torso', '250', copy)
        else:
            self.loadModel('phase_3' + filePrefix + '1000', 'torso', '1000', copy)
            self.loadModel('phase_3' + filePrefix + '500', 'torso', '500', copy)
            self.loadModel('phase_3' + filePrefix + '250', 'torso', '250', copy)
        if not copy:
            self.showPart('torso', '1000')
            self.showPart('torso', '500')
            self.showPart('torso', '250')
        self.loadAnims(TorsoAnimDict[torsoStyle], 'torso', '1000')
        self.loadAnims(TorsoAnimDict[torsoStyle], 'torso', '500')
        self.loadAnims(TorsoAnimDict[torsoStyle], 'torso', '250')
        if genClothes == 1 and not len(torsoStyle) == 1:
            self.generateToonClothes()
        return

    def swapToonTorso(self, torsoStyle, copy=1, genClothes=1):
        self.unparentToonParts()
        self.removePart('torso', '1000')
        self.removePart('torso', '500')
        self.removePart('torso', '250')
        if 'torso' in self._Actor__commonBundleHandles:
            del self._Actor__commonBundleHandles['torso']
        self.style.torso = torsoStyle
        self.generateToonTorso(copy, genClothes)
        self.generateToonColor()
        self.parentToonParts()
        self.rescaleToon()
        self.resetHeight()
        self.setupToonNodes()
        self.generateBackpack()
        self.setBlend(frameBlend=config.GetBool('interpolate-animations', True))

    def generateToonHead(self, copy=1):
        headHeight = ToonHead.generateToonHead(self, copy, self.style, ('1000', '500',
                                                                        '250'))
        if self.style.getAnimal() == 'dog' or self.style.getAnimal() == 'riggy':
            self.loadAnims(HeadAnimDict[self.style.head], 'head', '1000')
            self.loadAnims(HeadAnimDict[self.style.head], 'head', '500')
            self.loadAnims(HeadAnimDict[self.style.head], 'head', '250')

    def swapToonHead(self, headStyle, copy=1):
        self.stopLookAroundNow()
        self.eyelids.request('open')
        self.unparentToonParts()
        self.removePart('head', '1000')
        self.removePart('head', '500')
        self.removePart('head', '250')
        if 'head' in self._Actor__commonBundleHandles:
            del self._Actor__commonBundleHandles['head']
        self.style.head = headStyle
        self.generateToonHead(copy)
        self.generateToonColor()
        self.parentToonParts()
        self.rescaleToon()
        self.resetHeight()
        self.eyelids.request('open')
        self.setBlend(frameBlend=config.GetBool('interpolate-animations', True))
        self.startLookAround()

    def generateToonColor(self):
        ToonHead.generateToonColor(self, self.style)
        magicParallel = Parallel()
        armColor = self.style.getArmColor()
        gloveColor = self.style.getGloveColor()
        legColor = self.style.getLegColor()
        for lodName in self.getLODNames():
            torso = self.getPart('torso', lodName)
            if len(self.style.torso) == 1:
                parts = torso.findAllMatches('**/torso*')
                parts.setColor(armColor)
            for pieceName in ('arms', 'neck'):
                piece = torso.find('**/' + pieceName)
                piece.setColor(armColor)

            hands = torso.find('**/hands')
            hands.setColor(gloveColor)
            legs = self.getPart('legs', lodName)
            if len(self.style.torso) == 1:
                thisPart = self.getPart('torso', lodName)
                top = thisPart.find('**/torso')
                top.setColor(armColor)
            for pieceName in ('legs', 'feet'):
                piece = legs.find('**/%s;+s' % pieceName)
                piece.setColor(legColor)

        if self.cheesyEffect == ToontownGlobals.CEGreenToon:
            self.reapplyCheesyEffect()
        torsoPieces = self.getPieces(('torso', ('arms', 'neck')))
        if len(self.style.torso) == 1:
            torsoPieces = self.getPieces(('torso', ('arms', 'neck', 'torso')))
        glovePieces = self.getPieces(('torso', 'hands'))
        legPieces = self.getPieces(('legs', ('legs', 'feet')))
        if self.style.head[0] == 'h' or self.style.head[0] == 'p':
            headPieces = self.getPieces(('head', '*head*'))
            if self.style.head[0] == 'd':
                for h in headPieces:
                    if str(h).lower().__contains__('muzzle'):
                        headPieces.remove(h)

        else:
            if self.style.head[0] == 'd':
                headPieces = []
                for h in self.findAllMatches('**/head-front'):
                    headPieces.append(h)

                for h in self.findAllMatches('**/head'):
                    headPieces.append(h)

            else:
                headPieces = self.getPieces(('head', ('*head*', '*ear*')))
        allPieces = []
        if self.style.armColor == 39:
            allPieces.append(torsoPieces)
        if self.style.legColor == 39:
            allPieces.append(legPieces)
        if self.style.headColor == 39:
            allPieces.append(headPieces)
        if self.style.gloveColor == 39:
            allPieces.append(glovePieces)
        for pieces in allPieces:
            for piece in pieces:
                magicParallel.append(Sequence(LerpColorInterval(piece, duration=1, color=VBase4(0.996094, 0.898438, 0.320312, 1.0)), LerpColorInterval(piece, duration=1, color=VBase4(0.304688, 0.96875, 0.402344, 1.0)), LerpColorInterval(piece, duration=1, color=VBase4(0.191406, 0.5625, 0.773438, 1.0)), LerpColorInterval(piece, duration=0.5, color=VBase4(0.546875, 0.28125, 0.75, 1.0)), LerpColorInterval(piece, duration=0.5, color=VBase4(0.933594, 0.265625, 0.28125, 1.0))))

        if self.style.headColor == 39 or self.style.armColor == 39 or self.style.gloveColor == 39 or self.style.legColor == 39:
            self.magicRainbow.append(magicParallel)
            self.magicRainbow.loop()

    def swapToonColor(self, dna):
        self.setStyle(dna)
        self.generateToonColor()

    def __swapToonClothes(self, dna):
        self.setStyle(dna)
        self.generateToonClothes(fromNet=1)

    def sendLogSuspiciousEvent(self, msg):
        pass

    def generateToonClothes(self, fromNet=0):
        swappedTorso = 0
        if self.hasLOD():
            if self.style.getGender() == 'f' and fromNet == 0:
                try:
                    bottomPair = ToonDNA.GirlBottoms[self.style.botTex]
                except:
                    bottomPair = ToonDNA.GirlBottoms[0]

                if self.style.torso[1] == 's' and bottomPair[1] == ToonDNA.SKIRT:
                    self.swapToonTorso(self.style.torso[0] + 'd', genClothes=0)
                    swappedTorso = 1
                elif self.style.torso[1] == 'd' and bottomPair[1] == ToonDNA.SHORTS:
                    self.swapToonTorso(self.style.torso[0] + 's', genClothes=0)
                    swappedTorso = 1
            try:
                texName = ToonDNA.Shirts[self.style.topTex]
            except:
                texName = ToonDNA.Shirts[0]
            else:
                shirtTex = loader.loadTexture(texName, okMissing=True)
                if shirtTex is None:
                    self.sendLogSuspiciousEvent('failed to load texture %s' % texName)
                    shirtTex = loader.loadTexture(ToonDNA.Shirts[0])
                shirtTex.setMinfilter(Texture.FTLinearMipmapLinear)
                shirtTex.setMagfilter(Texture.FTLinear)
                try:
                    shirtColor = ToonDNA.ClothesColors[self.style.topTexColor]
                except:
                    shirtColor = ToonDNA.ClothesColors[0]
                else:
                    try:
                        texName = ToonDNA.Sleeves[self.style.sleeveTex]
                    except:
                        texName = ToonDNA.Sleeves[0]
                    else:
                        sleeveTex = loader.loadTexture(texName, okMissing=True)
                        if sleeveTex is None:
                            self.sendLogSuspiciousEvent('failed to load texture %s' % texName)
                            sleeveTex = loader.loadTexture(ToonDNA.Sleeves[0])
                        sleeveTex.setMinfilter(Texture.FTLinearMipmapLinear)
                        sleeveTex.setMagfilter(Texture.FTLinear)
                        try:
                            sleeveColor = ToonDNA.ClothesColors[self.style.sleeveTexColor]
                        except:
                            sleeveColor = ToonDNA.ClothesColors[0]

                    if self.style.getGender() == 'm':
                        try:
                            texName = ToonDNA.BoyShorts[self.style.botTex]
                        except:
                            texName = ToonDNA.BoyShorts[0]

                    else:
                        try:
                            texName = ToonDNA.GirlBottoms[self.style.botTex][0]
                        except:
                            texName = ToonDNA.GirlBottoms[0][0]

                bottomTex = loader.loadTexture(texName, okMissing=True)
                if bottomTex is None:
                    self.sendLogSuspiciousEvent('failed to load texture %s' % texName)
                    if self.style.getGender() == 'm':
                        bottomTex = loader.loadTexture(ToonDNA.BoyShorts[0])
                    else:
                        bottomTex = loader.loadTexture(ToonDNA.GirlBottoms[0][0])
                bottomTex.setMinfilter(Texture.FTLinearMipmapLinear)
                bottomTex.setMagfilter(Texture.FTLinear)
                try:
                    bottomColor = ToonDNA.ClothesColors[self.style.botTexColor]
                except:
                    bottomColor = ToonDNA.ClothesColors[0]

            darkBottomColor = bottomColor * 0.5
            darkBottomColor.setW(1.0)
            for lodName in self.getLODNames():
                thisPart = self.getPart('torso', lodName)
                if len(self.style.torso) == 2:
                    top = thisPart.find('**/torso-top')
                    if self.isAprilFools:
                        pass
                    else:
                        top.setTexture(shirtTex, 1)
                        top.setColor(shirtColor)
                    sleeves = thisPart.find('**/sleeves')
                    if self.isAprilFools:
                        pass
                    else:
                        sleeves.setTexture(sleeveTex, 1)
                        sleeves.setColor(sleeveColor)
                    bottoms = thisPart.findAllMatches('**/torso-bot')
                    for bottomNum in range(0, bottoms.getNumPaths()):
                        bottom = bottoms.getPath(bottomNum)
                        if self.isAprilFools:
                            pass
                        else:
                            bottom.setTexture(bottomTex, 1)
                            bottom.setColor(bottomColor)

                else:
                    top = thisPart.find('**/torso')
                caps = thisPart.findAllMatches('**/torso-bot-cap')
                caps.setColor(darkBottomColor)

        return swappedTorso

    def generateHat(self, fromRTM=False):
        hat = self.getHat()
        if hat[0] >= len(ToonDNA.HatModels):
            self.sendLogSuspiciousEvent('tried to put a wrong hat idx %d' % hat[0])
            return
        if len(self.hatNodes) > 0:
            for hatNode in self.hatNodes:
                hatNode.removeNode()

            self.hatNodes = []
        self.showEars()
        if hat[0] != 0:
            hatGeom = loader.loadModel(ToonDNA.HatModels[hat[0]], okMissing=True)
            if hatGeom:
                if hat[0] == 54:
                    self.hideEars()
                if hat[1] != 0:
                    texName = ToonDNA.HatTextures[hat[1]]
                    tex = loader.loadTexture(texName, okMissing=True)
                    if tex is None:
                        self.sendLogSuspiciousEvent('failed to load texture %s' % texName)
                    else:
                        tex.setMinfilter(Texture.FTLinearMipmapLinear)
                        tex.setMagfilter(Texture.FTLinear)
                        hatGeom.setTexture(tex, 1)
                if fromRTM:
                    reload(AccessoryGlobals)
                transOffset = None
                if AccessoryGlobals.ExtendedHatTransTable.get(hat[0]):
                    transOffset = AccessoryGlobals.ExtendedHatTransTable[hat[0]].get(self.style.head[:2])
                if transOffset is None:
                    transOffset = AccessoryGlobals.HatTransTable.get(self.style.head[:2])
                    if transOffset is None:
                        return
                hatGeom.setPos(transOffset[0][0], transOffset[0][1], transOffset[0][2])
                hatGeom.setHpr(transOffset[1][0], transOffset[1][1], transOffset[1][2])
                hatGeom.setScale(transOffset[2][0], transOffset[2][1], transOffset[2][2])
                headNodes = self.findAllMatches('**/__Actor_head')
                for headNode in headNodes:
                    hatNode = headNode.attachNewNode('hatNode')
                    self.hatNodes.append(hatNode)
                    hatGeom.instanceTo(hatNode)

        return

    def generateGlasses(self, fromRTM=False):
        glasses = self.getGlasses()
        if glasses[0] >= len(ToonDNA.GlassesModels):
            self.sendLogSuspiciousEvent('tried to put a wrong glasses idx %d' % glasses[0])
            return
        if len(self.glassesNodes) > 0:
            for glassesNode in self.glassesNodes:
                glassesNode.removeNode()

            self.glassesNodes = []
        self.showEyelashes()
        if glasses[0] != 0:
            glassesGeom = loader.loadModel(ToonDNA.GlassesModels[glasses[0]], okMissing=True)
            if glassesGeom:
                if glasses[0] in (15, 16):
                    self.hideEyelashes()
                if glasses[1] != 0:
                    texName = ToonDNA.GlassesTextures[glasses[1]]
                    tex = loader.loadTexture(texName, okMissing=True)
                    if tex is None:
                        self.sendLogSuspiciousEvent('failed to load texture %s' % texName)
                    else:
                        tex.setMinfilter(Texture.FTLinearMipmapLinear)
                        tex.setMagfilter(Texture.FTLinear)
                        glassesGeom.setTexture(tex, 1)
                if fromRTM:
                    reload(AccessoryGlobals)
                transOffset = None
                if AccessoryGlobals.ExtendedGlassesTransTable.get(glasses[0]):
                    transOffset = AccessoryGlobals.ExtendedGlassesTransTable[glasses[0]].get(self.style.head[:2])
                if transOffset is None:
                    transOffset = AccessoryGlobals.GlassesTransTable.get(self.style.head[:2])
                    if transOffset is None:
                        return
                glassesGeom.setPos(transOffset[0][0], transOffset[0][1], transOffset[0][2])
                glassesGeom.setHpr(transOffset[1][0], transOffset[1][1], transOffset[1][2])
                glassesGeom.setScale(transOffset[2][0], transOffset[2][1], transOffset[2][2])
                headNodes = self.findAllMatches('**/__Actor_head')
                for headNode in headNodes:
                    glassesNode = headNode.attachNewNode('glassesNode')
                    self.glassesNodes.append(glassesNode)
                    glassesGeom.instanceTo(glassesNode)

        return

    def generateBackpack(self, fromRTM=False):
        backpack = self.getBackpack()
        if backpack[0] >= len(ToonDNA.BackpackModels):
            self.sendLogSuspiciousEvent('tried to put a wrong backpack idx %d' % backpack[0])
            return
        if len(self.backpackNodes) > 0:
            for backpackNode in self.backpackNodes:
                backpackNode.removeNode()

            self.backpackNodes = []
        if backpack[0] != 0:
            geom = loader.loadModel(ToonDNA.BackpackModels[backpack[0]], okMissing=True)
            if geom:
                if backpack[1] != 0:
                    texName = ToonDNA.BackpackTextures[backpack[1]]
                    tex = loader.loadTexture(texName, okMissing=True)
                    if tex is None:
                        self.sendLogSuspiciousEvent('failed to load texture %s' % texName)
                    else:
                        tex.setMinfilter(Texture.FTLinearMipmapLinear)
                        tex.setMagfilter(Texture.FTLinear)
                        geom.setTexture(tex, 1)
                if fromRTM:
                    reload(AccessoryGlobals)
                transOffset = None
                if AccessoryGlobals.ExtendedBackpackTransTable.get(backpack[0]):
                    transOffset = AccessoryGlobals.ExtendedBackpackTransTable[backpack[0]].get(self.style.torso[:1])
                if transOffset is None:
                    transOffset = AccessoryGlobals.BackpackTransTable.get(self.style.torso[:1])
                    if transOffset is None:
                        return
                geom.setPos(transOffset[0][0], transOffset[0][1], transOffset[0][2])
                geom.setHpr(transOffset[1][0], transOffset[1][1], transOffset[1][2])
                geom.setScale(transOffset[2][0], transOffset[2][1], transOffset[2][2])
                nodes = self.findAllMatches('**/def_joint_attachFlower')
                for node in nodes:
                    theNode = node.attachNewNode('backpackNode')
                    self.backpackNodes.append(theNode)
                    geom.instanceTo(theNode)

        return

    def generateShoes(self):
        shoes = self.getShoes()
        if shoes[0] >= len(ToonDNA.ShoesModels):
            self.sendLogSuspiciousEvent('tried to put a wrong shoes idx %d' % shoes[0])
            return
        self.findAllMatches('**/feet;+s').stash()
        self.findAllMatches('**/boots_short;+s').stash()
        self.findAllMatches('**/boots_long;+s').stash()
        self.findAllMatches('**/shoes;+s').stash()
        geoms = self.findAllMatches('**/%s;+s' % ToonDNA.ShoesModels[shoes[0]])
        for geom in geoms:
            geom.unstash()

        if shoes[0] != 0:
            for geom in geoms:
                texName = ToonDNA.ShoesTextures[shoes[1]]
                if self.style.legs == 'l' and shoes[0] == 3:
                    texName = texName[:-4] + 'LL.jpg'
                tex = loader.loadTexture(texName, okMissing=True)
                if tex is None:
                    self.sendLogSuspiciousEvent('failed to load texture %s' % texName)
                else:
                    tex.setMinfilter(Texture.FTLinearMipmapLinear)
                    tex.setMagfilter(Texture.FTLinear)
                    geom.setTexture(tex, 1)

        return

    def generateToonAccessories(self):
        self.generateHat()
        self.generateGlasses()
        self.generateBackpack()
        self.generateShoes()

    def setHat(self, hatIdx, textureIdx, colorIdx, fromRTM=False):
        self.hat = (hatIdx, textureIdx, colorIdx)
        self.generateHat(fromRTM=fromRTM)

    def getHat(self):
        return self.hat

    def setGlasses(self, glassesIdx, textureIdx, colorIdx, fromRTM=False):
        self.glasses = (glassesIdx, textureIdx, colorIdx)
        self.generateGlasses(fromRTM=fromRTM)

    def getGlasses(self):
        return self.glasses

    def setBackpack(self, backpackIdx, textureIdx, colorIdx, fromRTM=False):
        self.backpack = (backpackIdx, textureIdx, colorIdx)
        self.generateBackpack(fromRTM=fromRTM)

    def getBackpack(self):
        return self.backpack

    def setShoes(self, shoesIdx, textureIdx, colorIdx):
        self.shoes = (
         shoesIdx, textureIdx, colorIdx)
        self.generateShoes()

    def getShoes(self):
        return self.shoes

    def getDialogueArray(self):
        animalType = self.style.getType()
        if self.isTransformed:
            charType = self.char.style.getCharName()
        else:
            charType = None
        if self.isBecomePet:
            animalType = 'doodle'
        if base.cr.newsManager:
            if base.cr.newsManager.isHolidayRunning(ToontownGlobals.APRIL_FOOLS_COSTUMES):
                animalType = random.choice(['dog', 'cat', 'mouse', 'horse', 'rabbit', 'duck', 'monkey', 'bear', 'pig', 'suit', 'skeleton'])
            elif self.isCog == 2 or self.isCog == 6 or self.isCog == 69 or self.isCog == 31:
                animalType = 'skeleton'
            elif self.isCog != 5 and self.isCog or self.isGoon:
                animalType = 'suit'
            elif self.isBossCog:
                animalType = 'boss'
            elif self.isBecomePet:
                animalType = 'doodle'
        if charType == 'mickey' or charType == 'vampire_mickey':
            dialogueArray = MickeyDialogueArray
        else:
            if charType == 'minnie' or charType == 'witch_minnie':
                dialogueArray = MinnieDialogueArray
            else:
                if charType == 'goofy' or charType == 'super_goofy':
                    dialogueArray = GoofyDialogueArray
                else:
                    if charType == 'donald-wheel' or charType == 'franken_donald':
                        dialogueArray = DonaldDialogueArray
                    else:
                        if charType == 'daisy' or charType == 'sockHop_daisy':
                            dialogueArray = DaisyDialogueArray
                        else:
                            if charType == 'pluto' or charType == 'western_pluto':
                                dialogueArray = DogDialogueArray
                            else:
                                if charType == 'chip' or charType == 'police_chip':
                                    dialogueArray = ChipDialogueArray
                                else:
                                    if charType == 'dale' or charType == 'jailbird_dale':
                                        dialogueArray = DaleDialogueArray
                                    else:
                                        if charType == 'donald' or charType == 'clarabelle':
                                            dialogueArray = None
                                        else:
                                            if animalType == 'dog':
                                                dialogueArray = DogDialogueArray
                                            else:
                                                if animalType == 'cat':
                                                    dialogueArray = CatDialogueArray
                                                else:
                                                    if animalType == 'horse':
                                                        dialogueArray = HorseDialogueArray
                                                    else:
                                                        if animalType == 'mouse':
                                                            dialogueArray = MouseDialogueArray
                                                        else:
                                                            if animalType == 'rabbit':
                                                                dialogueArray = RabbitDialogueArray
                                                            else:
                                                                if animalType == 'duck':
                                                                    dialogueArray = DuckDialogueArray
                                                                else:
                                                                    if animalType == 'monkey':
                                                                        dialogueArray = MonkeyDialogueArray
                                                                    else:
                                                                        if animalType == 'bear':
                                                                            dialogueArray = BearDialogueArray
                                                                        else:
                                                                            if animalType == 'pig':
                                                                                dialogueArray = PigDialogueArray
                                                                            else:
                                                                                if animalType == 'scrooge':
                                                                                    dialogueArray = ScroogeDialogueArray
                                                                                else:
                                                                                    if animalType == 'gyro':
                                                                                        dialogueArray = GyroDialogueArray
                                                                                    else:
                                                                                        if animalType == 'riggy':
                                                                                            dialogueArray = RabbitDialogueArray
                                                                                        else:
                                                                                            if animalType == 'suit':
                                                                                                dialogueArray = SuitDialogueArray
                                                                                            else:
                                                                                                if animalType == 'skeleton':
                                                                                                    dialogueArray = SkeletonDialogueArray
                                                                                                else:
                                                                                                    if animalType == 'boss':
                                                                                                        dialogueArray = BossDialogueArray
                                                                                                    else:
                                                                                                        if animalType == 'doodle':
                                                                                                            dialogueArray = DoodleDialogueArray
                                                                                                        else:
                                                                                                            dialogueArray = None
        if self.cheesyEffect == ToontownGlobals.CEMagicCat or self.cheesyEffect == ToontownGlobals.CEAnime:
            dialogueArray = None
        return dialogueArray

    def getShadowJoint(self):
        if hasattr(self, 'shadowJoint'):
            return self.shadowJoint
        shadowJoint = NodePath('shadowJoint')
        for lodName in self.getLODNames():
            joint = self.getPart('legs', lodName).find('**/joint_shadow')
            shadowJoint = shadowJoint.instanceTo(joint)

        self.shadowJoint = shadowJoint
        return shadowJoint

    def getNametagJoints(self):
        joints = []
        for lodName in self.getLODNames():
            bundle = self.getPartBundle('legs', lodName)
            joint = bundle.findChild('joint_nameTag')
            if joint:
                joints.append(joint)

        return joints

    def getRightHands(self):
        return self.rightHands

    def getLeftHands(self):
        return self.leftHands

    def getHeadParts(self):
        return self.headParts

    def getHipsParts(self):
        return self.hipsParts

    def getTorsoParts(self):
        return self.torsoParts

    def getLegsParts(self):
        return self.legsParts

    def findSomethingToLookAt(self):
        if self.randGen.random() < 0.1 or not hasattr(self, 'cr'):
            x = self.randGen.choice((-0.8, -0.5, 0, 0.5, 0.8))
            y = self.randGen.choice((-0.5, 0, 0.5, 0.8))
            self.lerpLookAt(Point3(x, 1.5, y), blink=1)
            return
        nodePathList = []
        for id, obj in self.cr.doId2do.items():
            if hasattr(obj, 'getStareAtNodeAndOffset') and obj != self:
                node, offset = obj.getStareAtNodeAndOffset()
                if node.getY(self) > 0.0:
                    nodePathList.append((node, offset))

        if nodePathList:
            nodePathList.sort(lambda x, y: cmp(x[0].getDistance(self), y[0].getDistance(self)))
            if len(nodePathList) >= 2:
                if self.randGen.random() < 0.9:
                    chosenNodePath = nodePathList[0]
                else:
                    chosenNodePath = nodePathList[1]
            else:
                chosenNodePath = nodePathList[0]
            self.lerpLookAt(chosenNodePath[0].getPos(self), blink=1)
        else:
            ToonHead.findSomethingToLookAt(self)

    def setForceJumpIdle(self, value):
        self.forceJumpIdle = value

    def setupPickTrigger(self):
        Avatar.Avatar.setupPickTrigger(self)
        torso = self.getPart('torso', '1000')
        if torso == None:
            return 0
        self.pickTriggerNp.reparentTo(torso)
        size = self.style.getTorsoSize()
        if size == 'short':
            self.pickTriggerNp.setPosHprScale(0, 0, 0.5, 0, 0, 0, 1.5, 1.5, 2)
        else:
            if size == 'medium':
                self.pickTriggerNp.setPosHprScale(0, 0, 0.5, 0, 0, 0, 1, 1, 2)
            else:
                self.pickTriggerNp.setPosHprScale(0, 0, 1, 0, 0, 0, 1, 1, 2)
        return 1

    def showBooks(self):
        for bookActor in self.getBookActors():
            bookActor.show()

    def hideBooks(self):
        for bookActor in self.getBookActors():
            bookActor.hide()

    def getWake(self):
        if not self.wake:
            self.wake = Wake.Wake(render, self)
        return self.wake

    def getJar(self):
        if not self.jar:
            self.jar = loader.loadModel('phase_5.5/models/estate/jellybeanJar')
            self.jar.setP(290.0)
            self.jar.setY(0.5)
            self.jar.setZ(0.5)
            self.jar.setScale(0.0)
        return self.jar

    def removeJar(self):
        if self.jar:
            self.jar.removeNode()
            self.jar = None
        return

    def setSpeed(self, forwardSpeed, rotateSpeed):
        pastRot = self.rotateSpeed
        self.forwardSpeed = forwardSpeed
        self.rotateSpeed = rotateSpeed
        action = None
        if self.standWalkRunReverse != None:
            if forwardSpeed >= ToontownGlobals.RunCutOff:
                action = OTPGlobals.RUN_INDEX
            else:
                if forwardSpeed > ToontownGlobals.WalkCutOff:
                    action = OTPGlobals.WALK_INDEX
                else:
                    if forwardSpeed < -ToontownGlobals.WalkCutOff:
                        action = OTPGlobals.REVERSE_INDEX
                    else:
                        if rotateSpeed != 0.0:
                            action = OTPGlobals.WALK_INDEX
                        else:
                            action = OTPGlobals.STAND_INDEX
            anim, rate = self.standWalkRunReverse[action]
            if self.forceRate:
                rate = self.rate
            pastAnim, pastRate = self.playingAnim, self.playingRate
            self.motion.enter()
            self.motion.setState(anim, rate)
            if anim != self.playingAnim:
                self.playingAnim = anim
                self.playingRate = rate
                self.stop()
                self.loop(anim)
                self.setPlayRate(rate, anim)
                if self.isDisguised:
                    rightHand = self.suit.rightHand
                    numChildren = rightHand.getNumChildren()
                    if numChildren > 0:
                        anim = 'tray-' + anim
                        if anim == 'tray-run':
                            anim = 'tray-walk'
                    self.suit.stop()
                    self.suit.loop(anim)
                    self.suit.setPlayRate(rate, anim)
                else:
                    if self.isTransformed:
                        self.char.stop()
                        self.char.loop(anim)
                        self.char.setPlayRate(rate, anim)
                    else:
                        if self.isBecomePet:
                            self.pet.stop()
                            self.pet.loop(anim)
                            self.pet.setPlayRate(rate, anim)
                        else:
                            if self.isGoon:
                                self.goon.stop()
                                if anim == 'neutral':
                                    self.goon.pose(anim, 96)
                                else:
                                    self.goon.loop(anim)
                                self.goon.setPlayRate(rate, anim)
                            else:
                                if self.isBossCog:
                                    if self.playingAnim != pastAnim or self.playingRate != pastRate or self.rotateSpeed != pastRot:
                                        if self.bossCogSeq:
                                            self.bossCogSeq.finish()
                                        if rotateSpeed != 0:
                                            self.bossCogSeq = Sequence(Parallel(self.boss.rollLeftTreads(0.25, rotateSpeed / 25), self.boss.rollRightTreads(0.25, -rotateSpeed / 25)))
                                        else:
                                            self.bossCogSeq = Sequence(Parallel(self.boss.rollLeftTreads(0.5, -forwardSpeed / 5), self.boss.rollRightTreads(0.5, -forwardSpeed / 5)))
                                        self.bossCogSeq.loop()
                if self.animeChair:
                    self.animeChair.stop()
                    self.animeChair.loop(anim)
                    self.animeChair.setPlayRate(rate, anim)
            else:
                if rate != self.playingRate:
                    self.playingRate = rate
                    if not self.isDisguised and not self.isTransformed and not self.isBecomePet and not self.isGoon:
                        self.setPlayRate(rate, anim)
                    else:
                        if self.isTransformed:
                            self.char.setPlayRate(rate, anim)
                        else:
                            if self.isBecomePet:
                                self.pet.setPlayRate(rate, anim)
                            else:
                                if self.isGoon:
                                    self.goon.setPlayRate(rate, anim)
                                else:
                                    self.suit.setPlayRate(rate, anim)
                    if self.animeChair:
                        self.animeChair.setPlayRate(rate, anim)
            showWake, wakeWaterHeight = ZoneUtil.getWakeInfo()
            if showWake and self.getZ(render) < wakeWaterHeight and abs(forwardSpeed) > ToontownGlobals.WalkCutOff:
                currT = globalClock.getFrameTime()
                deltaT = currT - self.lastWakeTime
                if action == OTPGlobals.RUN_INDEX and deltaT > ToontownGlobals.WakeRunDelta or deltaT > ToontownGlobals.WakeWalkDelta:
                    self.getWake().createRipple(wakeWaterHeight, rate=1, startFrame=4)
                    self.lastWakeTime = currT
        return action

    def enterOff(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        self.setActiveShadow(0)
        self.playingAnim = None
        return

    def exitOff(self):
        pass

    def enterNeutral(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        anim = self.neutralAnim
        if self.isDisguised:
            self.suit.pose('neutral', int(self.getNumFrames('neutral') * self.randGen.random()))
            self.suit.loop('neutral', restart=0)
            self.suit.setPlayRate(animMultiplier, 'neutral')
        else:
            self.pose(anim, int(self.getNumFrames(anim) * self.randGen.random()))
            self.loop(anim, restart=0)
            self.setPlayRate(animMultiplier, anim)
        self.playingAnim = anim
        self.setActiveShadow(1)

    def exitNeutral(self):
        self.stop()

    def enterVictory(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        anim = 'victory'
        frame = int(ts * self.getFrameRate(anim) * animMultiplier)
        self.pose(anim, frame)
        if self.isDisguised:
            self.suit.loop('victory', restart=0)
            self.suit.setPlayRate(animMultiplier, 'victory')
        else:
            self.loop('victory', restart=0)
            self.setPlayRate(animMultiplier, 'victory')
        self.playingAnim = anim
        self.setActiveShadow(0)

    def exitVictory(self):
        self.stop()

    def enterHappy(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        self.playingAnim = None
        self.playingRate = None
        self.standWalkRunReverse = ((self.neutralAnim, 1.0),
         (
          self.walkAnim, 1.0),
         (
          self.runAnim, 1.0),
         (
          self.walkAnim, -1.0))
        self.setSpeed(self.forwardSpeed, self.rotateSpeed)
        self.setActiveShadow(1)
        return

    def exitHappy(self):
        self.standWalkRunReverse = None
        self.stop()
        self.motion.exit()
        return

    def enterSad(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        self.playingAnim = 'sad'
        self.playingRate = None
        self.standWalkRunReverse = (('sad-neutral', 1.0),
         ('sad-walk', 1.2),
         ('sad-walk', 1.2),
         ('sad-walk', -1.0))
        self.setSpeed(0, 0)
        Emote.globalEmote.disableBody(self, 'toon, enterSad')
        self.setActiveShadow(1)
        if self.isLocal() and not self.isDisguised and not self.isTransformed and not self.isBecomePet and not self.isGoon:
            self.controlManager.disableAvatarJump()
        return

    def exitSad(self):
        self.standWalkRunReverse = None
        self.stop()
        self.motion.exit()
        Emote.globalEmote.releaseBody(self, 'toon, exitSad')
        if self.isLocal() and not self.isDisguised and not self.isTransformed and not self.isBecomePet and not self.isGoon:
            self.controlManager.enableAvatarJump()
        return

    def enterSlowCatching(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        self.playingAnim = None
        self.playingRate = None
        self.standWalkRunReverse = (('catch-neutral', 1.0),
         ('catch-run', 0.69),
         ('catch-run', 0.69),
         ('catch-run', -0.69))
        self.setSpeed(self.forwardSpeed, self.rotateSpeed)
        self.setActiveShadow(1)
        return

    def exitSlowCatching(self):
        self.standWalkRunReverse = None
        self.stop()
        self.motion.exit()
        return

    def enterCatching(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        self.playingAnim = None
        self.playingRate = None
        self.standWalkRunReverse = (('catch-neutral', 1.0),
         ('catch-run', 1.0),
         ('catch-run', 1.0),
         ('catch-run', -1.0))
        self.setSpeed(self.forwardSpeed, self.rotateSpeed)
        self.setActiveShadow(1)
        return

    def exitCatching(self):
        self.standWalkRunReverse = None
        self.stop()
        self.motion.exit()
        return

    def enterCatchEating(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        self.playingAnim = None
        self.playingRate = None
        self.standWalkRunReverse = (('catch-eatneutral', 1.0),
         ('catch-eatnrun', 1.0),
         ('catch-eatnrun', 1.0),
         ('catch-eatnrun', -1.0))
        self.setSpeed(self.forwardSpeed, self.rotateSpeed)
        self.setActiveShadow(0)
        return

    def exitCatchEating(self):
        self.standWalkRunReverse = None
        self.stop()
        self.motion.exit()
        return

    def enterWalk(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        if self.isDisguised:
            if self.walkAnim == 'riggyWalk' and self.suit.style.body == 'a':
                self.suit.loop('awalk')
                self.suit.setPlayRate(animMultiplier, 'awalk')
            else:
                self.suit.loop('walk')
                self.suit.setPlayRate(animMultiplier, 'walk')
        else:
            self.loop(self.walkAnim)
            self.setPlayRate(animMultiplier, self.walkAnim)
        self.setActiveShadow(1)

    def exitWalk(self):
        self.stop()

    def getJumpDuration(self):
        if self.playingAnim == self.neutralAnim:
            return self.getDuration('jump', 'legs')
        return self.getDuration('running-jump', 'legs')

    def enterJump(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        if not self.isDisguised:
            if self.playingAnim == self.neutralAnim:
                anim = 'jump'
            else:
                anim = 'running-jump'
            self.playingAnim = anim
            self.setPlayRate(animMultiplier, anim)
            self.play(anim)
        else:
            anim = 'slip-forward'
            self.playingAnim = anim
            self.suit.setPlayRate(animMultiplier, anim)
            if self.suit.style.body == 'a':
                self.ebicJumpVariable = ActorInterval(self.suit, 'slip-forward', startFrame=55)
            else:
                if self.suit.style.body == 'b':
                    self.ebicJumpVariable = Sequence(ActorInterval(self.suit, 'quick-jump', playRate=5, endFrame=15), ActorInterval(self.suit, 'quick-jump', startFrame=15, endFrame=30), ActorInterval(self.suit, 'quick-jump', startFrame=107))
                else:
                    if self.suit.style.body == 'c':
                        self.ebicJumpVariable = ActorInterval(self.suit, 'slip-forward', startFrame=59)
                    else:
                        self.notify.warning('Body type fucked up.')
            self.ebicJumpVariable.start()
            self.play('jump')
        if self.animeChair:
            self.animeChair.play('jump')
        self.setActiveShadow(1)

    def exitJump(self):
        self.stop()
        if self.isDisguised:
            self.ebicJumpVariable.finish()
        self.playingAnim = self.neutralAnim

    def enterJumpSquat(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        if not self.isDisguised:
            if self.playingAnim == self.neutralAnim:
                anim = 'jump-squat'
            else:
                anim = 'running-jump-squat'
            self.playingAnim = anim
            self.setPlayRate(animMultiplier, anim)
            self.play(anim)
        else:
            anim = 'slip-forward'
            self.playingAnim = anim
            self.suit.setPlayRate(animMultiplier, anim)
            if self.suit.style.body == 'a':
                self.ebicJumpVariable = ActorInterval(self.suit, 'slip-forward', startFrame=55, endFrame=63)
            else:
                if self.suit.style.body == 'b':
                    self.ebicJumpVariable = Sequence(ActorInterval(self.suit, 'quick-jump', playRate=5, endFrame=15), ActorInterval(self.suit, 'quick-jump', startFrame=15, endFrame=30))
                else:
                    if self.suit.style.body == 'c':
                        self.ebicJumpVariable = ActorInterval(self.suit, 'slip-forward', startFrame=59, endFrame=69)
                    else:
                        self.notify.warning('Body type fucked up.')
            self.ebicJumpVariable.start()
            self.play('jump-squat')
        self.setActiveShadow(1)

    def exitJumpSquat(self):
        self.stop()
        if self.isDisguised:
            self.ebicJumpVariable.finish()
        self.playingAnim = self.neutralAnim

    def enterJumpAirborne(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        if self.isDisguised:
            anim = 'slip-forward'
            self.playingAnim = anim
            self.suit.setPlayRate(animMultiplier, anim)
            if self.suit.style.body == 'a':
                self.suit.pose(anim, 66)
            else:
                if self.suit.style.body == 'b':
                    self.suit.pose('quick-jump', 30)
                else:
                    if self.suit.style.body == 'c':
                        self.suit.pose(anim, 69)
                    else:
                        self.notify.warning('Body type fucked up.')
            self.play('jump-idle')
        else:
            if self.playingAnim == self.neutralAnim or self.forceJumpIdle:
                anim = 'jump-idle'
            else:
                anim = 'running-jump-idle'
            self.playingAnim = anim
            self.setPlayRate(animMultiplier, anim)
            self.loop(anim)
        if self.animeChair:
            self.animeChair.loop('jump')
        self.setActiveShadow(1)

    def exitJumpAirborne(self):
        self.stop()
        self.playingAnim = self.neutralAnim

    def enterJumpLand(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        if not self.isDisguised:
            if self.playingAnim == 'running-jump-idle':
                anim = 'running-jump-land'
                skipStart = 0.2
            else:
                anim = 'jump-land'
                skipStart = 0.0
            self.playingAnim = anim
            self.setPlayRate(animMultiplier, anim)
            self.play(anim)
        else:
            anim = 'slip-forward'
            self.playingAnim = anim
            self.suit.setPlayRate(animMultiplier, anim)
            if self.suit.style.body == 'a':
                self.ebicJumpVariable = ActorInterval(self.suit, 'slip-forward', startFrame=66)
            else:
                if self.suit.style.body == 'b':
                    self.ebicJumpVariable = ActorInterval(self.suit, 'quick-jump', startFrame=107)
                else:
                    if self.suit.style.body == 'c':
                        self.ebicJumpVariable = ActorInterval(self.suit, 'slip-forward', startFrame=69)
                    else:
                        self.notify.warning('Body type fucked up.')
            self.ebicJumpVariable.start()
            self.play('jump-land')
        self.setActiveShadow(1)

    def exitJumpLand(self):
        self.stop()
        if self.isDisguised:
            self.ebicJumpVariable.finish()
        self.playingAnim = self.neutralAnim

    def enterRun(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        if self.isDisguised:
            self.suit.loop('walk')
            self.suit.setPlayRate(animMultiplier, 'walk')
        else:
            self.loop(self.runAnim)
            self.setPlayRate(animMultiplier, self.runAnim)
        Emote.globalEmote.disableBody(self, 'toon, enterRun')
        self.setActiveShadow(1)

    def exitRun(self):
        self.stop()
        Emote.globalEmote.releaseBody(self, 'toon, exitRun')

    def enterSwim(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        Emote.globalEmote.disableAll(self, 'enterSwim')
        self.playingAnim = 'swim'
        self.loop('swim')
        self.setPlayRate(animMultiplier, 'swim')
        self.getGeomNode().setP(-89.0)
        self.dropShadow.hide()
        if self.isLocal():
            self.useSwimControls()
        self.nametag3d.setPos(0, -2, 1)
        self.startBobSwimTask()
        self.setActiveShadow(0)

    def enterCringe(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        if self.isDisguised:
            self.loop('squirt-small-react')
            self.suit.setPlayRate(animMultiplier, 'swim')
        else:
            self.loop('cringe')
            self.getGeomNode().setPos(0, 0, -2)
            self.setPlayRate(animMultiplier, 'swim')

    def exitCringe(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        self.stop()
        self.getGeomNode().setPos(0, 0, 0)
        self.playingAnim = self.neutralAnim
        self.setPlayRate(animMultiplier, 'swim')

    def enterDive(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        self.loop('swim')
        if hasattr(self.getGeomNode(), 'setPos'):
            self.getGeomNode().setPos(0, 0, -2)
            self.setPlayRate(animMultiplier, 'swim')
            self.setActiveShadow(0)
            self.dropShadow.hide()
            self.nametag3d.setPos(0, -2, 1)

    def exitDive(self):
        self.stop()
        self.getGeomNode().setPos(0, 0, 0)
        self.playingAnim = self.neutralAnim
        self.dropShadow.show()
        self.nametag3d.setPos(0, 0, self.height + 0.5)

    def enterSwimHold(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        self.getGeomNode().setPos(0, 0, -2)
        self.nametag3d.setPos(0, -2, 1)
        self.pose('swim', 55)

    def exitSwimHold(self):
        self.stop()
        self.getGeomNode().setPos(0, 0, 0)
        self.playingAnim = self.neutralAnim
        self.dropShadow.show()
        self.nametag3d.setPos(0, 0, self.height + 0.5)

    def exitSwim(self):
        self.stop()
        self.playingAnim = self.neutralAnim
        self.stopBobSwimTask()
        self.getGeomNode().setPosHpr(0, 0, 0, 0, 0, 0)
        self.dropShadow.show()
        if self.isLocal():
            self.useWalkControls()
        self.nametag3d.setPos(0, 0, self.height + 0.5)
        Emote.globalEmote.releaseAll(self, 'exitSwim')

    def startBobSwimTask(self):
        if getattr(self, 'swimBob', None):
            self.swimBob.finish()
            self.swimBob = None
        self.nametag3d.setZ(5.0)
        geomNode = self.getGeomNode()
        geomNode.setZ(4.0)
        self.swimBob = Sequence(geomNode.posInterval(1, Point3(0, -3, 3), startPos=Point3(0, -3, 4), blendType='easeInOut'), geomNode.posInterval(1, Point3(0, -3, 4), startPos=Point3(0, -3, 3), blendType='easeInOut'))
        self.swimBob.loop()
        return

    def stopBobSwimTask(self):
        swimBob = getattr(self, 'swimBob', None)
        if swimBob:
            swimBob.finish()
        self.getGeomNode().setPos(0, 0, 0)
        self.nametag3d.setZ(1.0)
        return

    def enterOpenBook(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        Emote.globalEmote.disableAll(self, 'enterOpenBook')
        self.playingAnim = 'openBook'
        self.stopLookAround()
        self.lerpLookAt(Point3(0, 1, -2))
        bookTracks = Parallel()
        if self.isDisguised:
            self.loop('neutral')
            if not self.rollodex:
                self.rollodex = BattleProps.globalPropPool.getProp('rollodex')
                hand = self.suit.getLeftHand()
                self.rollodex.reparentTo(hand)
            if self.suit.style.body == 'b':
                self.rollodex.setPos(0.12, 0.24, 0.01)
                self.rollodex.setScale(0.91, 0.91, 0.91)
                self.rollodex.setHpr(99.032, 5.973, -179.839)
                growTrack = self.rollodex.scaleInterval(0.5, 0.91, startScale=0)
            else:
                self.rollodex.setPos(-0.51, -0.03, -0.1)
                self.rollodex.setScale(1.2, 1.2, 1.2)
                self.rollodex.setHpr(89.673, 2.166, 177.786)
                growTrack = self.rollodex.scaleInterval(0.5, 1.2, startScale=0)
            if hasattr(self, 'uniqueName'):
                trackName = self.uniqueName('openBook')
            else:
                trackName = 'openBook'
            if self.suit.style.body == 'c':
                self.track = Sequence(Parallel(ActorInterval(self.suit, 'phone', endFrame=24), growTrack), name=trackName)
            else:
                self.track = Sequence(Parallel(ActorInterval(self.suit, 'roll-o-dex', playRate=1.5, endFrame=36), growTrack), name=trackName)
        else:
            if self.isTransformed or self.isBecomePet or self.isGoon or self.isBossCog:
                pass
            else:
                for bookActor in self.getBookActors():
                    bookTracks.append(ActorInterval(bookActor, 'book', startTime=1.2, endTime=1.5))

                bookTracks.append(ActorInterval(self, 'book', startTime=1.2, endTime=1.5))
                if hasattr(self, 'uniqueName'):
                    trackName = self.uniqueName('openBook')
                else:
                    trackName = 'openBook'
                self.track = Sequence(Func(self.showBooks), bookTracks, Wait(0.1), name=trackName)
        if not self.isTransformed and not self.isBecomePet and not self.isGoon and not self.isBossCog:
            if callback:
                self.track.setDoneEvent(self.track.getName())
                self.acceptOnce(self.track.getName(), callback, extraArgs)
            self.track.start(ts)
        self.setActiveShadow(0)

    def exitOpenBook(self):
        self.playingAnim = 'neutralob'
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        if self.isDisguised and self.rollodex:
            self.rollodex.removeNode()
            self.rollodex = None
        else:
            self.hideBooks()
        self.startLookAround()
        Emote.globalEmote.releaseAll(self, 'exitOpenBook')
        return

    def enterReadBook(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        Emote.globalEmote.disableBody(self, 'enterReadBook')
        self.playingAnim = 'readBook'
        self.stopLookAround()
        self.lerpLookAt(Point3(0, 1, -2))
        if self.isDisguised:
            self.loop('neutral')
            if not self.rollodex:
                self.rollodex = BattleProps.globalPropPool.getProp('rollodex')
                hand = self.suit.getLeftHand()
                self.rollodex.reparentTo(hand)
            if self.suit.style.body == 'b':
                self.rollodex.setPos(0.12, 0.24, 0.01)
                self.rollodex.setScale(0.91, 0.91, 0.91)
                self.rollodex.setHpr(99.032, 5.973, -179.839)
            else:
                self.rollodex.setPos(-0.51, -0.03, -0.1)
                self.rollodex.setScale(1.2, 1.2, 1.2)
                self.rollodex.setHpr(89.673, 2.166, 177.786)
            if self.suit.style.body == 'c':
                self.suit.pose('phone', 24)
            else:
                self.suit.pose('roll-o-dex', 36)
        else:
            if self.isTransformed or self.isBecomePet or self.isGoon or self.isBossCog:
                pass
            else:
                self.showBooks()
                for bookActor in self.getBookActors():
                    bookActor.pingpong('book', fromFrame=38, toFrame=118)

                self.pingpong('book', fromFrame=38, toFrame=118)
        self.setActiveShadow(0)

    def exitReadBook(self):
        self.playingAnim = 'neutralrb'
        if self.isDisguised and self.rollodex:
            self.rollodex.removeNode()
            self.rollodex = None
        else:
            self.hideBooks()
        for bookActor in self.getBookActors():
            bookActor.stop()

        self.startLookAround()
        Emote.globalEmote.releaseBody(self, 'exitReadBook')
        return

    def enterCloseBook(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        Emote.globalEmote.disableAll(self, 'enterCloseBook')
        self.playingAnim = 'closeBook'
        if self.isDisguised:
            self.loop('neutral')
            if not self.rollodex:
                self.rollodex = BattleProps.globalPropPool.getProp('rollodex')
                hand = self.suit.getLeftHand()
                self.rollodex.reparentTo(hand)
            if self.suit.style.body == 'b':
                self.rollodex.setPos(0.12, 0.24, 0.01)
                self.rollodex.setScale(0.91, 0.91, 0.91)
                self.rollodex.setHpr(99.032, 5.973, -179.839)
                growTrack = self.rollodex.scaleInterval(0.5, 0, startScale=0.91)
            else:
                self.rollodex.setPos(-0.51, -0.03, -0.1)
                self.rollodex.setScale(1.2, 1.2, 1.2)
                self.rollodex.setHpr(89.673, 2.166, 177.786)
                growTrack = self.rollodex.scaleInterval(0.5, 0, startScale=1.2)
            if hasattr(self, 'uniqueName'):
                trackName = self.uniqueName('closeBook')
            else:
                trackName = 'closeBook'
            if self.suit.style.body == 'c':
                self.track = Sequence(Parallel(ActorInterval(self.suit, 'phone', startFrame=24, endFrame=0), growTrack), name=trackName)
            else:
                self.track = Sequence(Parallel(ActorInterval(self.suit, 'roll-o-dex', startFrame=36, endFrame=0), growTrack), name=trackName)
        else:
            if self.isTransformed or self.isBecomePet or self.isGoon or self.isBossCog:
                if hasattr(self, 'uniqueName'):
                    trackName = self.uniqueName('closeBook')
                else:
                    trackName = 'closeBook'
                self.track = Sequence(name=trackName)
            else:
                bookTracks = Parallel()
                for bookActor in self.getBookActors():
                    bookTracks.append(ActorInterval(bookActor, 'book', startTime=4.96, endTime=6.5))

                bookTracks.append(ActorInterval(self, 'book', startTime=4.96, endTime=6.5))
                if hasattr(self, 'uniqueName'):
                    trackName = self.uniqueName('closeBook')
                else:
                    trackName = 'closeBook'
                self.track = Sequence(Func(self.showBooks), bookTracks, Func(self.hideBooks), name=trackName)
        if callback:
            self.track.setDoneEvent(self.track.getName())
            self.acceptOnce(self.track.getName(), callback, extraArgs)
        self.track.start(ts)
        self.setActiveShadow(0)

    def exitCloseBook(self):
        self.playingAnim = 'neutralcb'
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        if self.isDisguised and self.rollodex:
            self.rollodex.removeNode()
            self.rollodex = None
        Emote.globalEmote.releaseAll(self, 'exitCloseBook')
        return

    def getSoundTeleport(self):
        if not self.soundTeleport:
            self.soundTeleport = base.loader.loadSfx('phase_3.5/audio/sfx/AV_teleport.ogg')
        return self.soundTeleport

    def getTeleportOutTrack(self, autoFinishTrack=1):
        if self.isDisguised:
            track = self.getSuitTeleport(moveIn=0)
        else:
            if self.isBecomePet:
                hole = self.getHoleActors()[0]
                hole.setBin('shadow', 0)
                hole.setDepthTest(0)
                hole.setDepthWrite(0)
                hole.reparentTo(self)
                pos = Point3(0, -1, 0)
                hole.setPos(self, pos)
                hole.hide()

                def cleanupHole(hole):
                    hole.setPos(0, 0, 0)
                    hole.detachNode()
                    hole.clearBin()
                    hole.clearDepthTest()
                    hole.clearDepthWrite()

                track = Sequence(Parallel(SoundInterval(loader.loadSfx('phase_5/audio/sfx/teleport_disappear.ogg')), Sequence(ActorInterval(self.pet, 'toDig'), Parallel(ActorInterval(self.pet, 'dig'), Func(hole.show), ActorInterval(hole, 'hole', startFrame=81, endFrame=71)), ActorInterval(self.pet, 'disappear'), ActorInterval(hole, 'hole', startFrame=71, endFrame=81), Func(cleanupHole, hole)), Sequence(Wait(1.0), Func(self.dropShadow.hide))))
                return track

            def showHoles(holes, hands):
                for hole, hand in zip(holes, hands):
                    hole.reparentTo(hand)

            def reparentHoles(holes, toon):
                holes[0].reparentTo(toon)
                holes[1].detachNode()
                holes[2].detachNode()
                holes[0].setBin('shadow', 0)
                holes[0].setDepthTest(0)
                holes[0].setDepthWrite(0)

            def cleanupHoles(holes):
                holes[0].detachNode()
                holes[0].clearBin()
                holes[0].clearDepthTest()
                holes[0].clearDepthWrite()

            holes = self.getHoleActors()
            hands = self.getRightHands()
            holeTrack = Track((0.0, Func(showHoles, holes, hands)), (0.5, SoundInterval(self.getSoundTeleport(), node=self)), (1.708, Func(reparentHoles, holes, self)), (2.9, Func(self.dropShadow.hide)), (3.4, Parallel(Func(self.nametag3d.hide), Func(cleanupHoles, holes))))
            if hasattr(self, 'uniqueName'):
                trackName = self.uniqueName('teleportOut')
            else:
                trackName = 'teleportOut'
            track = Parallel(holeTrack, name=trackName, autoFinish=autoFinishTrack)
            for hole in holes:
                track.append(ActorInterval(hole, 'hole', duration=3.4))

            track.append(ActorInterval(self, 'teleport', duration=3.4))
        return track

    def startQuestMap(self):
        pass

    def stopQuestMap(self):
        pass

    def enterTeleportOut(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        name = self.name
        if hasattr(self, 'doId'):
            name += '-' + str(self.doId)
        self.notify.debug('enterTeleportOut %s' % name)
        if self.ghostMode or self.isTransformed or self.isGoon or self.isBossCog:
            if callback:
                callback(*extraArgs)
            return
        self.playingAnim = 'teleport'
        Emote.globalEmote.disableAll(self, 'enterTeleportOut')
        if self.isLocal():
            autoFinishTrack = 0
        else:
            autoFinishTrack = 1
        self.track = self.getTeleportOutTrack(autoFinishTrack)
        self.track.setDoneEvent(self.track.getName())
        self.acceptOnce(self.track.getName(), self.finishTeleportOut, [callback, extraArgs])
        holeClip = PlaneNode('holeClip')
        self.holeClipPath = self.attachNewNode(holeClip)
        self.getGeomNode().setClipPlane(self.holeClipPath)
        self.nametag3d.setClipPlane(self.holeClipPath)
        self.track.start(ts)
        self.setActiveShadow(0)

    def finishTeleportOut(self, callback=None, extraArgs=[]):
        name = self.name
        if hasattr(self, 'doId'):
            name += '-' + str(self.doId)
        self.notify.debug('finishTeleportOut %s' % name)
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        if hasattr(self, 'animFSM'):
            self.animFSM.request('TeleportedOut')
        if callback:
            callback(*extraArgs)
        return

    def exitTeleportOut(self):
        name = self.name
        if hasattr(self, 'doId'):
            name += '-' + str(self.doId)
        self.notify.debug('exitTeleportOut %s' % name)
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            self.track = None
        geomNode = self.getGeomNode()
        if geomNode and not geomNode.isEmpty():
            self.getGeomNode().clearClipPlane()
        if self.nametag3d and not self.nametag3d.isEmpty():
            self.nametag3d.clearClipPlane()
        if self.holeClipPath:
            self.holeClipPath.removeNode()
            self.holeClipPath = None
        Emote.globalEmote.releaseAll(self, 'exitTeleportOut')
        if self and not self.isEmpty():
            self.show()
        return

    def enterTeleportedOut(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        self.setActiveShadow(0)

    def exitTeleportedOut(self):
        pass

    def createSuitDeathTrack(self):

        def insertDeathSuit(deathSuit, pos, hpr):
            self.suit.getGeomNode().stash()
            if deathSuit != None and not deathSuit.isEmpty():
                deathSuit.reparentTo(render)
                deathSuit.setPos(pos)
                deathSuit.setHpr(hpr)
                suitHeadNull = deathSuit.find('**/joint_head')
                toonHead = self.getPart('head', '1000')
                worldScale = toonHead.getScale(render)
                headPosNode = hidden.attachNewNode('headPos')
                toonHead.reparentTo(headPosNode)
                if self.isCog != 5 and self.isCog:
                    toonHead.reparentTo(hidden)
                toonHead.setPos(0, 0, 0.2)
                headPosNode.reparentTo(suitHeadNull)
                headPosNode.setScale(render, worldScale)
            return

        def removeDeathSuit(deathSuit):
            if not deathSuit.isEmpty():
                deathSuit.detachNode()
                self.suit.cleanupLoseActor()
            self.takeOffSuit()

        def createKapowExplosionTrack(parent, explosionPoint=None, scale=1.0):
            explosionTrack = Sequence()
            explosion = loader.loadModel('phase_3.5/models/props/explosion')
            explosion.setBillboardPointEye()
            explosion.setDepthWrite(False)
            if not explosionPoint:
                explosionPoint = Point3(0, 3.6, 2.1)
            explosionTrack.append(Func(explosion.reparentTo, parent))
            explosionTrack.append(Func(explosion.setPos, explosionPoint))
            explosionTrack.append(Func(explosion.setScale, 0.4 * scale))
            explosionTrack.append(Wait(0.6))
            explosionTrack.append(Func(explosion.removeNode))
            return explosionTrack

        suitTrack = Sequence()
        suitPos, suitHpr = self.getPos(), self.getHpr()
        deathSuit = self.suit.getLoseActor()
        suitTrack.append(Func(insertDeathSuit, deathSuit, suitPos, suitHpr))
        suitTrack.append(ActorInterval(deathSuit, 'lose', duration=6.0))
        suitTrack.append(Func(removeDeathSuit, deathSuit, name='remove-death-suit'))
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/Cog_Death.ogg')
        deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.ogg')
        deathSoundTrack = Sequence(Wait(0.8), SoundInterval(spinningSound, duration=1.2, startTime=1.5, volume=0.2), SoundInterval(spinningSound, duration=3.0, startTime=0.6, volume=0.8), SoundInterval(deathSound, volume=0.32))
        BattleParticles.loadParticles()
        smallGears = BattleParticles.createParticleEffect(file='gearExplosionSmall')
        singleGear = BattleParticles.createParticleEffect('GearExplosion', numParticles=1)
        smallGearExplosion = BattleParticles.createParticleEffect('GearExplosion', numParticles=10)
        bigGearExplosion = BattleParticles.createParticleEffect('BigGearExplosion', numParticles=30)
        gearPoint = Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() + self.suit.height - 0.2)
        smallGears.setPos(gearPoint)
        singleGear.setPos(gearPoint)
        smallGears.setDepthWrite(False)
        singleGear.setDepthWrite(False)
        smallGearExplosion.setPos(gearPoint)
        bigGearExplosion.setPos(gearPoint)
        smallGearExplosion.setDepthWrite(False)
        bigGearExplosion.setDepthWrite(False)
        explosionTrack = Sequence()
        explosionTrack.append(Wait(5.4))
        explosionTrack.append(createKapowExplosionTrack(render, explosionPoint=gearPoint))
        gears1Track = Sequence(Wait(2.1), ParticleInterval(smallGears, render, worldRelative=0, duration=4.3, cleanup=True), name='gears1Track')
        gears2MTrack = Track((0.0, explosionTrack), (0.7, ParticleInterval(singleGear, render, worldRelative=0, duration=5.7, cleanup=True)), (5.2, ParticleInterval(smallGearExplosion, render, worldRelative=0, duration=1.2, cleanup=True)), (5.4, ParticleInterval(bigGearExplosion, render, worldRelative=0, duration=1.0, cleanup=True)), name='gears2MTrack')
        return Parallel(suitTrack, deathSoundTrack, gears1Track, gears2MTrack)

    def createGoonDeathTrack(self, parent, explosionPoint, scale):

        def createExplosionTrack(parent, deathNode, scale):
            explosion = loader.loadModel('phase_3.5/models/props/explosion')
            explosion.getChild(0).setScale(scale)
            explosion.reparentTo(deathNode)
            explosion.setBillboardPointEye()
            explosion.setPos(0, 0, 2)
            return Sequence(Func(deathNode.reparentTo, parent), Wait(0.6), Func(deathNode.detachNode))

        def createGoonExplosion(parent, explosionPoint, scale):
            BattleParticles.loadParticles()
            deathNode = NodePath('goonDeath')
            deathNode.setPos(explosionPoint)
            explosion = createExplosionTrack(parent, deathNode, scale)
            smallGearExplosion = BattleParticles.createParticleEffect('GearExplosion', numParticles=10)
            bigGearExplosion = BattleParticles.createParticleEffect('WideGearExplosion', numParticles=30)
            deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.ogg')
            return Parallel(explosion, SoundInterval(deathSound), ParticleInterval(smallGearExplosion, deathNode, worldRelative=0, duration=1.0, cleanup=True), ParticleInterval(bigGearExplosion, deathNode, worldRelative=0, duration=1.0, cleanup=True), name='gears2MTrack')

        return createGoonExplosion(parent, explosionPoint, scale)

    def getDiedInterval(self, autoFinishTrack=1):
        sound = loader.loadSfx('phase_5/audio/sfx/ENC_Lose.ogg')
        if hasattr(self, 'uniqueName'):
            trackName = self.uniqueName('died')
        else:
            trackName = 'died'
        if self.isDisguised:
            ival = self.createSuitDeathTrack()
        else:
            if self.isBecomePet:
                ival = Sequence(Func(Emote.globalEmote.disableBody, self), Parallel(ActorInterval(self.pet, 'playDead'), SoundInterval(loader.loadSfx('phase_5/audio/sfx/play_dead.ogg'))), Func(self.noMorePet))
            else:
                if self.isGoon:
                    goonPos = self.getPos()
                    sx = random.uniform(0.3, 0.8) * self.goon.scale
                    sz = random.uniform(0.3, 0.8) * self.goon.scale
                    ival = Sequence(Parallel(Sequence(ActorInterval(self.goon, 'collapse'), Func(self.goon.pose, 'collapse', 48)), SoundInterval(loader.loadSfx('phase_9/audio/sfx/CHQ_GOON_hunker_down.ogg'), node=self)), self.createGoonDeathTrack(self.getParent(), goonPos, VBase3(sx, 1, sz)), Func(self.noMoreGoon))
                else:
                    if self.isBossCog:
                        ival = Sequence(self.getBossDiedInterval(), Func(self.noMoreBoss))
                    else:
                        ival = Sequence(Func(Emote.globalEmote.disableBody, self), Func(self.sadEyes), Func(self.blinkEyes), Track((0, ActorInterval(self, 'lose')), (2, SoundInterval(sound, node=self)), (5.333, self.scaleInterval(1.5, VBase3(0.01, 0.01, 0.01), blendType='easeInOut'))), Func(self.detachNode), Func(self.setScale, 1, 1, 1), Func(self.normalEyes), Func(self.blinkEyes), Func(Emote.globalEmote.releaseBody, self), name=trackName, autoFinish=autoFinishTrack)
        return ival

    def getBossDiedInterval(self):

        def createKapowExplosionTrack(parent):
            explosionTrack = Sequence()
            explosion = loader.loadModel('phase_3.5/models/props/explosion.bam')
            explosion.setBillboardPointEye()
            explosion.setDepthWrite(False)
            explosionPoint = Point3(0, 0, 4.1)
            explosionTrack.append(Func(explosion.reparentTo, parent))
            explosionTrack.append(Func(explosion.setPos, explosionPoint))
            explosionTrack.append(Func(explosion.setScale, 0.4))
            explosionTrack.append(Wait(0.6))
            explosionTrack.append(Func(explosion.removeNode))
            return explosionTrack

        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/Cog_Death.ogg')
        deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.ogg')
        deathSoundTrack = Sequence(Wait(0.6), SoundInterval(spinningSound, duration=1.2, startTime=1.5, volume=0.2), SoundInterval(spinningSound, duration=3.0, startTime=0.6, volume=0.8), SoundInterval(deathSound, volume=0.32))
        BattleParticles.loadParticles()
        smallGears = BattleParticles.createParticleEffect(file='gearExplosionSmall')
        singleGear = BattleParticles.createParticleEffect('GearExplosion', numParticles=1)
        smallGearExplosion = BattleParticles.createParticleEffect('GearExplosion', numParticles=10)
        bigGearExplosion = BattleParticles.createParticleEffect('BigGearExplosion', numParticles=30)
        smallGears.setDepthWrite(False)
        singleGear.setDepthWrite(False)
        smallGearExplosion.setDepthWrite(False)
        bigGearExplosion.setDepthWrite(False)
        explosionTrack = Sequence()
        explosionTrack.append(Wait(5.4))
        explosionTrack.append(createKapowExplosionTrack(self))
        gears1Track = Sequence(Wait(2.0), ParticleInterval(smallGears, self, worldRelative=0, duration=4.3, cleanup=True), name='gears1Track')
        gears2MTrack = Track((0.0, explosionTrack), (
         0.7, ParticleInterval(singleGear, self, worldRelative=0, duration=5.7, cleanup=True)), (5.2,
         ParticleInterval(smallGearExplosion, self, worldRelative=0, duration=1.2, cleanup=True)), (
         5.4,
         ParticleInterval(bigGearExplosion, self, worldRelative=0, duration=1.0, cleanup=True)), name='gears2MTrack')
        ival = Parallel(Sequence(ActorInterval(self.boss, 'death', playRate=1.125), Func(self.boss.getGeomNode().hide)), deathSoundTrack, gears1Track, gears2MTrack)
        return ival

    def enterDied(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        if self.ghostMode:
            if callback:
                callback(*extraArgs)
            return
        self.playingAnim = 'lose'
        Emote.globalEmote.disableAll(self, 'enterDied')
        if self.isLocal():
            autoFinishTrack = 0
        else:
            autoFinishTrack = 1
        if hasattr(self, 'jumpLandAnimFixTask') and self.jumpLandAnimFixTask:
            self.jumpLandAnimFixTask.remove()
            self.jumpLandAnimFixTask = None
        self.track = self.getDiedInterval(autoFinishTrack)
        if callback:
            self.track = Sequence(self.track, Func(callback, *extraArgs), autoFinish=autoFinishTrack)
        if self.isLocal():
            self.track.append(Func(self.exitIndex))
        self.track.start(ts)
        self.setActiveShadow(0)
        return

    def finishDied(self, callback=None, extraArgs=[]):
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        if hasattr(self, 'animFSM'):
            self.animFSM.request('TeleportedOut')
        if callback:
            callback(*extraArgs)
        return

    def exitDied(self):
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        Emote.globalEmote.releaseAll(self, 'exitDied')
        self.show()
        return

    def exitIndex(self):
        pass

    def getPlaygroundDiedInterval(self, autoFinishTrack=1):
        sound = loader.loadSfx('phase_5/audio/sfx/ENC_Lose.ogg')
        if hasattr(self, 'uniqueName'):
            trackName = self.uniqueName('playgroundDied')
        else:
            trackName = 'playgroundDied'
        ival = Sequence(Func(self.sadEyes), Func(self.blinkEyes), Track((0, ActorInterval(self, 'lose', startFrame=0, endFrame=89)), (2, Func(base.playSfx, sound, node=self))), Func(self.blinkEyes), Func(self.normalEyes), name=trackName, autoFinish=autoFinishTrack)
        return ival

    def enterPlaygroundDied(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        if self.ghostMode:
            if callback:
                callback(*extraArgs)
            return
        if self.isDisguised and not base.cr.newsManager.isHolidayRunning(ToontownGlobals.ORANGES):
            self.takeOffSuit()
        self.playingAnim = 'lose'
        Emote.globalEmote.disableAll(self, 'enterPlaygroundDied')
        if self.isLocal():
            autoFinishTrack = 0
        else:
            autoFinishTrack = 1
        if hasattr(self, 'jumpLandAnimFixTask') and self.jumpLandAnimFixTask:
            self.jumpLandAnimFixTask.remove()
            self.jumpLandAnimFixTask = None
        self.track = self.getPlaygroundDiedInterval(autoFinishTrack)
        if callback:
            self.track = Sequence(self.track, Func(callback, *extraArgs), autoFinish=autoFinishTrack)
        self.track.start(ts)
        self.setActiveShadow(0)
        return

    def finishPlaygroundDied(self, callback=None, extraArgs=[]):
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        if callback:
            callback(*extraArgs)
        return

    def exitPlaygroundDied(self):
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        Emote.globalEmote.releaseAll(self, 'exitPlaygroundDied')
        return

    def getFourBossDiedInterval(self, autoFinishTrack=1):
        sound = loader.loadSfx('phase_5/audio/sfx/ENC_Lose.ogg')
        if hasattr(self, 'uniqueName'):
            trackName = self.uniqueName('fourBossDied')
        else:
            trackName = 'fourBossDied'
        ival = Sequence(Func(self.setChatAbsolute, 'darn, i losed', CFSpeech), Func(self.sadEyes), Func(self.blinkEyes), Track((0, ActorInterval(self, 'lose', startFrame=0, endFrame=89)), (2, Func(base.playSfx, sound, node=self))), Func(self.blinkEyes), Func(self.normalEyes), name=trackName, autoFinish=autoFinishTrack)
        return ival

    def enterFourBossDied(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        if self.ghostMode:
            if callback:
                callback(*extraArgs)
            return
        if self.isDisguised and not base.cr.newsManager.isHolidayRunning(ToontownGlobals.ORANGES):
            self.takeOffSuit()
        self.playingAnim = 'lose'
        Emote.globalEmote.disableAll(self, 'enterFourBossDied')
        if self.isLocal():
            autoFinishTrack = 0
        else:
            autoFinishTrack = 1
        if hasattr(self, 'jumpLandAnimFixTask') and self.jumpLandAnimFixTask:
            self.jumpLandAnimFixTask.remove()
            self.jumpLandAnimFixTask = None
            self.track = self.getFourBossDiedInterval(autoFinishTrack)
        if callback:
            self.track = Sequence(self.track, Func(callback, *extraArgs), autoFinish=autoFinishTrack)
        self.track.start(ts)
        self.setActiveShadow(0)
        return

    def finishFourBossDied(self, callback=None, extraArgs=[]):
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        if callback:
            callback(*extraArgs)
        return

    def exitFourBossDied(self):
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        Emote.globalEmote.releaseAll(self, 'exitFourBossDied')
        return

    def getSuitTeleport(self, moveIn, greenPos=None):
        if base.cr.inEpisode:
            return Parallel()
        if self.suit.style.name != 'ty':
            if not greenPos:
                pos = Point3(self.getPos())
            else:
                pos = greenPos
            skyPos = Point3(pos)
            if not greenPos:
                if moveIn:
                    skyPos.setZ(pos.getZ() + SuitTimings.fromSky * ToontownGlobals.SuitWalkSpeed)
                else:
                    skyPos.setZ(pos.getZ() + SuitTimings.toSky * ToontownGlobals.SuitWalkSpeed)
            else:
                if moveIn:
                    skyPos.setZ(pos[2] + SuitTimings.fromSky * ToontownGlobals.SuitWalkSpeed)
                else:
                    skyPos.setZ(pos[2] + SuitTimings.toSky * ToontownGlobals.SuitWalkSpeed)
            groundF = 28
            dur = self.suit.getDuration('landing')
            fr = self.suit.getFrameRate('landing')
            animTimeInAir = groundF / fr
            impactLength = dur - animTimeInAir
            timeTillLanding = SuitTimings.fromSky - impactLength
            waitTime = timeTillLanding - animTimeInAir
            prop = BattleProps.globalPropPool.getProp('propeller')
            if self.isCog != 5 and self.isCog:
                parts = self.suit.getHeadParts()
            else:
                parts = self.getHeadParts()
            prop.reparentTo(parts[0])
            propInSound = base.loader.loadSfx('phase_5/audio/sfx/ENC_propeller_in.ogg')
            propOutSound = base.loader.loadSfx('phase_5/audio/sfx/ENC_propeller_out.ogg')
            propDur = prop.getDuration('propeller')
            lastSpinFrame = 8
            fr = prop.getFrameRate('propeller')
            spinTime = lastSpinFrame / fr
            openTime = (lastSpinFrame + 1) / fr
        else:
            fadingOn = loader.loadSfx('phase_14.5/audio/sfx/appearing_from_nowhere.ogg')
            fadingOff = loader.loadSfx('phase_14.5/audio/sfx/disappearing_from_now_on.ogg')
        if moveIn == 1:
            if self.suit.style.name != 'ty':
                lerpPosTrack = Sequence(self.posInterval(timeTillLanding, pos, startPos=skyPos), Wait(impactLength))
                shadowScale = self.suit.dropShadow.getScale()
                shadowTrack = Sequence(Func(self.suit.dropShadow.reparentTo, render), Func(self.suit.dropShadow.setPos, pos), self.suit.dropShadow.scaleInterval(timeTillLanding, self.suit.scale, startScale=Vec3(0.01, 0.01, 1.0)), Func(self.suit.dropShadow.reparentTo, self.suit.getShadowJoint()), Func(self.suit.dropShadow.setPos, 0, 0, 0), Func(self.suit.dropShadow.setScale, shadowScale), Func(self.suit.initializeDropShadow))
                fadeInTrack = Sequence(Func(self.setTransparency, 1), self.colorScaleInterval(1, colorScale=VBase4(1, 1, 1, 1), startColorScale=VBase4(1, 1, 1, 0)), Func(self.clearColorScale), Func(self.clearTransparency))
                animTrack = Sequence(Func(self.suit.pose, 'landing', 0), Wait(waitTime), ActorInterval(self.suit, 'landing', duration=dur))
                animTrack.append(Func(self.loop, 'neutral'))
                propTrack = Parallel(SoundInterval(propInSound, duration=waitTime + dur, node=self), Sequence(ActorInterval(prop, 'propeller', constrainedLoop=1, duration=waitTime + spinTime, startTime=0.0, endTime=spinTime), ActorInterval(prop, 'propeller', duration=propDur - openTime, startTime=openTime), Func(prop.cleanup), Func(prop.removeNode)))
                return Parallel(Func(self.nametag3d.show), lerpPosTrack, shadowTrack, fadeInTrack, animTrack, propTrack)
            fadeInTrack = Sequence(Func(self.setTransparency, True), Func(self.setColorScale, 1, 1, 1, 0), Func(self.suit.loop, 'neutral'), Func(base.playSfx, fadingOn, node=self), self.colorScaleInterval(5, VBase4(1, 1, 1, 1)), Func(self.clearColorScale), Func(self.clearTransparency))
            return Parallel(Func(self.nametag3d.show), fadeInTrack)
        else:
            if self.suit.style.name != 'ty':
                lerpPosTrack = Sequence(Wait(impactLength), LerpPosInterval(self, timeTillLanding, skyPos, startPos=pos))
                shadowTrack = Sequence(Func(self.suit.dropShadow.reparentTo, render), Func(self.suit.dropShadow.setPos, pos), self.suit.dropShadow.scaleInterval(timeTillLanding, Vec3(0.01, 0.01, 1.0), startScale=self.suit.scale), Func(self.suit.dropShadow.reparentTo, self.suit.getShadowJoint()), Func(self.suit.dropShadow.setPos, 0, 0, 0))
                fadeOutTrack = Sequence(Func(self.setTransparency, 1), self.colorScaleInterval(1, colorScale=VBase4(1, 1, 1, 0), startColorScale=VBase4(1, 1, 1, 1)), Func(self.clearColorScale), Func(self.clearTransparency), Func(self.reparentTo, hidden))
                actInt = ActorInterval(self.suit, 'landing', loop=0, startTime=dur, endTime=0.0)
                prop.hide()
                propTrack = Parallel(SoundInterval(propOutSound, duration=waitTime + dur, node=self), Sequence(Func(prop.show), ActorInterval(prop, 'propeller', endTime=openTime, startTime=propDur), ActorInterval(prop, 'propeller', constrainedLoop=1, duration=propDur - openTime, startTime=spinTime, endTime=0.0), Func(prop.cleanup), Func(prop.removeNode)))
                return Parallel(ParallelEndTogether(lerpPosTrack, shadowTrack, fadeOutTrack), actInt, propTrack)
            fadeOutTrack = Sequence(Func(self.setTransparency, True), Func(self.setColorScale, 1, 1, 1, 1), Func(self.suit.loop, 'neutral'), Func(base.playSfx, fadingOff, node=self), self.colorScaleInterval(5, VBase4(1, 1, 1, 0)), Func(self.clearColorScale), Func(self.clearTransparency))
            return Parallel(fadeOutTrack)

    def getTeleportInTrack(self):
        if self.ghostMode:
            track = Sequence()
            return track
        if self.isDisguised:
            track = self.getSuitTeleport(moveIn=1)
            return track
        if self.isBecomePet:
            hole = self.getHoleActors()[0]
            hole.setBin('shadow', 0)
            hole.setDepthTest(0)
            hole.setDepthWrite(0)
            hole.reparentTo(self)
            pos = Point3(0, -1, 0)
            hole.setPos(self, pos)

            def cleanupHole(hole):
                hole.setPos(0, 0, 0)
                hole.detachNode()
                hole.clearBin()
                hole.clearDepthTest()
                hole.clearDepthWrite()

            track = Sequence(Parallel(SoundInterval(loader.loadSfx('phase_5/audio/sfx/teleport_reappear.ogg')), Sequence(ActorInterval(hole, 'hole', startFrame=81, endFrame=71), ActorInterval(self.pet, 'reappear'), ActorInterval(hole, 'hole', startFrame=71, endFrame=81), Func(cleanupHole, hole), Func(self.pet.loop, 'neutral')), Sequence(Func(self.dropShadow.hide), Wait(1.0), Func(self.dropShadow.show), Func(self.nametag3d.show))))
            return track
        hole = self.getHoleActors()[0]
        hole.setBin('shadow', 0)
        hole.setDepthTest(0)
        hole.setDepthWrite(0)
        holeTrack = Sequence()
        holeTrack.append(Func(hole.reparentTo, self))
        pos = Point3(0, -2.4, 0)
        holeTrack.append(Func(hole.setPos, self, pos))
        holeTrack.append(ActorInterval(hole, 'hole', startTime=3.4, endTime=3.1))
        holeTrack.append(Wait(0.6))
        holeTrack.append(ActorInterval(hole, 'hole', startTime=3.1, endTime=3.4))

        def restoreHole(hole):
            hole.setPos(0, 0, 0)
            hole.detachNode()
            hole.clearBin()
            hole.clearDepthTest()
            hole.clearDepthWrite()

        holeTrack.append(Func(restoreHole, hole))
        if self.isDisguised or self.isTransformed:
            self.getGeomNode().setTransparency(1)
            self.getGeomNode().setColorScale(1, 1, 1, 0)
            toonTrack = Sequence(Wait(0.3), Func(self.getGeomNode().show), Func(self.nametag3d.show), Func(self.dropShadow.show), ActorInterval(self, 'jump', startTime=0.45), Wait(1e-07), Func(self.getGeomNode().setTransparency, 0), Func(self.getGeomNode().setColorScale, 1, 1, 1, 1), Func(self.getGeomNode().hide))
        else:
            toonTrack = Sequence(Wait(0.3), Func(self.getGeomNode().show), Func(self.nametag3d.show), Func(self.dropShadow.show), ActorInterval(self, 'jump', startTime=0.45))
        if hasattr(self, 'uniqueName'):
            trackName = self.uniqueName('teleportIn')
        else:
            trackName = 'teleportIn'
        return Parallel(holeTrack, toonTrack, name=trackName)

    def enterTeleportIn(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        if self.ghostMode or self.isTransformed or self.isGoon or self.isBossCog:
            if callback:
                callback(*extraArgs)
            return
        self.show()
        self.playingAnim = 'teleport'
        Emote.globalEmote.disableAll(self, 'enterTeleportIn')
        self.pose('teleport', self.getNumFrames('teleport') - 1)
        self.getGeomNode().hide()
        self.nametag3d.hide()
        if not self.isDisguised:
            self.dropShadow.hide()
        self.track = self.getTeleportInTrack()
        if callback:
            self.track.setDoneEvent(self.track.getName())
            self.acceptOnce(self.track.getName(), callback, extraArgs)
        self.track.start(ts)
        self.setActiveShadow(0)

    def exitTeleportIn(self):
        self.playingAnim = None
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        if not self.ghostMode:
            if not self.isTransformed and not self.isDisguised and not self.isBecomePet and not self.isGoon and not self.isBossCog:
                self.getGeomNode().show()
            self.nametag3d.show()
        self.dropShadow.show()
        Emote.globalEmote.releaseAll(self, 'exitTeleportIn')
        return

    def enterSitStart(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        Emote.globalEmote.disableBody(self)
        self.playingAnim = 'sit-start'
        if self.isLocal():
            self.track = Sequence(ActorInterval(self, 'sit-start'), Func(self.b_setAnimState, 'Sit', animMultiplier))
        else:
            self.track = Sequence(ActorInterval(self, 'sit-start'))
        self.track.start(ts)
        self.setActiveShadow(0)

    def exitSitStart(self):
        self.playingAnim = self.neutralAnim
        if self.track != None:
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        Emote.globalEmote.releaseBody(self)
        return

    def enterSit(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        Emote.globalEmote.disableBody(self)
        self.playingAnim = 'sit'
        if self.isDisguised:
            self.suit.loop('sit')
        else:
            self.loop('sit')
        self.setActiveShadow(0)

    def exitSit(self):
        self.playingAnim = self.neutralAnim
        Emote.globalEmote.releaseBody(self)

    def enterSleep(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        self.stopLookAround()
        self.stopBlink()
        self.closeEyes()
        self.lerpLookAt(Point3(0, 1, -4))
        self.loop(self.neutralAnim)
        self.setPlayRate(animMultiplier * 0.4, self.neutralAnim)
        self.setChatAbsolute(SLEEP_STRING, CFThought)
        if self == base.localAvatar:
            self.notify.debug('Adding timeout task to Toon.')
            taskMgr.doMethodLater(self.afkTimeout, self.__handleAfkTimeout, self.uniqueName('afkTimeout'))
        self.setActiveShadow(0)

    def __handleAfkTimeout(self, task):
        self.notify.debug('Handling timeout task on Toon.')
        self.ignore('wakeup')
        self.takeOffSuit()
        base.cr.playGame.getPlace().fsm.request('final')
        self.b_setAnimState('TeleportOut', 1, self.__handleAfkExitTeleport, [0])
        return Task.done

    def __handleAfkExitTeleport(self, requestStatus):
        self.notify.info('closing shard...')
        base.cr.gameFSM.request('closeShard', ['afkTimeout'])

    def exitSleep(self):
        taskMgr.remove(self.uniqueName('afkTimeout'))
        self.startLookAround()
        self.openEyes()
        self.startBlink()
        if config.GetBool('stuck-sleep-fix', 1):
            doClear = SLEEP_STRING in (self.nametag.getChat(), self.nametag.getStompText())
        else:
            doClear = self.nametag.getChat() == SLEEP_STRING
        if doClear:
            self.clearChat()
        self.lerpLookAt(Point3(0, 1, 0), time=0.25)
        self.stop()

    def enterPush(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        Emote.globalEmote.disableBody(self)
        self.playingAnim = 'push'
        self.track = Sequence(ActorInterval(self, 'push'))
        self.track.loop()
        self.setActiveShadow(1)

    def exitPush(self):
        self.playingAnim = self.neutralAnim
        if self.track != None:
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        Emote.globalEmote.releaseBody(self)
        return

    def enterEmote(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        if len(extraArgs) > 0:
            emoteIndex = extraArgs[0]
        else:
            return
        self.playingAnim = None
        self.playingRate = None
        self.standWalkRunReverse = ((self.neutralAnim, 1.0),
         (
          self.walkAnim, 1.0),
         (
          self.runAnim, 1.0),
         (
          self.walkAnim, -1.0))
        self.setSpeed(self.forwardSpeed, self.rotateSpeed)
        if self.isLocal() and emoteIndex != Emote.globalEmote.EmoteSleepIndex:
            if self.sleepFlag:
                self.b_setAnimState('Happy', self.animMultiplier)
            self.wakeUp()
        duration = 0
        self.emoteTrack, duration = Emote.globalEmote.doEmote(self, emoteIndex, ts)
        self.setActiveShadow(1)
        return

    def doEmote(self, emoteIndex, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        if not self.isLocal():
            if base.cr.avatarFriendsManager.checkIgnored(self.doId):
                return
        duration = 0
        if self.isLocal():
            self.wakeUp()
            if self.hasTrackAnimToSpeed():
                self.trackAnimToSpeed(None)
        self.emoteTrack, duration = Emote.globalEmote.doEmote(self, emoteIndex, ts)
        return

    def __returnToLastAnim(self, task):
        if self.playingAnim:
            self.loop(self.playingAnim)
        else:
            if self.hp > 0:
                self.loop(self.neutralAnim)
            else:
                self.loop('sad-neutral')
        return Task.done

    def __finishEmote(self, task):
        if self.isLocal():
            if self.hp > 0:
                self.b_setAnimState('Happy')
            else:
                self.b_setAnimState('Sad')
        return Task.done

    def exitEmote(self):
        self.stop()
        if self.emoteTrack != None:
            self.emoteTrack.finish()
            self.emoteTrack = None
        taskMgr.remove(self.taskName('finishEmote'))
        return

    def enterSquish(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        Emote.globalEmote.disableAll(self)
        sound = loader.loadSfx('phase_9/audio/sfx/toon_decompress.ogg')
        lerpTime = 0.1
        if self.isDisguised:
            node = self.suit.getGeomNode().getChild(0)
        else:
            node = self.getGeomNode().getChild(0)
        origScale = node.getScale()
        if self.isDisguised:
            self.track = Sequence(LerpScaleInterval(node, lerpTime, VBase3(2, 2, 0.025), blendType='easeInOut'), Wait(1.0), Parallel(Sequence(Wait(0.4), LerpScaleInterval(node, lerpTime, VBase3(1.4, 1.4, 1.4), blendType='easeInOut'), LerpScaleInterval(node, lerpTime / 2.0, VBase3(0.8, 0.8, 0.8), blendType='easeInOut'), LerpScaleInterval(node, lerpTime / 3.0, origScale, blendType='easeInOut')), ActorInterval(self.suit, 'drop-react', startFrame=30), SoundInterval(sound)))
        else:
            self.track = Sequence(LerpScaleInterval(node, lerpTime, VBase3(2, 2, 0.025), blendType='easeInOut'), Wait(1.0), Parallel(Sequence(Wait(0.4), LerpScaleInterval(node, lerpTime, VBase3(1.4, 1.4, 1.4), blendType='easeInOut'), LerpScaleInterval(node, lerpTime / 2.0, VBase3(0.8, 0.8, 0.8), blendType='easeInOut'), LerpScaleInterval(node, lerpTime / 3.0, origScale, blendType='easeInOut')), ActorInterval(self, 'jump', startTime=0.2), SoundInterval(sound)))
        self.track.start(ts)
        self.setActiveShadow(1)

    def exitSquish(self):
        self.playingAnim = self.neutralAnim
        if self.track != None:
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        Emote.globalEmote.releaseAll(self)
        return

    def enterFallDown(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        self.playingAnim = 'fallDown'
        Emote.globalEmote.disableAll(self)
        if self.isDisguised:
            self.track = Sequence(ActorInterval(self.suit, 'slip-backward'), name='fallTrack')
        else:
            self.track = Sequence(ActorInterval(self, 'slip-backward'), name='fallTrack')
        if callback:
            self.track.setDoneEvent(self.track.getName())
            self.acceptOnce(self.track.getName(), callback, extraArgs)
        self.track.start(ts)

    def exitFallDown(self):
        self.playingAnim = self.neutralAnim
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        Emote.globalEmote.releaseAll(self)
        return

    def stunToon(self, ts=0, callback=None, knockdown=0, time=0.5):
        if not self.isStunned:
            if self.stunTrack:
                self.stunTrack.finish()
                self.stunTrack = None

            def setStunned(stunned):
                self.isStunned = stunned
                if self == base.localAvatar:
                    messenger.send('toonStunned-' + str(self.doId), [self.isStunned])

            node = self.getGeomNode()
            lerpTime = time
            down = self.doToonColorScale(VBase4(1, 1, 1, 0.6), lerpTime)
            up = self.doToonColorScale(VBase4(1, 1, 1, 0.9), lerpTime)
            clear = self.doToonColorScale(self.defaultColorScale, lerpTime)
            track = Sequence(Func(setStunned, 1), down, up, down, up, down, up, down, clear, Func(self.restoreDefaultColorScale), Func(setStunned, 0))
            if knockdown:
                if self.isDisguised:
                    self.stunTrack = Parallel(ActorInterval(self.suit, animName='slip-backward'), track)
                else:
                    self.stunTrack = Parallel(ActorInterval(self, animName='slip-backward'), track)
            else:
                self.stunTrack = track
            self.stunTrack.start()
        return

    def getPieces(self, *pieces):
        results = []
        for lodName in self.getLODNames():
            for partName, pieceNames in pieces:
                part = self.getPart(partName, lodName)
                if part:
                    if type(pieceNames) == types.StringType:
                        pieceNames = (
                         pieceNames,)
                    for pieceName in pieceNames:
                        npc = part.findAllMatches('**/%s;+s' % pieceName)
                        for i in range(npc.getNumPaths()):
                            results.append(npc[i])

        return results

    def applyCheesyEffect(self, effect, lerpTime=0):
        if self.effectTrack != None:
            self.effectTrack.finish()
            self.effectTrack = None
        if self.cheesyEffect != effect:
            oldEffect = self.cheesyEffect
            self.cheesyEffect = effect
            if oldEffect == ToontownGlobals.CENormal:
                self.effectTrack = self.__doCheesyEffect(effect, lerpTime)
            else:
                if effect == ToontownGlobals.CENormal:
                    self.effectTrack = self.__undoCheesyEffect(oldEffect, lerpTime)
                else:
                    self.effectTrack = Sequence(self.__undoCheesyEffect(oldEffect, lerpTime / 2.0), self.__doCheesyEffect(effect, lerpTime / 2.0))
            self.effectTrack.start()
        return

    def reapplyCheesyEffect(self, lerpTime=0):
        if self.effectTrack != None:
            self.effectTrack.finish()
            self.effectTrack = None
        effect = self.cheesyEffect
        self.effectTrack = Sequence(self.__undoCheesyEffect(effect, 0), self.__doCheesyEffect(effect, lerpTime))
        self.effectTrack.start()
        return

    def clearCheesyEffect(self, lerpTime=0):
        self.applyCheesyEffect(ToontownGlobals.CENormal, lerpTime=lerpTime)
        if self.effectTrack != None:
            self.effectTrack.finish()
            self.effectTrack = None
        return

    def __doHeadScale(self, scale, lerpTime):
        if scale == None:
            scale = ToontownGlobals.toonHeadScales[self.style.getAnimal()]
        track = Parallel()
        for hi in range(self.headParts.getNumPaths()):
            head = self.headParts[hi]
            track.append(LerpScaleInterval(head, lerpTime, scale, blendType='easeInOut'))

        return track

    def __doLegsScale(self, scale, lerpTime):
        if scale == None:
            scale = 1
            invScale = 1
        else:
            invScale = 1.0 / scale
        track = Parallel()
        for li in range(self.legsParts.getNumPaths()):
            legs = self.legsParts[li]
            torso = self.torsoParts[li]
            track.append(LerpScaleInterval(legs, lerpTime, scale, blendType='easeInOut'))
            track.append(LerpScaleInterval(torso, lerpTime, invScale, blendType='easeInOut'))

        return track

    def __doToonScale(self, scale, lerpTime):
        if scale == None:
            scale = 1
        node = self.getGeomNode().getChild(0)
        track = Sequence(Parallel(LerpHprInterval(node, lerpTime, Vec3(0.0, 0.0, 0.0), blendType='easeInOut'), LerpScaleInterval(node, lerpTime, scale, blendType='easeInOut')), Func(self.resetHeight))
        return track

    def setNodeTransparency(self, node, transparency):
        try:
            node.setTransparency(transparency)
        except:
            pass

    def clearNodeTransparency(self, node):
        try:
            node.clearTransparency()
        except:
            pass

    def doToonColorScale(self, scale, lerpTime, keepDefault=0):
        if keepDefault:
            self.defaultColorScale = scale
        if scale == None:
            scale = VBase4(1, 1, 1, 1)
        node = self.getGeomNode()
        caps = self.getPieces(('torso', 'torso-bot-cap'))
        track = Sequence()
        track.append(Func(self.setNodeTransparency, node, 1))
        if scale[3] != 1:
            for cap in caps:
                track.append(HideInterval(cap))

        track.append(LerpColorScaleInterval(node, lerpTime, scale, blendType='easeInOut'))
        if scale[3] == 1:
            track.append(Func(self.clearNodeTransparency, node))
            for cap in caps:
                track.append(ShowInterval(cap))

        else:
            if scale[3] == 0:
                track.append(Func(self.clearNodeTransparency, node))
        return track

    def __doPumpkinHeadSwitch(self, lerpTime, toPumpkin):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toPumpkin:
            track.append(Func(self.stopBlink))
            track.append(Func(self.closeEyes))
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            def hideParts():
                self.notify.debug('hideParts')
                for head in self.headParts:
                    for p in head.getChildren():
                        if hasattr(self, 'pumpkins') and not self.pumpkins.hasPath(p):
                            p.hide()
                            p.setTag('pumpkin', 'enabled')

            track.append(Func(hideParts))
            track.append(Func(self.enablePumpkins, True))
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            def showHiddenParts():
                self.notify.debug('showHiddenParts')
                for head in self.headParts:
                    for p in head.getChildren():
                        if not self.pumpkins.hasPath(p) and p.getTag('pumpkin') == 'enabled':
                            p.show()
                            p.setTag('pumpkin', 'disabled')

            track.append(Func(showHiddenParts))
            track.append(Func(self.enablePumpkins, False))
            track.append(Func(self.startBlink))
        return track

    def __doSnowManHeadSwitch(self, lerpTime, toSnowMan):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toSnowMan:
            track.append(Func(self.stopBlink))
            track.append(Func(self.closeEyes))
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            def hideParts():
                self.notify.debug('HidePaths')
                for hi in range(self.headParts.getNumPaths()):
                    head = self.headParts[hi]
                    parts = head.getChildren()
                    for pi in range(parts.getNumPaths()):
                        p = parts[pi]
                        if not p.isHidden():
                            p.hide()
                            p.setTag('snowman', 'enabled')

            track.append(Func(hideParts))
            track.append(Func(self.enableSnowMen, True))
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            def showHiddenParts():
                self.notify.debug('ShowHiddenPaths')
                for hi in range(self.headParts.getNumPaths()):
                    head = self.headParts[hi]
                    parts = head.getChildren()
                    for pi in range(parts.getNumPaths()):
                        p = parts[pi]
                        if not self.snowMen.hasPath(p) and p.getTag('snowman') == 'enabled':
                            p.show()
                            p.setTag('snowman', 'disabled')

            track.append(Func(showHiddenParts))
            track.append(Func(self.enableSnowMen, False))
            track.append(Func(self.startBlink))
        return track

    def __doGreenToon(self, lerpTime, toGreen):
        track = Sequence()
        greenTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
        if toGreen:
            skinGreen = VBase4(76 / 255.0, 240 / 255.0, 84 / 255.0, 1)
            muzzleGreen = VBase4(4 / 255.0, 205 / 255.0, 90 / 255.0, 1)
            gloveGreen = VBase4(14 / 255.0, 173 / 255.0, 40 / 255.0, 1)
            greenTrack.append(self.__colorToonSkin(skinGreen, lerpTime))
            greenTrack.append(self.__colorToonEars(skinGreen, muzzleGreen, lerpTime))
            greenTrack.append(self.__colorScaleToonMuzzle(muzzleGreen, lerpTime))
            greenTrack.append(self.__colorToonGloves(gloveGreen, lerpTime))
        else:
            greenTrack.append(self.__colorToonSkin(None, lerpTime))
            greenTrack.append(self.__colorToonEars(None, None, lerpTime))
            greenTrack.append(self.__colorScaleToonMuzzle(None, lerpTime))
            greenTrack.append(self.__colorToonGloves(None, lerpTime))
        track.append(greenTrack)
        return track

    def __doRogerDog(self, lerpTime, toRoger):
        track = Sequence()
        rogerTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
        if toRoger:
            self.oldStyle = self.style.clone()
            self.oldHat = self.hat
            dna = ToonDNA.ToonDNA()
            dna.newToonFromProperties('dll', 'ls', 'l', 'm', 19, 0, 21, 8, 4, 0, 4, 0, 7, 15)
            rogerTrack.append(Func(self.updateToonDNA, dna, True))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                rogerTrack.append(Func(self.animFSM.request, 'off'))
                rogerTrack.append(Func(self.animFSM.request, state))
            rogerTrack.append(Func(self.nametag.setDisplayName, 'Roger Dog'))
            rogerTrack.append(Func(self.setHat, 24, 0, 0))
        else:
            rogerTrack.append(Func(self.updateToonDNA, self.oldStyle))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                rogerTrack.append(Func(self.animFSM.request, 'off'))
                rogerTrack.append(Func(self.animFSM.request, state))
            rogerTrack.append(Func(self.nametag.setDisplayName, self.nametag.name))
            rogerTrack.append(Func(self.setHat, self.oldHat[0], self.oldHat[1], self.oldHat[2]))
            rogerTrack.append(Func(self.generateToonAccessories))
        track.append(rogerTrack)
        return track

    def __doFlippy(self, lerpTime, toFlippy):
        track = Sequence()
        flippyTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
        if toFlippy:
            self.oldStyle = self.style.clone()
            self.oldHat = self.hat
            dna = ToonDNA.ToonDNA()
            dna.newToonFromProperties('dss', 'ms', 'm', 'm', 17, 0, 17, 17, 3, 3, 3, 3, 7, 2)
            flippyTrack.append(Func(self.updateToonDNA, dna, True))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                flippyTrack.append(Func(self.animFSM.request, 'off'))
                flippyTrack.append(Func(self.animFSM.request, state))
            flippyTrack.append(Func(self.nametag.setDisplayName, 'Flippy'))
        else:
            flippyTrack.append(Func(self.updateToonDNA, self.oldStyle))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                flippyTrack.append(Func(self.animFSM.request, 'off'))
                flippyTrack.append(Func(self.animFSM.request, state))
            flippyTrack.append(Func(self.nametag.setDisplayName, self.nametag.name))
            flippyTrack.append(Func(self.setHat, self.oldHat[0], self.oldHat[1], self.oldHat[2]))
            flippyTrack.append(Func(self.generateToonAccessories))
        track.append(flippyTrack)
        return track

    def __doSurlee(self, lerpTime, toSurlee):
        track = Sequence()
        surleeTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
        if toSurlee:
            self.oldStyle = self.style.clone()
            self.oldHat = self.hat
            dna = ToonDNA.ToonDNA()
            dna.newToonFromProperties('pls', 'ls', 'l', 'm', 9, 0, 9, 9, 98, 27, 86, 27, 38, 27)
            surleeTrack.append(Func(self.updateToonDNA, dna, True))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                surleeTrack.append(Func(self.animFSM.request, 'off'))
                surleeTrack.append(Func(self.animFSM.request, state))
            surleeTrack.append(Func(self.nametag.setDisplayName, 'Doctor Surlee'))
        else:
            surleeTrack.append(Func(self.updateToonDNA, self.oldStyle))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                surleeTrack.append(Func(self.animFSM.request, 'off'))
                surleeTrack.append(Func(self.animFSM.request, state))
            surleeTrack.append(Func(self.nametag.setDisplayName, self.nametag.name))
            surleeTrack.append(Func(self.setHat, self.oldHat[0], self.oldHat[1], self.oldHat[2]))
            surleeTrack.append(Func(self.generateToonAccessories))
        track.append(surleeTrack)
        return track

    def __doPrepostera(self, lerpTime, toPrepostera):
        track = Sequence()
        preposteraTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
        if toPrepostera:
            self.oldStyle = self.style.clone()
            self.oldHat = self.hat
            dna = ToonDNA.ToonDNA()
            dna.newToonFromProperties('hss', 'ms', 'm', 'm', 20, 0, 20, 20, 97, 27, 86, 27, 37, 27)
            preposteraTrack.append(Func(self.updateToonDNA, dna, True))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                preposteraTrack.append(Func(self.animFSM.request, 'off'))
                preposteraTrack.append(Func(self.animFSM.request, state))
            preposteraTrack.append(Func(self.nametag.setDisplayName, 'Professor Prepostera'))
        else:
            preposteraTrack.append(Func(self.updateToonDNA, self.oldStyle))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                preposteraTrack.append(Func(self.animFSM.request, 'off'))
                preposteraTrack.append(Func(self.animFSM.request, state))
            preposteraTrack.append(Func(self.nametag.setDisplayName, self.nametag.name))
            preposteraTrack.append(Func(self.setHat, self.oldHat[0], self.oldHat[1], self.oldHat[2]))
            preposteraTrack.append(Func(self.generateToonAccessories))
        track.append(preposteraTrack)
        return track

    def __doAnimeChair(self, lerpTime, toAnime):
        track = Sequence()
        animeTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
        if toAnime:
            self.animeChair = Actor.Actor('phase_14/models/char/anime-chairman-mod', {'neutral': 'phase_14/models/char/anime-chairman-neutral', 'walk': 'phase_14/models/char/anime-chairman-walk', 
               'run': 'phase_14/models/char/anime-chairman-run', 
               'jump': 'phase_14/models/char/anime-chairman-jump'})
            self.animeChair.setBlend(frameBlend=config.GetBool('interpolate-animations', True))
            self.animeChair.loop('neutral')
            self.animeChair.setH(180)
            self.animeChair.setScale(self.magicScale)
            shadow = loader.loadModel('phase_3/models/props/drop_shadow')
            shadow.reparentTo(self.animeChair)
            shadow.setScale(0.69)
            shadow.setAlphaScale(0.69)
            shadow.setZ(0.069)
            animeTrack.append(Func(self.find('**/actorGeom').hide))
            animeTrack.append(Func(self.animeChair.reparentTo, self))
            animeTrack.append(Func(self.resetHeight))
        else:
            if self.animeChair:
                animeTrack.append(Func(self.killAnime))
                animeTrack.append(Func(self.find('**/actorGeom').show))
                animeTrack.append(Func(self.resetHeight))
        track.append(animeTrack)
        return track

    def killAnime(self):
        self.animeChair.cleanup()
        self.animeChair.delete()
        self.animeChair.removeNode()
        self.animeChair = None
        return

    def setEyes(self, eyes):
        if eyes == 0:
            Sequence(Func(self.blinkEyes), Func(self.normalEyes), Func(self.startBlink)).start()
            if self.animeChair:
                self.animeChair.find('**/eyes').setTexture(loader.loadTexture('phase_14/maps/calm.png'), 1)
        else:
            if eyes == 1:
                Sequence(Func(self.blinkEyes), Func(self.sadEyes), Func(self.startBlink)).start()
                if self.animeChair:
                    self.animeChair.find('**/eyes').setTexture(loader.loadTexture('phase_14/maps/sad.png'), 1)
            else:
                if eyes == 2:
                    Sequence(Func(self.blinkEyes), Func(self.angryEyes), Func(self.startBlink)).start()
                    if self.animeChair:
                        self.animeChair.find('**/eyes').setTexture(loader.loadTexture('phase_14/maps/angry.png'), 1)
                else:
                    if eyes == 3:
                        Sequence(Func(self.blinkEyes), Func(self.surpriseEyes), Func(self.stopBlink)).start()
                        if self.animeChair:
                            self.animeChair.find('**/eyes').setTexture(loader.loadTexture('phase_14/maps/shock.png'), 1)
                    else:
                        if eyes == 4:
                            Sequence(Func(self.blinkEyes), Func(self.riggyEyes), Func(self.startBlink)).start()
                            if self.animeChair:
                                self.animeChair.find('**/eyes').setTexture(loader.loadTexture('phase_14/maps/weeb.png'), 1)

    def __doMagicCat(self, lerpTime, toMagicCat):
        track = Sequence()
        magicCatTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
        if toMagicCat:
            self.oldStyle = self.style.clone()
            self.oldHat = self.hat
            self.oldName = self.nametag.name
            dna = ToonDNA.ToonDNA()
            dna.newToonFromProperties('css', 'ms', 'm', 'm', 26, 0, 26, 26, 0, 10, 0, 10, 0, 10)
            magicCatTrack.append(Func(self.updateToonDNA, dna, True))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                magicCatTrack.append(Func(self.animFSM.request, 'off'))
                magicCatTrack.append(Func(self.animFSM.request, state))
            magicCatTrack.append(Func(self.nametag.setName, ''))
            magicCatTrack.append(Func(self.nametag.setDisplayName, ''))
            magicCatTrack.append(Func(LaughingManGlobals.addToonEffect, self))
        else:
            magicCatTrack.append(Func(self.updateToonDNA, self.oldStyle))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                magicCatTrack.append(Func(self.animFSM.request, 'off'))
                magicCatTrack.append(Func(self.animFSM.request, state))
            magicCatTrack.append(Func(self.nametag.setName, self.oldName))
            magicCatTrack.append(Func(self.nametag.setDisplayName, self.oldName))
            magicCatTrack.append(Func(self.setHat, self.oldHat[0], self.oldHat[1], self.oldHat[2]))
            magicCatTrack.append(Func(self.generateToonAccessories))
        track.append(magicCatTrack)
        return track

    def __doGhostHead(self, lerpTime, toGhostHead):
        track = Sequence()
        ghostHeadTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
        if toGhostHead:
            self.oldStyle = self.style.clone()
            self.oldHat = self.hat
            dna = ToonDNA.ToonDNA()
            dna.newToonFromProperties('dss', 'ms', 'm', 'm', 26, 0, 26, 26, 0, 27, 0, 27, 50, 27)
            ghostHeadTrack.append(Func(self.updateToonDNA, dna, True))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                ghostHeadTrack.append(Func(self.animFSM.request, 'off'))
                ghostHeadTrack.append(Func(self.animFSM.request, state))
            ghostHeadTrack.append(Func(self.nametag.setDisplayName, 'Crypt'))
            ghostHeadTrack.append(Func(GhostHeadGlobals.addToonEffect, self))
        else:
            ghostHeadTrack.append(Func(self.updateToonDNA, self.oldStyle))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                ghostHeadTrack.append(Func(self.animFSM.request, 'off'))
                ghostHeadTrack.append(Func(self.animFSM.request, state))
            ghostHeadTrack.append(Func(self.nametag.setDisplayName, self.nametag.name))
            ghostHeadTrack.append(Func(self.setHat, self.oldHat[0], self.oldHat[1], self.oldHat[2]))
            ghostHeadTrack.append(Func(self.generateToonAccessories))
        track.append(ghostHeadTrack)
        return track

    def __doSurleeCutout(self, lerpTime, toSurleeCutout):
        track = Sequence()
        surleeTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
        if toSurleeCutout:
            hotSurleeSign = loader.loadModel('phase_3.5/models/modules/tt_m_ara_int_scientistMonkeyFlat')
            hotSurleeSign.find('**/collision').removeNode()
            hotSurleeSign.setScale(0.47)
            hotSurleeSign.setH(180)
            shadow = loader.loadModel('phase_3/models/props/drop_shadow')
            shadow.reparentTo(hotSurleeSign)
            shadow.setScale(0.69)
            shadow.setAlphaScale(0.69)
            shadow.setZ(0.069)
            surleeTrack.append(Func(self.find('**/actorGeom').hide))
            surleeTrack.append(Func(hotSurleeSign.reparentTo, self))
        else:
            if self.findAllMatches('**/tt_m_ara_int_scientistMonkeyFlat.egg'):
                surleeTrack.append(Func(self.find('**/tt_m_ara_int_scientistMonkeyFlat.egg').removeNode))
                surleeTrack.append(Func(self.find('**/actorGeom').show))
        track.append(surleeTrack)
        return track

    def __doPreposteraCutout(self, lerpTime, toPreposteraCutout):
        track = Sequence()
        preposteraTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
        if toPreposteraCutout:
            preposteraIsGod = loader.loadModel('phase_3.5/models/modules/tt_m_ara_int_scientistHorseFlat')
            preposteraIsGod.find('**/collision').removeNode()
            preposteraIsGod.setScale(0.75)
            preposteraIsGod.setH(180)
            shadow = loader.loadModel('phase_3/models/props/drop_shadow')
            shadow.reparentTo(preposteraIsGod)
            shadow.setScale(0.75)
            shadow.setAlphaScale(0.75)
            shadow.setZ(0.075)
            preposteraTrack.append(Func(self.find('**/actorGeom').hide))
            preposteraTrack.append(Func(preposteraIsGod.reparentTo, self))
        else:
            if self.findAllMatches('**/tt_m_ara_int_scientistHorseFlat.egg'):
                preposteraTrack.append(Func(self.find('**/tt_m_ara_int_scientistHorseFlat.egg').removeNode))
                preposteraTrack.append(Func(self.find('**/actorGeom').show))
        track.append(preposteraTrack)
        return track

    def __doDimmCutout(self, lerpTime, toDimmCutout):
        track = Sequence()
        dimmTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
        if toDimmCutout:
            dimmThicc = loader.loadModel('phase_3.5/models/modules/tt_m_ara_int_scientistDuckFlat')
            dimmThicc.find('**/collision').removeNode()
            dimmThicc.setScale(0.75)
            dimmThicc.setH(180)
            shadow = loader.loadModel('phase_3/models/props/drop_shadow')
            shadow.reparentTo(dimmThicc)
            shadow.setScale(0.75)
            shadow.setAlphaScale(0.75)
            shadow.setZ(0.075)
            dimmTrack.append(Func(self.find('**/actorGeom').hide))
            dimmTrack.append(Func(dimmThicc.reparentTo, self))
        else:
            if self.findAllMatches('**/tt_m_ara_int_scientistDuckFlat.egg'):
                dimmTrack.append(Func(self.find('**/tt_m_ara_int_scientistDuckFlat.egg').removeNode))
                dimmTrack.append(Func(self.find('**/actorGeom').show))
        track.append(dimmTrack)
        return track

    def __doRiggy(self, lerpTime, toRiggy):
        track = Sequence()
        riggyTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
        if toRiggy:
            self.oldStyle = self.style.clone()
            self.oldShoes = self.shoes
            dna = ToonDNA.ToonDNA()
            dna.newToonFromProperties('gsl', 'ls', 'l', 'm', 27, 0, 27, 27, 160, 27, 149, 27, 67, 27)
            riggyTrack.append(Func(self.updateToonDNA, dna, True))
            riggyTrack.append(Func(self.loop, 'riggyNeutral'))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                riggyTrack.append(Func(self.animFSM.request, 'off'))
                riggyTrack.append(Func(self.animFSM.request, state))
            riggyTrack.append(Func(self.setShoes, 1, 54, 0))
            riggyTrack.append(Func(self.nametag.setDisplayName, 'Riggy Marole'))
        else:
            riggyTrack.append(Func(self.updateToonDNA, self.oldStyle))
            riggyTrack.append(Func(self.loop, 'neutral'))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                riggyTrack.append(Func(self.animFSM.request, 'off'))
                riggyTrack.append(Func(self.animFSM.request, state))
            riggyTrack.append(Func(self.nametag.setDisplayName, self.nametag.name))
            riggyTrack.append(Func(self.setShoes, self.oldShoes[0], self.oldShoes[1], self.oldShoes[2]))
            riggyTrack.append(Func(self.generateToonAccessories))
        track.append(riggyTrack)
        return track

    def __colorToonSkin(self, color, lerpTime):
        track = Sequence()
        colorTrack = Parallel()
        torsoPieces = self.getPieces(('torso', ('arms', 'neck')))
        legPieces = self.getPieces(('legs', ('legs', 'feet')))
        headPieces = self.getPieces(('head', '*head*'))
        if color == None:
            armColor = self.style.getArmColor()
            legColor = self.style.getLegColor()
            headColor = self.style.getHeadColor()
        else:
            armColor = color
            legColor = color
            headColor = color
        for piece in torsoPieces:
            colorTrack.append(Func(piece.setColor, armColor))

        for piece in legPieces:
            colorTrack.append(Func(piece.setColor, legColor))

        for piece in headPieces:
            if 'hatNode' not in str(piece) and 'glassesNode' not in str(piece):
                colorTrack.append(Func(piece.setColor, headColor))

        track.append(colorTrack)
        return track

    def __colorToonEars(self, color, colorScale, lerpTime):
        track = Sequence()
        earPieces = self.getPieces(('head', '*ear*'))
        if len(earPieces) == 0:
            return track
        colorTrack = Parallel()
        if earPieces[0].hasColor():
            if color == None:
                headColor = self.style.getHeadColor()
            else:
                headColor = color
            for piece in earPieces:
                colorTrack.append(Func(piece.setColor, headColor))

        else:
            if colorScale == None:
                colorScale = VBase4(1, 1, 1, 1)
            for piece in earPieces:
                colorTrack.append(Func(piece.setColorScale, colorScale))

        track.append(colorTrack)
        return track

    def __colorScaleToonMuzzle(self, scale, lerpTime):
        track = Sequence()
        colorTrack = Parallel()
        muzzlePieces = self.getPieces(('head', '*muzzle*'))
        if scale == None:
            scale = VBase4(1, 1, 1, 1)
        for piece in muzzlePieces:
            colorTrack.append(Func(piece.setColorScale, scale))

        track.append(colorTrack)
        return track

    def __colorToonGloves(self, color, lerpTime):
        track = Sequence()
        colorTrack = Parallel()
        glovePieces = self.getPieces(('torso', '*hands*'))
        if color == None:
            for piece in glovePieces:
                colorTrack.append(Func(piece.clearColor))

        else:
            for piece in glovePieces:
                colorTrack.append(Func(piece.setColor, color))

        track.append(colorTrack)
        return track

    def __doBigAndWhite(self, color, scale, lerpTime):
        track = Parallel()
        track.append(self.__doToonColor(color, lerpTime))
        track.append(self.__doToonScale(scale, lerpTime))
        return track

    def __doVirtual(self):
        track = Parallel()
        track.append(self.__doToonColor(VBase4(0.25, 0.25, 1.0, 1), 0.0))
        self.setPartsAdd(self.getHeadParts())
        self.setPartsAdd(self.getTorsoParts())
        self.setPartsAdd(self.getHipsParts())
        self.setPartsAdd(self.getLegsParts())
        return track

    def __doUnVirtual(self):
        track = Parallel()
        track.append(self.__doToonColor(None, 0.0))
        self.setPartsNormal(self.getHeadParts(), 1)
        self.setPartsNormal(self.getTorsoParts(), 1)
        self.setPartsNormal(self.getHipsParts(), 1)
        self.setPartsNormal(self.getLegsParts(), 1)
        return track

    def setPartsAdd(self, parts):
        actorCollection = parts
        for thingIndex in range(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            if thing.getName() not in ('joint_attachMeter', 'joint_nameTag'):
                thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                thing.setDepthWrite(False)
                self.setBin('fixed', 1)

    def setPartsNormal(self, parts, alpha=0):
        actorCollection = parts
        for thingIndex in range(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            if thing.getName() not in ('joint_attachMeter', 'joint_nameTag'):
                thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MNone))
                thing.setDepthWrite(True)
                self.setBin('default', 0)
                if alpha:
                    thing.setTransparency(1)
                    thing.setBin('transparent', 0)

    def __doToonGhostColorScale(self, scale, lerpTime, keepDefault=0):
        if keepDefault:
            self.defaultColorScale = scale
        if scale == None:
            scale = VBase4(1, 1, 1, 1)
        node = self.getGeomNode()
        caps = self.getPieces(('torso', 'torso-bot-cap'))
        track = Sequence()
        track.append(Func(node.setTransparency, 1))
        track.append(ShowInterval(node))
        if scale[3] != 1:
            for cap in caps:
                track.append(HideInterval(cap))

        track.append(LerpColorScaleInterval(node, lerpTime, scale, blendType='easeInOut'))
        if scale[3] == 1:
            track.append(Func(node.clearTransparency))
            for cap in caps:
                track.append(ShowInterval(cap))

        else:
            if scale[3] == 0:
                track.append(Func(node.clearTransparency))
                track.append(HideInterval(node))
        return track

    def restoreDefaultColorScale(self):
        node = self.getGeomNode()
        if node:
            if self.defaultColorScale:
                node.setColorScale(self.defaultColorScale)
                if self.defaultColorScale[3] != 1:
                    node.setTransparency(1)
                else:
                    node.clearTransparency()
            else:
                node.clearColorScale()
                node.clearTransparency()

    def __doToonColor(self, color, lerpTime):
        node = self.getGeomNode()
        if color == None:
            return Func(node.clearColor)
        return Func(node.setColor, color, 1)
        return

    def __doPartsColorScale(self, scale, lerpTime):
        if scale == None:
            scale = VBase4(1, 1, 1, 1)
        node = self.getGeomNode()
        pieces = self.getPieces(('torso', ('arms', 'neck')), ('legs', ('legs', 'feet')), ('head',
                                                                                          '+GeomNode'))
        track = Sequence()
        track.append(Func(node.setTransparency, 1))
        for piece in pieces:
            if piece.getName()[:7] == 'muzzle-' and piece.getName()[-8:] != '-neutral':
                continue
            track.append(ShowInterval(piece))

        p1 = Parallel()
        for piece in pieces:
            if piece.getName()[:7] == 'muzzle-' and piece.getName()[-8:] != '-neutral':
                continue
            p1.append(LerpColorScaleInterval(piece, lerpTime, scale, blendType='easeInOut'))

        track.append(p1)
        if scale[3] == 1:
            track.append(Func(node.clearTransparency))
        else:
            if scale[3] == 0:
                track.append(Func(node.clearTransparency))
                for piece in pieces:
                    if piece.getName()[:7] == 'muzzle-' and piece.getName()[-8:] != '-neutral':
                        continue
                    track.append(HideInterval(piece))

        self.generateHat()
        self.generateGlasses()
        return track

    def __doCheesyEffect(self, effect, lerpTime):
        if effect == ToontownGlobals.CEBigHead:
            return self.__doHeadScale(2.5, lerpTime)
        if effect == ToontownGlobals.CESmallHead:
            return self.__doHeadScale(0.5, lerpTime)
        if effect == ToontownGlobals.CEBigLegs:
            return self.__doLegsScale(1.4, lerpTime)
        if effect == ToontownGlobals.CESmallLegs:
            return self.__doLegsScale(0.6, lerpTime)
        if effect == ToontownGlobals.CEBigToon:
            return self.__doToonScale(ToontownGlobals.BigToonScale, lerpTime)
        if effect == ToontownGlobals.CESmallToon:
            return self.__doToonScale(ToontownGlobals.SmallToonScale, lerpTime)
        if effect == ToontownGlobals.CEFlatPortrait:
            return self.__doToonScale(VBase3(1, 0.05, 1), lerpTime)
        if effect == ToontownGlobals.CEFlatProfile:
            return self.__doToonScale(VBase3(0.05, 1, 1), lerpTime)
        if effect == ToontownGlobals.CETransparent:
            return self.doToonColorScale(VBase4(1, 1, 1, 0.6), lerpTime, keepDefault=1)
        if effect == ToontownGlobals.CENoColor:
            return self.__doToonColor(VBase4(1, 1, 1, 1), lerpTime)
        if effect == ToontownGlobals.CEInvisible:
            return self.__doPartsColorScale(VBase4(1, 1, 1, 0), lerpTime)
        if effect == ToontownGlobals.CEPumpkin:
            return self.__doPumpkinHeadSwitch(lerpTime, toPumpkin=True)
        if effect == ToontownGlobals.CEBigWhite:
            return self.__doBigAndWhite(VBase4(1, 1, 1, 1), ToontownGlobals.BigToonScale, lerpTime)
        if effect == ToontownGlobals.CESnowMan:
            return self.__doSnowManHeadSwitch(lerpTime, toSnowMan=True)
        if effect == ToontownGlobals.CEGreenToon:
            return self.__doGreenToon(lerpTime, toGreen=True)
        if effect == ToontownGlobals.CERogerDog:
            return self.__doRogerDog(lerpTime, toRoger=True)
        if effect == ToontownGlobals.CEFlippy:
            return self.__doFlippy(lerpTime, toFlippy=True)
        if effect == ToontownGlobals.CESurlee:
            return self.__doSurlee(lerpTime, toSurlee=True)
        if effect == ToontownGlobals.CEPrepostera:
            return self.__doPrepostera(lerpTime, toPrepostera=True)
        if effect == ToontownGlobals.CEMagicCat:
            return self.__doMagicCat(lerpTime, toMagicCat=True)
        if effect == ToontownGlobals.CEGhostHead:
            return self.__doGhostHead(lerpTime, toGhostHead=True)
        if effect == ToontownGlobals.CERiggy:
            return self.__doRiggy(lerpTime, toRiggy=True)
        if effect == ToontownGlobals.CEVirtual:
            return self.__doVirtual()
        if effect == ToontownGlobals.CEGhost:
            alpha = 0
            if localAvatar.seeGhosts:
                alpha = 0.2
            return Sequence(self.__doToonGhostColorScale(VBase4(1, 1, 1, alpha), lerpTime, keepDefault=1), Func(self.nametag3d.hide))
        if effect == ToontownGlobals.CESurleeCutout:
            return self.__doSurleeCutout(lerpTime, toSurleeCutout=True)
        if effect == ToontownGlobals.CEPreposteraCutout:
            return self.__doPreposteraCutout(lerpTime, toPreposteraCutout=True)
        if effect == ToontownGlobals.CEDimmCutout:
            return self.__doDimmCutout(lerpTime, toDimmCutout=True)
        if effect == ToontownGlobals.CEAnime:
            return self.__doAnimeChair(lerpTime, toAnime=True)
        return Sequence()

    def __undoCheesyEffect(self, effect, lerpTime):
        if effect == ToontownGlobals.CEBigHead:
            return self.__doHeadScale(None, lerpTime)
        if effect == ToontownGlobals.CESmallHead:
            return self.__doHeadScale(None, lerpTime)
        if effect == ToontownGlobals.CEBigLegs:
            return self.__doLegsScale(None, lerpTime)
        if effect == ToontownGlobals.CESmallLegs:
            return self.__doLegsScale(None, lerpTime)
        if effect == ToontownGlobals.CEBigToon:
            return self.__doToonScale(None, lerpTime)
        if effect == ToontownGlobals.CESmallToon:
            return self.__doToonScale(None, lerpTime)
        if effect == ToontownGlobals.CEFlatPortrait:
            return self.__doToonScale(None, lerpTime)
        if effect == ToontownGlobals.CEFlatProfile:
            return self.__doToonScale(None, lerpTime)
        if effect == ToontownGlobals.CETransparent:
            return self.doToonColorScale(None, lerpTime, keepDefault=1)
        if effect == ToontownGlobals.CENoColor:
            return self.__doToonColor(None, lerpTime)
        if effect == ToontownGlobals.CEInvisible:
            return self.__doPartsColorScale(None, lerpTime)
        if effect == ToontownGlobals.CEPumpkin:
            return self.__doPumpkinHeadSwitch(lerpTime, toPumpkin=False)
        if effect == ToontownGlobals.CEBigWhite:
            return self.__doBigAndWhite(None, None, lerpTime)
        if effect == ToontownGlobals.CESnowMan:
            return self.__doSnowManHeadSwitch(lerpTime, toSnowMan=False)
        if effect == ToontownGlobals.CEGreenToon:
            return self.__doGreenToon(lerpTime, toGreen=False)
        if effect == ToontownGlobals.CERogerDog:
            return self.__doRogerDog(lerpTime, toRoger=False)
        if effect == ToontownGlobals.CEFlippy:
            return self.__doFlippy(lerpTime, toFlippy=False)
        if effect == ToontownGlobals.CESurlee:
            return self.__doSurlee(lerpTime, toSurlee=False)
        if effect == ToontownGlobals.CEPrepostera:
            return self.__doPrepostera(lerpTime, toPrepostera=False)
        if effect == ToontownGlobals.CEMagicCat:
            return self.__doMagicCat(lerpTime, toMagicCat=False)
        if effect == ToontownGlobals.CEGhostHead:
            return self.__doGhostHead(lerpTime, toGhostHead=False)
        if effect == ToontownGlobals.CERiggy:
            return self.__doRiggy(lerpTime, toRiggy=False)
        if effect == ToontownGlobals.CEVirtual:
            return self.__doUnVirtual()
        if effect == ToontownGlobals.CEGhost:
            return Sequence(Func(self.nametag3d.show), self.__doToonGhostColorScale(None, lerpTime, keepDefault=1))
        if effect == ToontownGlobals.CESurleeCutout:
            return self.__doSurleeCutout(lerpTime, toSurleeCutout=False)
        if effect == ToontownGlobals.CEPreposteraCutout:
            return self.__doPreposteraCutout(lerpTime, toPreposteraCutout=False)
        if effect == ToontownGlobals.CEDimmCutout:
            return self.__doDimmCutout(lerpTime, toDimmCutout=False)
        if effect == ToontownGlobals.CEAnime:
            return self.__doAnimeChair(lerpTime, toAnime=False)
        return Sequence()

    def putOnSuit(self, suitType, setDisplayName=True, rental=False, becomeCog=0, tpose=False):
        if self.isDisguised:
            self.takeOffSuit()
        if self.isTransformed:
            self.becomeToon()
        if self.isBecomePet:
            self.noMorePet()
        if self.isGoon:
            self.noMoreGoon()
        if self.isBossCog:
            self.noMoreBoss()
        if launcher and not launcher.getPhaseComplete(5) or suitType == '':
            return
        from toontown.suit import Suit
        from toontown.suit import DistributedFactorySuit
        deptIndex = suitType
        suit = Suit.Suit(isToon=True)
        dna = SuitDNA.SuitDNA()
        if rental == True:
            if SuitDNA.suitDepts[deptIndex] == 's':
                suitType = 'cc'
            elif SuitDNA.suitDepts[deptIndex] == 'm':
                suitType = 'sc'
            elif SuitDNA.suitDepts[deptIndex] == 'l':
                suitType = 'bf'
            elif SuitDNA.suitDepts[deptIndex] == 'c':
                suitType = 'f'
            elif SuitDNA.suitDepts[deptIndex] == 'g':
                suitType = 'm1'
            else:
                self.notify.warning('Suspicious: Incorrect rental suit department requested')
                suitType = 'cc'
        else:
            if becomeCog in SuitDNA.extraSuitsIndex:
                suitType = SuitDNA.extraSuitsIndex.get(becomeCog)
        dna.newSuit(suitType)
        suit.setStyle(dna)
        suit.dna = dna
        suit.isDisguised = 1
        suit.generateSuit()
        suit.initializeDropShadow()
        suit.setPos(self.getPos())
        suit.setHpr(self.getHpr())
        if becomeCog == 5 or not becomeCog:
            for part in suit.getHeadParts():
                part.hide()

        if becomeCog == 2 or becomeCog == 6 or becomeCog == 81 or becomeCog == 31:
            suit.makeSkeleton()
        else:
            if becomeCog == 3 or becomeCog == 5 or becomeCog == 25:
                suit.makeWaiter()
        if becomeCog == 6 or becomeCog == 7:
            suit.virtualify()
        else:
            if becomeCog == 31:
                suit.skelemishify()
        Emote.globalEmote.disableAll(self)
        if suit.style.body == 'a':
            suitHeadNull = suit.find('**/to_head')
        else:
            suitHeadNull = suit.find('**/joint_head')
        toonHead = self.getPart('head', '1000')
        toonGeom = self.getGeomNode()
        toonGeom.hide()
        worldScale = toonHead.getScale(render)
        self.headOrigScale = toonHead.getScale()
        headPosNode = hidden.attachNewNode('headPos')
        toonHead.reparentTo(headPosNode)
        if becomeCog != 5 and becomeCog:
            toonHead.reparentTo(hidden)
        toonHead.setPos(0, 0, 0.2)
        headPosNode.reparentTo(suitHeadNull)
        headPosNode.setScale(render, worldScale)
        suitGeom = suit.getGeomNode()
        suitGeom.reparentTo(self)
        if rental == True and not (suitType == 'cc' and becomeCog == 2):
            suit.makeRentalSuit(SuitDNA.suitDepts[deptIndex])
        self.suit = suit
        self.suitGeom = suitGeom
        self.setHeight(suit.getHeight() * self.magicScale)
        self.nametag3d.setPos(0, 0, self.height + 1.3)
        isOranges = hasattr(base, 'cr') and hasattr(base.cr, 'newsManager') and base.cr.newsManager.isHolidayRunning(ToontownGlobals.ORANGES)
        if self.isLocal():
            self.oldForward = ToontownGlobals.ToonForwardSpeed
            self.oldReverse = ToontownGlobals.ToonReverseSpeed
            self.oldRotate = ToontownGlobals.ToonRotateSpeed
            ToontownGlobals.ToonForwardSpeed = ToontownGlobals.SuitWalkSpeed
            ToontownGlobals.ToonReverseSpeed = ToontownGlobals.SuitWalkSpeed
            ToontownGlobals.ToonRotateSpeed = ToontownGlobals.ToonRotateSlowSpeed
            if self.hasTrackAnimToSpeed():
                self.stopTrackAnimToSpeed()
                self.startTrackAnimToSpeed()
            indices = range(OTPLocalizer.SCMenuCommonCogIndices[0], OTPLocalizer.SCMenuCommonCogIndices[1] + 1)
            customIndices = OTPLocalizer.SCMenuCustomCogIndices[suitType]
            indices += range(customIndices[0], customIndices[1] + 1)
            self.chatMgr.chatInputSpeedChat.addCogMenu(indices)
        if not tpose:
            self.suit.loop('neutral')
        self.isDisguised = 1
        self.isCog = becomeCog
        self.setFont(ToontownGlobals.getSuitFont())
        self.setSpeechFont(ToontownGlobals.getSuitFont())
        if setDisplayName:
            if hasattr(base, 'idTags') and base.idTags:
                name = self.getAvIdName()
            else:
                name = self.getName()
            level = self.cogLevels[SuitDNA.suitDepts.index(SuitDNA.getSuitDept(suitType))] + 1
            if isOranges:
                if level < SuitBattleGlobals.SuitAttributes[suitType]['level'] + 1 or level > SuitBattleGlobals.SuitAttributes[suitType]['level'] + 5 and SuitDNA.suitHeadTypes.index(suitType) % SuitDNA.suitsPerDept < 7:
                    level = min(SuitBattleGlobals.SuitAttributes[suitType]['level'] + self.style.legColor % 5 + 1, 50)
            if becomeCog != 5 and becomeCog:
                suitDept = SuitDNA.suitDepts.index(SuitDNA.getSuitDept(suitType))
                if becomeCog == 2 or becomeCog == 6 or becomeCog == 31:
                    if suitType == 'sj':
                        suitName = SuitBattleGlobals.SuitAttributes[suitType]['name']
                    else:
                        suitName = TTLocalizer.Skeleton
                else:
                    if becomeCog == 69:
                        suitName = TTLocalizer.SuitSwagForeman
                    else:
                        suitName = SuitBattleGlobals.SuitAttributes[suitType]['name']
                if becomeCog == 4 or becomeCog == 42:
                    self.nametag.setDisplayName(TTLocalizer.SuitBaseNameWithLevel % {'name': suitName, 'dept': SuitDNA.getDeptFullname(SuitDNA.getSuitDept(suitType)), 
                       'level': '%s%s' % (level, TTLocalizer.SkeleRevivePostFix)})
                else:
                    if becomeCog == 76:
                        self.nametag.setDisplayName(TTLocalizer.SuitBaseNameWithoutDept % {'name': suitName, 'level': 'TY'})
                    else:
                        if suitType == 'sj':
                            self.nametag.setDisplayName(suitName)
                        else:
                            if becomeCog == 49:
                                self.nametag.setDisplayName(TTLocalizer.SuitBaseNameWithLevel % {'name': suitName, 'dept': 'Crazybot', 
                                   'level': '13'})
                            else:
                                if becomeCog == 50:
                                    self.nametag.setDisplayName(TTLocalizer.SuitBaseNameWithLevel % {'name': suitName, 'dept': SuitDNA.getDeptFullname(SuitDNA.getSuitDept(suitType)), 
                                       'level': '11' + TTLocalizer.SkeleRevivePostFix})
                                else:
                                    if becomeCog == 51:
                                        self.nametag.setDisplayName(TTLocalizer.SuitBaseNameWithLevel % {'name': suitName, 'dept': 'Boatbot', 
                                           'level': '12'})
                                    else:
                                        if becomeCog == 24:
                                            self.nametag.setDisplayName(TTLocalizer.SuitBaseNameWithLevel % {'name': suitName, 'dept': SuitDNA.getDeptFullname(SuitDNA.getSuitDept(suitType)), 
                                               'level': '88 v3.0'})
                                        else:
                                            self.nametag.setDisplayName(TTLocalizer.SuitBaseNameWithLevel % {'name': suitName, 'dept': SuitDNA.getDeptFullname(SuitDNA.getSuitDept(suitType)), 
                                               'level': level})
                self.nametag.setWordwrap(9.0)
            else:
                suitDept = SuitDNA.suitDepts.index(SuitDNA.getSuitDept(suitType))
                suitName = SuitBattleGlobals.SuitAttributes[suitType]['name']
                self.nametag.setDisplayName(TTLocalizer.SuitBaseNameWithLevel % {'name': name, 'dept': suitName, 
                   'level': level})
                self.nametag.setWordwrap(9.0)
        if hasattr(self, 'hp'):
            self.suit.currHP = self.hp
            self.suit.maxHP = self.maxHp
            if self.maxHp == self.hp:
                self.suit.corpMedallion.show()
                self.suit.healthBar.hide()
            else:
                self.suit.corpMedallion.hide()
                self.suit.healthBar.show()
                self.suit.updateHealthBar(self.hp, True, True)
        self.suitGeom.setScale(suitGeom.getScale() * self.magicScale)

    def takeOffSuit(self):
        if not self.isDisguised:
            return
        suitType = self.suit.style.name
        toonHeadNull = self.find('**/1000/**/def_head')
        if not toonHeadNull:
            toonHeadNull = self.find('**/1000/**/joint_head')
        toonHead = self.getPart('head', '1000')
        toonHead.reparentTo(toonHeadNull)
        toonHead.setScale(self.headOrigScale)
        toonHead.setPos(0, 0, 0)
        headPosNode = self.suitGeom.find('**/headPos')
        headPosNode.removeNode()
        self.suitGeom.reparentTo(self.suit)
        self.resetHeight()
        self.nametag3d.setPos(0, 0, self.height + 0.5)
        toonGeom = self.getGeomNode()
        toonGeom.show()
        Emote.globalEmote.releaseAll(self)
        self.isDisguised = 0
        self.isCog = False
        self.setFont(ToontownGlobals.getToonFont())
        self.setSpeechFont(ToontownGlobals.getToonFont())
        self.nametag.setWordwrap(None)
        if hasattr(base, 'idTags') and base.idTags:
            name = self.getAvIdName()
        else:
            name = self.getName()
        self.setDisplayName(name)
        if self.isLocal():
            ToontownGlobals.ToonForwardSpeed = self.oldForward
            ToontownGlobals.ToonReverseSpeed = self.oldReverse
            ToontownGlobals.ToonRotateSpeed = self.oldRotate
            if self.hasTrackAnimToSpeed():
                self.stopTrackAnimToSpeed()
                self.startTrackAnimToSpeed()
            del self.oldForward
            del self.oldReverse
            del self.oldRotate
            self.chatMgr.chatInputSpeedChat.removeCogMenu()
        self.suit.delete()
        self.suit = None
        del self.suitGeom
        return

    def becomeChar(self, charType, tpose=False):
        if self.isDisguised:
            self.takeOffSuit()
        if self.isTransformed:
            self.becomeToon()
        if self.isBecomePet:
            self.noMorePet()
        if self.isGoon:
            self.noMoreGoon()
        if self.isBossCog:
            self.noMoreBoss()
        if launcher and not launcher.getPhaseComplete(5):
            return
        from toontown.char import Char
        from toontown.char import CharDNA
        char = Char.Char()
        dna = CharDNA.CharDNA()
        dna.newChar(CharDNA.charTypes[charType])
        char.setDNA(dna)
        char.addActive()
        char.startEarTask()
        char.isTransformed = 1
        char.initializeDropShadow()
        char.setPos(self.getPos())
        char.setHpr(self.getHpr())
        Emote.globalEmote.disableAll(self)
        toonGeom = self.getGeomNode()
        toonGeom.hide()
        charGeom = char.getGeomNode()
        charGeom.reparentTo(self)
        self.char = char
        self.charGeom = charGeom
        self.setHeight(char.getHeight() * self.magicScale)
        self.nametag3d.setPos(0, 0, self.height + 0.5)
        if self.isLocal():
            if hasattr(self, 'book'):
                self.book.obscureButton(1)
            self.oldForward = ToontownGlobals.ToonForwardSpeed
            self.oldReverse = ToontownGlobals.ToonReverseSpeed
            self.oldRotate = ToontownGlobals.ToonRotateSpeed
            ToontownGlobals.ToonForwardSpeed = ToontownGlobals.SuitWalkSpeed
            ToontownGlobals.ToonReverseSpeed = ToontownGlobals.SuitWalkSpeed
            ToontownGlobals.ToonRotateSpeed = ToontownGlobals.ToonRotateSlowSpeed
            if self.hasTrackAnimToSpeed():
                self.stopTrackAnimToSpeed()
                self.startTrackAnimToSpeed()
            try:
                self.controlManager.disableAvatarJump()
            except:
                pass

        if not tpose:
            self.char.loop('neutral')
        self.isTransformed = 1
        self.setFont(ToontownGlobals.getToonFont())
        self.nametag.setDisplayName(TTLocalizer.charName2Id[charType])
        self.charGeom.setScale(self.magicScale)

    def becomeToon(self):
        if not self.isTransformed:
            return
        self.charGeom.reparentTo(self.char)
        self.resetHeight()
        self.nametag3d.setPos(0, 0, self.height + 0.5)
        toonGeom = self.getGeomNode()
        toonGeom.show()
        Emote.globalEmote.releaseAll(self)
        self.isTransformed = 0
        self.setFont(ToontownGlobals.getToonFont())
        if hasattr(base, 'idTags') and base.idTags:
            name = self.getAvIdName()
        else:
            name = self.getName()
        self.setDisplayName(name)
        if self.isLocal():
            if hasattr(self, 'book'):
                self.book.obscureButton(0)
            ToontownGlobals.ToonForwardSpeed = self.oldForward
            ToontownGlobals.ToonReverseSpeed = self.oldReverse
            ToontownGlobals.ToonRotateSpeed = self.oldRotate
            if self.hasTrackAnimToSpeed():
                self.stopTrackAnimToSpeed()
                self.startTrackAnimToSpeed()
            del self.oldForward
            del self.oldReverse
            del self.oldRotate
            self.controlManager.enableAvatarJump()
            self.chatMgr.chatInputSpeedChat.removeCogMenu()
        self.char.removeActive()
        self.char.stopEarTask()
        self.char.delete()
        del self.char
        del self.charGeom

    def becomePet(self, petName='Fluffy', petDNA=None, tpose=False):
        if self.isDisguised:
            self.takeOffSuit()
        if self.isTransformed:
            self.becomeToon()
        if self.isBecomePet:
            self.noMorePet()
        if self.isGoon:
            self.noMoreGoon()
        if self.isBossCog:
            self.noMoreBoss()
        if launcher and not launcher.getPhaseComplete(5):
            return
        from toontown.pets import Pet
        pet = Pet.Pet()
        if not petDNA:
            petDNA = [
             -1, 0, 0, -1, 4, 0, 0, 5, 1, 191, -263, 4.597, 109]
        if petName == '':
            petName = self.getName()
        pet.setDNA(petDNA)
        pet.addActive()
        pet.startBlink()
        pet.isBecomePet = 1
        pet.initializeDropShadow()
        pet.setPos(self.getPos())
        pet.setHpr(self.getHpr())
        Emote.globalEmote.disableAll(self)
        toonGeom = self.getGeomNode()
        toonGeom.hide()
        petGeom = pet.getGeomNode()
        petGeom.reparentTo(self)
        self.pet = pet
        self.petGeom = petGeom
        self.setHeight(pet.getHeight() * self.magicScale)
        self.nametag3d.setPos(0, 0, self.height + 0.5)
        if self.isLocal():
            if hasattr(self, 'book'):
                self.book.obscureButton(1)
            self.oldForward = ToontownGlobals.ToonForwardSpeed
            self.oldReverse = ToontownGlobals.ToonReverseSpeed
            self.oldRotate = ToontownGlobals.ToonRotateSpeed
            ToontownGlobals.ToonForwardSpeed = ToontownGlobals.SuitWalkSpeed
            ToontownGlobals.ToonReverseSpeed = ToontownGlobals.SuitWalkSpeed
            ToontownGlobals.ToonRotateSpeed = ToontownGlobals.ToonRotateSlowSpeed
            if self.hasTrackAnimToSpeed():
                self.stopTrackAnimToSpeed()
                self.startTrackAnimToSpeed()
            try:
                self.controlManager.disableAvatarJump()
            except:
                pass

        if not tpose:
            self.pet.loop('neutral')
        self.isBecomePet = 1
        self.setFont(ToontownGlobals.getToonFont())
        self.nametag.setName(petName)
        self.nametag.setDisplayName(petName)
        self.petGeom.setScale(self.petGeom.getScale() * self.magicScale)

    def noMorePet(self):
        if not self.isBecomePet:
            return
        self.petGeom.reparentTo(self.pet)
        self.resetHeight()
        self.nametag3d.setPos(0, 0, self.height + 0.5)
        toonGeom = self.getGeomNode()
        toonGeom.show()
        Emote.globalEmote.releaseAll(self)
        self.isBecomePet = 0
        self.setFont(ToontownGlobals.getToonFont())
        if hasattr(base, 'idTags') and base.idTags:
            name = self.getAvIdName()
        else:
            name = self.getName()
        self.setDisplayName(name)
        if self.isLocal():
            if hasattr(self, 'book'):
                self.book.obscureButton(0)
            ToontownGlobals.ToonForwardSpeed = self.oldForward
            ToontownGlobals.ToonReverseSpeed = self.oldReverse
            ToontownGlobals.ToonRotateSpeed = self.oldRotate
            if self.hasTrackAnimToSpeed():
                self.stopTrackAnimToSpeed()
                self.startTrackAnimToSpeed()
            del self.oldForward
            del self.oldReverse
            del self.oldRotate
            self.controlManager.enableAvatarJump()
            self.chatMgr.chatInputSpeedChat.removeCogMenu()
        self.pet.removeActive()
        self.pet.delete()
        del self.pet
        del self.petGeom

    def becomeGoon(self, goonType, tpose=False):
        if self.isDisguised:
            self.takeOffSuit()
        if self.isTransformed:
            self.becomeToon()
        if self.isBecomePet:
            self.noMorePet()
        if self.isGoon:
            self.noMoreGoon()
        if self.isBossCog:
            self.noMoreBoss()
        if launcher and not launcher.getPhaseComplete(5):
            return
        from toontown.suit import Goon
        goonType = SuitDNA.goonTypes[goonType]
        goon = Goon.Goon(goonType)
        goon.addActive()
        goon.isGoon = 1
        goon.doId = self.doId
        goon.initializeDropShadow()
        goon.setPos(self.getPos())
        goon.setHpr(self.getHpr())
        Emote.globalEmote.disableAll(self)
        toonGeom = self.getGeomNode()
        toonGeom.hide()
        goonGeom = goon.getGeomNode()
        goonGeom.reparentTo(self)
        self.goon = goon
        self.goonGeom = goonGeom
        self.setHeight(goon.getHeight() * self.magicScale)
        self.nametag3d.setPos(0, 0, self.height + 0.5)
        self.setFont(ToontownGlobals.getSuitFont())
        self.setSpeechFont(ToontownGlobals.getSuitFont())
        if self.isLocal():
            if hasattr(self, 'book'):
                self.book.obscureButton(1)
            self.oldForward = ToontownGlobals.ToonForwardSpeed
            self.oldReverse = ToontownGlobals.ToonReverseSpeed
            self.oldRotate = ToontownGlobals.ToonRotateSpeed
            ToontownGlobals.ToonForwardSpeed = ToontownGlobals.SuitWalkSpeed
            ToontownGlobals.ToonReverseSpeed = ToontownGlobals.SuitWalkSpeed
            ToontownGlobals.ToonRotateSpeed = ToontownGlobals.ToonRotateSlowSpeed
            if self.hasTrackAnimToSpeed():
                self.stopTrackAnimToSpeed()
                self.startTrackAnimToSpeed()
            try:
                self.controlManager.disableAvatarJump()
            except:
                pass

        if not tpose:
            self.goon.pose('neutral', 96)
        self.isGoon = 1
        self.nametag.setDisplayName('Goon')
        self.goonGeom.setScale(self.goonGeom.getScale() * self.magicScale)

    def noMoreGoon(self):
        if not self.isGoon:
            return
        self.goonGeom.reparentTo(self.goon)
        self.resetHeight()
        self.nametag3d.setPos(0, 0, self.height + 0.5)
        toonGeom = self.getGeomNode()
        toonGeom.show()
        Emote.globalEmote.releaseAll(self)
        self.isGoon = 0
        self.setFont(ToontownGlobals.getToonFont())
        self.setSpeechFont(ToontownGlobals.getToonFont())
        if hasattr(base, 'idTags') and base.idTags:
            name = self.getAvIdName()
        else:
            name = self.getName()
        self.setDisplayName(name)
        if self.isLocal():
            if hasattr(self, 'book'):
                self.book.obscureButton(0)
            ToontownGlobals.ToonForwardSpeed = self.oldForward
            ToontownGlobals.ToonReverseSpeed = self.oldReverse
            ToontownGlobals.ToonRotateSpeed = self.oldRotate
            if self.hasTrackAnimToSpeed():
                self.stopTrackAnimToSpeed()
                self.startTrackAnimToSpeed()
            del self.oldForward
            del self.oldReverse
            del self.oldRotate
            self.controlManager.enableAvatarJump()
            self.chatMgr.chatInputSpeedChat.removeCogMenu()
        self.goon.removeActive()
        self.goon.delete()
        del self.goon
        del self.goonGeom

    def becomeBoss(self, dept, tpose=False):
        if self.isDisguised:
            self.takeOffSuit()
        if self.isTransformed:
            self.becomeToon()
        if self.isBecomePet:
            self.noMorePet()
        if self.isGoon:
            self.noMoreGoon()
        if self.isBossCog:
            self.noMoreBoss()
        if launcher and not launcher.getPhaseComplete(5):
            return
        from toontown.suit import BossCog
        from toontown.suit import SuitDNA
        boss = BossCog.BossCog()
        dna = SuitDNA.SuitDNA()
        dna.newBossCog(SuitDNA.suitDepts[dept])
        boss.setDNA(dna)
        boss.addActive()
        boss.isTransformed = 1
        boss.initializeDropShadow()
        boss.setPos(self.getPos())
        boss.setHpr(self.getHpr())
        Emote.globalEmote.disableAll(self)
        toonGeom = self.getGeomNode()
        toonGeom.hide()
        bossGeom = boss.getGeomNode()
        bossGeom.reparentTo(self)
        self.boss = boss
        self.bossGeom = bossGeom
        self.bossGeom.setScale(0.2)
        self.setHeight(boss.getHeight() / 5 * self.magicScale)
        self.nametag3d.setPos(0, 0, self.height + 0.5)
        self.setFont(ToontownGlobals.getSuitFont())
        self.setSpeechFont(ToontownGlobals.getSuitFont())
        suitType = self.boss.style.name
        if self.isLocal():
            if hasattr(self, 'book'):
                self.book.obscureButton(1)
            self.oldForward = ToontownGlobals.ToonForwardSpeed
            self.oldReverse = ToontownGlobals.ToonReverseSpeed
            self.oldRotate = ToontownGlobals.ToonRotateSpeed
            ToontownGlobals.ToonForwardSpeed = ToontownGlobals.SuitWalkSpeed
            ToontownGlobals.ToonReverseSpeed = ToontownGlobals.SuitWalkSpeed
            ToontownGlobals.ToonRotateSpeed = ToontownGlobals.ToonRotateSlowSpeed
            if self.hasTrackAnimToSpeed():
                self.stopTrackAnimToSpeed()
                self.startTrackAnimToSpeed()
            try:
                self.controlManager.disableAvatarJump()
            except:
                pass

            indices = range(OTPLocalizer.SCMenuCommonCogIndices[0], OTPLocalizer.SCMenuCommonCogIndices[1] + 1)
            customIndices = OTPLocalizer.SCMenuCustomCogIndices[suitType]
            indices += range(customIndices[0], customIndices[1] + 1)
            self.chatMgr.chatInputSpeedChat.addCogMenu(indices)
        if not tpose:
            self.boss.loop('Bb_neutral')
        self.isBossCog = 1
        if dept == 0:
            bossName = TTLocalizer.BossbotBossName
        else:
            if dept == 1:
                bossName = TTLocalizer.LawbotBossName
            else:
                if dept == 2:
                    bossName = TTLocalizer.CashbotBossName
                else:
                    if dept == 3:
                        bossName = TTLocalizer.SellbotBossName
                    else:
                        if dept == 4:
                            bossName = 'The Chairman'
                        else:
                            self.notify.warning('aaaAAAAAAAAAAAAAA')
                            bossName = 'FUCKER'
        nameInfo = TTLocalizer.BossCogNameWithDept % {'name': bossName, 'dept': SuitDNA.getDeptFullname(SuitDNA.suitDepts[dept])}
        if suitType == 'chairman':
            nameInfo = bossName
        self.nametag.setDisplayName(nameInfo)
        self.bossGeom.setScale(self.bossGeom.getScale() * self.magicScale)

    def noMoreBoss(self):
        if not self.isBossCog:
            return
        self.bossGeom.reparentTo(self.boss)
        self.resetHeight()
        self.nametag3d.setPos(0, 0, self.height + 0.5)
        toonGeom = self.getGeomNode()
        toonGeom.show()
        Emote.globalEmote.releaseAll(self)
        self.isBossCog = 0
        self.setFont(ToontownGlobals.getToonFont())
        self.setSpeechFont(ToontownGlobals.getToonFont())
        if hasattr(base, 'idTags') and base.idTags:
            name = self.getAvIdName()
        else:
            name = self.getName()
        self.setDisplayName(name)
        if self.isLocal():
            if hasattr(self, 'book'):
                self.book.obscureButton(0)
            ToontownGlobals.ToonForwardSpeed = self.oldForward
            ToontownGlobals.ToonReverseSpeed = self.oldReverse
            ToontownGlobals.ToonRotateSpeed = self.oldRotate
            if self.hasTrackAnimToSpeed():
                self.stopTrackAnimToSpeed()
                self.startTrackAnimToSpeed()
            del self.oldForward
            del self.oldReverse
            del self.oldRotate
            self.controlManager.enableAvatarJump()
            self.chatMgr.chatInputSpeedChat.removeCogMenu()
        self.boss.removeActive()
        self.boss.delete()
        del self.boss
        del self.bossGeom

    def makeWaiter(self):
        if not self.isDisguised:
            return
        self.suit.makeWaiter(self.suitGeom)

    def getPieModel(self):
        from toontown.toonbase import ToontownBattleGlobals
        from toontown.battle import BattleProps
        if self.pieModel != None and self.__pieModelType != self.pieType:
            self.pieModel.detachNode()
            self.pieModel = None
        if self.pieModel == None:
            self.__pieModelType = self.pieType
            pieName = ToontownBattleGlobals.pieNames[self.pieType]
            self.pieModel = BattleProps.globalPropPool.getProp(pieName)
            self.pieScale = self.pieModel.getScale()
        return self.pieModel

    def getPresentPieInterval(self, x, y, z, h):
        from toontown.toonbase import ToontownBattleGlobals
        from toontown.battle import BattleProps
        from toontown.battle import MovieUtil
        pie = self.getPieModel()
        pieName = ToontownBattleGlobals.pieNames[self.pieType]
        pieType = BattleProps.globalPropPool.getPropType(pieName)
        animPie = Sequence()
        pingpongPie = Sequence()
        if pieType == 'actor':
            animPie = ActorInterval(pie, pieName, startFrame=0, endFrame=31)
            pingpongPie = Func(pie.pingpong, pieName, fromFrame=32, toFrame=47)
        if self.isDisguised:
            if self.suit.style.body != 'c':
                track = Sequence(Func(self.suit.setPosHpr, x, y, z, h, 0, 0), Func(pie.reparentTo, self.suit.rightHand), Func(pie.setPosHpr, 0, 0, 0, 0, 180, 0), Parallel(pie.scaleInterval(1, self.pieScale, startScale=MovieUtil.PNT3_NEARZERO), ActorInterval(self.suit, 'throw-object', startFrame=0, endFrame=40), animPie), Func(self.suit.pingpong, 'throw-object', fromFrame=40, toFrame=50), pingpongPie)
            else:
                track = Sequence(Func(self.suit.setPosHpr, x, y, z, h, 0, 0), Func(pie.reparentTo, self.suit.rightHand), Func(pie.setPosHpr, 0, 0, 0, 0, 180, 0), Parallel(pie.scaleInterval(1, self.pieScale, startScale=MovieUtil.PNT3_NEARZERO), ActorInterval(self.suit, 'throw-paper', startFrame=0, endFrame=30), animPie), Func(self.suit.pingpong, 'throw-paper', fromFrame=30, toFrame=40), pingpongPie)
        else:
            track = Sequence(Func(self.setPosHpr, x, y, z, h, 0, 0), Func(pie.reparentTo, self.rightHand), Func(pie.setPosHpr, 0, 0, 0, 0, 0, 0), Parallel(pie.scaleInterval(1, self.pieScale, startScale=MovieUtil.PNT3_NEARZERO), ActorInterval(self, 'throw', startFrame=0, endFrame=31), animPie), Func(self.pingpong, 'throw', fromFrame=32, toFrame=47), pingpongPie)
        return track

    def getTossPieInterval(self, x, y, z, h, power, throwType, beginFlyIval=Sequence()):
        from toontown.toonbase import ToontownBattleGlobals
        from toontown.battle import BattleProps
        pie = self.getPieModel()
        flyPie = pie.copyTo(NodePath('a'))
        pieName = ToontownBattleGlobals.pieNames[self.pieType]
        pieType = BattleProps.globalPropPool.getPropType(pieName)
        animPie = Sequence()
        if pieType == 'actor':
            animPie = ActorInterval(pie, pieName, startFrame=48)
        sound = loader.loadSfx('phase_3.5/audio/sfx/AA_pie_throw_only.ogg')
        if throwType == ToontownGlobals.PieThrowArc:
            t = power / 100.0
            dist = 100 - 70 * t
            time = 1 + 0.5 * t
            proj = ProjectileInterval(None, startPos=Point3(0, 0, 0), endPos=Point3(0, dist, 0), duration=time)
            relVel = proj.startVel
        else:
            if throwType == ToontownGlobals.PieThrowLinear:
                magnitude = power / 2.0 + 25
                relVel = Vec3(0, 1, 0.25)
                relVel.normalize()
                relVel *= magnitude

        def getVelocity(toon=self, relVel=relVel):
            return render.getRelativeVector(toon, relVel)

        if self.isDisguised:
            if self.suit.style.body != 'c':
                toss = Track((
                 0,
                 Sequence(Func(self.suit.setPosHpr, x, y, z, h, 0, 0), Func(pie.reparentTo, self.suit.rightHand), Func(pie.setPosHpr, 0, 0, 0, 0, 180, 0), Parallel(ActorInterval(self.suit, 'throw-object', playRate=1.5, startFrame=50), animPie), Func(self.suit.loop, self.neutralAnim))), (16.0 / 24.0, Func(pie.detachNode)))
            else:
                toss = Track((0,
                 Sequence(Func(self.suit.setPosHpr, x, y, z, h, 0, 0), Func(pie.reparentTo, self.suit.rightHand), Func(pie.setPosHpr, 0, 0, 0, 0, 180, 0), Parallel(ActorInterval(self.suit, 'throw-paper', startFrame=40), animPie), Func(self.suit.loop, self.neutralAnim))), (16.0 / 24.0, Func(pie.detachNode)))
        else:
            toss = Track((0, Sequence(Func(self.setPosHpr, x, y, z, h, 0, 0), Func(pie.reparentTo, self.rightHand), Func(pie.setPosHpr, 0, 0, 0, 0, 0, 0), Parallel(ActorInterval(self, 'throw', startFrame=48), animPie), Func(self.loop, self.neutralAnim))), (16.0 / 24.0, Func(pie.detachNode)))
        fly = Track((14.0 / 24.0, SoundInterval(sound, node=self)), (16.0 / 24.0, Sequence(Func(flyPie.reparentTo, render), Func(flyPie.setScale, self.pieScale), Func(flyPie.setPosHpr, self, 0.52, 0.97, 2.24, 89.42, -10.56, 87.94), beginFlyIval, ProjectileInterval(flyPie, startVel=getVelocity, duration=3), Func(flyPie.detachNode))))
        return (
         toss, fly, flyPie)

    def getPieSplatInterval(self, x, y, z, pieCode):
        from toontown.toonbase import ToontownBattleGlobals
        from toontown.battle import BattleProps
        pieName = ToontownBattleGlobals.pieNames[self.pieType]
        splatName = 'splat-%s' % pieName
        if pieName == 'wedding-cake':
            splatName = 'splat-birthday-cake'
        if pieName == 'lawbook':
            splatName = 'dust'
        if pieName == 'emp':
            splatName = 'kapow'
        splat = BattleProps.globalPropPool.getProp(splatName)
        splat.setBillboardPointWorld(2)
        color = ToontownGlobals.PieCodeColors.get(pieCode)
        if color and pieName != 'emp':
            splat.setColor(*color)
        vol = 1.0
        if pieName == 'lawbook':
            sound = loader.loadSfx('phase_11/audio/sfx/LB_evidence_miss.ogg')
            vol = 0.25
        else:
            if pieName == 'emp':
                sound = loader.loadSfx('phase_4/audio/sfx/MG_cannon_fire_alt.ogg')
                splat.setScale(0.5)
            else:
                sound = loader.loadSfx('phase_4/audio/sfx/AA_wholepie_only.ogg')
        ival = Parallel(Func(splat.reparentTo, render), Func(splat.setPos, x, y, z), SoundInterval(sound, node=splat, volume=vol), Sequence(ActorInterval(splat, splatName), Func(splat.detachNode)))
        return ival

    def cleanupPieModel(self):
        if self.pieModel != None:
            self.pieModel.detachNode()
            self.pieModel = None
        return

    def getFeedPetIval(self):
        if self.isDisguised:
            if self.suit.style.body == 'c':
                return Sequence(ActorInterval(self.suit, 'throw-paper', playRate=1.0), Func(self.animFSM.request, 'neutral'))
            return Sequence(ActorInterval(self.suit, 'throw-paper', playRate=1.3), Func(self.animFSM.request, 'neutral'))
        else:
            return Sequence(ActorInterval(self, 'feedPet'), Func(self.animFSM.request, 'neutral'))

    def getScratchPetIval(self):
        return Sequence(ActorInterval(self, 'pet-start'), ActorInterval(self, 'pet-loop'), ActorInterval(self, 'pet-end'))

    def getCallPetIval(self):
        return ActorInterval(self, 'callPet')

    def enterGolfPuttLoop(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        self.loop('loop-putt')
        if self.isDisguised:
            self.suit.pose('golf-club-swing', 50)

    def exitGolfPuttLoop(self):
        self.stop()

    def enterGolfRotateLeft(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        self.loop('rotateL-putt')

    def exitGolfRotateLeft(self):
        self.stop()

    def enterGolfRotateRight(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        self.loop('rotateR-putt')

    def exitGolfRotateRight(self):
        self.stop()

    def enterGolfPuttSwing(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        self.loop('swing-putt')
        if self.isDisguised:
            self.suit.actorInterval('golf-club-swing', startFrame=65, playRate=5 * animMultiplier).start()

    def exitGolfPuttSwing(self):
        self.stop()

    def enterGolfGoodPutt(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        self.loop('good-putt', restart=0)

    def exitGolfGoodPutt(self):
        self.stop()

    def enterGolfBadPutt(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        self.loop('badloop-putt', restart=0)

    def exitGolfBadPutt(self):
        self.stop()

    def enterFlattened(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        Emote.globalEmote.disableAll(self)
        sound = loader.loadSfx('phase_9/audio/sfx/toon_decompress.ogg')
        lerpTime = 0.1
        node = self.getGeomNode().getChild(0)
        self.origScale = node.getScale()
        self.track = Sequence(LerpScaleInterval(node, lerpTime, VBase3(2, 2, 0.025), blendType='easeInOut'))
        self.track.start(ts)
        self.setActiveShadow(1)

    def exitFlattened(self):
        self.playingAnim = self.neutralAnim
        if self.track != None:
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        node = self.getGeomNode().getChild(0)
        node.setScale(self.origScale)
        Emote.globalEmote.releaseAll(self)
        return

    def enterCogThiefRunning(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        self.playingAnim = None
        self.playingRate = None
        self.standWalkRunReverse = ((self.neutralAnim, 1.0),
         (
          self.runAnim, 1.0),
         (
          self.runAnim, 1.0),
         (
          self.runAnim, -1.0))
        self.setSpeed(self.forwardSpeed, self.rotateSpeed)
        self.setActiveShadow(1)
        return

    def exitCogThiefRunning(self):
        self.standWalkRunReverse = None
        self.stop()
        self.motion.exit()
        return

    def enterScientistJealous(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        self.loop('scientistJealous')
        if hasattr(self, 'showScientistProp'):
            self.showScientistProp()

    def exitScientistJealous(self):
        self.stop()

    def enterScientistEmcee(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        self.loop('scientistEmcee')

    def exitScientistEmcee(self):
        self.stop()

    def enterScientistWork(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        self.loop('scientistWork')

    def exitScientistWork(self):
        self.stop()

    def enterScientistLessWork(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        self.loop('scientistWork', fromFrame=319, toFrame=619)

    def exitScientistLessWork(self):
        self.stop()

    def enterScientistPlay(self, animMultiplier=1, ts=0, callback=None, extraArgs=[]):
        self.loop('scientistGame')
        if hasattr(self, 'scientistPlay'):
            self.scientistPlay()

    def exitScientistPlay(self):
        self.stop()


loadModels()
compileGlobalAnimList()