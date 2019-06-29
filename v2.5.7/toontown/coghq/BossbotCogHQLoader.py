from direct.directnotify import DirectNotifyGlobal
from direct.fsm import StateData
import CogHQLoader
from toontown.toonbase import ToontownGlobals
from direct.gui import DirectGui
from toontown.toonbase import TTLocalizer
from toontown.toon import Toon
from direct.fsm import State
from toontown.coghq import BossbotHQExterior
from toontown.coghq import BossbotHQBossBattle
from toontown.coghq import BossbotOfficeExterior
from toontown.coghq import CountryClubInterior
from toontown.battle import BattleParticles
from panda3d.core import *
from toontown.coghq import MoleHillProp, MoleFieldBase
import random
aspectSF = 0.7227

class BossbotCogHQLoader(CogHQLoader.CogHQLoader):
    notify = DirectNotifyGlobal.directNotify.newCategory('BossbotCogHQLoader')

    def __init__(self, hood, parentFSMState, doneEvent):
        CogHQLoader.CogHQLoader.__init__(self, hood, parentFSMState, doneEvent)
        self.fsm.addState(State.State('countryClubInterior', self.enterCountryClubInterior, self.exitCountryClubInterior, ['quietZone', 'cogHQExterior']))
        self.fsm.addState(State.State('golfcourse', self.enterGolfCourse, self.exitGolfCourse, ['quietZone', 'cogHQExterior']))
        for stateName in ['start', 'cogHQExterior', 'quietZone']:
            state = self.fsm.getStateNamed(stateName)
            state.addTransition('countryClubInterior')
            state.addTransition('golfcourse')

        self.musicFile = random.choice(['phase_12/audio/bgm/Bossbot_Entry_v1.ogg', 'phase_12/audio/bgm/Bossbot_Entry_v2.ogg', 'phase_12/audio/bgm/Bossbot_Entry_v3.ogg'])
        self.bushSfx = loader.loadSfx('phase_12/audio/sfx/CHQ_bush.ogg')
        self.cogHQExteriorModelPath = 'phase_14/models/neighborhoods/CogGolfCourtyard'
        self.cogHQLobbyModelPath = 'phase_12/models/bossbotHQ/CogGolfCourtyard'
        self.playingBushSound = False
        self.geom = None
        return

    def load(self, zoneId):
        CogHQLoader.CogHQLoader.load(self, zoneId)
        Toon.loadBossbotHQAnims()

    def unload(self):
        Toon.unloadBossbotHQAnims()
        CogHQLoader.CogHQLoader.unload(self)

    def unloadPlaceGeom(self):
        if self.geom:
            self.geom.removeNode()
            self.geom = None
        CogHQLoader.CogHQLoader.unloadPlaceGeom(self)
        self.battleMusic = base.loader.loadMusic('phase_9/audio/bgm/encntr_suit_winning.ogg')
        return

    def loadPlaceGeom(self, zoneId):
        self.notify.info('loadPlaceGeom: %s' % zoneId)
        zoneId = zoneId - zoneId % 100
        self.notify.debug('zoneId = %d ToontownGlobals.BossbotHQ=%d' % (zoneId, ToontownGlobals.BossbotHQ))
        if zoneId == ToontownGlobals.BossbotHQ:
            self.geom = loader.loadModel(self.cogHQExteriorModelPath)
            self.geom.find('**/ground').setBin('ground', -10)
            self.post = loader.loadModel('phase_6/models/golf/golf_construction_sign')
            self.post.reparentTo(self.geom.find('**/sign_post'))
            self.makeSigns(zoneId)
            gzLinkTunnel = self.geom.find('**/TunnelEntrance')
            gzLinkTunnel.setName('linktunnel_gz_17000_DNARoot')
            molePHs = [
             (4.0, -53.0, -1.0, 690.0),
             (-3.0, -14.75, -0.8, 420.0),
             (21.0, -0.75, -0.85, 1337.0),
             (10.0, 18.25, -0.7, 123.4),
             (102.0, 10.0, -1.112, 220.0),
             (117.0, -11.0, -0.927, 392.0),
             (96.0, -34.0, -1.055, 111.1),
             (87.0, -64.0, -1.055, 911.0)]
            for molePH in molePHs:
                mole = MoleHillProp.MoleHillProp(molePH[0], molePH[1], molePH[2])
                mole.setH(molePH[3])
                mole.reparentTo(self.geom)

        else:
            if zoneId == ToontownGlobals.BossbotLobby:
                if config.GetBool('want-qa-regression', 0):
                    self.notify.info('QA-REGRESSION: COGHQ: Visit BossbotLobby')
                self.notify.debug('cogHQLobbyModelPath = %s' % self.cogHQLobbyModelPath)
                self.geom = loader.loadModel(self.cogHQLobbyModelPath)
            else:
                self.notify.warning('loadPlaceGeom: unclassified zone %s' % zoneId)
        CogHQLoader.CogHQLoader.loadPlaceGeom(self, zoneId)

    def makeSign(self, topStr, signStr, textId, scale=TTLocalizer.BCHQLsignText):
        if signStr != 'sign_2':
            text = TextEncoder.upper(TTLocalizer.GlobalStreetNames[textId][(-1)])
        else:
            text = 'The Chairman'
        if topStr != '':
            top = self.geom.find('**/' + topStr)
            sign = top.find('**/' + signStr)
            if topStr == 'TunnelEntrance':
                topple = top.find('**/TunnelFront')
                locator = topple.find('**/sign_origin')
            else:
                locator = top.find('**/sign_origin')
            signText = DirectGui.OnscreenText(text=text, font=ToontownGlobals.getSuitFont(), scale=scale, fg=(0,
                                                                                                              0,
                                                                                                              0,
                                                                                                              1), parent=sign)
            signText.setPosHpr(locator, 0, -0.1, -0.25, 0, 0, 0)
        else:
            sign = self.geom.find('**/' + signStr)
            signText = DirectGui.OnscreenText(text=text, font=ToontownGlobals.getSuitFont(), scale=scale, fg=(0,
                                                                                                              0,
                                                                                                              0,
                                                                                                              1), parent=sign)
            signText.setPosHpr(sign, 0.4, -174.5, -8.75, 0, 0, 0)
        signText.setDepthWrite(0)

    def makeSigns(self, zoneId):
        if zoneId == ToontownGlobals.BossbotHQ:
            self.makeSign('TunnelEntrance', 'Sign_2', 1000)
            self.makeSign('Gate_1', 'Sign_3', 10400)
            self.makeSign('Gate_2', 'Sign_6', 10700)
            self.makeSign('TunnelEntrance', 'Sign_2', 1000)
            self.makeSign('Gate_3', 'Sign_3', 10600)
            self.makeSign('Gate_4', 'Sign_4', 10500)
            self.makeSign('Gate_5', 'Sign_3', 10750, scale=0.87)
            self.makeSign('GateHouse', 'Sign_5', 10760)

    def getExteriorPlaceClass(self):
        self.notify.debug('getExteriorPlaceClass')
        return BossbotHQExterior.BossbotHQExterior

    def getBossPlaceClass(self):
        self.notify.debug('getBossPlaceClass')
        return BossbotHQBossBattle.BossbotHQBossBattle

    def enterCogHQExterior(self, requestStatus):
        self.placeClass = self.getExteriorPlaceClass()
        self.enterPlace(requestStatus)
        self.hood.spawnTitleText(requestStatus['zoneId'])

    def exitCogHQExterior(self):
        taskMgr.remove('titleText')
        self.hood.hideTitleText()
        self.exitPlace()
        self.placeClass = None
        return

    def enterCogHQLobby(self, requestStatus):
        self.hood.setWhiteFog()
        self.hood.startSky()
        CogHQLoader.CogHQLoader.enterCogHQLobby(self, requestStatus)

    def exitCogHQLobby(self):
        self.hood.setNoFog()
        self.hood.stopSky()
        CogHQLoader.CogHQLoader.exitCogHQLobby(self)

    def enterCountryClubInterior(self, requestStatus):
        self.placeClass = CountryClubInterior.CountryClubInterior
        self.notify.info('enterCountryClubInterior, requestStatus=%s' % requestStatus)
        self.countryClubId = requestStatus['countryClubId']
        self.enterPlace(requestStatus)

    def exitCountryClubInterior(self):
        self.exitPlace()
        self.placeClass = None
        del self.countryClubId
        return

    def enterStageInterior(self, requestStatus):
        self.placeClass = StageInterior.StageInterior
        self.stageId = requestStatus['stageId']
        self.enterPlace(requestStatus)

    def exitStageInterior(self):
        self.exitPlace()
        self.placeClass = None
        return

    def enterCogHQBossBattle(self, requestStatus):
        self.notify.debug('BossbotCogHQLoader.enterCogHQBossBattle')
        CogHQLoader.CogHQLoader.enterCogHQBossBattle(self, requestStatus)
        base.cr.forbidCheesyEffects(1)

    def exitCogHQBossBattle(self):
        self.notify.debug('BossbotCogHQLoader.exitCogHQBossBattle')
        CogHQLoader.CogHQLoader.exitCogHQBossBattle(self)
        base.cr.forbidCheesyEffects(0)

    def enteringARace(self, status):
        if not status['where'] == 'golfcourse':
            return 0
        if ZoneUtil.isDynamicZone(status['zoneId']):
            return status['hoodId'] == self.hood.hoodId
        return ZoneUtil.getHoodId(status['zoneId']) == self.hood.hoodId

    def enteringAGolfCourse(self, status):
        if not status['where'] == 'golfcourse':
            return 0
        if ZoneUtil.isDynamicZone(status['zoneId']):
            return status['hoodId'] == self.hood.hoodId
        return ZoneUtil.getHoodId(status['zoneId']) == self.hood.hoodId

    def enterGolfCourse(self, requestStatus):
        if requestStatus.has_key('curseId'):
            self.golfCourseId = requestStatus['courseId']
        else:
            self.golfCourseId = 0
        self.accept('raceOver', self.handleRaceOver)
        self.accept('leavingGolf', self.handleLeftGolf)
        base.transitions.irisOut(t=0.2)

    def exitGolfCourse(self):
        del self.golfCourseId

    def handleRaceOver(self):
        print 'Terrifying Two Completed.'

    def handleLeftGolf(self):
        self.loadPlaceGeom(ToontownGlobals.BossbotHQ)
        req = {'loader': 'cogHQLoader', 'where': 'cogHQExterior', 
           'how': 'teleportIn', 
           'zoneId': self.hood.hoodId, 
           'hoodId': self.hood.hoodId, 
           'shardId': None}
        self.fsm.request('quietZone', [req])
        return

    def __riverDamageTick(self, task):
        base.localAvatar.b_stun(ToontownGlobals.BossbotOilDamage)
        task.delayTime = 1.0
        return task.again

    def startRiverDamage(self, collision):
        taskMgr.add(self.__riverDamageTick, 'oil-river-tick')

    def stopRiverDamage(self, collision):
        taskMgr.remove('oil-river-tick')

    def startCollisionDetection(self):
        self.accept('enterouch', self.startRiverDamage)
        self.accept('exitouch', self.stopRiverDamage)

    def stopCollisionDetection(self):
        taskMgr.remove('oil-river-tick')
        self.ignore('enterouch')
        self.ignore('exitouch')

    def __bushTick(self, task):
        if not self.playingBushSound:
            if base.localAvatar.soundRun.status() == base.localAvatar.soundRun.PLAYING or base.localAvatar.soundWalk.status() == base.localAvatar.soundWalk.PLAYING:
                base.playSfx(self.bushSfx, looping=1)
                self.playingBushSound = True
        else:
            if self.playingBushSound:
                if base.localAvatar.soundRun.status() != base.localAvatar.soundRun.PLAYING and base.localAvatar.soundWalk.status() != base.localAvatar.soundWalk.PLAYING:
                    self.bushSfx.stop()
                    self.playingBushSound = False
        return task.again

    def startBush(self, collision):
        base.playSfx(self.bushSfx, looping=1)
        self.playingBushSound = True
        taskMgr.add(self.__bushTick, 'bush-tick')

    def stopBush(self, collision):
        taskMgr.remove('bush-tick')
        self.bushSfx.stop()

    def startBushCollisionDetection(self):
        self.accept('enterbush_trigger', self.startBush)
        self.accept('exitbush_trigger', self.stopBush)

    def stopBushCollisionDetection(self):
        self.ignore('enterbush_trigger')
        self.ignore('exitbush_trigger')