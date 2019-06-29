from panda3d.core import *
from direct.distributed.ClockDelta import *
from direct.distributed import DistributedObject
from direct.interval.IntervalGlobal import *
from toontown.toonbase import ToontownGlobals
from direct.task import Task
import random
SPIN_RATE = 12.5

class DistributedDGFlower(DistributedObject.DistributedObject):

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)

    def generate(self):
        DistributedObject.DistributedObject.generate(self)
        self.bigFlower = loader.loadModel('phase_8/models/props/DG_flower-mod')
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

    def disable(self):
        DistributedObject.DistributedObject.disable(self)
        taskMgr.remove(self.taskName('DG-flowerRaise'))
        taskMgr.remove(self.taskName('DG-flowerSpin'))
        self.ignore('enterbigFlowerTrigger')
        self.ignore('exitbigFlowerTrigger')

    def delete(self):
        DistributedObject.DistributedObject.delete(self)
        self.bigFlower.removeNode()
        del self.bigFlower
        del self.flowerCollSphere
        del self.flowerCollSphereNode

    def __flowerSpin(self, task):
        self.bigFlower.setH(self.bigFlower.getH() + SPIN_RATE * globalClock.getDt())
        return Task.cont

    def __flowerEnter(self, collisionEntry):
        self.sendUpdate('avatarEnter', [])

    def __flowerExit(self, collisionEntry):
        self.sendUpdate('avatarExit', [])

    def setHeight(self, newHeight, optional):
        if optional:
            self.__doomToons(newHeight)
        else:
            pos = self.bigFlower.getPos()
            self.bigFlower.posInterval(0.5, (pos[0], pos[1], newHeight)).start()

    def soundBreak(self):
        growTrack = Parallel()
        wait = 0
        for circle in range(0, 5):
            ring = loader.loadModel('phase_5/models/props/uberSoundEffects').find('**/Circle')
            ring.setTransparency(TransparencyAttrib.MAlpha)
            ring.setP(90)
            growTrack.append(Sequence(Wait(wait), Func(ring.reparentTo, self.bigFlower), Parallel(ring.scaleInterval(0.5, (40,
                                                                                                                           40,
                                                                                                                           40)), Sequence(Wait(0.25), ring.colorInterval(0.25, (0,
                                                                                                                                                                                0,
                                                                                                                                                                                0,
                                                                                                                                                                                0)))), Func(ring.removeNode)))
            wait = wait + 0.03

        growTrack.start()

    def shake(self):
        fall = random.choice(['slip-forward', 'slip-backward'])
        Sequence(ActorInterval(base.localAvatar, fall), Func(base.localAvatar.loop, 'neutral')).start()

    def __doomToons(self, newHeight):
        pos = self.bigFlower.getPos()
        seq = Sequence(Wait(5), Func(self.soundBreak), Func(self.shake), self.bigFlower.posInterval(0.5, (pos[0], pos[1], newHeight))).start()