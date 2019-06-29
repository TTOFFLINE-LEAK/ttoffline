import random
from panda3d.core import *
from direct.directnotify import DirectNotifyGlobal
from direct.fsm import StateData, State
from direct.gui import DirectGui
from direct.interval.IntervalGlobal import *
from otp.nametag.NametagConstants import *
from toontown.avatar import ToontownAvatarUtils
from toontown.credits.ModelLoader import addModels
from toontown.toonbase import TTLocalizer, ToontownGlobals
from toontown.toon import Toon
import CogHQLoader, MintInterior, FactoryExterior, CashbotHQExterior, CashbotHQBossBattle, CashbotHQShortChangeOffice, CashbotHQHighriseHallway, CashbotHQBathroom, CashbotHQBar, CashbotHQBuffOffice
from toontown.avatar.ToontownAvatarUtils import createDistributedCog
aSize = 6.06
bSize = 5.29
cSize = 4.14
playRate = 1
TABLES = [
 (
  12, 'bossbotHQ', 'BanquetTableChairs', (-43.7, -11.85, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0), None, None),
 (
  12, 'bossbotHQ', 'BanquetTableChairs', (-43.7, 12.15, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0), None, None),
 (
  12, 'bossbotHQ', 'BanquetTableChairs', (-43.7, 37.15, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0), None, None),
 (
  12, 'bossbotHQ', 'BanquetTableChairs', (39.95, -35.95, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0), None, None),
 (
  12, 'bossbotHQ', 'BanquetTableChairs', (14.8, -36.25, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0), None, None),
 (
  12, 'bossbotHQ', 'BanquetTableChairs', (14.8, -11.85, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0), None, None),
 (
  12, 'bossbotHQ', 'BanquetTableChairs', (14.8, 12.75, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0), None, None),
 (
  12, 'bossbotHQ', 'BanquetTableChairs', (14.8, 37.55, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0), None, None),
 (
  12, 'bossbotHQ', 'BanquetTableChairs', (39.8, -11.45, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0), None, None),
 (
  12, 'bossbotHQ', 'BanquetTableChairs', (39.8, 13.55, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0), None, None)]
seatPos = [
 (3.35, -6.75, 0.725), (6.45, -2.7, 0.725), (2.6, 6.55, 0.725), (-2.8, 6.3, 0.725), (-6.25, 2.15, 0.725)]
