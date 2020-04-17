from direct.actor.Actor import Actor
from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObject
from direct.interval.IntervalGlobal import *
from panda3d.core import *
from toontown.toonbase import ToontownGlobals

class DistributedTTCHQEventMgr(DistributedObject.DistributedObject):
    HQCollisionName = 'HQ-Collision-{}'
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedTTCHQEventMgr')

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        self.task = None
        self.oldHQ = None
        self.newHQ = None
        self.destroySeq = None
        self.colNodePath = None
        return

    def announceGenerate(self):
        DistributedObject.DistributedObject.announceGenerate(self)
        self.task = taskMgr.add(self._findHQ)
        self.cr.hq = self

    def _findHQ(self, task):
        hq = render.find('**/*hqTT*')
        if hq:
            self.placeHQ(hq)
            return task.done
        else:
            return task.cont

    def placeHQ(self, hq):
        self.oldHQ = hq
        self.newHQ = Actor('phase_14/models/modules/hqTT', {'shake': 'phase_14/models/modules/hqTT-shake', 'destroy': 'phase_14/models/modules/hqTT-fall', 
           'destroyed': 'phase_14/models/modules/hqTT-destroyed'})
        self.newHQ.reparentTo(render)
        self.newHQ.setPos(24.6425, 24.8587, 4.00001)
        self.newHQ.setH(135)
        self.newHQ.stash()
        cs = CollisionSphere(24.6425, 24.8587, 4.00001, 25)
        cs.setTangible(0)
        self.colNodePath = self.oldHQ.attachNewNode(CollisionNode('cnode'))
        self.colNodePath.node().addSolid(cs)
        self.colNodePath.node().setCollideMask(ToontownGlobals.WallBitmask)
        self.colNodePath.node().setName(self.HQCollisionName.format(self.getDoId()))
        self.accept('enter' + self.HQCollisionName.format(self.getDoId()), self.d_acceptStink)
        self.accept('exit' + self.HQCollisionName.format(self.getDoId()), self.d_rejectStink)

    def disable(self):
        self.ignoreAll()
        if self.destroySeq is not None:
            self.destroySeq.finish()
            self.destroySeq = None
        DistributedObject.DistributedObject.disable(self)
        return

    def delete(self):
        if self.task is not None:
            taskMgr.remove(self.task)
            self.task = None
        if self.newHQ is not None:
            self.newHQ.cleanup()
            self.newHQ.removeNode()
            self.newHQ = None
        self.oldHQ = None
        DistributedObject.DistributedObject.delete(self)
        return

    def die(self):
        self.destroySeq = Sequence(Func(self.newHQ.unstash), Func(self.oldHQ.stash), Func(self.newHQ.loop, 'shake'), Wait(2), ActorInterval(self.newHQ, 'destroy', startFrame=0, endFrame=24), Func(self.newHQ.loop, 'destroyed'), Wait(5), Func(self.newHQ.setPlayRate, -1, 'destroy'), ActorInterval(self.newHQ, 'destroy', startFrame=24, endFrame=0), Func(self.newHQ.setPlayRate, 1, 'destroy'), Func(self.oldHQ.unstash), Func(self.newHQ.stash))
        self.destroySeq.start()

    def d_acceptStink(self, _=None):
        self.sendUpdate('acceptStink', [])

    def d_rejectStink(self, _=None):
        self.sendUpdate('rejectStink', [])