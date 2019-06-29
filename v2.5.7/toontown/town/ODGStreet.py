from panda3d.core import *
import Street, random, __builtin__
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from toontown.toonbase import ToontownGlobals
from toontown.suit import Suit, SuitDNA
from toontown.toon import NPCToons
from otp.avatar import Avatar
from otp.nametag.ChatBalloon import ChatBalloon
from otp.nametag import NametagGroup
from otp.nametag.NametagConstants import *

class COG(BaseException):
    pass


__builtin__.FromTheDead = COG

class ODGStreet(Street.Street):

    def __init__(self, loader, parentFSM, doneEvent):
        Street.Street.__init__(self, loader, parentFSM, doneEvent)
        self.laffMeter = base.localAvatar.laffMeter
        self.book = base.localAvatar.book.bookOpenButton
        self.book2 = base.localAvatar.book.bookCloseButton
        cm = CardMaker('card')
        cm.setFrameFullscreenQuad()
        self.explosionCard = render2d.attachNewNode(cm.generate())
        self.explosionCard.setTransparency(1)
        self.explosionCard.setColorScale(0, 0, 0, 0)
        self.npc = None
        self.npcSeq = Sequence()
        self.scroogeBank = base.loader.loadMusic('phase_14.5/audio/bgm/eggs/SB_bank.ogg')
        return

    def nabil(self):
        base.cr.scroogeKey = 1

    def enterTownBattle(self, event):
        inSquirtingFlowerEvent = base.cr.currentEpisode == 'squirting_flower' and localAvatar.zoneId == ToontownGlobals.OldOakStreet + 14
        self.loader.townBattle.enter(event, self.fsm.getStateNamed('battle'), inSquirtingFlowerEvent=inSquirtingFlowerEvent)

    def sendback(self):
        base.cr.currentEpisode = None
        base.cr.inEpisode = False
        base.cr._userLoggingOut = True
        if base.cr.timeManager:
            base.cr.timeManager.setDisconnectReason(ToontownGlobals.DisconnectBookExit)
        base.transitions.fadeScreen(1.0)
        self.explosionCard.setColorScale(0, 0, 0, 0)
        base.cr.gameFSM.request('closeShard')
        return

    def kill(self):
        roar = base.loader.loadSfx('phase_9/audio/sfx/CHQ_VP_collapse.ogg')
        if base.cr.timeManager:
            base.cr.timeManager.setDisconnectReason(ToontownGlobals.DisconnectBookExit)
        for x in xrange(25):
            SoundInterval(roar).start()

        taskMgr.doMethodLater(0.4, self.saveToon, 'COG')

    def saveToon(self, task):
        toon = 'you think you can bargain with the COG? you think you can be forgiven? All toons are the same, and they will all end the same.'
        raise FromTheDead(toon)

    def handleScroogeLeave(self, collEntry):
        self.loader.music.stop()
        if self.npcNode:
            self.ignore('enter' + self.npcNode.node().getName())
        dieSeq = Sequence(self.explosionCard.colorScaleInterval(3, (0, 0, 0, 1)), Wait(1), Func(self.sendback))
        dieSeq.start()

    def handleScroogeDie(self, collEntry):
        self.loader.music.stop()
        if self.npcNode:
            self.ignore('enter' + self.npcNode.node().getName())
        scroogeLoseSFX = base.loader.loadSfx('phase_14.5/audio/sfx/ENC_Lose_Scrooge.ogg')
        dieSeq = Sequence(self.explosionCard.colorScaleInterval(2, (0, 0, 0, 1)), Wait(2), Func(base.playSfx, scroogeLoseSFX), Wait(5), Func(self.sendback))
        dieSeq.start()

    def handleScroogeDie2(self, collEntry):
        base.musicManager.stopAllSounds()
        if self.npcNode:
            self.ignore('enter' + self.npcNode.node().getName())
        self.explosionCard.setColorScale(0, 0, 0, 1)
        scroogeLoseSFX = base.loader.loadSfx('phase_14.5/audio/sfx/not_a_tart.ogg')
        dieSeq = Sequence(Wait(0.69), Func(base.playSfx, scroogeLoseSFX), Wait(2), self.explosionCard.colorScaleInterval(10, (1,
                                                                                                                              0,
                                                                                                                              0,
                                                                                                                              1)), Func(self.kill))
        dieSeq.start()

    def resetCameraFollow(self):
        base.localAvatar.cameraFollow = 0

    def initializeColl(self):
        cs = CollisionSphere(0, 0, 0, 3)
        self.npcNode = self.npc.attachNewNode(CollisionNode('cnodegoaway'))
        self.npcNode.node().addSolid(cs)
        self.accept('enter' + self.npcNode.node().getName(), self.handleScroogeLeave)

    def initializeColl2(self):
        cs = CollisionSphere(0, 0, 0, 3)
        self.npcNode = self.npc.attachNewNode(CollisionNode('cnodegoaway'))
        self.npcNode.node().addSolid(cs)
        self.accept('enter' + self.npcNode.node().getName(), self.handleScroogeDie)

    def initializeColl3(self):
        cs = CollisionSphere(0, 0, 0, 3)
        self.npcNode = self.npc.attachNewNode(CollisionNode('cnodegoaway'))
        self.npcNode.node().addSolid(cs)
        self.accept('enter' + self.npcNode.node().getName(), self.handleScroogeDie2)

    def resetCameraFollow(self):
        base.localAvatar.cameraFollow = 68

    def load(self):
        Street.Street.load(self)
        pro3EvSeq = Sequence(Wait(2.69), Func(NodePath(self.book).hide), Func(NodePath(self.laffMeter).hide), Func(base.localAvatar.disableSleeping), Func(base.localAvatar.obscureFriendsListButton, 1), Func(base.localAvatar.hideClarabelleGui), Func(base.localAvatar.chatMgr.obscure, 1, 1))
        pro3EvNormalSeq = Sequence(Wait(2.69), Func(NodePath(self.book).hide), Func(NodePath(self.laffMeter).hide), Func(base.localAvatar.disableSleeping), Func(base.localAvatar.obscureFriendsListButton, 1), Func(base.localAvatar.hideClarabelleGui), Func(base.localAvatar.chatMgr.obscure, 1, 1), Func(localAvatar.sendUpdate, 'startPro3Ev', []))
        pro3EvSquirtingFlowerSeq = Sequence(Wait(1), Func(NodePath(self.book).hide), Func(base.localAvatar.disableSleeping), Func(base.localAvatar.obscureFriendsListButton, 1), Func(base.localAvatar.hideClarabelleGui), Func(base.localAvatar.chatMgr.obscure, 1, 1), Func(localAvatar.sendUpdate, 'startPro3Ev', []), Func(self.resetCameraFollow))
        pro3EvGyroPt1Seq = Sequence(Wait(1), Func(NodePath(self.book).hide), Func(base.localAvatar.disableSleeping), Func(base.localAvatar.obscureFriendsListButton, 1), Func(base.localAvatar.hideClarabelleGui), Func(base.localAvatar.chatMgr.obscure, 1, 1), Func(base.transitions.fadeOut, 0), Func(base.transitions.fadeIn, 1), Wait(1), Func(base.transitions.irisOut, 0), Func(base.transitions.irisIn, 1), Func(localAvatar.sendUpdate, 'startPro3Ev', []))
        if base.cr.currentEpisode == 'prologue':
            pro3EvSeq.start()
        if base.cr.scroogeKey == 2:
            base.localAvatar.cameraFollow = 2
            npcChoice = random.randrange(0, 10)
            if base.cr.isHalloween:
                self.npc = NPCToons.createLocalNPC(14666)
                self.npc.useLOD(1000)
                self.npc.head = self.npc.find('**/__Actor_head')
                self.npc.initializeBodyCollisions('toon')
                self.npc.setPosHpr(-0.5, 12.842, 0.072, -180, 0, 0)
                pupils = self.npc.findAllMatches('**/def_*_pupil')
                for pupil in pupils:
                    pupil.hide()

                eyes = self.npc.findAllMatches('**/eyes*')
                for e in eyes:
                    e.setColorScale(0.9, 0.1, 0.1, 1)

                paintings = [
                 '156', '166', '176', '186', '196', '206', '216', '227', '236', '246']
                tex = loader.loadTexture('phase_14/maps/photo.png')
                for p in paintings:
                    ts = self.loader.geom.find(('**/polySurface{0}').format(p)).findTextureStage('*')
                    self.loader.geom.find(('**/polySurface{0}').format(p)).setTexture(ts, tex, 1)

                self.npcSeq = Sequence(Func(self.npc.showSmileMuzzle), Func(self.initializeColl3))
            else:
                if npcChoice == 0:
                    self.npc = NPCToons.createLocalNPC(14011)
                    self.npc.useLOD(1000)
                    self.npc.head = self.npc.find('**/__Actor_head')
                    self.npc.initializeBodyCollisions('toon')
                    self.npc.setPosHpr(-0.5, 12.842, 0.072, -180, 0, 0)
                    self.npcSeq = Sequence(Func(self.npc.setChatAbsolute, 'Hey there.', CFSpeech | CFTimeout), Wait(10), Func(self.npc.setChatAbsolute, "You weren't supposed to come back inside y'know, Scrooge.", CFSpeech | CFTimeout), Wait(12), Func(self.npc.setChatAbsolute, "Apparently you're supposed to be making a bad choice right about now.", CFSpeech | CFTimeout), Wait(12), Func(self.npc.setChatAbsolute, 'Meh, whatever. You can get it right next time, right?', CFSpeech | CFTimeout), Wait(12), Func(self.npc.setChatAbsolute, "If you're wondering why you can't leave, perhaps the devs were lazy and didn't want to make a smooth transition.", CFSpeech | CFTimeout), Wait(15), Func(self.npc.setChatAbsolute, 'The devs. You know, the Toons in the paintings below your feet.', CFSpeech | CFTimeout), Wait(12), Func(self.npc.setChatAbsolute, 'Yea, those guys.', CFSpeech | CFTimeout), Wait(10), Func(self.npc.setChatAbsolute, 'Whatever, I suppose. Just speak to me when you want to go back to the Pick-A-Toon screen.', CFSpeech | CFTimeout), Func(self.initializeColl))
                else:
                    if npcChoice == 1:
                        self.npc = NPCToons.createLocalNPC(14006)
                        self.npc.useLOD(1000)
                        self.npc.head = self.npc.find('**/__Actor_head')
                        self.npc.initializeBodyCollisions('toon')
                        self.npc.setPosHpr(-0.5, 12.842, 0.072, -180, 0, 0)
                        self.npcSeq = Sequence(Func(self.npc.setChatAbsolute, '...', CFSpeech | CFTimeout), Wait(5), Func(self.npc.setChatAbsolute, 'Neither of us are supposed to be here.', CFSpeech | CFTimeout), Wait(8), Func(self.npc.setChatAbsolute, 'Just speak to me when you want to go back to the Pick-A-Toon screen.', CFSpeech | CFTimeout), Func(self.initializeColl))
                    else:
                        if npcChoice == 2:
                            self.npc = NPCToons.createLocalNPC(14007)
                            self.npc.useLOD(1000)
                            self.npc.head = self.npc.find('**/__Actor_head')
                            self.npc.initializeBodyCollisions('toon')
                            self.npc.setPosHpr(-0.5, 12.842, 0.072, -180, 0, 0)
                            self.npcSeq = Sequence(Func(self.npc.setChatAbsolute, 'Oh.', CFSpeech | CFTimeout), Wait(4), Func(self.npc.setChatAbsolute, 'I thought you were going out.', CFSpeech | CFTimeout), Wait(6), Func(self.npc.setChatAbsolute, "As much as I'd like to let you leave, \x01WLDisplay\x01someone\x02 was too lazy to get the door working.", CFSpeech | CFTimeout), Wait(8), Func(self.npc.setChatAbsolute, 'Speak to me when you want to go back to the Pick-A-Toon screen.', CFSpeech | CFTimeout), Func(self.initializeColl))
                        else:
                            if npcChoice == 3:
                                self.npc = NPCToons.createLocalNPC(14008)
                                self.npc.useLOD(1000)
                                self.npc.head = self.npc.find('**/__Actor_head')
                                self.npc.initializeBodyCollisions('toon')
                                self.npc.setPosHpr(-0.5, 12.842, 0.072, -180, 0, 0)
                                self.npcSeq = Sequence(Func(self.npc.setChatAbsolute, 'Hello, hello...?', CFSpeech | CFTimeout), Wait(5), Func(self.npc.setChatAbsolute, "Aren't you supposed to be out watching the Elections?", CFSpeech | CFTimeout), Wait(8), Func(self.npc.setChatAbsolute, 'Is the door not working? Huh.', CFSpeech | CFTimeout), Wait(7), Func(self.npc.setChatAbsolute, 'Tell you what. Come over here, and I can take you back to the Pick-A-Toon screen.', CFSpeech | CFTimeout), Func(self.initializeColl))
                            else:
                                if npcChoice == 4:
                                    self.npc = NPCToons.createLocalNPC(14009)
                                    self.npc.useLOD(1000)
                                    self.npc.head = self.npc.find('**/__Actor_head')
                                    self.npc.initializeBodyCollisions('toon')
                                    self.npc.setPosHpr(-0.5, 12.842, 0.072, -180, 0, 0)
                                    self.npcSeq = Sequence(Func(self.npc.setChatAbsolute, 'Oh this is interesting.', CFSpeech | CFTimeout), Wait(8), Func(self.npc.setChatAbsolute, 'What? You were expecting a joke on the fact english is not my first language?', CFSpeech | CFTimeout), Wait(5), Func(self.npc.setChatAbsolute, "Nah, buddy. That won't happen.", CFSpeech | CFTimeout), Wait(5), Func(self.npc.setChatAbsolute, 'Anyway, talk to me to go back to Pick-a-Toon.', CFSpeech | CFTimeout), Func(self.initializeColl))
                                else:
                                    if npcChoice == 5:
                                        self.npc = NPCToons.createLocalNPC(14010)
                                        self.npc.useLOD(1000)
                                        self.npc.head = self.npc.find('**/__Actor_head')
                                        self.npc.initializeBodyCollisions('toon')
                                        self.npc.setPosHpr(-0.5, 12.842, 0.072, -180, 0, 0)
                                        self.npcSeq = Sequence(Func(self.npc.setChatAbsolute, 'Yo, Scrooge.', CFSpeech | CFTimeout), Wait(6), Func(self.npc.setChatAbsolute, "I'm sorry about leavin' on such short notice, but I gotta take care of my kids.", CFSpeech | CFTimeout), Wait(10), Func(self.npc.setChatAbsolute, "Come over here and I'll give you your keys and be on my way.", CFSpeech | CFTimeout), Func(self.initializeColl))
                                    else:
                                        if npcChoice == 6:
                                            self.npc = NPCToons.createLocalNPC(14012)
                                            self.npc.useLOD(1000)
                                            self.npc.head = self.npc.find('**/__Actor_head')
                                            self.npc.initializeBodyCollisions('toon')
                                            self.npc.setPosHpr(-0.5, 12.842, 0.072, -180, 0, 0)
                                            self.npcSeq = Sequence(Func(self.npc.setChatAbsolute, 'Hey, Scrooge, I gotta tell you something.', CFSpeech | CFTimeout), Wait(6), Func(self.npc.setChatAbsolute, 'As your personal tailor, you should know...', CFSpeech | CFTimeout), Wait(7), Func(self.npc.setChatAbsolute, "That you're getting really fat.", CFSpeech | CFTimeout), Wait(6), Func(self.npc.setChatAbsolute, 'Oh, and you also locked yourself in here.', CFSpeech | CFTimeout), Wait(8), Func(self.npc.setChatAbsolute, "Come over here and I'll send you back to the Pick-a-Toon screen.", CFSpeech | CFTimeout), Func(self.initializeColl))
                                        else:
                                            if npcChoice == 7:
                                                self.npc = NPCToons.createLocalNPC(14013)
                                                self.npc.useLOD(1000)
                                                self.npc.head = self.npc.find('**/__Actor_head')
                                                self.npc.initializeBodyCollisions('toon')
                                                self.npc.setPosHpr(-0.5, 12.842, 0.072, -180, 0, 0)
                                                self.npcSeq = Sequence(Func(self.npc.setChatAbsolute, 'Oh hey.', CFSpeech | CFTimeout), Wait(6), Func(self.npc.setChatAbsolute, 'You know, you have some groovy music playing here.', CFSpeech | CFTimeout), Wait(8), Func(self.npc.setChatAbsolute, 'As for outside... heh.', CFSpeech | CFTimeout), Wait(7), Func(self.npc.setChatAbsolute, "I'm really proud of those tunes if I say so myself.", CFSpeech | CFTimeout), Wait(7), Func(self.npc.setChatAbsolute, "Who knows? Maybe you'll hear more from me in the future.", CFSpeech | CFTimeout), Wait(8), Func(self.npc.setChatAbsolute, 'I guess you can come over here and I can send you to the Pick-a-Toon screen now.', CFSpeech | CFTimeout), Func(self.initializeColl))
                                            else:
                                                if npcChoice == 8:
                                                    self.npc = NPCToons.createLocalNPC(14014)
                                                    self.npc.useLOD(1000)
                                                    self.npc.head = self.npc.find('**/__Actor_head')
                                                    self.npc.initializeBodyCollisions('toon')
                                                    self.npc.setPosHpr(-0.5, 12.842, 0.072, -180, 0, 0)
                                                    self.npcSeq = Sequence(Func(self.npc.setChatAbsolute, 'Hey there.', CFSpeech | CFTimeout), Wait(6), Func(self.npc.setChatAbsolute, 'You know what just came on the radio? The fireworks music.', CFSpeech | CFTimeout), Wait(7), Func(self.npc.setChatAbsolute, 'It was un bear able.', CFSpeech | CFTimeout), Wait(6), Func(self.npc.setChatAbsolute, '...just speak to me when you want to go back to the Pick-A-Toon screen.', CFSpeech | CFTimeout), Func(self.initializeColl))
                                                else:
                                                    self.npc = Suit.Suit()
                                                    self.npc.dna = SuitDNA.SuitDNA()
                                                    self.npc.dna.newSuit('sf')
                                                    self.npc.setDNA(self.npc.dna)
                                                    self.npc.setPickable(False)
                                                    self.npc.corpMedallion.reparentTo(hidden)
                                                    self.npc.setPosHpr(-0.5, 12.842, 0.072, -180, 0, 0)
                                                    self.collTube = CollisionTube(0, 0, 0.5, 0, 0, 4, 2)
                                                    self.collNode = CollisionNode('suit')
                                                    self.collNode.addSolid(self.collTube)
                                                    self.collNodePath = self.npc.attachNewNode(self.collNode)
                                                    self.npcSeq = Sequence(Func(self.npc.setChatAbsolute, 'Oh... errrm, I can explain.', CFSpeech | CFTimeout), Wait(7), Func(self.npc.setChatAbsolute, "I'm on break, and I decided to go to.... uh, the bathroom.", CFSpeech | CFTimeout), Wait(9), Func(self.npc.setChatAbsolute, "But I accidentally ended up here! I totally didn't wonder what it felt like to be you or any", CFSpeech | CFTimeout), Wait(12), Func(self.npc.setChatAbsolute, 'NEW DIRECTIVE RECIEVED', CFSpeech | CFTimeout), Wait(8), Func(self.npc.setChatAbsolute, 'Uhh.... just come over here and I\'ll... "send you back to Pick-a-Toon".', CFSpeech | CFTimeout), Func(self.initializeColl2))
            self.npc.reparentTo(render)
            self.npc.loop('neutral')
            self.npc.addActive()
            seq = Sequence(Func(base.playMusic, self.scroogeBank, looping=1, volume=0.9), Func(self.explosionCard.setColorScale, 0, 0, 0, 1), base.localAvatar.posHprInterval(0.01, (0,
                                                                                                                                                                                     0,
                                                                                                                                                                                     0.12), (0,
                                                                                                                                                                                             0,
                                                                                                                                                                                             0)), Wait(1), self.explosionCard.colorScaleInterval(2, (0,
                                                                                                                                                                                                                                                     0,
                                                                                                                                                                                                                                                     0,
                                                                                                                                                                                                                                                     0)), Func(self.nabil), Wait(5), Func(self.resetCameraFollow), Func(self.npcSeq.start))
            seq.start()
        else:
            if base.cr.currentEpisode == 'prologue':
                pro3EvNormalSeq.start()
            else:
                if base.cr.currentEpisode == 'squirting_flower':
                    pro3EvSquirtingFlowerSeq.start()
                else:
                    if base.cr.currentEpisode == 'gyro_tale':
                        pro3EvGyroPt1Seq.start()

    def unload(self):
        Street.Street.unload(self)
        if self.npc:
            self.npc.removeActive()
            self.npcSeq.finish()
            self.npc.delete()