seatHpr = [(0, 0, 0), (90, 0, 0), (180, 0, 0), (180, 0, 0), (270, 0, 0)]
seating = [
 (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4),
 (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4),
 (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4),
 (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4),
 (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (9, 0), (9, 1), (9, 2), (9, 3), (9, 4)]

class CashbotCogHQLoader(CogHQLoader.CogHQLoader):
    notify = DirectNotifyGlobal.directNotify.newCategory('CashbotCogHQLoader')

    def __init__(self, hood, parentFSMState, doneEvent):
        CogHQLoader.CogHQLoader.__init__(self, hood, parentFSMState, doneEvent)
        self.fsm.addState(State.State('mintInterior', self.enterMintInterior, self.exitMintInterior, ['quietZone', 'cogHQExterior']))
        for stateName in ['start', 'cogHQExterior', 'quietZone']:
            state = self.fsm.getStateNamed(stateName)
            state.addTransition('mintInterior')
            state.addTransition('factoryExterior')

        self.fsm.addState(State.State('factoryExterior', self.enterFactoryExterior, self.exitFactoryExterior, ['quietZone', 'factoryInterior', 'cogHQExterior']))
        for stateName in ['start', 'cogHQExterior', 'quietZone']:
            state = self.fsm.getStateNamed(stateName)
            state.addTransition('factoryExterior')

        self.musicFile = 'phase_9/audio/bgm/encntr_suit_HQ_nbrhood.ogg'
        self.cogHQExteriorModelPath = 'phase_10/models/cogHQ/CashBotShippingStation'
        self.cogHQLobbyModelPath = 'phase_10/models/cogHQ/VaultLobby'
        self.cogHQShortChangeOfficeModelPath = 'phase_14/models/modules/cog-office'
        self.cogHQHighriseHallwayModelPath = 'phase_14/models/modules/office-hallway'
        self.cogHQBathroomModelPath = 'phase_14/models/modules/cog-bathroom'
        self.cogHQBarModelPath = 'phase_14/models/modules/cog-bar'
        self.geom = None
        self.factGeom = None
        self.bartenderRipoff = None
        self.downsizerNode = None
        self.aloneCog = None
        self.minglerNode = None
        self.bigCheeze = None
        self.cheeseNode = None
        self.cheezeTalkSeq = None
        self.pencilPusher = None
        self.talkingCog1 = None
        self.talkingCog2 = None
        self.eagleNode = None
        self.telemarketerNode = None
        self.talk = None
        self.talkSeq = None
        self.cashbots = None
        self.otherCogs = None
        self.vault = None
        self.cooler = None
        self.leftElevator = None
        self.rightElevator = None
        self.boiler = None
        self.crate = None
        self.crate2 = None
        self.crate3 = None
        self.crate4 = None
        self.highriseProps = []
        self.isHighriseProps = False
        self.gearsSfx = None
        return

    def load(self, zoneId):
        CogHQLoader.CogHQLoader.load(self, zoneId)
        Toon.loadCashbotHQAnims()
        if zoneId == ToontownGlobals.CashbotHQ and base.cr.currentEpisode == 'short_work':
            base.localAvatar.sendUpdate('startCogHighriseEv', [])

    def handleDownsizerCollision(self, collEntry):
        if base.cr.doneInitialBathroomEnter:
            talkOne = TTLocalizer.DownsizerSpeakCog2
        else:
            talkOne = TTLocalizer.DownsizerSpeakCog
        self.ignore('enter' + self.downsizerNode.node().getName())
        self.bartenderRipoff.nametag3d.unstash()
        self.bartenderRipoff.setLocalPageChat(talkOne, 1)
        self.accept(self.bartenderRipoff.uniqueName('doneChatPage'), self.downsizerCollisionDone)

    def downsizerCollisionDone(self, elapsed):
        self.bartenderRipoff.nametag3d.stash()

    def interactWithDownsizer(self):
        cs = CollisionSphere(0, 0, 3, 3)
        self.downsizerNode = self.bartenderRipoff.attachNewNode(CollisionNode('ripoffNode'))
        self.downsizerNode.node().addSolid(cs)
        self.accept('enter' + self.downsizerNode.node().getName(), self.handleDownsizerCollision)

    def handleAloneCogCollision(self, collEntry):
        if base.cr.doneInitialBathroomEnter:
            talkOne = TTLocalizer.MinglerSpeakCog2
        else:
            talkOne = TTLocalizer.MinglerSpeakCog
        self.ignore('enter' + self.minglerNode.node().getName())
        self.aloneCog.nametag3d.unstash()
        self.aloneCog.setLocalPageChat(talkOne, 1)
        self.accept(self.aloneCog.uniqueName('doneChatPage'), self.aloneCogCollisionDone)

    def aloneCogCollisionDone(self, elapsed):
        self.aloneCog.nametag3d.stash()

    def interactWithAloneCog(self):
        cs = CollisionSphere(0, 0, 3, 3)
        self.minglerNode = self.aloneCog.attachNewNode(CollisionNode('minglerNode'))
        self.minglerNode.node().addSolid(cs)
        self.accept('enter' + self.minglerNode.node().getName(), self.handleAloneCogCollision)

    def handleCheezeCollision(self, collEntry):
        talkOne = TTLocalizer.CheezeSpeakCog1
        self.ignore('enter' + self.cheeseNode.node().getName())
        self.bigCheeze.nametag3d.unstash()
        self.bigCheeze.setLocalPageChat(talkOne, 1)
        self.accept(self.bigCheeze.uniqueName('doneChatPage'), self.continueCheezeSeq)

    def interactCheeze(self):
        cs = CollisionSphere(0, 0, 3, 3)
        self.cheeseNode = self.bigCheeze.attachNewNode(CollisionNode('cheeseNode'))
        self.cheeseNode.node().addSolid(cs)
        self.accept('enter' + self.cheeseNode.node().getName(), self.handleCheezeCollision)

    def handleEagleCollision(self, collEntry):
        talkOne = TTLocalizer.EagleSpeakCog1
        self.ignore('enter' + self.eagleNode.node().getName())
        self.talkingCog1.nametag3d.unstash()
        self.talkingCog1.setLocalPageChat(talkOne, 1)
        self.accept(self.talkingCog1.uniqueName('doneChatPage'), self.eagleCollisionDone)

    def interactWithEagle(self):
        cs = CollisionSphere(0, 0, 3, 3)
        self.eagleNode = self.talkingCog1.attachNewNode(CollisionNode('eagleNode'))
        self.eagleNode.node().addSolid(cs)
        self.accept('enter' + self.eagleNode.node().getName(), self.handleEagleCollision)

    def eagleCollisionDone(self, elapsed):
        self.talkingCog1.nametag3d.stash()

    def handleTelemarketerCollision(self, collEntry):
        talkOne = TTLocalizer.TelemarketerSpeakCog1
        self.ignore('enter' + self.telemarketerNode.node().getName())
        self.talkingCog2.nametag3d.unstash()
        self.talkingCog2.setLocalPageChat(talkOne, 1)
        self.accept(self.talkingCog2.uniqueName('doneChatPage'), self.telemarketerCollisionDone)

    def interactWithTelemarketer(self):
        cs = CollisionSphere(0, 0, 3, 3)
        self.telemarketerNode = self.talkingCog2.attachNewNode(CollisionNode('telemarketerNode'))
        self.telemarketerNode.node().addSolid(cs)
        self.accept('enter' + self.telemarketerNode.node().getName(), self.handleTelemarketerCollision)

    def telemarketerCollisionDone(self, elapsed):
        self.talkingCog2.nametag3d.stash()

    def openElevator(self):
        seq = Sequence(Parallel(self.rightElevator.find('**/left_door').posInterval(2, (0,
                                                                                        0,
                                                                                        0)), self.rightElevator.find('**/right_door').posInterval(2, (0,
                                                                                                                                                      0,
                                                                                                                                                      0))), Func(self.pencilPusher.loop, 'walk'), self.pencilPusher.posHprInterval(1, (31.649,
                                                                                                                                                                                                                                       200.79,
                                                                                                                                                                                                                                       0.325), (-180,
                                                                                                                                                                                                                                                0.0,
                                                                                                                                                                                                                                                0.0)), self.pencilPusher.hprInterval(1, (-201.276,
                                                                                                                                                                                                                                                                                         0.0,
                                                                                                                                                                                                                                                                                         0.0)), self.pencilPusher.posInterval(8, (-6.867,
                                                                                                                                                                                                                                                                                                                                  95.554,
                                                                                                                                                                                                                                                                                                                                  0.325)), self.pencilPusher.hprInterval(1, (-180,
                                                                                                                                                                                                                                                                                                                                                                             0.0,
                                                                                                                                                                                                                                                                                                                                                                             0.0)), self.pencilPusher.posInterval(11, (-8.807,
                                                                                                                                                                                                                                                                                                                                                                                                                       -42.611,
                                                                                                                                                                                                                                                                                                                                                                                                                       0.325)), Func(self.pencilPusher.loop, 'neutral'), Func(self.pencilPusher.nametag3d.unstash), Func(self.pencilPusher.setChatAbsolute, 'Hello Mr. Big Cheese. The Chairman sent me on an urgent matter.', CFSpeech | CFTimeout), Wait(2), Func(self.bigCheeze.nametag3d.unstash), Func(self.bigCheeze.setChatAbsolute, 'Yes? Is it related to the upcoming banquet?', CFSpeech | CFTimeout), Wait(4), Func(self.pencilPusher.setChatAbsolute, 'Not quite. The C.E.O. has been defeated by the Toons once again.', CFSpeech | CFTimeout)).start()

    def fadeScreen(self):
        seq = Sequence(Wait(1), Func(base.transitions.fadeOut))
        seq.start()

    def sendback(self):
        base.localAvatar.sendUpdate('resetEpisodeFlags')
        base.localAvatar.cameraFollow = 0
        base.cr.loadingStuff = 0
        for table in render.findAllMatches('**/Table_Banquet'):
            table.removeNode()

        for cogs in [self.currentCogs, self.otherCogs]:
            for cog in cogs:
                cog.cleanup()
                cog.removeNode()
                cog = None

        self.talk.finish()
        self.talkSeq.finish()
        self.unloadPlaceGeom()
        base.cr.inEpisode = False
        base.cr.currentEpisode = None
        base.cr.doneInitialHighriseEnter = False
        base.cr.doneInitialBathroomEnter = False
        base.cr.cameFromBathroom = False
        base.cr.cameFromBar = False
        base.cr._userLoggingOut = True
        if base.cr.timeManager:
            base.cr.timeManager.setDisconnectReason(ToontownGlobals.DisconnectBookExit)
        base.transitions.fadeScreen(1.0)
        base.cr.gameFSM.request('closeShard')
        return

    def continueCheezeSeq(self, elapsed):
        base.transitions.letterboxOn()
        self.pencilPusher = ToontownAvatarUtils.createCog('p', 31.649, 205.79, 0.325, -180, 0.0, 0.0, level=2)
        self.pencilPusher.nametag3d.stash()
        self.pencilPusher.addActive()
        self.pencilPusher.loop('neutral')
        self.pencilPusher.reparentTo(self.geom)
        self.laffMeter = base.localAvatar.laffMeter
        seq = Sequence(Func(base.localAvatar.disableAvatarControls), Func(base.camera.wrtReparentTo, render), Func(base.localAvatar.stopUpdateSmartCamera), Func(base.localAvatar.shutdownSmartCamera), Func(base.camera.setPosHpr, -53.68, -7.958, 12.353, -167, -4.6, 0.0), LerpPosHprInterval(camera, 6.9, (-4.914,
                                                                                                                                                                                                                                                                                                               -31.29,
                                                                                                                                                                                                                                                                                                               3.7207), (-201,
                                                                                                                                                                                                                                                                                                                         0.64,
                                                                                                                                                                                                                                                                                                                         0.0), blendType='easeInOut'), Wait(1.5), Func(base.camera.setPosHpr, -21.21, -67.29, 7.6029, -384, -6.8, 0.0), LerpPosHprInterval(camera, 6.9, (-17.09,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                         -58.26,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                         7.0939), (-382,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   -4.9,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   0.0), blendType='easeInOut'), Wait(1.5), Func(base.camera.setPosHpr, -13.75, -57.22, 4.3772, -361, 15, 0.0), Func(self.bigCheeze.nametag3d.unstash), Func(self.bigCheeze.setChatAbsolute, 'Are you looking to get a Pink Slip, Mr. Short Change?', CFSpeech | CFTimeout), Wait(5), Func(self.bigCheeze.nametag3d.stash), Func(base.camera.setPosHpr, 7.7502, 111.45, 13.402, -17.0, -2.2, 0.0), Func(self.openElevator), LerpPosHprInterval(base.camera, 4, (20.714,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                160.99,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                10.284), (-16.0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          -6.1,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          0.0), blendType='easeInOut'), Wait(1), base.camera.posHprInterval(11, (-42.29,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 -81.7,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 32), (-14.0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       -18.0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       0.0)), base.camera.posHprInterval(4.5, (-72.87,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               28.675,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               32), (-135,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     -22.0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     0.0)), base.camera.posHprInterval(5, (-17.7,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           -22.75,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           12.041), (-162,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     -15.0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     0.0)), Wait(10), Func(base.camera.setPosHpr, -16.74, -70, 8.3765, -4.5, -4.3, 0.0), Func(self.bigCheeze.setChatAbsolute, 'Well then.', CFSpeech | CFTimeout), Wait(4), Func(self.bigCheeze.setChatAbsolute, "I suppose it's time to get my promotion.", CFSpeech | CFTimeout), Wait(1), base.camera.posHprInterval(1, (-15.49,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            -59.48,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            5.9885), (-4.5,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      4.69,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      0.0)), Wait(2), Func(self.fadeScreen), Wait(2), Func(base.transitions.letterboxOff), Func(base.localAvatar.attachCamera), Func(base.localAvatar.initializeSmartCamera), Func(base.localAvatar.startUpdateSmartCamera), Func(NodePath(base.marginManager).show), Func(NodePath(self.laffMeter).show), Func(self.sendback))
        seq.start()

    def unloadPlaceGeom(self):
        if self.geom:
            self.geom.removeNode()
            self.geom = None
        if self.factGeom:
            self.factGeom.removeNode()
            self.factGeom = None
        if self.bartenderRipoff:
            self.bartenderRipoff.removeActive()
            self.bartenderRipoff.cleanup()
            self.bartenderRipoff.removeNode()
            self.bartenderRipoff = None
            self.ignore('enter' + self.downsizerNode.node().getName())
        if self.aloneCog:
            self.aloneCog.removeActive()
            self.aloneCog.cleanup()
            self.aloneCog.removeNode()
            self.aloneCog = None
            self.ignore('enter' + self.minglerNode.node().getName())
        if self.bigCheeze:
            self.bigCheeze.removeActive()
            self.bigCheeze.cleanup()
            self.bigCheeze.removeNode()
            self.bigCheeze = None
            if self.cheeseNode:
                self.ignore('enter' + self.cheeseNode.node().getName())
        if self.cheezeTalkSeq:
            self.cheezeTalkSeq.finish()
        if self.pencilPusher:
            self.pencilPusher.removeActive()
            self.pencilPusher.cleanup()
            self.pencilPusher.removeNode()
            self.pencilPusher = None
        if self.talkingCog1:
            self.talkingCog1.removeActive()
            self.talkingCog1.cleanup()
            self.talkingCog1.removeNode()
            self.talkingCog1 = None
            if self.eagleNode:
                self.ignore('enter' + self.eagleNode.node().getName())
        if self.talkingCog2:
            self.talkingCog2.removeActive()
            self.talkingCog2.cleanup()
            self.talkingCog2.removeNode()
            self.talkingCog2 = None
            if self.telemarketerNode:
                self.ignore('enter' + self.telemarketerNode.node().getName())
        if base.cr.cameFromBar:
            for table in render.findAllMatches('**/Table_Banquet'):
                table.removeNode()

            for cogs in [self.currentCogs, self.otherCogs]:
                for cog in cogs:
                    cog.cleanup()
                    cog.removeNode()
                    cog = None

            self.talk.finish()
            self.talkSeq.finish()
        if self.gearsSfx:
            self.gearsSfx.stop()
            base.loader.unloadSfx(self.gearsSfx)
            self.gearsSfx = None
        if self.vault:
            self.vault.removeNode()
        if self.cooler:
            self.cooler.removeNode()
        if self.isHighriseProps:
            for prop in self.highriseProps:
                prop.removeNode()
                prop = None

        CogHQLoader.CogHQLoader.unloadPlaceGeom(self)
        return

    def loadPlaceGeom(self, zoneId):
        self.notify.info('loadPlaceGeom: %s' % zoneId)
        if zoneId == ToontownGlobals.CashbotHQ:
            self.geom = loader.loadModel(self.cogHQExteriorModelPath)
            ddLinkTunnel = self.geom.find('**/LinkTunnel1')
            ddLinkTunnel.setName('linktunnel_dl_9252_DNARoot')
            locator = self.geom.find('**/sign_origin')
            backgroundGeom = self.geom.find('**/EntranceFrameFront')
            backgroundGeom.node().setEffect(DecalEffect.make())
            signText = DirectGui.OnscreenText(text=TTLocalizer.DonaldsDreamland[(-1)], font=ToontownGlobals.getSuitFont(), scale=3, fg=(0.87,
                                                                                                                                        0.87,
                                                                                                                                        0.87,
                                                                                                                                        1), mayChange=False, parent=backgroundGeom)
            signText.setPosHpr(locator, 0, 0, 0, 0, 0, 0)
            signText.setDepthWrite(0)
        else:
            if zoneId == ToontownGlobals.CashbotLobby:
                if config.GetBool('want-qa-regression', 0):
                    self.notify.info('QA-REGRESSION: COGHQ: Visit CashbotLobby')
                self.geom = loader.loadModel(self.cogHQLobbyModelPath)
            else:
                if zoneId == ToontownGlobals.CashbotShortChangeOffice:
                    if config.GetBool('want-qa-regression', 0):
                        self.notify.info('QA-REGRESSION: COGHQ: Visit CashbotShortChangeOffice')
                    self.geom = loader.loadModel(self.cogHQShortChangeOfficeModelPath)
                    self.geom.find('**/office_floor').setBin('ground', -10)
                    self.vault = loader.loadModel('phase_10/models/cashbotHQ/VaultDoorCover')
                    self.vault.reparentTo(self.geom)
                    self.vault.setScale(0.5)
                    self.vault.setPosHpr(-13.91, -23.86, 0.0, 180.0, 0.0, 0.0)
                    self.cooler = loader.loadModel('phase_5/models/props/watercooler')
                    self.cooler.reparentTo(self.geom)
                    self.cooler.setPosHpr(11.624, -23.22, 0.8629, -534, -483, 0.0)
                else:
                    if zoneId == ToontownGlobals.CashbotHighriseHallway:
                        if config.GetBool('want-qa-regression', 0):
                            self.notify.info('QA-REGRESSION: COGHQ: Visit CashbotHighriseHallway')
                        self.geom = loader.loadModel(self.cogHQHighriseHallwayModelPath)
                        self.geom.find('**/hallway_floor').setBin('ground', -10)
                        self.bartenderRipoff = ToontownAvatarUtils.createCog('ds', -6.448, 16.704, 0.025, -37.47, 0, 0, isWaiter=True, level=9)
                        self.bartenderRipoff.nametag3d.stash()
                        self.bartenderRipoff.addActive()
                        self.interactWithDownsizer()
                        gearsNode = self.geom.find('**/vents')
                        self.gearsSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_gears_turning.ogg')
                        base.playSfx(self.gearsSfx, looping=1, volume=1, node=gearsNode)
                    else:
                        if zoneId == ToontownGlobals.CashbotBathroom:
                            if config.GetBool('want-qa-regression', 0):
                                self.notify.info('QA-REGRESSION: COGHQ: Visit CashbotBathroom')
                            self.geom = loader.loadModel(self.cogHQBathroomModelPath)
                            shitters = self.geom.find('**/urinal1')
                            shitters.setPosHpr(2, -1, 12, 0, 16, 16)
                        else:
                            if zoneId == ToontownGlobals.CashbotBar:
                                if config.GetBool('want-qa-regression', 0):
                                    self.notify.info('QA-REGRESSION: COGHQ: Visit CashbotBar')
                                self.geom = loader.loadModel(self.cogHQBarModelPath)
                                self.leftElevator = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_csa_elevatorB')
                                self.leftElevator.reparentTo(self.geom)
                                self.leftElevator.setPosHpr(-48.24, 200.79, 0.0, 0.0, 0.0, 0.0)
                                self.leftElevator.find('**/left_door').setPos(3.5, 0, 0)
                                self.leftElevator.find('**/right_door').setPos(-3.5, 0, 0)
                                self.rightElevator = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_csa_elevatorB')
                                self.rightElevator.reparentTo(self.geom)
                                self.rightElevator.setPosHpr(31.649, 200.79, 0.0, 0.0, 0.0, 0.0)
                                self.rightElevator.find('**/left_door').setPos(3.5, 0, 0)
                                self.rightElevator.find('**/right_door').setPos(-3.5, 0, 0)
                                self.boiler = loader.loadModel('phase_10/models/cashbotHQ/boiler_B2')
                                self.boiler.reparentTo(self.geom)
                                self.boiler.setPosHpr(51.5, 188.33, 0.06, -182, 0.0, 0.0)
                                self.crate = loader.loadModel('phase_10/models/cashbotHQ/CBMetalCrate')
                                self.crate.reparentTo(self.geom)
                                self.crate.setPosHpr(-66.84, 173.45, 0.0, -182, 0.0, 0.0)
                                self.crate2 = loader.loadModel('phase_10/models/cashbotHQ/CBMetalCrate')
                                self.crate2.reparentTo(self.geom)
                                self.crate2.setPosHpr(-66.63, 179.44, 0.0, -182, 0.0, 0.0)
                                self.crate3 = loader.loadModel('phase_10/models/cashbotHQ/CBMetalCrate')
                                self.crate3.reparentTo(self.geom)
                                self.crate3.setPosHpr(-67.07, 176.7, 5.5999, -182, 0.0, 0.0)
                                self.crate4 = loader.loadModel('phase_10/models/cashbotHQ/CBMetalCrate')
                                self.crate4.reparentTo(self.geom)
                                self.crate4.setPosHpr(-60.77, 175.23, 0.0, -182, 0.0, 0.0)
                                self.vaultBig = loader.loadModel('phase_10/models/cashbotHQ/VaultDoorCover')
                                self.vaultBig.reparentTo(self.geom)
                                self.vaultBig.setPosHpr(-69.82, 142.44, 0.0, 90, 0.0, 0.0)
                                self.comfy = loader.loadModel('phase_11/models/lawbotHQ/LB_couchA')
                                self.comfy.reparentTo(self.geom)
                                self.comfy.setPosHpr(16.455, 55.559, 0.05, -13.0, 0.0, 0.0)
                                self.comfy2 = loader.loadModel('phase_11/models/lawbotHQ/LB_couchA')
                                self.comfy2.reparentTo(self.geom)
                                self.comfy2.setPosHpr(-55.97, 54.798, 0.05, 37.4, 0.0, 0.0)
                                self.highriseProps = [
                                 self.leftElevator, self.rightElevator, self.boiler, self.crate, self.crate2, self.crate3, self.crate4, self.vaultBig, self.comfy, self.comfy2]
                                self.isHighriseProps = True
                                self.aloneCog = ToontownAvatarUtils.createCog('m', 38.386, 101.617, 0.325, 41.519, 0, 0, parent=self.geom, level=7)
                                self.aloneCog.nametag3d.stash()
                                self.aloneCog.addActive()
                                self.interactWithAloneCog()
                                self.bigCheeze = ToontownAvatarUtils.createDistributedCog('tbc', -14.87, -47.67, -0.225, 174.0, 0.0, 0.0, anim='sit', parent=self.geom, level=50)
                                self.bigCheeze.nametag3d.stash()
                                self.bigCheeze.addActive()
                                self.bigCheeze.nametag3d.setZ(9)
                                self.interactCheeze()
                                self.talkingCog1 = ToontownAvatarUtils.createCog('le', -50.906, 108.119, 0.325, 224, 0, 0, parent=self.geom, level=11)
                                self.talkingCog1.nametag3d.stash()
                                self.talkingCog1.addActive()
                                self.interactWithEagle()
                                self.talkingCog2 = ToontownAvatarUtils.createCog('tm', -42.535, 99.554, 0.325, 44, 0, 0, parent=self.geom, level=5)
                                self.talkingCog2.nametag3d.stash()
                                self.talkingCog2.addActive()
                                self.interactWithTelemarketer()
                                addModels(TABLES, render)
                                tableNum = -1
                                tableHpr = 0
                                for table in render.findAllMatches('**/Table_Banquet'):
                                    tableNum = tableNum + 1
                                    tableHpr = tableHpr + 90
                                    tableNode = table.attachNewNode('table_%s' % tableNum)
                                    tableNode.setHpr(tableHpr, 0, 0)
                                    tableNode.setZ(10)
                                    for seat in range(0, 5):
                                        seatNode = table.find('table_%s' % tableNum).attachNewNode('seat_%s' % seat)
                                        seatNode.setPos(seatPos[seat])
                                        seatNode.setHpr(seatHpr[seat])

                                self.bigwig = ToontownAvatarUtils.createCog('bw', -38.49, -47.28, -0.224, 174.0, 0.0, 0.0, anim='sit')
                                self.bigwig.nametag3d.stash()
                                self.loanshark = ToontownAvatarUtils.createCog('ls', 53.047, -57.81, 0.1259, 403.0, 0.0, 0.0, isWaiter=True, coll=False)
                                self.loanshark.nametag3d.stash()
                                loanCollision = CollisionSphere(0, 0, 3, 4)
                                self.loanNode = self.loanshark.attachNewNode(CollisionNode('loanCollision'))
                                self.loanNode.node().addSolid(loanCollision)
                                self.fatraider = ToontownAvatarUtils.createCog('cr', -53.62, 50.942, -2.723, 211.0, 0.0, 0.0, anim='sit')
                                self.fatraider.nametag3d.stash()
                                self.waiter = ToontownAvatarUtils.createCog('bc', -42.59, -55.69, -0.224, 0.0, 0.0, 0.0, isWaiter=True)
                                self.waiter.nametag3d.stash()
                                self.cashbots = [
                                 'pp', 'tw', 'sc', 'nc', 'rb']
                                self.otherCogs = [self.bigwig, self.loanshark, self.waiter, self.fatraider]
                                self.currentCogs = []
                                seatNum = -1
                                for cog in range(0, 35):
                                    randCog = random.choice(self.cashbots)
                                    if randCog == 'pp':
                                        z = -9.5
                                    else:
                                        z = -10
                                    seatNum = seatNum + 1
                                    seat = seating[seatNum]
                                    seatNode = render.find('**/table_%s/**/seat_%s' % (seat[0], seat[1])).attachNewNode('cog_%s' % seatNum)
                                    newCog = ToontownAvatarUtils.createCog(randCog, z=z, anim='sit', parent=seatNode)
                                    newCog.nametag3d.stash()
                                    self.currentCogs.append(newCog)

                                self.talk = Sequence(Wait(1.8), Func(self.doPhrase))
                                self.talk.loop()
                            else:
                                if zoneId == ToontownGlobals.CashbotBuffOffice:
                                    self.geom = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_crg_penthouse_sell.bam')
                                    self.geom.reparentTo(render)
                                    self.geom.find('**/cloudAnimation_GRP').removeNode()
                                    Elevator = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_csa_elevatorB.bam')
                                    Elevator.reparentTo(self.geom.find('**/elevatorOUT_node'))
                                    Elevator.find('**/left_door').setX(3.5)
                                    Elevator.find('**/right_door').setX(-3.5)
                                    Elevator.setY(0.24)
                                    Elevator2 = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_csa_elevatorB.bam')
                                    Elevator2.reparentTo(self.geom.find('**/elevatorIN_node'))
                                    Elevator2.find('**/left_door').setX(3.5)
                                    Elevator2.find('**/right_door').setX(-3.5)
                                    Elevator2.setY(0.18)
                                    safes = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_ccg_safesA.bam')
                                    safes.reparentTo(self.geom.find('**/Grp_room'))
                                    safes.setPos(0, -45, 0)
                                    safes.setHpr(169.99, 0, 0)
                                    portrait = loader.loadModel('phase_5.5/models/estate/tropicView.bam')
                                    portrait.reparentTo(self.geom.find('**/Grp_room'))
                                    portrait.setPos(-22, 0, 21)
                                    portrait.setHpr(270, 0, 0)
                                    portrait.setScale(15)
                                    portrait.find('**/frame').removeNode()
                                    portrait2 = loader.loadModel('phase_5.5/models/estate/tropicView.bam')
                                    portrait2.reparentTo(self.geom.find('**/Grp_room'))
                                    portrait2.setPos(10, 0, 21)
                                    portrait2.setHpr(90, 0, 0)
                                    portrait2.setScale(15)
                                    portrait2.find('**/frame').removeNode()
                                    BuffShark = createDistributedCog('bfs', -18.3, 0, 0, 267.14, 0, 0, False, False, 'sit', self.geom, 'Buff Shark', None, '88 v3.0', True, False)
                                    self.flexman = Sequence(Wait(5), Func(BuffShark.setChatAbsolute, 'What are you doing in my office?', CFSpeech | CFTimeout), Wait(9), Func(BuffShark.setChatAbsolute, "You may stay, just don't touch my weight lifting trophies.", CFSpeech | CFTimeout), Wait(14))
                                    self.flexman.start()
                                else:
                                    self.notify.warning('loadPlaceGeom: unclassified zone %s' % zoneId)
        CogHQLoader.CogHQLoader.loadPlaceGeom(self, zoneId)
        return

    def unload(self):
        CogHQLoader.CogHQLoader.unload(self)
        Toon.unloadCashbotHQAnims()

    def enterFactoryExterior(self, requestStatus):
        if requestStatus['zoneId'] == ToontownGlobals.CashbotShortChangeOffice:
            self.placeClass = CashbotHQShortChangeOffice.CashbotHQShortChangeOffice
        if requestStatus['zoneId'] == ToontownGlobals.CashbotHighriseHallway:
            self.placeClass = CashbotHQHighriseHallway.CashbotHQHighriseHallway
        if requestStatus['zoneId'] == ToontownGlobals.CashbotBathroom:
            self.placeClass = CashbotHQBathroom.CashbotHQBathroom
        if requestStatus['zoneId'] == ToontownGlobals.CashbotBar:
            self.placeClass = CashbotHQBar.CashbotHQBar
        if requestStatus['zoneId'] == ToontownGlobals.CashbotBuffOffice:
            self.placeClass = CashbotHQBuffOffice.CashbotHQBuffOffice
        self.enterPlace(requestStatus)
        self.hood.spawnTitleText(requestStatus['zoneId'])

    def exitFactoryExterior(self):
        taskMgr.remove('titleText')
        self.hood.hideTitleText()
        self.exitPlace()
        self.placeClass = None
        return

    def enterMintInterior(self, requestStatus):
        self.placeClass = MintInterior.MintInterior
        self.mintId = requestStatus['mintId']
        self.enterPlace(requestStatus)

    def exitMintInterior(self):
        self.exitPlace()
        self.placeClass = None
        del self.mintId
        return

    def getExteriorPlaceClass(self):
        return CashbotHQExterior.CashbotHQExterior

    def getBossPlaceClass(self):
        return CashbotHQBossBattle.CashbotHQBossBattle

    def doPhrase(self):
        blabble = [
         "Where's my drink!?",
         'Arrgh!',
         'Hmmmph.',
         'Bah.',
         'Garble.',
         'Bah bah bah bah-bah, bah bah-bah bah.']
        phrase = random.choice(blabble)
        cog = random.choice(self.currentCogs)
        randomWait = random.randint(3, 13)
        self.talkSeq = Sequence(Wait(randomWait), Func(cog.nametag3d.unstash), Func(cog.setChatAbsolute, phrase, CFSpeech | CFTimeout), Wait(5), Func(cog.nametag3d.stash))
        self.talkSeq.start()