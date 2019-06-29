from direct.distributed.DistributedObject import DistributedObject
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase.AprilToonsGlobals import *
from toontown.toonbase import ToontownGlobals

class DistributedAprilToonsMgr(DistributedObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('AprilToonsMgr')

    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        cr.aprilToonsMgr = self
        self.events = []

    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        self.d_requestEventsList()

    def d_requestEventsList(self):
        self.notify.debug('Requesting events list from AI.')
        self.sendUpdate('requestEventsList', [])

    def requestEventsListResp(self, eventIds):
        self.events = eventIds
        self.checkActiveEvents()

    def isEventActive(self, eventId):
        if not base.cr.config.GetBool('want-april-toons', False):
            return False
        return eventId in self.events

    def setEventActive(self, eventId, active):
        if active and eventId not in self.events:
            self.events.append(eventId)
        else:
            if not active and eventId in self.events:
                del self.events[eventId]

    def checkActiveEvents(self):
        if self.isEventActive(EventGlobalGravity):
            base.localAvatar.controlManager.currentControls.setGravity(ToontownGlobals.GravityValue * 0.75)