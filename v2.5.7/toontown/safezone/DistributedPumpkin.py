from panda3d.core import *
from direct.distributed.ClockDelta import *
from direct.interval.IntervalGlobal import *
from direct.distributed import DistributedNode
from direct.fsm import ClassicFSM, State
from direct.fsm import State
import Pumpkin

class DistributedPumpkin(Pumpkin.Pumpkin, DistributedNode.DistributedNode):

    def __init__(self, cr):
        try:
            self.DistributedPump_initialized
        except:
            self.DistributedPump_initialized = 1
            DistributedNode.DistributedNode.__init__(self, cr)
            Pumpkin.Pumpkin.__init__(self)