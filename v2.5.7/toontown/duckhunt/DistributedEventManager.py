from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObject import DistributedObject
from direct.gui.DirectGui import *
from toontown.duckhunt.EventSettingsGUI import EventSettingsGUI
from toontown.hood import ZoneUtil
from toontown.toonbase import ToontownGlobals, TTLocalizer

class DistributedEventManager(DistributedObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedEventManager')
    neverDisable = 1

    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        self.isElections = False
        self.settingsButton = None
        self.startEventButton = None
        self.eventSettings = None
        self.eventStarted = False
        return

    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        self.determineEvent()

    def determineEvent(self):
        electionsActive = config.GetBool('want-doomsday', False)
        if electionsActive:
            self.isElections = True

    def showAdminGui(self):
        if base.localAvatar.getAdminAccess() < 407 or self.eventStarted:
            return
        gui = loader.loadModel('phase_3/models/gui/pick_a_toon_gui')
        font = ToontownGlobals.getSignFont()
        textFg = (0.977, 0.816, 0.133, 1)
        settingsButtonPos = (-0.456, 0, 0.223)
        startEventButtonPos = (-0.456, 0, 0.093)
        quitHover = gui.find('**/QuitBtn_RLVR')
        self.settingsButton = DirectButton(image=(quitHover, quitHover, quitHover), relief=None, text=TTLocalizer.EventManagerSettings, text_font=font, text_fg=textFg, text_pos=TTLocalizer.EMsettingsButtonPos, text_scale=TTLocalizer.EMsettingsButton, image_scale=1, image1_scale=1.05, image2_scale=1.05, scale=1.05, pos=settingsButtonPos, command=self.openAdminSettings)
        self.settingsButton.reparentTo(base.a2dBottomRight)
        self.settingsButton.flattenMedium()
        self.startEventButton = DirectButton(image=(quitHover, quitHover, quitHover), relief=None, text=TTLocalizer.EventManagerStartEvent, text_font=font, text_fg=textFg, text_pos=TTLocalizer.EMstartEventButtonPos, text_scale=TTLocalizer.EMstartEventButton, image_scale=1, image1_scale=1.05, image2_scale=1.05, scale=1.05, pos=startEventButtonPos, command=self.startEvent)
        self.startEventButton.reparentTo(base.a2dBottomRight)
        self.startEventButton.flattenMedium()
        return

    def hideAdminGui(self):
        if self.settingsButton:
            self.settingsButton.removeNode()
        if self.startEventButton:
            self.startEventButton.removeNode()

    def openAdminSettings(self):
        if base.localAvatar.getAdminAccess() < 407:
            return
        if not self.eventSettings:
            self.eventSettings = EventSettingsGUI(self)
        self.eventSettings.enter()

    def startEvent(self):
        if base.localAvatar.getAdminAccess() < 407:
            return
        if self.eventStarted == True:
            base.localAvatar.setSystemMessage(0, "You've already started the event!")
            return
        self.hideAdminGui()
        if not self.eventSettings:
            eventMode = ToontownGlobals.EventManagerFreeMode
            eventDelay = 60
        else:
            eventMode = self.eventSettings.eventMode
            eventDelay = self.eventSettings.eventDelay
        self.sendUpdate('setEventMode', [eventMode])
        self.sendUpdate('setEventDelay', [eventDelay])
        self.sendUpdate('startEvent', [])

    def setEventStarted(self, eventStarted):
        self.eventStarted = eventStarted

    def requestTeleport(self, loaderId, whereId, hoodId, zoneId, avId):
        place = base.cr.playGame.getPlace()
        if loaderId == '':
            loaderId = ZoneUtil.getBranchLoaderName(zoneId)
        if whereId == '':
            whereId = ZoneUtil.getToonWhereName(zoneId)
        if hoodId == 0:
            hoodId = place.loader.hood.id
        if avId == 0:
            avId = -1
        place.fsm.forceTransition('teleportOut', [
         {'loader': loaderId, 'where': whereId, 
            'how': 'teleportIn', 
            'hoodId': hoodId, 
            'zoneId': zoneId, 
            'shardId': None, 
            'avId': avId}])
        return