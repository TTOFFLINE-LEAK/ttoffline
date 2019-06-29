from panda3d.core import NodePath, Point3, CollisionSphere, CollisionNode, Vec4
from direct.interval.IntervalGlobal import Sequence, LerpPosInterval, Parallel, LerpScaleInterval, Track, ParticleInterval, Wait, Func
from toontown.toonbase import ToontownGlobals
from toontown.coghq import MoleFieldBase
from direct.particles import ParticleEffect
from toontown.battle import BattleParticles
from toontown.battle import BattleProps

class MoleHillProp(NodePath):

    def __init__(self, x, y, z):
        NodePath.__init__(self, 'MoleHill')
        self.loadModel()
        self.reparentTo(render)
        self.setPos(x, y, z)
        self.schedule = []
        self.popIval = None
        self.downIval = None
        self.popupNum = 0
        self.hillType = None
        self.isUp = 0
        return

    def loadModel(self):
        self.hill = loader.loadModel('phase_12/models/bossbotHQ/mole_hole')
        self.hill.setZ(0.0)
        self.hill.reparentTo(self)
        self.mole = self.attachNewNode('mole')
        self.mole.reparentTo(self)
        self.mole.setScale(0.75)
        self.mole.setZ(-2.5)
        self.moleHead = loader.loadModel('phase_12/models/bossbotHQ/mole_norm')
        self.moleHead.reparentTo(self.mole)
        moleColName = 'moleCol'
        moleSphere = CollisionSphere(0, 0, 0, 1.0)
        collNode = CollisionNode(moleColName)
        collNode.setIntoCollideMask(ToontownGlobals.WallBitmask)
        collNode.addSolid(moleSphere)
        self.moleColNodePath = self.mole.attachNewNode(collNode)
        self.moleColNodePath.stash()
        self.moleColNodePath.setScale(1.0)

    def destroy(self):
        if self.popIval:
            self.popIval.pause()
            self.popIval = None
        if self.downIval:
            self.downIval.pause()
            self.downIval = None
        self.removeNode()
        return

    def switchUp(self):
        self.isUp = 1

    def switchDown(self):
        self.isUp = 0

    def setHillType(self, type):
        self.hillType = type
        self.moleHead.removeNode()
        if type == MoleFieldBase.HILL_MOLE:
            self.moleHead = loader.loadModel('phase_12/models/bossbotHQ/mole_norm')
            self.moleColNodePath.setScale(3.0)
            self.moleHead.setH(0)
        else:
            if type == MoleFieldBase.HILL_WHACKED:
                self.moleHead = loader.loadModel('phase_12/models/bossbotHQ/mole_hit')
                self.mole.setBillboardAxis(0)
                self.moleColNodePath.setScale(0.0)
                if self.popIval:
                    self.popIval.finish()
                if self.downIval:
                    self.downIval.finish()
                self.mole.setPos(0.0, 0.0, 0.0)
                self.popIval = Sequence(Parallel(Sequence(LerpPosInterval(self.moleHead, 0.05, Point3(0.18, 0.0, 0.0)), LerpPosInterval(self.moleHead, 0.05, Point3(0.0, -0.13, 0.0)), LerpPosInterval(self.moleHead, 0.05, Point3(0.0, 0.0, 0.18)), LerpPosInterval(self.moleHead, 0.05, Point3(-0.15, 0.0, 0.0)), LerpPosInterval(self.moleHead, 0.05, Point3(0.0, 0.18, 0.0)), LerpPosInterval(self.moleHead, 0.05, Point3(0.11, 0.0, 0.0)), LerpPosInterval(self.moleHead, 0.05, Point3(0.0, -0.12, 0.0)), LerpPosInterval(self.moleHead, 0.05, Point3(0.0, 0.0, 0.18)), LerpPosInterval(self.moleHead, 0.05, Point3(-0.18, 0.0, 0.0)), LerpPosInterval(self.moleHead, 0.05, Point3(0.0, 0.13, 0.0)), LerpPosInterval(self.moleHead, 0.05, Point3(0.18, 0.0, 0.0)), LerpPosInterval(self.moleHead, 0.05, Point3(0.0, -0.15, 0.0)), LerpPosInterval(self.moleHead, 0.05, Point3(0.0, 0.0, 0.18)), LerpPosInterval(self.moleHead, 0.05, Point3(-0.16, 0.0, 0.0)), LerpPosInterval(self.moleHead, 0.05, Point3(0.0, 0.18, 0.0)), LerpPosInterval(self.moleHead, 0.05, Point3(0.11, 0.0, 0.0)), LerpPosInterval(self.moleHead, 0.05, Point3(0.0, -0.18, 0.0)), LerpPosInterval(self.moleHead, 0.05, Point3(0.0, 0.0, 0.17)), LerpPosInterval(self.moleHead, 0.05, Point3(-0.18, 0.0, 0.0)), LerpPosInterval(self.moleHead, 0.05, Point3(0.0, 0.0, 0.0))), Sequence(LerpScaleInterval(self.moleHead, 0.5, 3.5), LerpScaleInterval(self.moleHead, 0.5, 1.0))), LerpPosInterval(self.mole, 0.5, Point3(0, 0, -2.5)), Func(self.setHillType, MoleFieldBase.HILL_MOLE))
                self.popIval.start()
        self.moleHead.reparentTo(self.mole)

    def doMolePop(self, startTime, timeToMoveUp, timeToStayUp, timeToMoveDown, moleType):
        if self.hillType == MoleFieldBase.HILL_WHACKED:
            return
        if self.popIval:
            self.popIval.pause()
        if self.downIval:
            self.downIval.pause()
            self.downIval = None
        moleColor = None
        self.switchUp()
        self.popupNum += 1
        self.popIval = Sequence(Func(self.setHillType, moleType), LerpPosInterval(self.mole, timeToMoveUp, Point3(0, 0, 0.0)), Func(self.moleColNodePath.unstash), Wait(timeToStayUp), Func(self.stashMoleCollision), LerpPosInterval(self.mole, timeToMoveDown, Point3(0, 0, -2.5)), Func(self.switchDown))
        self.popIval.start()
        return

    def setGameStartTime(self, gameStartTime):
        self.gameStartTime = gameStartTime
        self.popupNum = 0

    def stashMoleCollision(self):
        self.moleColNodePath.stash()

    def getPopupNum(self):
        return self.popupNum

    def doMoleDown(self):
        if self.hillType == MoleFieldBase.HILL_WHACKED or self.hillType == MoleFieldBase.HILL_COGWHACKED:
            return
        if self.popIval:
            self.popIval.pause()
            self.popIval = None
        if self.downIval:
            self.downIval.pause()
        self.downIval = Sequence(Func(self.stashMoleCollision), LerpPosInterval(self.mole, 1, Point3(0, 0, -2.5)), Func(self.switchDown))
        self.downIval.start()
        return

    def forceMoleDown(self):
        if self.popIval:
            self.popIval.pause()
            self.popIval = None
        if self.downIval:
            self.downIval.pause()
            self.downIval = None
        self.stashMoleCollision()
        self.switchDown()
        self.mole.setPos(0, 0, -2.5)
        return