from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedNodeAI

class DistributedPumpkinAI(DistributedNodeAI.DistributedNodeAI):

    def __init__(self, air):
        try:
            self.DistributedPumpkinAI_initialized
        except:
            self.DistributedPumpkinAI_initialized = 1
            DistributedNodeAI.DistributedNodeAI.__init__(self, air)
            self.size = ''

    def setSize(self, size):
        self.size = size
        self.sendUpdate('setSize', [size])

    def getSize(self):
        return self.size