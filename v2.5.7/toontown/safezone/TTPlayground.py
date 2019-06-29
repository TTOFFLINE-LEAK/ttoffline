from panda3d.core import *
from toontown.toonbase import ToontownGlobals
import Playground, random, time
from otp.nametag.NametagConstants import *
from toontown.launcher import DownloadForceAcknowledge
from direct.task.Task import Task
from toontown.hood import ZoneUtil
from toontown.election import SafezoneInvasionGlobals
from toontown.suit import Suit, SuitDNA
from toontown.toon import NPCToons
from toontown.toonbase import TTLocalizer
from toontown.toontowngui import TTDialog
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
import HolidayCar, DistributedPumpkin

class TTPlayground(Playground.Playground):

    def __init__(self, loader, parentFSM, doneEvent):
        Playground.Playground.__init__(self, loader, parentFSM, doneEvent)

    def load(self):
        Playground.Playground.load(self)
        self.swagtaClaus = None
        self.saySwag = None
        self.swag = None
        self.doc = None
        self.docSpeech = None
        if base.cr.newsManager.isHolidayRunning(ToontownGlobals.TRICK_OR_TREAT) or base.cr.newsManager.isHolidayRunning(ToontownGlobals.HALLOWEEN_PROPS) or base.cr.newsManager.isHolidayRunning(ToontownGlobals.HALLOWEEN):
            self.pumpkin1 = DistributedPumpkin.DistributedPumpkin(base.cr)
            self.pumpkin1.setSize('s')
            self.pumpkin2 = DistributedPumpkin.DistributedPumpkin(base.cr)
            self.pumpkin2.setSize('s')
            self.pumpkin3 = DistributedPumpkin.DistributedPumpkin(base.cr)
            self.pumpkin3.setSize('s')
            self.pumpkin4 = DistributedPumpkin.DistributedPumpkin(base.cr)
            self.pumpkin4.setSize('s')
            self.pumpkintall1 = DistributedPumpkin.DistributedPumpkin(base.cr)
            self.pumpkintall1.setSize('l')
            self.pumpkintall2 = DistributedPumpkin.DistributedPumpkin(base.cr)
            self.pumpkintall2.setSize('l')
            self.pumpkintall3 = DistributedPumpkin.DistributedPumpkin(base.cr)
            self.pumpkintall3.setSize('l')
            self.pumpkintall4 = DistributedPumpkin.DistributedPumpkin(base.cr)
            self.pumpkintall4.setSize('l')
            self.pumpkinList = [
             [
              self.pumpkin1, 79.688, 158.123, 2.483, -15.427, self.pumpkinloop, 0], [self.pumpkin2, -128.618, -65.178, 0.484, -230.316, self.pumpkinloop2, 1],
             [
              self.pumpkin3, -62.478, -22.103, -1.975, 0, self.pumpkinloop3, 2], [self.pumpkin4, 140.478, -84.103, 2.525, -80, self.pumpkinloop4, 3],
             [
              self.pumpkintall1, 10.371, -130.137, 3.025, -227, self.pumpkinloop5, 0], [self.pumpkintall2, 110.094, 26.642, 4.025, -55, self.pumpkinloop6, 1],
             [
              self.pumpkintall3, 44.119, 60.559, 4.025, 16, self.pumpkinloop7, 2], [self.pumpkintall4, 127.134, 57.558, 2.525, -165, self.pumpkinloop8, 3]]
            self.preparePumpkins(self.pumpkinList)
        if base.cr.newsManager.isHolidayRunning(ToontownGlobals.WINTER_DECORATIONS):
            self.swagtaClaus = HolidayCar.HolidayCar()
            self.swagtaClaus.generate()
            self.swagtaClaus.cart.setH(-60)
            self.swagtaClaus.cart.setPos(125.941, -76.18, 2.525)
            self.saySwag = Sequence(Func(self.swagtaClaus.swagPhrase), Wait(25))
            self.saySwag.loop()
        if base.cr.newsManager.isHolidayRunning(ToontownGlobals.ORANGES):
            self.createDoctorWeird()
        return

    def unload(self):
        Playground.Playground.unload(self)
        if self.swagtaClaus:
            self.swagtaClaus.disable()
        if self.saySwag:
            self.saySwag.finish()
        if self.docSpeech:
            self.docSpeech.finish()
            self.docSpeech = None
        if self.doc:
            self.doc.removeActive()
            self.doc.cleanup()
            self.doc.delete()
        if self.swag:
            self.swag.removeActive()
            self.swag.cleanup()
            self.swag.delete()
        return

    def createDoctorWeird(self):
        self.doc = NPCToons.createLocalNPC(2030)
        self.doc.useLOD(1000)
        self.doc.initializeBodyCollisions('toon')
        self.doc.reparentTo(render)
        self.doc.setPosHpr(36.219, -19.729, 4.025, 33, 0, 0)
        self.doc.pingpong('think', fromFrame=20, toFrame=40)
        self.doc.setPickable(False)
        self.doc.addActive()
        self.swag = Suit.Suit()
        self.swag.dna = SuitDNA.SuitDNA()
        self.swag.dna.newSuit('sf')
        self.swag.setDNA(self.swag.dna)
        self.swag.setPickable(False)
        self.swag.addActive()
        self.swag.reparentTo(render)
        self.swag.setPosHpr(40.71, -19.041, 4.025, 40, 0, 0)
        self.swag.setPlayRate(0.5, 'cigar-smoke')
        self.swag.pingpong('cigar-smoke', fromFrame=37, toFrame=47)
        self.swag.cigar.reparentTo(self.swag.find('**/joint_Rhold'))
        self.swag.cigar.setPosHprScale(-0.34, -0.49, -0.24, 180.0, 0.0, 180.0, 8.0, 8.0, 8.0)
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': TTLocalizer.SuitSwagForeman, 'dept': TTLocalizer.Sellbot, 
           'level': 50}
        self.swag.setDisplayName(nameInfo)
        self.swag.collTube = CollisionTube(0, 0, 0.5, 0, 0, 4, 2)
        self.swag.collNode = CollisionNode('suit')
        self.swag.collNode.addSolid(self.swag.collTube)
        self.swag.collNodePath = self.swag.attachNewNode(self.swag.collNode)
        self.docSpeech = Sequence(Wait(6.9), Func(self.doc.setChatAbsolute, 'This is absolutely absurd...', CFSpeech | CFTimeout), Wait(6.9), Func(self.doc.setChatAbsolute, "A game that doesn't exist on a day that doesn't exist...", CFSpeech | CFTimeout), Wait(8), Func(self.doc.setChatAbsolute, "And to top it all off, here I am, a Toon that doesn't exist!", CFSpeech | CFTimeout), Wait(8), Func(self.swag.setChatAbsolute, "If you don't exist, then how are you here?", CFSpeech | CFTimeout), Wait(6.9), Func(self.doc.setChatAbsolute, 'I existed... at one point. But not in this timeline.', CFSpeech | CFTimeout), Wait(8), Func(self.doc.setChatAbsolute, "I was erased... I shouldn't be here. These Cogs shouldn't be here!", CFSpeech | CFTimeout), Wait(4), Func(self.swag.setChatAbsolute, 'Hey, what do you have against Cogs?', CFSpeech | CFTimeout), Wait(6.9), Func(self.doc.setChatAbsolute, "Oh, nothing, nothing... It's just that...", CFSpeech | CFTimeout), Wait(6.9), Func(self.doc.setChatAbsolute, 'How could this all be?', CFSpeech | CFTimeout), Wait(5), Func(self.swag.setChatAbsolute, "Well, gee, could it be because it's April Toon's Day?", CFSpeech | CFTimeout), Wait(7), Func(self.doc.setChatAbsolute, "No, of course not. It's March 32nd.", CFSpeech | CFTimeout), Wait(5), Func(self.swag.setChatAbsolute, 'Whatever you say, doc. Can I go now?', CFSpeech | CFTimeout), Wait(7), Func(self.doc.setChatAbsolute, 'No! You are quite a unique specimen! I must study you while I can!', CFSpeech | CFTimeout), Wait(9), Func(self.swag.setChatAbsolute, "Alright, you do that. I'll just be standing here, starving, craving Frizzy Fried Chicken.", CFSpeech | CFTimeout), Wait(4))
        self.docSpeech.loop()

    def enter(self, requestStatus):
        Playground.Playground.enter(self, requestStatus)
        taskMgr.doMethodLater(1, self.__birds, 'TT-birds')

    def exit(self):
        Playground.Playground.exit(self)
        taskMgr.remove('TT-birds')

    def __birds(self, task):
        base.playSfx(random.choice(self.loader.birdSound))
        t = random.random() * 20.0 + 1
        taskMgr.doMethodLater(t, self.__birds, 'TT-birds')
        return Task.done

    def doRequestLeave(self, requestStatus):
        if config.GetBool('want-doomsday', False):
            base.localAvatar.disableAvatarControls()
            self.confirm = TTDialog.TTGlobalDialog(doneEvent='confirmDone', message=SafezoneInvasionGlobals.LeaveToontownCentralAlert, style=TTDialog.Acknowledge)
            self.confirm.show()
            self.accept('confirmDone', self.handleConfirm)
            return
        self.fsm.request('trialerFA', [requestStatus])

    def enterDFA(self, requestStatus):
        doneEvent = 'dfaDoneEvent'
        self.accept(doneEvent, self.enterDFACallback, [requestStatus])
        self.dfa = DownloadForceAcknowledge.DownloadForceAcknowledge(doneEvent)
        hood = ZoneUtil.getCanonicalZoneId(requestStatus['hoodId'])
        if hood == ToontownGlobals.MyEstate:
            self.dfa.enter(base.cr.hoodMgr.getPhaseFromHood(ToontownGlobals.MyEstate))
        else:
            if hood == ToontownGlobals.GoofySpeedway:
                self.dfa.enter(base.cr.hoodMgr.getPhaseFromHood(ToontownGlobals.GoofySpeedway))
            else:
                if hood == ToontownGlobals.PartyHood:
                    self.dfa.enter(base.cr.hoodMgr.getPhaseFromHood(ToontownGlobals.PartyHood))
                else:
                    self.dfa.enter(5)

    def handleConfirm(self):
        status = self.confirm.doneStatus
        self.ignore('confirmDone')
        self.confirm.cleanup()
        del self.confirm
        if status == 'ok':
            base.localAvatar.enableAvatarControls()

    def showPaths(self):
        from toontown.classicchars import CCharPaths
        from toontown.toonbase import TTLocalizer
        self.showPathPoints(CCharPaths.getPaths(TTLocalizer.Mickey))