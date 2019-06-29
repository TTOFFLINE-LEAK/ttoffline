from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObject import DistributedObject

class DistributedToonFestActivities(DistributedObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedToonFestActivities')

    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        self.defaultSignModel = loader.loadModel('phase_13/models/parties/eventSign')
        self.activityIconsModel = loader.loadModel('phase_4/models/parties/eventSignIcons')