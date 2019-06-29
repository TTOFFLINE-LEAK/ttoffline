import math, random
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from direct.task import Task
from toontown.battle import BattleProps
from toontown.suit import Suit, SuitDNA

class BackgroundFlyingCog(Suit.Suit):
    notify = DirectNotifyGlobal.directNotify.newCategory('BackgroundFlyingCog')

    def __init__(self, radius=0):
        Suit.Suit.__init__(self)
        self.prop = None
        self.radius = radius
        self.theta = 0.0
        self.dna = SuitDNA.SuitDNA()
        self.dna.newSuitRandom()
        self.setDNA(self.dna)
        self.pose('landing', 0)
        self.setPickable(0)
        self.attachPropeller()
        self.controlNode = render.attachNewNode('control')
        self.controlNode.setH(random.randrange(0, 360))
        self.flyTaskName = 'FlyTask' + str(id(self))
        return

    def cleanup(self):
        self.removeTask(self.flyTaskName)
        Suit.Suit.cleanup(self)

    def delete(self):
        self.controlNode.removeNode()
        self.detachPropeller()
        Suit.Suit.delete(self)

    def attachPropeller(self):
        if self.prop == None:
            self.prop = BattleProps.globalPropPool.getProp('propeller')
        self.prop.loop('propeller', fromFrame=0, toFrame=14)
        head = self.find('**/joint_head')
        self.prop.reparentTo(head)
        return

    def detachPropeller(self):
        if self.prop:
            self.prop.cleanup()
            self.prop.removeNode()
            self.prop = None
        return

    def setDNA(self, dna):
        if self.style:
            self.flush()
        self.style = dna
        self.generateSuit()
        self.initializeDropShadow()
        self.initializeNametag3d()

    def start(self):
        self.reparentTo(self.controlNode)
        self.setPos(0, 0, -self.radius * 0.5)
        self.setH(90)
        taskMgr.doMethodLater(0.001, self.flyTask, self.flyTaskName)

    def flyTask(self, task):
        try:
            self.theta = (self.theta + 0.1) % 360
            if self.theta == 270:
                self.detachPropeller()
                self.dna.newSuitRandom()
                self.setDNA(self.dna)
                self.pose('landing', 0)
                self.attachPropeller()
            self.setPos(math.cos(math.radians(self.theta)) * self.radius, 0, math.sin(math.radians(self.theta)) * self.radius * 0.5)
            return Task.again
        except:
            return Task.done