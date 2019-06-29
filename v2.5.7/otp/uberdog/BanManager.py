from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal

class BanManager(DistributedObjectGlobal):

    def __init__(self, cr):
        DistributedObjectGlobal.__init__(self, cr)

    def d_sendHardwareId(self, hwId):
        self.sendUpdate('sendHardwareId', [hwId])