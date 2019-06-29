from panda3d.core import *
import DistributedCCharBase
from direct.directnotify import DirectNotifyGlobal
from direct.fsm import ClassicFSM, State
from direct.fsm import State
import CharStateDatas
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.hood import DGHood

class DistributedRiggy(DistributedCCharBase.DistributedCCharBase):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedRiggy')

    def __init__(self, cr):
        DistributedCCharBase.DistributedCCharBase.__init__(self, cr, 'Riggy', 'riggy')
        self.fsm = ClassicFSM.ClassicFSM(self.getName(), [State.State('Off', self.enterOff, self.exitOff, ['Neutral']),
         State.State('Neutral', self.enterNeutral, self.exitNeutral, ['Walk']),
         State.State('Walk', self.enterWalk, self.exitWalk, ['Neutral'])], 'Off', 'Off')
        self.fsm.enterInitialState()

    def disable(self):
        self.fsm.requestFinalState()
        DistributedCCharBase.DistributedCCharBase.disable(self)
        self.neutralDoneEvent = None
        self.neutral = None
        self.walkDoneEvent = None
        self.walk = None
        self.fsm.requestFinalState()
        return

    def delete(self):
        del self.fsm

    def generate(self):
        DistributedCCharBase.DistributedCCharBase.generate(self, self.diffPath)
        name = self.getName()
        self.neutralDoneEvent = self.taskName(name + '-neutral-done')
        self.neutral = CharStateDatas.CharNeutralState(self.neutralDoneEvent, self)
        self.walkDoneEvent = self.taskName(name + '-walk-done')
        if self.diffPath == None:
            self.walk = CharStateDatas.CharWalkState(self.walkDoneEvent, self)
        else:
            self.walk = CharStateDatas.CharWalkState(self.walkDoneEvent, self, self.diffPath)
        self.fsm.request('Neutral')
        return

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterNeutral(self):
        self.neutral.enter()
        self.acceptOnce(self.neutralDoneEvent, self.__decideNextState)

    def exitNeutral(self):
        self.ignore(self.neutralDoneEvent)
        self.neutral.exit()

    def enterWalk(self):
        self.walk.enter()
        self.acceptOnce(self.walkDoneEvent, self.__decideNextState)

    def exitWalk(self):
        self.ignore(self.walkDoneEvent)
        self.walk.exit()

    def __decideNextState(self, doneStatus):
        self.fsm.request('Neutral')

    def setWalk(self, srcNode, destNode, timestamp):
        if destNode and not destNode == srcNode:
            self.walk.setWalk(srcNode, destNode, timestamp)
            self.fsm.request('Walk')

    def walkSpeed(self):
        return 5.0