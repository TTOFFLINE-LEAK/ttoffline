from panda3d.core import *
from direct.distributed.ClockDelta import *
from direct.distributed import DistributedObject
from direct.interval.IntervalGlobal import *
from direct.task import Task
from toontown.toonbase import ToontownGlobals
import random
SPIN_RATE = 1.25
MIN_HEIGHT = 2.0

class DistributedDGFlower(DistributedObject.DistributedObject):

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        self.moveIval = None
        self.easterEggActivated = False
        return

    def generate(self):
        DistributedObject.DistributedObject.generate(self)
        self.bigFlower = loader.loadModel('phase_8/models/props/DG_flower-mod.bam')
        self.bigFlower.setPos(1.39, 92.91, 2.0)
        self.bigFlower.setScale(2.5)
        self.bigFlower.reparentTo(render)
        self.flowerCollSphere = CollisionSphere(0, 0, 0, 4.5)
        self.flowerCollSphereNode = CollisionNode('bigFlowerCollide')
        self.flowerCollSphereNode.addSolid(self.flowerCollSphere)
        self.flowerCollSphereNode.setCollideMask(ToontownGlobals.WallBitmask)
        self.bigFlower.attachNewNode(self.flowerCollSphereNode)
        self.flowerTrigSphere = CollisionSphere(0, 0, 0, 6.0)
        self.flowerTrigSphere.setTangible(0)
        self.flowerTrigSphereNode = CollisionNode('bigFlowerTrigger')
        self.flowerTrigSphereNode.addSolid(self.flowerTrigSphere)
        self.flowerTrigSphereNode.setCollideMask(ToontownGlobals.WallBitmask)
        self.bigFlower.attachNewNode(self.flowerTrigSphereNode)
        taskMgr.add(self.__flowerSpin, self.taskName('DG-flowerSpin'))
        self.accept('enterbigFlowerTrigger', self.__flowerEnter)
        self.accept('exitbigFlowerTrigger', self.__flowerExit)
        self.easterEggSfx = loader.loadSfx('phase_5/audio/sfx/SA_canned_impact_only.ogg')

    def disable(self):
        DistributedObject.DistributedObject.disable(self)
        if self.moveIval:
            self.moveIval.finish()
            self.moveIval = None
        taskMgr.remove(self.taskName('DG-flowerSpin'))
        self.ignore('enterbigFlowerTrigger')
        self.ignore('exitbigFlowerTrigger')
        return

    def delete(self):
        DistributedObject.DistributedObject.delete(self)
        self.bigFlower.removeNode()
        del self.moveIval
        del self.bigFlower
        del self.flowerCollSphere
        del self.flowerCollSphereNode
        del self.easterEggSfx

    def __flowerSpin(self, task):
        self.bigFlower.setH(self.bigFlower.getH() + SPIN_RATE)
        return Task.cont

    def __flowerEnter(self, collisionEntry):
        self.sendUpdate('avatarEnter', [])

    def __flowerExit(self, collisionEntry):
        self.sendUpdate('avatarExit', [])

    def setHeight(self, newHeight):
        time = 0.5
        if self.easterEggActivated:
            newHeight = 15.0
            time = 5.0
        pos = self.bigFlower.getPos()
        self.moveIval = self.bigFlower.posInterval(time, (pos[0], pos[1], newHeight), blendType='easeOut', name=self.taskName('DG-flowerRaise'))
        self.moveIval.start()

    def soundBreak(self, pos):
        growTrack = Parallel()
        wait = 0
        for circle in xrange(0, 5):
            ring = loader.loadModel('phase_5/models/props/uberSoundEffects').find('**/Circle')
            ring.setTransparency(TransparencyAttrib.MAlpha)
            ring.setP(90)
            growTrack.append(Sequence(Wait(wait), Func(ring.reparentTo, render), Func(ring.setPos, pos[0], pos[1], 0.025), Parallel(ring.scaleInterval(0.5, (50,
                                                                                                                                                             50,
                                                                                                                                                             50)), Sequence(Wait(0.25), ring.colorInterval(0.25, (0,
                                                                                                                                                                                                                  0,
                                                                                                                                                                                                                  0,
                                                                                                                                                                                                                  0)))), Func(ring.removeNode)))
            wait = wait + 0.03

        growTrack.start()

    def shake(self, avIds):
        for avId in avIds:
            toon = base.cr.doId2do.get(avId)
            if toon:
                fall = random.choice(['slip-forward', 'slip-backward'])
                Sequence(ActorInterval(toon, fall), Func(toon.loop, 'neutral')).start()

    def activateEasterEgg(self, avIds):
        self.easterEggActivated = True
        pos = self.bigFlower.getPos()
        seq = Sequence(Wait(5), Func(self.soundBreak, pos), Func(base.localAvatar.disableAvatarControls), Func(self.shake, avIds), Func(self.easterEggSfx.play), self.bigFlower.posInterval(0.5, (pos[0], pos[1], MIN_HEIGHT)), Func(self.deactivateEasterEgg)).start()

    def deactivateEasterEgg(self):
        self.easterEggActivated = False