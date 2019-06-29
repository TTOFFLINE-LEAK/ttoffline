from direct.distributed.ClockDelta import *
from direct.distributed.DistributedObject import DistributedObject
from direct.fsm.FSM import FSM
from direct.interval.IntervalGlobal import *
from panda3d.core import *
from otp.margins.WhisperPopup import *
from toontown.toon import NPCToons
from toontown.toonbase import ToontownGlobals

class DistributedPrologue3Event(DistributedObject, FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPrologue3Event')

    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        FSM.__init__(self, 'Prologue3EventFSM')
        self.cr.prologue3Event = self
        self.laffMeter = base.localAvatar.laffMeter
        self.book = base.localAvatar.book.bookOpenButton
        self.book2 = base.localAvatar.book.bookCloseButton
        self.geom = base.cr.playGame.hood.loader.geom
        self.newsky = loader.loadModel('phase_8/models/props/DL_sky')
        self.newsky.setBin('background', 100)
        self.newsky.setColor(0.3, 0.3, 0.28, 1)
        self.newsky.setTransparency(TransparencyAttrib.MDual, 1)
        self.newsky.setDepthTest(0)
        self.newsky.setDepthWrite(0)
        self.newsky.setFogOff()
        self.newsky.setZ(-20.0)
        ce = CompassEffect.make(NodePath(), CompassEffect.PRot | CompassEffect.PZ)
        self.newsky.node().setEffect(ce)
        self.fadeIn = self.newsky.colorScaleInterval(50.0, Vec4(1, 1, 1, 1), startColorScale=Vec4(1, 1, 1, 0), blendType='easeInOut')
        self.newSkyBegin = LerpColorScaleInterval(self.geom, 45.0, Vec4(0.4, 0.4, 0.4, 1), blendType='easeInOut')
        self.beginSkySequence = Sequence(Func(self.fadeIn.start), Func(self.newSkyBegin.start))
        self.fadeIn2 = self.newsky.colorScaleInterval(0.5, Vec4(1, 1, 1, 1), startColorScale=Vec4(1, 1, 1, 0), blendType='easeInOut')
        self.newSkyBegin2 = LerpColorScaleInterval(self.geom, 0.5, Vec4(0.4, 0.4, 0.4, 1), blendType='easeInOut')
        self.beginSkySequence2 = Sequence(Func(self.fadeIn2.start), Func(self.newSkyBegin2.start))
        base.localAvatar.cameraFollow = 2
        self.cog = None
        self.dimm = None
        self.prepostera = None
        self.warn = None
        return

    def enterOff(self, offset):
        pass

    def exitOff(self):
        pass

    def __cleanupNPCs(self):
        npcs = [
         self.dimm, self.prepostera]
        for npc in npcs:
            if npc:
                npc.removeActive()
                npc.hide()

    def delete(self):
        self.demand('Off', 0.0)
        self.ignore('entercnode')
        self.newsky.removeNode()
        del self.newsky
        self.__cleanupNPCs()
        DistributedObject.delete(self)

    def resetCameraFollow(self):
        base.localAvatar.cameraFollow = 0

    def enterIdle(self, offset):
        pass

    def exitIdle(self):
        pass

    def resetSquirtingAttributes(self):
        base.localAvatar.cameraFollow = 0
        base.cr.loadingStuff = 0

    def sendback(self):
        base.localAvatar.sendUpdate('resetEpisodeFlags')
        self.resetSquirtingAttributes()
        base.cr.inEpisode = False
        base.cr.currentEpisode = None
        base.localAvatar.cameraFollow = 0
        base.cr._userLoggingOut = True
        if base.cr.timeManager:
            base.cr.timeManager.setDisconnectReason(ToontownGlobals.DisconnectBookExit)
        base.transitions.fadeScreen(1.0)
        base.cr.gameFSM.request('closeShard')
        return

    def doCogStuff(self):
        self.cog = base.cr.doFind('Mover & Shaker') or base.cr.doFind('Glad Hander')
        self.extMusic = base.loader.loadMusic('phase_14.5/audio/bgm/SE_stinger_cogs_2.ogg')
        self.sfxGrunt = loader.loadSfx('phase_3.5/audio/dial/COG_VO_murmur.ogg')
        self.doTheStuff = Sequence(Func(base.camera.wrtReparentTo, self.cog), Func(base.localAvatar.stopUpdateSmartCamera), Func(base.localAvatar.shutdownSmartCamera), Func(base.playMusic, self.extMusic, looping=1, volume=1.1), Func(base.camera.setPosHpr, 0, 15, 5, -180, 0, 0), Wait(3), Func(self.makeCogTalk, "Offhandedly, I'd say you're in trouble."), Func(base.playSfx, self.sfxGrunt, volume=1.69), Wait(6), Func(base.localAvatar.setPos, -256.65, 230.751, 0.025), Func(base.localAvatar.setHpr, 153.823, 0, 0), Func(base.localAvatar.attachCamera), Func(base.localAvatar.initializeSmartCamera), Func(base.localAvatar.startUpdateSmartCamera), Func(base.localAvatar.displayTalk, "Great big weights, what's that?!"), Wait(5), Func(base.localAvatar.enableAvatarControls), Func(base.localAvatar.displayTalk, 'Trouble, eh? Get out of my Town, you greasy Robot!'))
        self.doTheStuff.start()

    def enterEvent(self, offset):
        base.localAvatar.disableSleeping()
        base.localAvatar.invPage.ignoreOnscreenHooks()
        base.localAvatar.questPage.ignoreOnscreenHooks()
        self.hideTunnel()
        self.eventInterval = Sequence(Wait(2), Func(NodePath(self.book).hide), Func(NodePath(self.laffMeter).hide), Func(base.localAvatar.obscureFriendsListButton, 1), Func(base.localAvatar.hideClarabelleGui), Func(base.localAvatar.invPage.ignoreOnscreenHooks), Func(base.localAvatar.questPage.ignoreOnscreenHooks), Func(self.newsky.reparentTo, camera), Func(self.beginSkySequence.start), Wait(6), Func(self.resetCameraFollow), Wait(8), Func(base.localAvatar.displayTalk, "Sure is smoggy around 'ere. The skies are getting darker too!"))
        self.handleCoachZ = Sequence(Func(self.newsky.reparentTo, camera), Func(self.beginSkySequence2.start), Wait(2), Func(NodePath(self.book).hide), Func(base.localAvatar.obscureFriendsListButton, 1), Func(base.localAvatar.hideClarabelleGui), Func(base.localAvatar.invPage.ignoreOnscreenHooks), Func(base.localAvatar.questPage.ignoreOnscreenHooks), Func(NodePath(base.marginManager).hide), Func(self.newsky.reparentTo, camera), Func(self.beginSkySequence2.start), Func(base.localAvatar.displayTalk, "What's going on?"), Wait(3), Func(base.localAvatar.disableAvatarControls), Func(self.doCogStuff))
        self.handleGyro = Sequence(Func(self.newsky.reparentTo, camera), Func(self.beginSkySequence2.start), Func(base.localAvatar.brickLay, 'daisygardens'), Wait(2), Func(base.localAvatar.disableAvatarControls), Func(base.localAvatar.invPage.ignoreOnscreenHooks), Func(base.localAvatar.questPage.ignoreOnscreenHooks), Func(base.localAvatar.stopUpdateSmartCamera), Func(base.localAvatar.shutdownSmartCamera), Func(base.camera.wrtReparentTo, base.localAvatar), Func(base.camera.setPosHpr, 0, 15, 3, 180, 0, 0), Func(base.localAvatar.setPosHpr, 15.242, 102.481, -0.475, 45.352, 0, 0), Wait(1), Func(base.localAvatar.loop, 'run'), Func(base.localAvatar.displayTalk, 'Oh no, why is it all dark now?'), base.localAvatar.posHprInterval(6, (-22.985,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              140.242,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              -0.475), (45.352,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        0)), Func(base.localAvatar.loop, 'neutral'), Func(base.localAvatar.brickLay, 'none'), Func(base.localAvatar.attachCamera), Func(base.localAvatar.initializeSmartCamera), Func(base.localAvatar.startUpdateSmartCamera), Func(base.localAvatar.enableAvatarControls))
        if base.cr.currentEpisode == 'prologue':
            self.eventInterval.start()
            self.eventInterval.setT(offset)
        if base.cr.currentEpisode == 'squirting_flower':
            self.handleCoachZ.start()
            self.handleCoachZ.setT(offset)
        if base.cr.currentEpisode == 'gyro_tale':
            self.handleGyro.start()
            self.handleGyro.setT(offset)
            self.dimm = NPCToons.createLocalNPC(2018)
            self.dimm.useLOD(1000)
            self.dimm.head = self.dimm.find('**/__Actor_head')
            self.dimm.initializeBodyCollisions('toon')
            self.dimm.setPosHpr(-322.91, 295.469, -0.284, 216.599, 0, 0)
            self.dimm.reparentTo(render)
            self.dimm.loop('neutral')
            self.dimm.addActive()
            self.prepostera = NPCToons.createLocalNPC(2020)
            self.prepostera.useLOD(1000)
            self.prepostera.head = self.prepostera.find('**/__Actor_head')
            self.prepostera.initializeBodyCollisions('toon')
            self.prepostera.setPosHpr(-325.829, 292.584, -0.284, 216.599, 0, 0)
            self.prepostera.setScale(1.2)
            self.prepostera.reparentTo(render)
            self.prepostera.loop('neutral')
            self.prepostera.addActive()
            self.warn = Sequence(Wait(15), Func(self.prepostera.setChatAbsolute, 'Gyro, the Robot has gone bonkers!', CFSpeech | CFTimeout), Wait(6.9), Func(self.dimm.setChatAbsolute, "Don't go inside- it has Scrooge!", CFSpeech | CFTimeout), Wait(10))
            self.warn.loop()

    def exitEvent(self):
        if base.cr.currentEpisode == 'prologue':
            self.eventInterval.finish()
        if base.cr.currentEpisode == 'squirting_flower':
            self.handleCoachZ.finish()
        if base.cr.currentEpisode == 'gyro_tale':
            self.handleGyro.finish()
            self.warn.finish()

    def enterEventTwo(self, offset):
        pass

    def exitEventTwo(self):
        pass

    def setState(self, state, timestamp):
        self.request(state, globalClockDelta.localElapsedTime(timestamp))

    def hideTunnel(self):
        self.geom = base.cr.playGame.hood.loader.geom
        tunnel = self.geom.find('**/linktunnel_odg_21000_DNARoot')
        if tunnel:
            tunnel.reparentTo(hidden)
        dummyTunnel = self.geom.find('**/prop_odg_dummy')
        if dummyTunnel:
            dummyTunnel.reparentTo(self.geom)

    def makeCogTalk(self, text):
        cog = base.cr.doFind('Mover & Shaker') or base.cr.doFind('Glad Hander')
        if cog:
            cog.displayTalk(text)