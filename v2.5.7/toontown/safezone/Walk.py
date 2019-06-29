from panda3d.core import *
from otp.nametag.NametagConstants import *
from direct.task.Task import Task
from direct.directnotify import DirectNotifyGlobal
from direct.gui.DirectGui import *
from direct.fsm import StateData
from direct.fsm import ClassicFSM, State
from direct.fsm import State
from toontown.toonbase import ToontownGlobals
from direct.interval.IntervalGlobal import *
from toontown.hood import ZoneUtil
from direct.actor import Actor
from toontown.avatar import ToontownAvatarUtils
from toontown.battle import MovieTrap
from toontown.battle.BattleProps import *
from toontown.battle import BattleProps as BP
from toontown.battle import MovieUtil
import FakeElections, random

class Walk(StateData.StateData):
    notify = DirectNotifyGlobal.directNotify.newCategory('Walk')

    def __init__(self, doneEvent):
        StateData.StateData.__init__(self, doneEvent)
        self.fsm = ClassicFSM.ClassicFSM('Walk', [State.State('off', self.enterOff, self.exitOff, ['walking', 'swimming', 'slowWalking']),
         State.State('walking', self.enterWalking, self.exitWalking, ['swimming', 'slowWalking']),
         State.State('swimming', self.enterSwimming, self.exitSwimming, ['walking', 'slowWalking']),
         State.State('slowWalking', self.enterSlowWalking, self.exitSlowWalking, ['walking', 'swimming'])], 'off', 'off')
        self.fsm.enterInitialState()
        self.isSwimSoundAudible = 0
        self.swimSoundPlaying = 0
        if base.cr.currentEpisode == 'short_work':
            cm = CardMaker('card')
            cm.setFrameFullscreenQuad()
            self.explosionCard = render2d.attachNewNode(cm.generate())
            self.explosionCard.setTransparency(1)
            self.explosionCard.setColorScale(0, 0, 0, 0)
            self.doneHighrise = False
            self.gufawToon = None
            self.newspaperButton = None
            self.redtapeButton = None
            self.bowtieButton = None
        return

    def load(self):
        pass

    def unload(self):
        del self.fsm

    def oakStreetTeleport(self):
        hoodId = ZoneUtil.getTrueZoneId(21000, 21000)
        zoneId = ZoneUtil.getTrueZoneId(21306, 21000)
        how = 'teleportIn'
        tunnelOriginPlaceHolder = render.attachNewNode('toph_21000_21306')
        tutorialFlag = 0
        requestStatus = {'loader': ZoneUtil.getLoaderName(zoneId), 'where': ZoneUtil.getToonWhereName(zoneId), 
           'how': how, 
           'hoodId': hoodId, 
           'zoneId': zoneId, 
           'shardId': None, 
           'tunnelOrigin': tunnelOriginPlaceHolder, 
           'tutorial': tutorialFlag, 
           'avId': -1}
        place = base.cr.playGame.getPlace()
        if place:
            place.requestLeave(requestStatus)
        return

    def resetCameraFollow(self):
        base.localAvatar.cameraFollow = 0

    def prepareFadeout(self):
        Seq = Sequence(Wait(5.9), Func(base.transitions.fadeOut), Wait(1), Func(self.cogHighriseTeleport), Func(self.explosionCard.setColorScale, 0, 0, 0, 1), Wait(3), self.explosionCard.colorScaleInterval(2, (0,
                                                                                                                                                                                                                  0,
                                                                                                                                                                                                                  0,
                                                                                                                                                                                                                  0)), Wait(1), Func(self.explosionCard.removeNode))
        Seq.start()

    def cogHighriseTeleport(self):
        hoodId = ZoneUtil.getTrueZoneId(12000, 12000)
        zoneId = ZoneUtil.getTrueZoneId(12200, 12000)
        how = 'teleportIn'
        tunnelOriginPlaceHolder = render.attachNewNode('toph_12000_12200')
        tutorialFlag = 0
        requestStatus = {'loader': ZoneUtil.getLoaderName(zoneId), 'where': ZoneUtil.getToonWhereName(zoneId), 
           'how': how, 
           'hoodId': hoodId, 
           'zoneId': zoneId, 
           'shardId': None, 
           'tunnelOrigin': tunnelOriginPlaceHolder, 
           'tutorial': tutorialFlag, 
           'avId': -1}
        place = base.cr.playGame.getPlace()
        if place:
            place.requestLeave(requestStatus)
        return

    def shortFly(self):
        propeller = Actor.Actor('phase_4/models/props/propeller-mod.bam', {'spin': 'phase_4/models/props/propeller-chan.bam'})
        propeller.setBlend(frameBlend=config.GetBool('interpolate-animations', True))
        propeller.reparentTo(hidden)
        endFly = base.loader.loadSfx('phase_5/audio/sfx/ENC_propeller_in.ogg')
        startFly = base.loader.loadSfx('phase_5/audio/sfx/ENC_propeller_out.ogg')
        cogSuit = base.localAvatar.suit
        suit = base.localAvatar
        cogLeave = Sequence(ActorInterval(cogSuit, 'sit-lose'), Wait(0.1), Func(suit.setZ, 2.75), ActorInterval(cogSuit, 'landing', startTime=2.5, endTime=0), Wait(1.5), ActorInterval(cogSuit, 'landing'), Func(cogSuit.loop, 'neutral'))
        cogMovement = Sequence(Wait(3), Parallel(Sequence(suit.posInterval(0.5, (0,
                                                                                 15,
                                                                                 5)), suit.posInterval(0.5, (0,
                                                                                                             10,
                                                                                                             6)), suit.posInterval(0.5, (0,
                                                                                                                                         5,
                                                                                                                                         5)), suit.posInterval(1.5, (0,
                                                                                                                                                                     0,
                                                                                                                                                                     0))), suit.hprInterval(1, (180,
                                                                                                                                                                                                0,
                                                                                                                                                                                                0))))
        spinTrack = Sequence(ActorInterval(propeller, 'spin', startTime=0, endTime=0.25))
        propellerTrack = Sequence(Wait(1), Func(propeller.reparentTo, suit.find('**/joint_head')), ActorInterval(propeller, 'spin', startTime=4, endTime=2), Func(spinTrack.loop), Wait(2.25), Func(spinTrack.finish), ActorInterval(propeller, 'spin'), Func(propeller.delete))
        soundTrack = Sequence(Wait(1), Parallel(SoundInterval(startFly, duration=3), Sequence(Wait(2.5), SoundInterval(endFly))))
        return Parallel(cogLeave, cogMovement, propellerTrack, soundTrack)

    def shortCrash(self):
        propeller = Actor.Actor('phase_4/models/props/propeller-mod.bam', {'spin': 'phase_4/models/props/propeller-chan.bam'})
        propeller.setBlend(frameBlend=config.GetBool('interpolate-animations', True))
        propeller.reparentTo(hidden)
        startFly = base.loader.loadSfx('phase_5/audio/sfx/ENC_propeller_out.ogg')
        crash = base.loader.loadSfx('phase_5/audio/sfx/TL_train_cog.ogg')
        land = base.loader.loadSfx('phase_5/audio/sfx/Toon_bodyfall_synergy.ogg')
        cogSuit = base.localAvatar.suit
        suit = base.localAvatar
        cogLeave = Sequence(ActorInterval(cogSuit, 'sit-lose'), Wait(0.1), Func(suit.setZ, 2.75), ActorInterval(cogSuit, 'landing', startTime=2.5, endTime=0), Wait(1.4), ActorInterval(cogSuit, 'slip-backward', playRate=0.75, startTime=0.3), Func(cogSuit.loop, 'neutral'))
        cogMovement = Sequence(Wait(3), Parallel(Sequence(suit.posInterval(0.5, (0,
                                                                                 15,
                                                                                 5)), suit.posInterval(1, (0,
                                                                                                           10,
                                                                                                           10)), suit.posInterval(0.7, (0,
                                                                                                                                        5,
                                                                                                                                        12)), Wait(0.05), suit.posInterval(0.55, (0,
                                                                                                                                                                                  0,
                                                                                                                                                                                  0), (0,
                                                                                                                                                                                       5,
                                                                                                                                                                                       9))), suit.hprInterval(1, (180,
                                                                                                                                                                                                                  0,
                                                                                                                                                                                                                  0))))
        spinTrack = Sequence(ActorInterval(propeller, 'spin', startTime=0, endTime=0.25))
        propellerTrack = Sequence(Wait(1), Func(propeller.reparentTo, suit.find('**/joint_head')), ActorInterval(propeller, 'spin', startTime=4, endTime=2), Func(spinTrack.loop), Wait(2.25), Func(spinTrack.finish), ActorInterval(propeller, 'spin'), Func(propeller.delete))
        soundTrack = Sequence(Wait(1), Parallel(SoundInterval(startFly, duration=5), Sequence(Wait(4.05), SoundInterval(crash)), Sequence(Wait(4.8), SoundInterval(land))))
        return Parallel(cogLeave, cogMovement, propellerTrack, soundTrack)

    def doShortChangeLeave(self):
        if random.randint(0, 100) < 5:
            shortCrash = self.shortCrash()
            shortCrash.start()
        else:
            shortFly = self.shortFly()
            shortFly.start()

    def trapCog(self):
        toonTracks = Parallel()
        trap = {'toon': self.gufawToon, 'level': 0, 'battle': render, 'target': [{'suit': base.localAvatar}]}
        banana = globalPropPool.getProp('banana')
        banana2 = MovieUtil.copyProp(banana)
        trapPropList = [banana, banana2]
        tracks = MovieTrap.createThrownTrapMultiTrack(trap, trapPropList, 'banana', anim=1, explode=1)
        if tracks:
            for track in tracks:
                toonTracks.append(track)

        return toonTracks

    def laugh(self, volume=1):
        sfx = base.loader.loadSfx('phase_4/audio/sfx/avatar_emotion_laugh.ogg')

        def playSfx(volume=1):
            base.playSfx(sfx, volume=volume, node=self.gufawToon)

        def playAnim():
            self.gufawToon.setPlayRate(10, 'neutral')
            self.gufawToon.loop('neutral')

        def stopAnim():
            self.gufawToon.setPlayRate(1, 'neutral')

        exitTrack = Sequence(Func(self.gufawToon.hideLaughMuzzle), Func(self.gufawToon.blinkEyes), Func(stopAnim))
        track = Sequence(Func(self.gufawToon.blinkEyes), Func(self.gufawToon.showLaughMuzzle), Func(playAnim), Func(playSfx, volume), Wait(2), Func(exitTrack.start))
        return track

    def doLaugh(self):
        self.toonLaugh = self.laugh()
        self.toonLaugh.start()

    def launchProp(self, prop):
        base.transitions.letterboxOn()
        sfxSad = loader.loadSfx('phase_5/audio/sfx/ENC_Lose.ogg')
        self.destroyAttackGUI()
        self.prop = BP.globalPropPool.getProp(prop)

        def throwProp():
            base.localAvatar.headsUp(self.gufawToon)
            self.prop.setScale(4)
            self.prop.wrtReparentTo(render)
            hitPos = self.gufawToon.getPos() + Vec3(0, 0, 2.5)
            distance = (self.prop.getPos() - hitPos).length()
            speed = 50.0
            Sequence(self.prop.posInterval(distance / speed, hitPos), Func(self.prop.removeNode), Wait(1), Func(base.localAvatar.suit.loop, 'neutral')).start()

        def toonSad():
            self.normalMusic = base.loader.loadMusic('phase_9/audio/bgm/encntr_suit_HQ_nbrhood.ogg')
            seq = Sequence(self.gufawToon.head.hprInterval(1, (0, 0, 0)), Func(self.gufawToon.sadEyes), Wait(1), Func(self.gufawToon.play, 'lose'), Wait(2), Func(base.playSfx, sfxSad, volume=0.6), Wait(2.8), Func(base.playMusic, self.normalMusic, looping=1, volume=1.1), Func(base.localAvatar.setPosHpr, 21.43, 13.009, 0.025, 130.223, 0, 0), Func(base.localAvatar.displayTalk, "I'll have to complain to the Money Bags about this."), Func(base.localAvatar.attachCamera), Func(base.localAvatar.initializeSmartCamera), Func(base.localAvatar.startUpdateSmartCamera), Func(base.localAvatar.enableAvatarControls), self.gufawToon.scaleInterval(1.5, VBase3(0.01, 0.01, 0.01), blendType='easeInOut'), Func(self.gufawToon.removeActive), Func(base.transitions.letterboxOff)).start()

        track = Sequence(Parallel(ActorInterval(base.localAvatar.suit, 'throw-paper'), Track((
         0.4, Func(self.prop.reparentTo, base.localAvatar.suit.getRightHand())), (
         0.0, Func(self.prop.setPosHpr, -0.07, 0.17, -0.13, 161.867, -33.149, -48.086)), (
         2.6, Func(throwProp)), (
         1.0, Func(toonSad)))))
        return track

    def onClickNewspaper(self):
        self.attackSeq = self.launchProp('newspaper')
        self.attackSeq.start()

    def onClickBowtie(self):
        self.attackSeq = self.launchProp('power-tie')
        self.attackSeq.start()

    def onClickRedtape(self):
        self.attackSeq = self.launchProp('redtape')
        self.attackSeq.start()

    def setupAttackGUI(self):
        pieScale = 0.2
        guiNews = loader.loadModel('phase_3.5/models/gui/stickerbook_gui')
        guiBow = loader.loadModel('phase_3.5/models/gui/stickerbook_gui')
        guiTape = loader.loadModel('phase_3.5/models/gui/stickerbook_gui')
        self.buttonModels = loader.loadModel('phase_3.5/models/gui/inventory_gui')
        self.buttonModels.setScale(2)
        self.upButton = self.buttonModels.find('**/InventoryButtonUp')
        self.downButton = self.buttonModels.find('**/InventoryButtonDown')
        self.rolloverButton = self.buttonModels.find('**/InventoryButtonRollover')
        newspaperGui = guiNews.find('**/summons')
        newspaperTex = loader.loadTexture('phase_3.5/maps/newspaperGUI.png')
        newspaperTs = newspaperGui.findTextureStage('*')
        newspaperGui.setTexture(newspaperTs, newspaperTex, 1)
        newspaperGui.setTransparency(1)
        bowtieGui = guiBow.find('**/summons')
        bowtieTex = loader.loadTexture('phase_3.5/maps/bowtieGUI.png')
        bowtieTs = bowtieGui.findTextureStage('*')
        bowtieGui.setTexture(bowtieTs, bowtieTex, 1)
        bowtieGui.setTransparency(1)
        redtapeGui = guiTape.find('**/summons')
        redtapeTex = loader.loadTexture('phase_3.5/maps/redtapeGUI.png')
        redtapeTs = redtapeGui.findTextureStage('*')
        redtapeGui.setTexture(redtapeTs, redtapeTex, 1)
        redtapeGui.setTransparency(1)
        self.newspaperButton = DirectButton(image=(self.upButton, self.downButton, self.rolloverButton), geom=newspaperGui, image_scale=2, text='', text_scale=0.04, text_align=TextNode.ARight, geom_scale=pieScale, geom_pos=(-0.01,
                                                                                                                                                                                                                                0,
                                                                                                                                                                                                                                0), text_fg=Vec4(1, 1, 1, 1), text_pos=(0.07,
                                                                                                                                                                                                                                                                        -0.04), relief=None, image_color=(0,
                                                                                                                                                                                                                                                                                                          0.6,
                                                                                                                                                                                                                                                                                                          1,
                                                                                                                                                                                                                                                                                                          1), pos=(0,
                                                                                                                                                                                                                                                                                                                   0.1,
                                                                                                                                                                                                                                                                                                                   0.69), command=self.onClickNewspaper)
        self.newspaperButton.setColorScale(1, 1, 1, 0)
        self.bowtieButton = DirectButton(image=(self.upButton, self.downButton, self.rolloverButton), geom=bowtieGui, image_scale=2, text='', text_scale=0.04, text_align=TextNode.ARight, geom_scale=pieScale, geom_pos=(-0.01,
                                                                                                                                                                                                                          0,
                                                                                                                                                                                                                          0), text_fg=Vec4(1, 1, 1, 1), text_pos=(0.07,
                                                                                                                                                                                                                                                                  -0.04), relief=None, image_color=(0,
                                                                                                                                                                                                                                                                                                    0.6,
                                                                                                                                                                                                                                                                                                    1,
                                                                                                                                                                                                                                                                                                    1), pos=(0.45,
                                                                                                                                                                                                                                                                                                             0.1,
                                                                                                                                                                                                                                                                                                             0.69), command=self.onClickBowtie)
        self.bowtieButton.setColorScale(1, 1, 1, 0)
        self.redtapeButton = DirectButton(image=(self.upButton, self.downButton, self.rolloverButton), geom=redtapeGui, image_scale=2, text='', text_scale=0.04, text_align=TextNode.ARight, geom_scale=pieScale, geom_pos=(-0.01,
                                                                                                                                                                                                                            0,
                                                                                                                                                                                                                            0), text_fg=Vec4(1, 1, 1, 1), text_pos=(0.07,
                                                                                                                                                                                                                                                                    -0.04), relief=None, image_color=(0,
                                                                                                                                                                                                                                                                                                      0.6,
                                                                                                                                                                                                                                                                                                      1,
                                                                                                                                                                                                                                                                                                      1), pos=(-0.45,
                                                                                                                                                                                                                                                                                                               0.1,
                                                                                                                                                                                                                                                                                                               0.69), command=self.onClickRedtape)
        self.redtapeButton.setColorScale(1, 1, 1, 0)
        fadeIn = Sequence(Wait(2), Parallel(self.newspaperButton.colorScaleInterval(2, (1,
                                                                                        1,
                                                                                        1,
                                                                                        1)), self.bowtieButton.colorScaleInterval(2, (1,
                                                                                                                                      1,
                                                                                                                                      1,
                                                                                                                                      1)), self.redtapeButton.colorScaleInterval(2, (1,
                                                                                                                                                                                     1,
                                                                                                                                                                                     1,
                                                                                                                                                                                     1)))).start()
        return

    def destroyAttackGUI(self):
        self.newspaperButton.destroy()
        self.bowtieButton.destroy()
        self.redtapeButton.destroy()

    def enter(self, slowWalk=0):
        base.localAvatar.startPosHprBroadcast()
        base.localAvatar.startBlink()

        def trapAll():
            trapInterval = self.trapCog()
            trapInterval.start()

        if base.localAvatar.cameraFollow == 69:
            self.laffMeter = base.localAvatar.laffMeter
            self.book = base.localAvatar.book.bookOpenButton
            self.intMusic = base.loader.loadMusic('phase_8/audio/bgm/DG_SZ_activity_retro.ogg')
            self.jumpOver = Sequence(Func(base.localAvatar.loop, 'jump'), base.localAvatar.posHprInterval(1.4, (0,
                                                                                                                14,
                                                                                                                3), (-180,
                                                                                                                     0,
                                                                                                                     0)), Func(base.localAvatar.loop, 'neutral'), Func(base.localAvatar.enableAvatarControls))
            self.seq = Sequence(Func(base.camera.wrtReparentTo, render), Func(base.localAvatar.stopUpdateSmartCamera), Func(base.localAvatar.shutdownSmartCamera), Func(base.playMusic, self.intMusic, looping=1, volume=1.1), Func(base.localAvatar.disableAvatarControls), Func(NodePath(self.laffMeter).hide), Func(NodePath(base.marginManager).hide), Func(NodePath(self.book).hide), Func(base.localAvatar.invPage.ignoreOnscreenHooks), Func(base.localAvatar.questPage.ignoreOnscreenHooks), Func(base.localAvatar.setPos, 0, 24.22, 0.025), Func(base.localAvatar.setHpr, -180, 0, 0), Func(base.camera.setPosHpr, 0, 9.616, 3, 0, 0, 0), Wait(1), Func(base.localAvatar.displayTalk, 'Boy, what a workout!'), Wait(6), Func(base.localAvatar.displayTalk, "Darn, looks like I'm nearly out of those squirting flowers I was training with..."), Wait(8), Func(base.localAvatar.displayTalk, "I'll go see my buddy Herb back in the Playground for some!"), Wait(4), Func(self.jumpOver.start), base.camera.posHprInterval(0.569, (0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            3), (0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 0), blendType='noBlend'), Func(NodePath(base.marginManager).show), Func(base.localAvatar.attachCamera), Func(base.localAvatar.initializeSmartCamera), Func(base.localAvatar.startUpdateSmartCamera), Func(self.resetCameraFollow), Wait(5))
            self.seq.start()
        else:
            if base.localAvatar.zoneId == ToontownGlobals.ToontownCentral and base.cr.currentEpisode == 'gyro_tale':
                base.localAvatar.collisionsOff()
                base.localAvatar.brickLay('toontowncentral')
                self.fakeElections = FakeElections.FakeElections()
                evSeq = Sequence(Func(base.localAvatar.sendUpdate, 'startGyroPt1Ev', []), Func(base.localAvatar.disableAvatarControls), Func(base.localAvatar.setPos, 0, 0, 0), Func(NodePath(base.localAvatar.laffMeter).hide), Func(base.localAvatar.disableSleeping), Func(NodePath(base.marginManager).hide), Func(base.localAvatar.chatMgr.obscure, 1, 1), Func(base.localAvatar.invPage.ignoreOnscreenHooks), Func(base.localAvatar.questPage.ignoreOnscreenHooks), Func(self.fakeElections.generate), Wait(136.3), Func(self.oakStreetTeleport), Func(NodePath(base.localAvatar.laffMeter).hide), Wait(4), Func(self.fakeElections.disable), Func(base.localAvatar.attachCamera), Func(base.localAvatar.initializeSmartCamera), Func(base.localAvatar.startUpdateSmartCamera))
                evSeq.start()
            else:
                if base.localAvatar.zoneId == ToontownGlobals.CashbotHQ and base.cr.currentEpisode == 'short_work':
                    base.localAvatar.collisionsOff()
                    base.transitions.letterboxOn()
                    evSeq = Sequence(Func(base.localAvatar.disableAvatarControls), Func(base.localAvatar.setPos, 999, 999, 0), Func(NodePath(base.localAvatar.laffMeter).hide), Func(base.localAvatar.disableSleeping), Func(NodePath(base.marginManager).hide), Func(base.localAvatar.chatMgr.obscure, 1, 1), Func(base.localAvatar.invPage.ignoreOnscreenHooks), Func(base.localAvatar.questPage.ignoreOnscreenHooks), Func(base.camera.setPosHpr, 170.877, -250, -60, 30, 15, 0), Wait(3), base.camera.posHprInterval(10, (110,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              -250,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              -20), (0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     12,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     0), blendType='easeInOut'), Wait(0.69), base.camera.posHprInterval(5.69, (110,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               150,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               -20), (0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      12,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      0), blendType='easeInOut'), base.camera.posHprInterval(2, (110,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 190,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 -20), (69,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        28,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        0), blendType='easeInOut'), Wait(0.3), Func(self.prepareFadeout), base.camera.posHprInterval(6.9, (-260,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           345,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           320), (85,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  28,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  0), blendType='easeOut'), Func(base.localAvatar.attachCamera), Func(base.localAvatar.initializeSmartCamera), Func(base.localAvatar.startUpdateSmartCamera))
                    evSeq.start()
                else:
                    if base.localAvatar.zoneId == ToontownGlobals.CashbotShortChangeOffice and base.cr.currentEpisode == 'short_work' and not base.cr.doneInitialHighriseEnter:
                        base.cr.doneInitialHighriseEnter = True
                        base.localAvatar.setPlayerType(3, True)
                        evSeq = Sequence(Func(base.camera.wrtReparentTo, render), Func(base.localAvatar.stopUpdateSmartCamera), Func(base.localAvatar.shutdownSmartCamera), Func(base.localAvatar.disableAvatarControls), Func(base.localAvatar.setPos, -1, 19, 1), Func(base.localAvatar.suit.loop, 'sit'), Func(NodePath(base.localAvatar.laffMeter).hide), Func(base.localAvatar.disableSleeping), Func(NodePath(base.marginManager).hide), Func(base.localAvatar.chatMgr.obscure, 1, 1), Func(base.localAvatar.invPage.ignoreOnscreenHooks), Func(base.localAvatar.questPage.ignoreOnscreenHooks), Func(base.camera.setPosHpr, 6, 10, 3, 40, 14, 0), Wait(3), Func(base.localAvatar.displayTalk, 'This will be a short-term assignment.'), Wait(4.5), Func(base.localAvatar.displayTalk, 'Hmmph? It appears to be my lunch break.'), Wait(5.5), Func(base.localAvatar.displayTalk, "About time. I've needed an oil change all day."), Wait(6), Func(base.localAvatar.displayTalk, "Let's make this a short stop."), Wait(4), Func(self.doShortChangeLeave), Wait(1.3), Func(base.localAvatar.attachCamera), Func(base.localAvatar.initializeSmartCamera), Func(base.localAvatar.startUpdateSmartCamera), Wait(7.7), Func(base.localAvatar.enableAvatarControls), Func(base.transitions.letterboxOff))
                        evSeq.start()
                    else:
                        if base.localAvatar.zoneId == ToontownGlobals.CashbotBathroom and base.cr.currentEpisode == 'short_work' and not base.cr.doneInitialBathroomEnter:
                            self.gufawToon = ToontownAvatarUtils.createToon(2126, -2.704, -5.247, 0.057, 112.761, 0, 0)
                            self.scrambleMusic = base.loader.loadMusic('phase_14.5/audio/bgm/HR_bathroom.ogg')
                            base.cr.doneInitialBathroomEnter = True
                            base.cr.cameFromBathroom = True
                            base.transitions.letterboxOn()
                            evSeq = Sequence(Func(base.camera.wrtReparentTo, render), Func(base.localAvatar.stopUpdateSmartCamera), Func(base.localAvatar.shutdownSmartCamera), Func(base.playMusic, self.scrambleMusic, looping=1, volume=1.1), Func(base.localAvatar.disableAvatarControls), Func(base.localAvatar.disableSleeping), Func(base.localAvatar.invPage.ignoreOnscreenHooks), Func(base.localAvatar.questPage.ignoreOnscreenHooks), Func(base.camera.setPosHpr, 27, 30, 4.5, 150, 0, 0), Wait(1), Func(base.localAvatar.setPosHpr, 25.481, 16.85, 0.057, 131.2, 0, 0), Func(base.localAvatar.displayTalk, 'A Toon?!'), Wait(3), Func(self.gufawToon.setChatAbsolute, "Hee Hee! How's it hanging, greedy Short Change?", CFSpeech | CFTimeout), Func(self.gufawToon.loop, 'walk'), self.gufawToon.hprInterval(1, (-50,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              0)), Func(self.gufawToon.loop, 'neutral'), Func(self.doLaugh), Wait(2), Func(trapAll), Func(base.localAvatar.displayTalk, 'What are you doing with that?! No jokes allowed!'), Wait(3), Parallel(ActorInterval(base.localAvatar.suit, 'slip-backward'), Func(base.localAvatar.takeDamage, 3), Func(base.localAvatar.setHp, 10)), Func(base.localAvatar.suit.loop, 'neutral'), Wait(1), Func(base.localAvatar.displayTalk, 'Arrrgh! Pesky Toon!'), Wait(2), Wait(2), Func(base.localAvatar.setChatAbsolute, 'What should I do?', CFThought | CFTimeout), Wait(1), Func(base.transitions.letterboxOff), Func(self.setupAttackGUI)).start()
                        else:
                            if base.localAvatar.zoneId == ToontownGlobals.CashbotHighriseHallway and base.cr.currentEpisode == 'short_work':
                                if base.cr.cameFromBathroom:
                                    spawnSeq = Sequence(Wait(1), Func(base.localAvatar.invPage.ignoreOnscreenHooks), Func(base.localAvatar.questPage.ignoreOnscreenHooks), Func(base.localAvatar.attachCamera), Func(base.localAvatar.initializeSmartCamera), Func(base.localAvatar.startUpdateSmartCamera), Func(base.localAvatar.setPosHpr, 7.347, -28.835, 0.025, -270, 0, 0)).start()
                                else:
                                    if base.cr.cameFromBar:
                                        spawnSeq = Sequence(Wait(1), Func(base.localAvatar.invPage.ignoreOnscreenHooks), Func(base.localAvatar.questPage.ignoreOnscreenHooks), Func(base.localAvatar.attachCamera), Func(base.localAvatar.initializeSmartCamera), Func(base.localAvatar.startUpdateSmartCamera), Func(base.localAvatar.setPosHpr, 1.793, -43.274, 0.025, 0, 0, 0)).start()
                                    else:
                                        spawnSeq = Sequence(Wait(1), Func(base.localAvatar.invPage.ignoreOnscreenHooks), Func(base.localAvatar.questPage.ignoreOnscreenHooks), Func(base.localAvatar.attachCamera), Func(base.localAvatar.initializeSmartCamera), Func(base.localAvatar.startUpdateSmartCamera), Func(base.localAvatar.setPosHpr, 0, 42, 0, -180, 0, 0)).start()
                                base.cr.cameFromBar = False
                                base.cr.cameFromBathroom = False
                            else:
                                if base.localAvatar.zoneId == ToontownGlobals.CashbotBar and base.cr.currentEpisode == 'short_work':
                                    base.cr.cameFromBar = True
                                    spawnSeq = Sequence(Wait(1), Func(base.localAvatar.invPage.ignoreOnscreenHooks), Func(base.localAvatar.questPage.ignoreOnscreenHooks), Func(base.localAvatar.attachCamera), Func(base.localAvatar.initializeSmartCamera), Func(base.localAvatar.startUpdateSmartCamera)).start()
                                else:
                                    base.localAvatar.attachCamera()
                                    shouldPush = 1
                                    if len(base.localAvatar.cameraPositions) > 0:
                                        shouldPush = not base.localAvatar.cameraPositions[base.localAvatar.cameraIndex][4]
                                    base.localAvatar.startUpdateSmartCamera(shouldPush)
        base.localAvatar.showName()
        base.localAvatar.collisionsOn()
        base.localAvatar.startGlitchKiller()
        base.localAvatar.enableAvatarControls()

    def exit(self):
        self.fsm.request('off')
        self.ignore('control')
        base.localAvatar.disableAvatarControls()
        base.localAvatar.stopUpdateSmartCamera()
        base.localAvatar.stopPosHprBroadcast()
        base.localAvatar.stopBlink()
        base.localAvatar.detachCamera()
        base.localAvatar.stopGlitchKiller()
        base.localAvatar.collisionsOff()
        base.localAvatar.controlManager.placeOnFloor()

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterWalking(self):
        if base.localAvatar.hp > 0:
            base.localAvatar.startTrackAnimToSpeed()
            base.localAvatar.setWalkSpeedNormal()
        else:
            self.fsm.request('slowWalking')

    def exitWalking(self):
        base.localAvatar.stopTrackAnimToSpeed()

    def setSwimSoundAudible(self, isSwimSoundAudible):
        self.isSwimSoundAudible = isSwimSoundAudible
        if isSwimSoundAudible == 0 and self.swimSoundPlaying:
            self.swimSound.stop()
            self.swimSoundPlaying = 0

    def enterSwimming(self, swimSound):
        base.localAvatar.setWalkSpeedNormal()
        self.swimSound = swimSound
        self.swimSoundPlaying = 0
        base.localAvatar.b_setAnimState('swim', base.localAvatar.animMultiplier)
        base.localAvatar.startSleepSwimTest()
        taskMgr.add(self.__swim, 'localToonSwimming')

    def exitSwimming(self):
        taskMgr.remove('localToonSwimming')
        self.swimSound.stop()
        del self.swimSound
        self.swimSoundPlaying = 0
        base.localAvatar.stopSleepSwimTest()

    def __swim(self, task):
        speed = base.localAvatar.controlManager.get('swim').vel
        if speed == 0 and self.swimSoundPlaying:
            self.swimSoundPlaying = 0
            self.swimSound.stop()
        else:
            if not self.swimSoundPlaying and self.isSwimSoundAudible:
                self.swimSoundPlaying = 1
                base.playSfx(self.swimSound, looping=1)
        return Task.cont

    def enterSlowWalking(self):
        self.accept(base.localAvatar.uniqueName('positiveHP'), self.__handlePositiveHP)
        base.localAvatar.startTrackAnimToSpeed()
        base.localAvatar.setWalkSpeedSlow()

    def __handlePositiveHP(self):
        self.fsm.request('walking')

    def exitSlowWalking(self):
        base.localAvatar.stopTrackAnimToSpeed()
        self.ignore(base.localAvatar.uniqueName('positiveHP'))