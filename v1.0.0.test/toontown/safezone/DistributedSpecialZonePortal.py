from panda3d.core import *
from direct.distributed.ClockDelta import *
from direct.distributed import DistributedObject
from direct.interval.IntervalGlobal import *
from direct.task import Task
from toontown.toonbase import ToontownGlobals
from otp.otpbase import OTPLocalizer
from libotp.nametag._constants import CFSpeech, CFQuicktalker, CFTimeout
from toontown.toon import NPCToons

class DistributedSpecialZonePortal(DistributedObject.DistributedObject):
    MeetHereCollisionName = 'MeetHere-Collision-{}'

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        self.fountainNode = None
        self.destinationZoneId = None
        self.portalPos = None
        self.portalSeq = None
        self.portalIntervals = []
        self.portalNode = None
        self.portalParent = None
        self.portalAppearSfx = None
        self.portalDisappearSfx = None
        self.npc = None
        self.previousState = -1
        return

    def announceGenerate(self):
        DistributedObject.DistributedObject.announceGenerate(self)
        if self.zoneId in (2000, 30000):
            self.portalPos = (93.205, -106.482, 2.5)
            self.destinationZoneId = 19000
            self.generateMeetHere()
        else:
            if self.zoneId == 19000:
                self.portalPos = (119.999, -99.9999, 0)
                self.destinationZoneId = 2000
            else:
                self.notify.error('DistributedSpecialZonePortal geom could not be found!')
        self.fountainNode = loader.loadModel('phase_4/models/props/toontown_central_fountain')
        self.fountainNode.setPos(self.portalPos)
        self.fountainNode.reparentTo(render)

    def disable(self):
        self.ignoreAll()
        self.destinationZoneId = None
        if self.portalSeq:
            self.portalSeq.finish()
            del self.portalSeq
        for interval in self.portalIntervals:
            if interval:
                interval.finish()
                del interval

        if self.portalNode:
            self.portalNode.removeNode()
            del self.portalNode
        if self.portalParent:
            del self.portalParent
        if self.portalAppearSfx:
            del self.portalAppearSfx
        if self.portalDisappearSfx:
            del self.portalDisappearSfx
        if self.npc:
            self.npc.removeActive()
            self.npc.detachNode()
            self.npc.delete()
        if self.fountainNode:
            self.fountainNode.removeNode()
        DistributedObject.DistributedObject.disable(self)
        return

    def cleanupInterval(self, interval):
        if interval:
            interval.finish()
            self.portalIntervals.remove(interval)
            interval = None
        return

    def enterPortal(self, hoodId, zoneId, event):
        self.togglePortalColl(False)
        base.cr.playGame.getPlace().handleEnterPortal(hoodId, zoneId)

    def generateMeetHere(self):
        place = base.cr.playGame.getPlace()
        if not place:
            self.acceptOnce('playGameSetPlace', self.generateMeetHere)
            return
        geom = place.loader.geom
        meetHerecoll = CollisionNode('meetHereTrigger')
        meetHereBox = CollisionSphere(121.2, -53.5, 4, 15)
        meetHereBox.setTangible(0)
        meetHerecoll.addSolid(meetHereBox)
        box = geom.attachNewNode(meetHerecoll)
        box.node().setCollideMask(ToontownGlobals.WallBitmask)
        box.node().setName(self.MeetHereCollisionName.format(self.getDoId()))
        self.accept('enter' + self.MeetHereCollisionName.format(self.getDoId()), self.d_acceptPhrase)
        self.accept('exit' + self.MeetHereCollisionName.format(self.getDoId()), self.d_rejectPhrase)

    def d_acceptPhrase(self, _=None):
        self.sendUpdate('acceptPhrase', [])

    def d_rejectPhrase(self, _=None):
        self.sendUpdate('rejectPhrase', [])

    def togglePortal(self, state, zoneId, npcId, avId, ts):
        place = base.cr.playGame.getPlace()
        if not place:
            self.acceptOnce('playGameSetPlace', self.togglePortal, extraArgs=[state, zoneId, npcId, avId, ts])
            return
        if self.portalSeq:
            if self.portalSeq.isPlaying():
                self.portalSeq.finish()
        if zoneId in ToontownGlobals.Location2Hood.keys():
            hoodId = ToontownGlobals.Location2Hood[zoneId]
        else:
            hoodId = zoneId
        if state == 0:
            self.makePortalOpenSequence(hoodId, zoneId)
        else:
            if state == 1:
                if self.previousState != 0:
                    self.makePortalOpenSequence(hoodId, zoneId)
                    self.portalSeq.finish()
                self.makePortalCloseSequence()
            else:
                if state == 2:
                    self.makeMeetHereSequence(npcId, avId)
                else:
                    if state == 3:
                        if self.previousState != 2:
                            self.makeMeetHereSequence(npcId, avId)
                            if self.portalSeq != None:
                                self.portalSeq.finish()
                        self.makeNoResponseSequence()
        if self.portalSeq:
            ts = globalClockDelta.localElapsedTime(ts)
            self.portalSeq.start(ts)
        self.previousState = state
        return

    def makePortalOpenSequence(self, hoodId, zoneId):
        place = base.cr.playGame.getPlace()
        geom = place.loader.geom
        self.portalNode = geom.attachNewNode('portalNode')
        self.portalNode.setPos(*self.portalPos)
        self.portalParent = self.fountainNode.getParent()
        self.fountainNode.wrtReparentTo(self.portalNode)
        self.portal = loader.loadModel('phase_14/models/props/specialZone_portal')
        self.portal.reparentTo(self.portalNode)
        for node in ('beam', 'beam1', 'beam2', 'beam3', 'beam4', 'base_shine'):
            self.portal.find('**/' + node).setScale(0.01)

        self.portal.find('**/beam').setColorScale(1, 1, 1, 0)
        portalTriggerColl = CollisionNode('portalTrigger')
        portalTriggerBox = CollisionBox(Point3(0, 0, 4), 6, 6, 6)
        portalTriggerBox.setTangible(0)
        portalTriggerColl.addSolid(portalTriggerBox)
        collNode = self.portal.attachNewNode(portalTriggerColl)
        collNode.node().setCollideMask(ToontownGlobals.WallBitmask)
        self.portalAppearSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_stomper_large.ogg')
        self.portalSeq = Parallel()
        hoverFloat = Sequence(LerpPosInterval(self.fountainNode, 2, (self.fountainNode.getX() - 40.0, self.fountainNode.getY() - 40.0, self.fountainNode.getZ() + 15.5), blendType='easeInOut'), LerpPosInterval(self.fountainNode, 2, (self.fountainNode.getX() - 40.0, self.fountainNode.getY() - 40.0, self.fountainNode.getZ() + 16.0), blendType='easeInOut'))
        self.portalIntervals.append(hoverFloat)
        flipSeq = Sequence(LerpPosInterval(self.fountainNode, 2, (self.fountainNode.getX(), self.fountainNode.getY(), self.fountainNode.getZ() + 1), blendType='easeInOut'), LerpPosInterval(self.fountainNode, 1, (self.fountainNode.getX(), self.fountainNode.getY(), self.fountainNode.getZ() + 16), blendType='easeOut'), LerpPosInterval(self.fountainNode, 1, (self.fountainNode.getX(), self.fountainNode.getY(), self.fountainNode.getZ() + 15.5), blendType='easeOut'), LerpPosInterval(self.fountainNode, 3, (self.fountainNode.getX() - 40.0, self.fountainNode.getY() - 40.0, self.fountainNode.getZ() + 16.0), blendType='easeInOut'), Func(hoverFloat.loop))
        portalTurn = LerpHprInterval(self.portal.find('**/base_shine'), 60, (360.0,
                                                                             0.0,
                                                                             0.0), blendType='noBlend')
        self.portalIntervals.append(portalTurn)
        beamTurn = LerpHprInterval(self.portal.find('**/beam'), 30, (360.0, 0.0, 0.0), blendType='noBlend')
        self.portalIntervals.append(beamTurn)
        nodeAppearSeq = Sequence()
        nodeTurnSeq = Parallel()
        self.portalIntervals.append(nodeTurnSeq)
        for x in range(4):
            node = self.portal.find('**/beam' + str(x + 1))
            nodeAppear = LerpScaleInterval(node, 0.5, (1, 1, 1), blendType='easeInOut')
            nodeAppearSeq.append(Sequence(Func(base.playSfx, self.portalAppearSfx, node=self.portalNode), nodeAppear, Wait(0.5)))
            nodeTurnSeq.append(LerpHprInterval(node, 30, (-360.0, 0.0, 0.0), blendType='noBlend'))

        portalAppear = Sequence(Func(nodeTurnSeq.loop), nodeAppearSeq, Wait(1), Func(self.togglePortalColl, True, hoodId, zoneId), Parallel(Func(beamTurn.loop), Func(portalTurn.loop), LerpColorScaleInterval(self.portal.find('**/beam'), 3, (1,
                                                                                                                                                                                                                                                1,
                                                                                                                                                                                                                                                1,
                                                                                                                                                                                                                                                1), blendType='easeInOut'), LerpScaleInterval(self.portal.find('**/beam'), 3, (1,
                                                                                                                                                                                                                                                                                                                               1,
                                                                                                                                                                                                                                                                                                                               1), blendType='easeInOut'), LerpScaleInterval(self.portal.find('**/base_shine'), 2, (1,
                                                                                                                                                                                                                                                                                                                                                                                                                    1,
                                                                                                                                                                                                                                                                                                                                                                                                                    1), blendType='easeInOut')))
        portalSpawnSeq = Sequence(Wait(3.25), flipSeq, portalAppear)
        self.portalSeq.append(portalSpawnSeq)
        if self.zoneId in (2000, 30000) and self.npc:
            npcPortalSeq = Sequence(Wait(1), Func(self.npc.setChatAbsolute, OTPLocalizer.SpeedChatStaticTextToontown[1000], CFSpeech | CFQuicktalker | CFTimeout), Wait(1), Func(self.npc.loop, 'walk'), LerpHprInterval(self.npc, 0.75, (152.15,
                                                                                                                                                                                                                                          0,
                                                                                                                                                                                                                                          0)), Func(self.npc.loop, 'neutral'), ActorInterval(self.npc, 'hypnotize'), Func(self.npc.loop, 'run'), Parallel(LerpPosInterval(self.npc, 10, (self.portalNode.getX(), self.portalNode.getY(), self.portalNode.getZ())), Sequence(Wait(8), self.npc._Toon__doToonGhostColorScale(VBase4(1, 1, 1, 0), 2.0, keepDefault=1))), Func(self.npc.removeActive), Func(self.npc.detachNode), Func(self.npc.delete))
            self.portalSeq.append(npcPortalSeq)

    def togglePortalColl(self, state, hoodId=0, zoneId=0):
        if state:
            self.accept('enterportalTrigger', self.enterPortal, extraArgs=[hoodId, zoneId])
        else:
            if not state:
                self.ignore('enterportalTrigger')

    def makePortalCloseSequence(self):
        self.portalDisappearSfx = loader.loadSfx('phase_11/audio/sfx/LB_evidence_miss.ogg')
        self.portalSeq = Parallel()
        if self.zoneId in (2000, 30000):
            z = 2.5
        else:
            z = 0
        flipSeq = Sequence(Func(self.cleanupInterval, self.portalIntervals[0]), Func(self.fountainNode.wrtReparentTo, self.portalParent), Func(self.portalNode.removeNode), LerpPosInterval(self.fountainNode, 3, (self.fountainNode.getX(self.portalParent) + 40.0, self.fountainNode.getY(self.portalParent) + 40.0, self.fountainNode.getZ(self.portalParent)), blendType='easeInOut'), LerpPosInterval(self.fountainNode, 5, (self.fountainNode.getX(self.portalParent) + 40.0, self.fountainNode.getY(self.portalParent) + 40.0, z), blendType='easeOut'))
        nodeDisappearSeq = Sequence()
        for x in range(4):
            node = self.portal.find('**/beam' + str(x + 1))
            nodeDisappear = LerpScaleInterval(node, 0.5, 0.1, blendType='easeInOut')
            nodeDisappearSeq.append(Sequence(Func(base.playSfx, self.portalDisappearSfx, node=self.portalNode), nodeDisappear, Func(node.removeNode)))

        portalDisappear = Sequence(Parallel(LerpColorScaleInterval(self.portal.find('**/beam'), 3, (1,
                                                                                                    1,
                                                                                                    1,
                                                                                                    0), blendType='easeInOut'), LerpScaleInterval(self.portal.find('**/beam'), 3, 0.01, blendType='easeInOut'), LerpScaleInterval(self.portal.find('**/base_shine'), 2, 0.01, blendType='easeInOut')), Func(self.cleanupInterval, self.portalIntervals[1]), Func(self.cleanupInterval, self.portalIntervals[2]), Wait(1), nodeDisappearSeq, Func(self.cleanupInterval, self.portalIntervals[3]))
        portalCloseSeq = Sequence(Func(self.togglePortalColl, False), portalDisappear, flipSeq)
        self.portalSeq.append(portalCloseSeq)

    def makeMeetHereSequence(self, npcId, avId):
        place = base.cr.playGame.getPlace()
        geom = place.loader.geom
        self.npc = NPCToons.createLocalNPC(npcId)
        toon = base.cr.doId2do.get(avId)
        if not toon:
            return
        self.portalSeq = Sequence(Wait(2), Func(self.npc.reparentTo, geom), Func(self.npc.setPos, 121.2, -53.5, 2.525), Func(self.npc.setH, 180), Func(self.npc.addActive), Func(self.npc.pose, 'teleport', self.npc.getNumFrames('teleport') - 1), Func(self.npc.setChatAbsolute, OTPLocalizer.TeleportGreeting % toon.getName(), CFSpeech | CFTimeout), self.npc.getTeleportInTrack(), Func(self.npc.loop, 'neutral'), Wait(1), Func(self.npc.clearChat), Wait(1), Func(self.npc.setChatAbsolute, OTPLocalizer.SpeedChatStaticTextToontown[1003], CFSpeech | CFQuicktalker | CFTimeout))

    def makeNoResponseSequence(self):
        if not self.npc:
            return
        self.portalSeq = Sequence(Func(self.npc.setChatAbsolute, OTPLocalizer.SpeedChatStaticTextToontown[109], CFSpeech | CFQuicktalker | CFTimeout), Wait(3), Func(self.npc.clearChat), Wait(1), Func(self.npc.setChatAbsolute, OTPLocalizer.SpeedChatStaticTextToontown[207], CFSpeech | CFQuicktalker | CFTimeout), self.npc.getTeleportOutTrack(), Func(self.npc.removeActive), Func(self.npc.detachNode), Func(self.npc.delete))