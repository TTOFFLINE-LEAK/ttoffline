from panda3d.core import *
from direct.distributed import DistributedObject
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *

class DistributedPresent(DistributedObject.DistributedObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPresent')

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        self.x = 0
        self.y = 0
        self.z = 0
        self.h = 0
        self.p = 0
        self.r = 0
        self.modelId = 1
        self.model = None
        self.collNode = None
        self.fadeInSeq = None
        self.idleSeq = None
        self.collectSeq = None
        self.vanishSeq = None
        self.collNodeName = 'present_collision-%d' % id(self)
        self.unavailable = False
        self.presentSfx = loader.loadSfx('phase_4/audio/sfx/MG_pairing_match_bonus_both.ogg')
        return

    def announceGenerate(self):
        self.collNodeName = self.uniqueName('present_collision')
        if not self.unavailable:
            self.respawn()

    def disable(self):
        self.ignoreAll()
        if self.fadeInSeq:
            self.fadeInSeq.finish()
            self.fadeInSeq = None
        if self.collectSeq:
            self.collectSeq.finish()
            self.collectSeq = None
        if self.idleSeq:
            self.idleSeq.finish()
            self.idleSeq = None
        if self.vanishSeq:
            self.vanishSeq.finish()
            self.vanishSeq = None
        if self.model:
            self.model.removeNode()
            self.model = None
        if self.collNode:
            self.collNode.clearSolids()
            self.collNode = None
        self.presentSfx = None
        DistributedObject.DistributedObject.disable(self)
        return

    def setPosHpr(self, x, y, z, h, p, r):
        self.x = x
        self.y = y
        self.z = z
        self.h = h
        self.p = p
        self.r = r

    def setModelId(self, id):
        self.modelId = id

    def setUnavailable(self, avail):
        if avail:
            if self.model:
                self.disablePresent()
        else:
            self.respawn()
        self.unavailable = avail

    def respawn(self):
        if not self.model:
            self.model = loader.loadModel(('phase_14/models/props/christmasBox{0}').format(self.modelId))
            self.model.reparentTo(render)
            self.model.setPosHpr(self.x, self.y, self.z, self.h, self.p, self.r)
        if self.fadeInSeq:
            self.fadeInSeq = None
        if self.idleSeq:
            self.idleSeq = None
        self.fadeInSeq = LerpFunctionInterval(self.model.setAlphaScale, toData=1.0, fromData=0.0, duration=1)
        self.fadeInSeq.start()
        self.idleSeq = Sequence(self.model.posHprInterval(6.9, (self.x, self.y, self.z + 1), (self.h, 0, 0), blendType='easeInOut'), self.model.posHprInterval(16.9, (self.x, self.y, self.z), (self.h + 360, 0, 0), blendType='easeInOut'))
        self.idleSeq.loop()
        cs = CollisionSphere(0, 0, 0, 3)
        self.collNode = self.model.attachNewNode(CollisionNode('cnode1')).node()
        self.collNode.addSolid(cs)
        self.collNode.setName(self.collNodeName)
        self.model.unstash()
        self.acceptOnce(('enter{0}').format(self.collNodeName), self.reward)
        return

    def disablePresent(self):
        self.vanishSeq = LerpFunctionInterval(self.model.setAlphaScale, toData=0.0, fromData=1.0, duration=1)
        self.vanishSeq.start()
        self.collectSeq = Sequence(Func(base.playSfx, self.presentSfx, volume=0.9), Wait(1), Func(self.model.stash), Func(self.idleSeq.finish))
        self.collectSeq.start()

    def reward(self, collEntry):
        self.sendUpdate('giveReward', [])