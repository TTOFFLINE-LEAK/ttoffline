import datetime
from direct.distributed.ClockDelta import *
from direct.distributed.DistributedObject import DistributedObject
from direct.fsm.FSM import FSM
from direct.gui.OnscreenText import OnscreenText
from direct.interval.IntervalGlobal import *
from panda3d.core import *
from otp.margins.WhisperPopup import *
from toontown.election import SafezoneInvasionGlobals
from toontown.electionsuit import DistributedSuitBase, SuitDNA
from toontown.hood import ZoneUtil
from toontown.suit import SuitDNA, Suit
from toontown.toon import NPCToons
from toontown.toonbase import TTLocalizer as TTL
from toontown.toonbase import ToontownGlobals

class DistributedPrologue2Event(DistributedObject, FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPrologue2Event')

    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        FSM.__init__(self, 'Prologue2EventFSM')
        self.cr.prologue2Event = self
        self.laffMeter = base.localAvatar.laffMeter
        self.book = base.localAvatar.book.bookOpenButton
        self.book2 = base.localAvatar.book.bookCloseButton
        self.rocky = NPCToons.createLocalNPC(14011)
        self.rocky.useLOD(1000)
        self.rocky.head = self.rocky.find('**/__Actor_head')
        self.rocky.initializeBodyCollisions('toon')
        self.rocky.setPosHpr(-53.317, 229.216, 10.015, -518, 0, 0)
        self.rocky.reparentTo(render)
        self.rocky.loop('neutral')
        self.rocky.addActive()
        self.logano = NPCToons.createLocalNPC(14006)
        self.logano.useLOD(1000)
        self.logano.head = self.logano.find('**/__Actor_head')
        self.logano.initializeBodyCollisions('toon')
        self.logano.setPosHpr(17.805, 25.009, 0.025, -102, 0, 0)
        self.logano.addActive()
        self.logano.startBlink()
        self.logano.reparentTo(render)
        self.logano.loop('neutral')
        self.logano.addActive()
        self.sparky = NPCToons.createLocalNPC(14007)
        self.sparky.useLOD(1000)
        self.sparky.head = self.sparky.find('**/__Actor_head')
        self.sparky.initializeBodyCollisions('toon')
        self.sparky.setPosHpr(-62, 213.407, 10.015, -422, 0, 0)
        self.sparky.reparentTo(render)
        self.sparky.loop('neutral')
        self.sparky.addActive()
        self.weird = NPCToons.createLocalNPC(14008)
        self.weird.useLOD(1000)
        self.weird.head = self.weird.find('**/__Actor_head')
        self.weird.initializeBodyCollisions('toon')
        self.weird.setPosHpr(-41.676, 229.239, 10.015, -602, 0, 0)
        self.weird.reparentTo(render)
        self.weird.loop('neutral')
        self.weird.addActive()
        self.ned = NPCToons.createLocalNPC(14009)
        self.ned.useLOD(1000)
        self.ned.head = self.ned.find('**/__Actor_head')
        self.ned.initializeBodyCollisions('toon')
        self.ned.setPosHpr(64.153, 74.389, 0.025, 87.9, 0, 0)
        self.ned.reparentTo(render)
        self.ned.loop('neutral')
        self.ned.addActive()
        self.supertricky = NPCToons.createLocalNPC(14010)
        self.supertricky.useLOD(1000)
        self.supertricky.head = self.supertricky.find('**/__Actor_head')
        self.supertricky.initializeBodyCollisions('toon')
        self.supertricky.setPosHpr(55.043, 158.484, 10.025, -15, 0, 0)
        self.supertricky.reparentTo(render)
        self.supertricky.loop('neutral')
        self.supertricky.addActive()
        self.loony = NPCToons.createLocalNPC(14012)
        self.loony.useLOD(1000)
        self.loony.head = self.loony.find('**/__Actor_head')
        self.loony.initializeBodyCollisions('toon')
        self.loony.setPosHpr(78.257, 165.554, 10.125, 44.5, 0, 0)
        self.loony.reparentTo(render)
        self.loony.loop('neutral')
        self.loony.addActive()
        self.ttmusician = NPCToons.createLocalNPC(14013)
        self.ttmusician.useLOD(1000)
        self.ttmusician.head = self.ttmusician.find('**/__Actor_head')
        self.ttmusician.initializeBodyCollisions('toon')
        self.ttmusician.setPosHpr(37.952, 208.329, 10.026, 106, 0, 0)
        self.ttmusician.reparentTo(render)
        self.ttmusician.loop('neutral')
        self.ttmusician.addActive()
        self.patrick = NPCToons.createLocalNPC(14014)
        self.patrick.useLOD(1000)
        self.patrick.head = self.patrick.find('**/__Actor_head')
        self.patrick.initializeBodyCollisions('toon')
        self.patrick.setPosHpr(-78.568, 163.722, 10.025, -415, 0, 0)
        self.patrick.reparentTo(render)
        self.patrick.loop('neutral')
        self.patrick.addActive()
        if base.cr.currentEpisode == 'prologue':
            self.ryno = NPCToons.createLocalNPC(14041)
        else:
            self.ryno = NPCToons.createLocalNPC(14035)
        self.ryno.useLOD(1000)
        self.ryno.head = self.ryno.find('**/__Actor_head')
        self.ryno.initializeBodyCollisions('toon')
        self.ryno.setPosHpr(-84.194, 91.382, 0.025, -119.567, 0, 0)
        self.ryno.reparentTo(render)
        self.ryno.loop('neutral')
        self.ryno.addActive()
        self.nickdoge = NPCToons.createLocalNPC(14036)
        self.nickdoge.useLOD(1000)
        self.nickdoge.head = self.nickdoge.find('**/__Actor_head')
        self.nickdoge.initializeBodyCollisions('toon')
        self.nickdoge.setPosHpr(48.7522, 209.507, 10.0246, -415, 0, 0)
        self.nickdoge.reparentTo(render)
        self.nickdoge.loop('neutral')
        self.nickdoge.addActive()
        self.bill = NPCToons.createLocalNPC(14038)
        self.bill.useLOD(1000)
        self.bill.head = self.bill.find('**/__Actor_head')
        self.bill.initializeBodyCollisions('toon')
        self.bill.setPosHpr(-17.309, 20.2793, 0.025, -1115.69, 0, 0)
        self.bill.reparentTo(render)
        self.bill.loop('neutral')
        self.bill.addActive()
        self.cheeze = NPCToons.createLocalNPC(14037)
        self.cheeze.useLOD(1000)
        self.cheeze.head = self.cheeze.find('**/__Actor_head')
        self.cheeze.initializeBodyCollisions('toon')
        self.cheeze.setPosHpr(22.096, 15.248, 0.025, 15.288, 0, 0)
        self.cheeze.reparentTo(render)
        self.cheeze.loop('neutral')
        self.cheeze.addActive()
        self.swag = Suit.Suit()
        self.swag.dna = SuitDNA.SuitDNA()
        self.swag.dna.newSuit('sf')
        self.swag.setDNA(self.swag.dna)
        self.swag.setPickable(False)
        self.swag.addActive()
        self.swag.reparentTo(render)
        self.swag.setPosHpr(24.94, 226.835, 10.025, -180, 0, 0)
        self.swag.loop('neutral')
        self.swag.corpMedallion.reparentTo(hidden)
        self.collTube = CollisionTube(0, 0, 0.5, 0, 0, 4, 2)
        self.collNode = CollisionNode('suit')
        self.collNode.addSolid(self.collTube)
        self.collNodePath = self.swag.attachNewNode(self.collNode)
        self.doomsdayMusic = base.loader.loadMusic('phase_4/audio/bgm/DD_main_temp.ogg')
        cm = CardMaker('card')
        cm.setFrameFullscreenQuad()
        self.explosionCard = render2d.attachNewNode(cm.generate())
        self.explosionCard.setTransparency(1)
        self.explosionCard.setColorScale(0, 0, 0, 0)
        now = datetime.datetime.now()
        self.text = '%d years ago...' % (datetime.date.today().year - 2003)
        self.text2 = 'The Cogs invaded Toontown.'
        self.title = OnscreenText(text=self.text, pos=(0, 0.2), scale=0.15, font=ToontownGlobals.getSignFont(), fg=(1,
                                                                                                                    1,
                                                                                                                    1,
                                                                                                                    1), shadow=(0.1,
                                                                                                                                0.1,
                                                                                                                                0.1,
                                                                                                                                1))
        self.title.setColorScale(1, 1, 1, 0)
        self.title2 = OnscreenText(text=self.text2, pos=(0, -0.3), scale=0.15, font=ToontownGlobals.getSignFont(), fg=(1,
                                                                                                                       1,
                                                                                                                       1,
                                                                                                                       1), shadow=(0.1,
                                                                                                                                   0.1,
                                                                                                                                   0.1,
                                                                                                                                   1))
        self.title2.setColorScale(1, 1, 1, 0)
        self.namedropper = DistributedSuitBase.DistributedSuitBase(cr)
        self.namedropper.dna = SuitDNA.SuitDNA()
        self.namedropper.dna.newSuit('nd')
        self.namedropper.setDNA(self.namedropper.dna)
        self.namedropper.setDisplayName(TTL.SuitNameDropper + '\n' + TTL.Sellbot + '\n' + TTL.Level.title() + ' 3')
        self.namedropper.setPickable(0)
        self.namedropper.setPosHpr(0, 0, 0.025, 75.8, 0, 0)
        self.namedropper.doId = id(self.namedropper)
        self.namedropper.reparentTo(hidden)
        self.collTube = CollisionTube(0, 0, 0.5, 0, 0, 4, 2)
        self.collNode = CollisionNode('suit')
        self.collNode.addSolid(self.collTube)
        self.collNodePath = self.namedropper.attachNewNode(self.collNode)
        self.coldcaller = DistributedSuitBase.DistributedSuitBase(cr)
        self.coldcaller.dna = SuitDNA.SuitDNA()
        self.coldcaller.dna.newSuit('cc')
        self.coldcaller.setDNA(self.coldcaller.dna)
        self.coldcaller.setDisplayName(TTL.SuitColdCaller + '\n' + TTL.Sellbot + '\n' + TTL.Level.title() + ' 1')
        self.coldcaller.setPickable(0)
        self.coldcaller.setPosHpr(-42.771, 210, 10.015, -180, 0, 0)
        self.coldcaller.doId = id(self.coldcaller)
        self.coldcaller.reparentTo(hidden)
        self.collTube = CollisionTube(0, 0, 0.5, 0, 0, 4, 2)
        self.collNode = CollisionNode('suit')
        self.collNode.addSolid(self.collTube)
        self.collNodePath = self.coldcaller.attachNewNode(self.collNode)
        self.movershaker = DistributedSuitBase.DistributedSuitBase(cr)
        self.movershaker.dna = SuitDNA.SuitDNA()
        self.movershaker.dna.newSuit('ms')
        self.movershaker.setDNA(self.movershaker.dna)
        self.movershaker.setDisplayName(TTL.SuitMoverShaker + '\n' + TTL.Sellbot + '\n' + TTL.Level.title() + ' 5')
        self.movershaker.setPickable(0)
        self.movershaker.setPosHpr(-37.771, 210, 10.015, -180, 0, 0)
        self.movershaker.doId = id(self.movershaker)
        self.movershaker.reparentTo(hidden)
        self.collTube = CollisionTube(0, 0, 0.5, 0, 0, 4, 2)
        self.collNode = CollisionNode('suit')
        self.collNode.addSolid(self.collTube)
        self.collNodePath = self.movershaker.attachNewNode(self.collNode)
        self.mingler = DistributedSuitBase.DistributedSuitBase(cr)
        self.mingler.dna = SuitDNA.SuitDNA()
        self.mingler.dna.newSuit('m')
        self.mingler.setDNA(self.mingler.dna)
        self.mingler.setDisplayName(TTL.SuitTheMingler + '\n' + TTL.Sellbot + '\n' + TTL.Level.title() + ' 7')
        self.mingler.setPickable(0)
        self.mingler.setPosHpr(-47.771, 210, 10.015, -180, 0, 0)
        self.mingler.doId = id(self.mingler)
        self.mingler.reparentTo(hidden)
        self.collTube = CollisionTube(0, 0, 0.5, 0, 0, 4, 2)
        self.collNode = CollisionNode('suit')
        self.collNode.addSolid(self.collTube)
        self.collNodePath = self.mingler.attachNewNode(self.collNode)
        self.telemarketer = DistributedSuitBase.DistributedSuitBase(cr)
        self.telemarketer.dna = SuitDNA.SuitDNA()
        self.telemarketer.dna.newSuit('tm')
        self.telemarketer.setDNA(self.telemarketer.dna)
        self.telemarketer.setDisplayName(TTL.SuitTelemarketer + '\n' + TTL.Sellbot + '\n' + TTL.Level.title() + ' 2')
        self.telemarketer.setPickable(0)
        self.telemarketer.setPosHpr(0, 0, 0.015, -232.769, 0, 0)
        self.telemarketer.doId = id(self.telemarketer)
        self.telemarketer.reparentTo(hidden)
        self.collTube = CollisionTube(0, 0, 0.5, 0, 0, 4, 2)
        self.collNode = CollisionNode('suit')
        self.collNode.addSolid(self.collTube)
        self.collNodePath = self.telemarketer.attachNewNode(self.collNode)
        self.hollywood = DistributedSuitBase.DistributedSuitBase(cr)
        self.hollywood.dna = SuitDNA.SuitDNA()
        self.hollywood.dna.newSuit('mh')
        self.hollywood.setDNA(self.hollywood.dna)
        self.hollywood.setDisplayName(TTL.SuitMrHollywood + '\n' + TTL.Sellbot + '\n' + TTL.Level.title() + ' 8')
        self.hollywood.setPickable(0)
        self.hollywood.setPosHpr(0, 0, 0.015, -134.639, 0, 0)
        self.hollywood.doId = id(self.hollywood)
        self.hollywood.reparentTo(hidden)
        self.collTube = CollisionTube(0, 0, 0.5, 0, 0, 4, 2)
        self.collNode = CollisionNode('suit')
        self.collNode.addSolid(self.collTube)
        self.collNodePath = self.hollywood.attachNewNode(self.collNode)
        self.twoface = DistributedSuitBase.DistributedSuitBase(cr)
        self.twoface.dna = SuitDNA.SuitDNA()
        self.twoface.dna.newSuit('tf')
        self.twoface.setDNA(self.twoface.dna)
        self.twoface.setDisplayName(TTL.SuitTwoFace + '\n' + TTL.Sellbot + '\n' + TTL.Level.title() + ' 6')
        self.twoface.setPickable(0)
        self.twoface.setPosHpr(0, 0, 0.015, -126.153, 0, 0)
        self.twoface.doId = id(self.twoface)
        self.twoface.reparentTo(hidden)
        self.collTube = CollisionTube(0, 0, 0.5, 0, 0, 4, 2)
        self.collNode = CollisionNode('suit')
        self.collNode.addSolid(self.collTube)
        self.collNodePath = self.twoface.attachNewNode(self.collNode)
        self.geom = base.cr.playGame.hood.loader.geom
        self.sky = loader.loadModel(SafezoneInvasionGlobals.CogSkyFile)
        self.sky.setBin('background', 100)
        self.sky.setColor(0.3, 0.3, 0.28, 1)
        self.sky.setTransparency(TransparencyAttrib.MDual, 1)
        self.sky.setDepthTest(0)
        self.sky.setDepthWrite(0)
        self.sky.setFogOff()
        self.sky.setZ(-20.0)
        ce = CompassEffect.make(NodePath(), CompassEffect.PRot | CompassEffect.PZ)
        self.sky.node().setEffect(ce)
        self.fadeIn = self.sky.colorScaleInterval(5.0, Vec4(1, 1, 1, 1), startColorScale=Vec4(1, 1, 1, 0), blendType='easeInOut')
        self.cogSkyBegin = LerpColorScaleInterval(self.geom, 6.0, Vec4(0.4, 0.4, 0.4, 1), blendType='easeInOut')
        self.beginSkySequence = Sequence(Func(self.fadeIn.start), Func(self.cogSkyBegin.start))

    def enterOff(self, offset):
        pass

    def exitOff(self):
        pass

    def __cleanupNPCs(self):
        npcs = [
         self.rocky, self.logano, self.sparky, self.weird, self.ned, self.ttmusician, self.loony,
         self.supertricky, self.patrick, self.swag, self.ryno, self.nickdoge, self.bill, self.cheeze]
        for npc in npcs:
            if npc:
                npc.removeActive()
                npc.hide()

    def __cleanupSquirtingFlowerNPCs(self):
        npcs = [
         self.namedropper, self.coldcaller, self.movershaker, self.mingler, self.telemarketer, self.hollywood,
         self.twoface]
        for npc in npcs:
            if npc:
                npc.removeActive()
                npc.hide()

    def delete(self):
        self.demand('Off', 0.0)
        self.ignore('entercnode')
        self.__cleanupNPCs()
        DistributedObject.delete(self)

    def squirtingFlowerTeleport(self):
        hoodId = ZoneUtil.getTrueZoneId(21000, 21000)
        zoneId = ZoneUtil.getTrueZoneId(21821, 21000)
        how = 'teleportIn'
        tunnelOriginPlaceHolder = render.attachNewNode('toph_21000_21821')
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

    def enterIdle(self, offset):
        pass

    def exitIdle(self):
        pass

    def setCameraFollow(self):
        base.localAvatar.cameraFollow = 69
        base.cr.loadingStuff = 69

    def enterEvent(self, offset):
        base.localAvatar.disableSleeping()
        base.localAvatar.invPage.ignoreOnscreenHooks()
        base.localAvatar.questPage.ignoreOnscreenHooks()
        self.hideTunnel()
        self.ttmusicianWalkInterval = Sequence(Func(self.ttmusician.loop, 'walk'), self.ttmusician.posHprInterval(4, (15.188,
                                                                                                                      204.227,
                                                                                                                      10.026), (88,
                                                                                                                                0,
                                                                                                                                0)), self.ttmusician.posHprInterval(7, (-39.275,
                                                                                                                                                                        205.043,
                                                                                                                                                                        10.025), (88,
                                                                                                                                                                                  0,
                                                                                                                                                                                  0)), self.ttmusician.posHprInterval(1, (-39.275,
                                                                                                                                                                                                                          205.043,
                                                                                                                                                                                                                          10.025), (28,
                                                                                                                                                                                                                                    0,
                                                                                                                                                                                                                                    0)), self.ttmusician.posHprInterval(3, (-44.788,
                                                                                                                                                                                                                                                                            214.04,
                                                                                                                                                                                                                                                                            10.025), (43.3,
                                                                                                                                                                                                                                                                                      0,
                                                                                                                                                                                                                                                                                      0)), Func(self.ttmusician.loop, 'neutral'))
        self.ttmusicianWalk2Interval = Sequence(Func(self.ttmusician.loop, 'walk'), self.ttmusician.posHprInterval(1, (-39.275,
                                                                                                                       205.043,
                                                                                                                       10.025), (28,
                                                                                                                                 0,
                                                                                                                                 0)), self.ttmusician.posHprInterval(7, (-39.275,
                                                                                                                                                                         205.043,
                                                                                                                                                                         10.025), (88,
                                                                                                                                                                                   0,
                                                                                                                                                                                   0)), self.ttmusician.posHprInterval(4, (15.188,
                                                                                                                                                                                                                           204.227,
                                                                                                                                                                                                                           10.026), (88,
                                                                                                                                                                                                                                     0,
                                                                                                                                                                                                                                     0)), self.ttmusician.posHprInterval(3, (37.952,
                                                                                                                                                                                                                                                                             208.329,
                                                                                                                                                                                                                                                                             10.026), (106,
                                                                                                                                                                                                                                                                                       0,
                                                                                                                                                                                                                                                                                       0)), Func(self.ttmusician.loop, 'neutral'))
        self.eventInterval = Sequence(Wait(2), Func(NodePath(self.book).hide), Func(NodePath(self.laffMeter).hide), Func(base.localAvatar.obscureFriendsListButton, 1), Func(base.localAvatar.hideClarabelleGui), Func(base.localAvatar.invPage.ignoreOnscreenHooks), Func(base.localAvatar.questPage.ignoreOnscreenHooks), Wait(3), Func(base.localAvatar.displayTalk, "If I recall correctly, Gyro's Lab is located on Oak Street. Suppose I'll head on o'er then!"), Wait(8), Func(base.localAvatar.displayTalk, 'This here place needs some renovations. A nice fishing pond at this pool would do just nicely.'))
        self.eventInterval2 = Sequence(Wait(3), Func(self.sparky.setChatAbsolute, 'I sure do like me some Jazz.', CFSpeech | CFTimeout), Wait(7), Func(self.sparky.setChatAbsolute, 'Gayyyyygs.', CFSpeech | CFTimeout), Wait(7), Func(self.sparky.setChatAbsolute, 'Cawwwwwwgs.', CFSpeech | CFTimeout), Wait(7), Func(self.sparky.setChatAbsolute, 'Wow. These guys are silent.', CFThought | CFTimeout), Wait(7), Func(self.sparky.setChatAbsolute, "Hey guys. Wanna hear something these younglings call a, 'joke'?", CFSpeech | CFTimeout), Wait(7), Func(self.rocky.setChatAbsolute, 'No.', CFSpeech | CFTimeout), Func(self.weird.setChatAbsolute, 'No.', CFSpeech | CFTimeout), Wait(3), Func(self.sparky.setChatAbsolute, 'Wow, okay then. Sheesh.', CFSpeech | CFTimeout), Wait(5))
        self.eventInterval3 = Sequence(Wait(2), Func(self.patrick.setChatAbsolute, 'Ah, finally. Funny Farms 1.3.7 is now out.', CFThought | CFTimeout), Wait(5), Func(self.patrick.setChatAbsolute, 'I wonder what the Toon Construction is leading to.', CFThought | CFTimeout), Wait(7), Func(self.patrick.setChatAbsolute, 'I have so many ideas for the game, I cannot wait for everyone to see them.', CFThought | CFTimeout), Wait(7), Func(self.patrick.setChatAbsolute, "Although it's not much...", CFThought | CFTimeout), Wait(4), Func(self.patrick.setChatAbsolute, '...people seem to have appreciated it for what it is.', CFThought | CFTimeout), Wait(5), Func(self.patrick.setChatAbsolute, 'I wonder when I can get the next update out?', CFSpeech | CFTimeout), Wait(3), Func(self.patrick.setChatAbsolute, 'Who knows...', CFThought | CFTimeout), Wait(5))
        self.eventInterval4 = Sequence(Wait(12), Func(self.logano.setChatAbsolute, 'I like underwater habitats for sharks.', CFSpeech | CFTimeout), Wait(5), Func(self.logano.setChatAbsolute, "IT'S HIPSTER LOGANO HERE!", CFSpeech | CFTimeout), Wait(4.5), Func(self.logano.setChatAbsolute, 'What even is a Duck Hunt?', CFSpeech | CFTimeout), Wait(5.5), Func(self.logano.setChatAbsolute, "I am a random Toon, please don't mind me.", CFSpeech | CFTimeout), Wait(5.5), Func(self.logano.setChatAbsolute, 'I wonder what it feels like to go sad...', CFSpeech | CFTimeout), Wait(8))
        self.eventInterval5 = Sequence(Func(self.eventInterval2.start), Wait(2), Func(self.ttmusician.setChatAbsolute, 'Doot Ding Diddly Dop, Music Music.', CFSpeech | CFTimeout), Wait(4), Func(self.ttmusician.setChatAbsolute, 'Music music music music music.', CFThought | CFTimeout), Wait(5), Func(self.ttmusician.setChatAbsolute, 'Toontown Music.', CFThought | CFTimeout), Wait(5), Func(self.ttmusician.setChatAbsolute, 'Where can I search for some more Tunes?', CFSpeech | CFTimeout), Wait(5), Func(self.ttmusician.setChatAbsolute, 'Maybe there Toons will help me with some Tunes!', CFSpeech | CFTimeout), Wait(1), Func(self.ttmusicianWalkInterval.start), Wait(16), Func(self.ttmusician.setChatAbsolute, 'Do any of you Toons know where I can find some Tunes?', CFSpeech | CFTimeout), Wait(5), Func(self.ttmusician.setChatAbsolute, 'Welp. Better luck next time I suppose.', CFSpeech | CFTimeout), Wait(5), Func(self.ttmusicianWalk2Interval.start), Wait(16))
        self.nabil = Sequence(Wait(13), Func(self.loony.setChatAbsolute, 'helo helo.', CFSpeech | CFTimeout), Wait(7), Func(self.loony.setChatAbsolute, 'you want see?', CFSpeech | CFTimeout), Wait(8), Func(self.loony.setChatAbsolute, 'you want see my plastic pa-', CFSpeech | CFTimeout), Wait(9), Func(self.loony.setChatAbsolute, "Hey! That's not very Toony! I'll shut up now :(", CFSpeech | CFTimeout), Wait(9), Func(self.loony.setChatAbsolute, "Not like I've been terminated 20 times already...", CFSpeech | CFTimeout))
        self.infowars = Sequence(Wait(13), Func(self.bill.setChatAbsolute, 'You are fighting the war on information.', CFSpeech | CFTimeout), Wait(7), Func(self.bill.setChatAbsolute, "There's a war on for your mind!", CFSpeech | CFTimeout), Wait(9), Func(self.bill.setChatAbsolute, 'The pond water is turning the ducks untoony.', CFSpeech | CFTimeout), Wait(11), Func(self.bill.setChatAbsolute, 'TOONTOWN IS A HOLOGRAM!', CFSpeech | CFTimeout), Wait(16))
        self.cheezetalk = Sequence(Wait(13), Func(self.cheeze.setChatAbsolute, 'Remember that one time I hosted a mini-server?', CFSpeech | CFTimeout), Wait(7), Func(self.cheeze.setChatAbsolute, 'That was pretty fun.', CFSpeech | CFTimeout), Wait(9), Func(self.cheeze.setChatAbsolute, 'Have you ever seen a black dog with white clothes and black gloves running around?', CFSpeech | CFTimeout), Wait(11), Func(self.cheeze.setChatAbsolute, 'Wait I have black gloves too...', CFSpeech | CFTimeout), Wait(16))
        self.nocigars = Sequence(Wait(10), Func(self.swag.setChatAbsolute, "The trolley's broken, so I'm on break right now.", CFSpeech | CFTimeout), Wait(9), Func(self.swag.setChatAbsolute, 'Have you seen a short Lawbot driving an ambulance?', CFSpeech | CFTimeout), Wait(9), Func(self.swag.setChatAbsolute, 'They call me the foreman, because I have the strength of four men.', CFSpeech | CFTimeout), Wait(10), Func(self.swag.setChatAbsolute, 'Downsizer has a secret dancing passion.', CFSpeech | CFTimeout), Wait(9), Func(self.swag.setChatAbsolute, 'I might drive my golf kart later.', CFSpeech | CFTimeout), Wait(9), Func(self.swag.setChatAbsolute, 'I slept in too late, so Downsizer kicked me out of the house.', CFSpeech | CFTimeout), Wait(9), Func(self.swag.setChatAbsolute, 'Moles and cars are not a good combination.', CFSpeech | CFTimeout), Wait(25))
        self.dumbstupid = Sequence(Parallel(Func(self.ryno.loop, 'walk'), Sequence(self.ryno.posInterval(18.315, (5.506,
                                                                                                                  40.494,
                                                                                                                  0.025)), Func(self.ryno.loop, 'neutral')), Sequence(Func(self.ryno.setChatAbsolute, 'Hmm...', CFSpeech | CFTimeout), Func(self.ryno.findSomethingToLookAt), Wait(4), Func(self.ryno.setChatAbsolute, 'This is really cool thing for Offline to do.', CFSpeech | CFTimeout), Func(self.ryno.findSomethingToLookAt), Wait(7), Func(self.ryno.setChatAbsolute, 'Maybe I should bug Logano about adding Beta TTC.', CFSpeech | CFTimeout), Func(self.ryno.stopStareAt), Wait(7), Func(self.ryno.startStareAt, self.logano.head, None), Wait(1), Func(self.ryno.surpriseEyes), Func(self.ryno.setChatAbsolute, '...', CFSpeech | CFTimeout), Wait(5), Func(self.ryno.setChatAbsolute, 'Yea, probably not.', CFSpeech | CFTimeout), Func(self.ryno.normalEyes), Func(self.ryno.blinkEyes), Wait(1), Func(self.ryno.stopStareAt), Wait(3), Func(self.ryno.setChatAbsolute, 'ooo i should go to the elections', CFSpeech | CFTimeout), Wait(1), Func(self.ryno.animFSM.request, 'OpenBook', [1.0, 0, None]), Wait(0.3), Func(self.ryno.animFSM.request, 'ReadBook', [1.0, 0, None]), Wait(0.5), Func(self.ryno.animFSM.request, 'CloseBook', [1.0, 0, None]), Wait(1.54), Func(self.ryno.animFSM.request, 'CloseBook', [1.0, 0, None]), Func(self.ryno.animFSM.request, 'TeleportOut'), Wait(self.ryno.getDuration('teleport')), Func(self.ryno.reparentTo, hidden), Func(self.ryno.removeActive))))
        self.nickdogeSequence = Sequence(Func(self.nickdoge.findSomethingToLookAt), Func(self.nickdoge.setChatAbsolute, 'This is a really nice wall to look at.', CFSpeech | CFTimeout), Wait(5), Func(self.nickdoge.stopStareAt), Wait(0.5), Wait(1), Func(self.nickdoge.setChatAbsolute, "Oh hey! I didn't see you there!", CFSpeech | CFTimeout))
        ndFlyIn = self.namedropper.beginSupaFlyMove(VBase3(28.924, 22.418, 0.025), 1, 'flyIn', walkAfterLanding=False)
        ccFlyIn = self.coldcaller.beginSupaFlyMove(VBase3(-42.771, 210, 10.015), 1, 'flyIn', walkAfterLanding=False)
        msFlyIn = self.movershaker.beginSupaFlyMove(VBase3(-37.771, 210, 10.015), 1, 'flyIn', walkAfterLanding=False)
        mFlyIn = self.mingler.beginSupaFlyMove(VBase3(-47.771, 210, 10.015), 1, 'flyIn', walkAfterLanding=False)
        tmFlyIn = self.telemarketer.beginSupaFlyMove(VBase3(-69.007, 169.723, 10.015), 1, 'flyIn', walkAfterLanding=False)
        hwFlyIn = self.hollywood.beginSupaFlyMove(VBase3(1.563, 54.92, 0.025), 1, 'flyIn', walkAfterLanding=False)
        tfFlyIn = self.twoface.beginSupaFlyMove(VBase3(-79.164, 87.915, 0.025), 1, 'flyIn', walkAfterLanding=False)
        sfxSad = loader.loadSfx('phase_5/audio/sfx/ENC_Lose.ogg')
        self.handleCoachZ = Sequence(Func(base.localAvatar.invPage.ignoreOnscreenHooks), Func(base.localAvatar.questPage.ignoreOnscreenHooks), Func(NodePath(self.book).hide), Func(NodePath(self.laffMeter).hide), Func(base.localAvatar.obscureFriendsListButton, 1), Func(base.localAvatar.hideClarabelleGui), Func(base.localAvatar.invPage.ignoreOnscreenHooks), Func(base.localAvatar.questPage.ignoreOnscreenHooks), Func(self.explosionCard.setColorScale, 0, 0, 0, 1), self.title.colorScaleInterval(2, (1,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  1,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  1,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  1)), Wait(1.69), self.title2.colorScaleInterval(2, (1,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      1,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      1,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      1)), Func(base.camera.wrtReparentTo, render), Func(base.localAvatar.stopUpdateSmartCamera), Func(base.localAvatar.shutdownSmartCamera), base.camera.posHprInterval(0.01, (-43.552,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                -87.884,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                69), (-16.435,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      -13,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      0), blendType='noBlend'), Wait(2), Parallel(self.title.colorScaleInterval(2, (1,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    1,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    1,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    0)), self.title2.colorScaleInterval(2, (1,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            1,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            1,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            0))), Func(base.localAvatar.setPos, -699.42, 13.37, 5.721), Func(base.playMusic, self.doomsdayMusic, looping=1, volume=1.2), Func(self.sky.reparentTo, camera), Func(self.beginSkySequence.start), Parallel(Func(self.coldcaller.reparentTo, render), Func(self.coldcaller.addActive), Func(self.movershaker.reparentTo, render), Func(self.movershaker.addActive), Func(self.mingler.reparentTo, render), Func(self.mingler.addActive)), Parallel(Func(ccFlyIn.start, offset), Func(msFlyIn.start, offset), Func(mFlyIn.start, offset)), Parallel(base.camera.posHprInterval(9, (-44.419,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              195.303,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              15.325), (2.86,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        0), blendType='easeOut'), self.explosionCard.colorScaleInterval(2, (1,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            1,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            1,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            0)), Func(self.mingler.setChatAbsolute, "Let's Mingle, Toons!", CFSpeech | CFTimeout)), Parallel(Func(self.namedropper.reparentTo, render), Func(self.namedropper.addActive)), Func(ndFlyIn.start, offset), Func(base.camera.setPosHpr, 47.881, 17.621, 4.025, 75.8, 0, 0), Wait(3), Parallel(Func(self.hollywood.reparentTo, render), Func(self.hollywood.addActive)), Func(hwFlyIn.start, offset), Func(self.namedropper.setChatAbsolute, "Here's the deal, Toon.", CFSpeech | CFTimeout), base.camera.posHprInterval(2, (34.432,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        9.95,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        4.025), (41,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 0), blendType='easeOut'), Wait(0.5), Parallel(Func(self.telemarketer.reparentTo, render), Func(self.telemarketer.addActive)), Func(tmFlyIn.start, offset), self.logano.head.hprInterval(1, (0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             0)), Func(self.logano.sadEyes), Parallel(Func(self.twoface.reparentTo, render), Func(self.twoface.addActive)), Func(tfFlyIn.start, offset), Wait(1), Func(self.logano.play, 'lose'), Wait(2), Func(base.playSfx, sfxSad, volume=0.6), Wait(1), Func(self.squirtingFlowerTeleport), self.logano.scaleInterval(1.5, VBase3(0.01, 0.01, 0.01), blendType='easeInOut'), Wait(0.5), Func(base.transitions.fadeOut), Func(self.setCameraFollow), Wait(1), Func(localAvatar.sendUpdate, 'startSquirtingFlowerEv', []), Func(base.localAvatar.attachCamera), Func(base.localAvatar.initializeSmartCamera), Func(base.localAvatar.startUpdateSmartCamera), Func(NodePath(base.marginManager).show), Func(self.__cleanupSquirtingFlowerNPCs))
        if base.cr.currentEpisode == 'prologue':
            self.eventInterval.start()
            self.eventInterval4.loop()
            self.dumbstupid.start()
        if base.cr.currentEpisode == 'squirting_flower':
            self.handleCoachZ.start()
            self.ryno.removeActive()
            self.ryno.reparentTo(hidden)
        self.eventInterval3.loop()
        self.eventInterval5.loop()
        self.nabil.loop()
        self.nocigars.loop()
        self.nickdogeSequence.loop()
        self.infowars.loop()
        self.cheezetalk.loop()
        return

    def exitEvent(self):
        if base.cr.currentEpisode == 'prologue':
            self.eventInterval.finish()
            self.eventInterval4.finish()
            if self.dumbstupid.isPlaying():
                self.dumbstupid.finish()
        if base.cr.currentEpisode == 'squirting_flower':
            self.handleCoachZ.finish()
        self.eventInterval2.finish()
        self.eventInterval3.finish()
        self.eventInterval5.finish()
        self.ttmusicianWalkInterval.finish()
        self.ttmusicianWalk2Interval.finish()
        self.nabil.finish()
        self.nocigars.finish()
        self.nickdogeSequence.finish()
        self.infowars.finish()
        self.cheezetalk.finish()

    def enterEventTwo(self, offset):
        pass

    def exitEventTwo(self):
        pass

    def setState(self, state, timestamp):
        self.request(state, globalClockDelta.localElapsedTime(timestamp))

    def hideTunnel(self):
        self.geom = base.cr.playGame.hood.loader.geom
        tunnel = self.geom.find('**/linktunnel_sb_1002000_DNARoot')
        if tunnel:
            tunnel.reparentTo(hidden)
        dummyTunnel = self.geom.find('**/prop_safe_zone_tunnel_dummy')
        if dummyTunnel:
            dummyTunnel.reparentTo(self.geom)