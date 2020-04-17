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
from panda3d.core import DecalEffect, TextEncoder
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
        self.cogHQExteriorModelPath = 'phase_14/models/neighborhoods/CogGolfCourtyard'
        self.cogHQLobbyModelPath = 'phase_12/models/bossbotHQ/CogGolfCourtyard'
        self.geom = None
        return

    def load(self, zoneId):
        CogHQLoader.CogHQLoader.load(self, zoneId)
        Toon.loadBossbotHQAnims()

    def unloadPlaceGeom(self):
        if self.geom:
            self.geom.removeNode()
            self.geom = None
        self.stopCollisionDetection()
        CogHQLoader.CogHQLoader.unloadPlaceGeom(self)
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
            gzLinkTunnel = self.geom.find('**/LinkTunnel1')
            gzLinkTunnel.setName('linktunnel_gz_17000_DNARoot')
            self.makeSigns()
            top = self.geom.find('**/TunnelEntrance')
            origin = top.find('**/tunnel_origin')
            origin.setH(-33.33)
        elif zoneId == ToontownGlobals.BossbotLobby:
            if base.config.GetBool('want-qa-regression', 0):
                self.notify.info('QA-REGRESSION: COGHQ: Visit BossbotLobby')
            self.notify.debug('cogHQLobbyModelPath = %s' % self.cogHQLobbyModelPath)
            self.geom = loader.loadModel(self.cogHQLobbyModelPath)
        else:
            self.notify.warning('loadPlaceGeom: unclassified zone %s' % zoneId)
        self.startCollisionDetection()
        CogHQLoader.CogHQLoader.loadPlaceGeom(self, zoneId)

    def makeSigns(self):

        def makeSign(topStr, signStr, textId, scale=TTLocalizer.BCHQLsignText):
            top = self.geom.find('**/' + topStr)
            sign = top.find('**/' + signStr)
            locator = top.find('**/sign_origin')
            signText = DirectGui.OnscreenText(text=TextEncoder.upper(TTLocalizer.GlobalStreetNames[textId][(-1)]), font=ToontownGlobals.getSuitFont(), scale=scale, fg=(0,
                                                                                                                                                                        0,
                                                                                                                                                                        0,
                                                                                                                                                                        1), parent=sign)
            signText.setPosHpr(locator, 0, -0.1, -0.25, 0, 0, 0)
            signText.setDepthWrite(0)

        makeSign('Gate_1', 'Sign_3', 10400)
        makeSign('Gate_2', 'Sign_6', 10700)
        makeSign('TunnelEntrance', 'Sign_2', 1000)
        makeSign('Gate_3', 'Sign_3', 10600)
        makeSign('Gate_4', 'Sign_4', 10500)
        makeSign('GateHouse', 'Sign_5', 10200)
        makeSign('Gate_5', 'Sign_3', 10800, scale=0.87)

    def unload(self):
        CogHQLoader.CogHQLoader.unload(self)
        Toon.unloadSellbotHQAnims()

    def enterStageInterior(self, requestStatus):
        self.placeClass = StageInterior.StageInterior
        self.stageId = requestStatus['stageId']
        self.enterPlace(requestStatus)

    def exitStageInterior(self):
        self.exitPlace()
        self.placeClass = None
        return

    def getExteriorPlaceClass(self):
        self.notify.debug('getExteriorPlaceClass')
        return BossbotHQExterior.BossbotHQExterior

    def getBossPlaceClass(self):
        self.notify.debug('getBossPlaceClass')
        return BossbotHQBossBattle.BossbotHQBossBattle

    def enterFactoryExterior(self, requestStatus):
        self.placeClass = BossbotOfficeExterior.BossbotOfficeExterior
        self.enterPlace(requestStatus)

    def exitFactoryExterior(self):
        taskMgr.remove('titleText')
        self.hood.hideTitleText()
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

    def enteringARace(self, status):
        if not status['where'] == 'golfcourse':
            return 0
        else:
            if ZoneUtil.isDynamicZone(status['zoneId']):
                return status['hoodId'] == self.hood.hoodId
            return ZoneUtil.getHoodId(status['zoneId']) == self.hood.hoodId

    def enteringAGolfCourse(self, status):
        if not status['where'] == 'golfcourse':
            return 0
        else:
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
        print 'you done!!'

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
        base.localAvatar.b_squish(20, True)
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