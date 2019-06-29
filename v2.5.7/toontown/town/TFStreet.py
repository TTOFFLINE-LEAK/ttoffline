from direct.interval.IntervalGlobal import *
from direct.gui.OnscreenText import OnscreenText
from direct.interval.IntervalGlobal import *
from panda3d.core import *
from toontown.toonbase import ToontownGlobals
import Street

class TFStreet(Street.Street):

    def __init__(self, loader, parentFSM, doneEvent):
        Street.Street.__init__(self, loader, parentFSM, doneEvent)

    def load(self):
        Street.Street.load(self)

    def unload(self):
        Street.Street.unload(self)

    def doRequestLeave(self, requestStatus):
        self.fsm.request('trialerFA', [requestStatus])