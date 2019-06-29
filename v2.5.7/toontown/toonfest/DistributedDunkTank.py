from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObject
from direct.interval.IntervalGlobal import *
from panda3d.core import *
from otp.nametag.NametagConstants import *
from toontown.avatar import ToontownAvatarUtils
from toontown.toonbase import ToontownGlobals

class DistributedDunkTank(DistributedObject.DistributedObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedDunkTank')

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        self.rocky = None
        self.rockyIdleSeq = None
        self.target = None
        self.isAvailable = False
        self.hitSfx = None
        self.resetSfx = None
        self.tgtMoveSequence = None
        self.dunkSeq = None
        return

    def disable(self):
        DistributedObject.DistributedObject.disable(self)
        if self.rockyIdleSeq:
            self.rockyIdleSeq.finish()
            self.rockyIdleSeq = None
        if self.tgtMoveSequence:
            self.tgtMoveSequence.finish()
            self.tgtMoveSequence = None
        if self.dunkSeq:
            self.dunkSeq.finish()
            self.dunkSeq = None
        if self.rocky:
            self.rocky.stopBlink()
            self.rocky.removeActive()
            self.rocky.delete()
            self.rocky = None
        self.hitSfx = None
        self.resetSfx = None
        render.clearTag('pieCode')
        return

    def announceGenerate(self):
        self.duckTank = base.cr.playGame.hood.loader.geom.find('**/toonfest_duck_tank_DNARoot')
        self.rocky = ToontownAvatarUtils.createToon(14011, 0, -1.69, -0.69, 180, 0, 0)
        self.rocky.reparentTo(self.duckTank.find('**/tank_seat'))
        self.rocky.addActive()
        self.rocky.startBlink()
        self.rocky.loop('sit')
        self.rockyIdleSeq = Sequence(Wait(10), Func(self.rocky.setChatAbsolute, "I can't believe this!", CFSpeech | CFTimeout), Wait(5), Func(self.rocky.setChatAbsolute, 'I have to do community service for greening!', CFSpeech | CFTimeout), Wait(8), Func(self.rocky.setChatAbsolute, "But I can't just sweep up Toontown Central or work at the Library, no...", CFSpeech | CFTimeout), Wait(8), Func(self.rocky.setChatAbsolute, 'I have to sit in here and get dunked all day in this Duck Tank!', CFSpeech | CFTimeout), Wait(8), Func(self.rocky.setChatAbsolute, "The worst part is that the water's freezing!", CFSpeech | CFTimeout), Wait(8), Func(self.rocky.setChatAbsolute, "This stinks! I'd rather get banned again.", CFSpeech | CFTimeout))
        self.rockyIdleSeq.loop()
        self.target = self.duckTank.find('**/target_collision')
        render.setTag('pieCode', str(ToontownGlobals.PieCodeNotTarget))
        self.target.setTag('pieCode', str(ToontownGlobals.PieCodeTarget))
        self.accept('pieSplat', self.__pieSplat)
        self.accept('localPieSplat', self.__localPieSplat)
        self.hitSfx = loader.loadSfx('phase_4/audio/sfx/MG_cannon_hit_tower.ogg')
        self.resetSfx = loader.loadSfx('phase_5.5/audio/sfx/mailbox_open_2.ogg')
        self.isAvailable = True
        self.notify.warning('Making self available')

    def __pieSplat(self, toon, pieCode):
        if pieCode != ToontownGlobals.PieCodeTarget or toon == localAvatar or not self.isAvailable:
            return
        self.isAvailable = False
        self.hitTarget()

    def __localPieSplat(self, pieCode, entry):
        if pieCode != ToontownGlobals.PieCodeTarget:
            return
        if self.isAvailable:
            self.isAvailable = False
            self.b_hitTarget()

    def b_hitTarget(self):
        self.d_hitTarget()
        self.hitTarget()

    def d_hitTarget(self):
        self.sendUpdate('hitTarget', [])

    def hitTarget(self):
        self.rockyIdleSeq.pause()
        tgt = self.duckTank.find('**/target')
        self.tgtMoveSequence = tgt.hprInterval(0.25, (0, -25, 0), startHpr=(0, tgt.getP(), 0))
        self.hitSfx.play()
        self.tgtMoveSequence.start()

    def dunk(self):
        tgt = self.duckTank.find('**/target')
        self.dunkSeq = Sequence(Wait(12), tgt.hprInterval(0.25, (0, 0, 0), startHpr=(0,
                                                                                     -25,
                                                                                     0)))
        self.dunkSeq.start()

    def rewardAv(self):
        pass