from direct.directnotify import DirectNotifyGlobal
from direct.fsm import StateData
from direct.gui.DirectGui import *
from panda3d.core import Vec4
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals

class EventSettingsGUI(DirectFrame, StateData.StateData):
    notify = DirectNotifyGlobal.directNotify.newCategory('EventSettingsGUI')

    def __init__(self, eventManager):
        DirectFrame.__init__(self, pos=(0, 0, 0.05), relief=None, image=DGG.getDefaultDialogGeom(), image_scale=(2.2,
                                                                                                                 1,
                                                                                                                 1.4), image_pos=(0,
                                                                                                                                  0,
                                                                                                                                  -0.05), image_color=ToontownGlobals.GlobalDialogColor, text=TTLocalizer.EventManagerSettings, text_scale=0.12, text_pos=(0,
                                                                                                                                                                                                                                                           0.5), borderWidth=(0.01,
                                                                                                                                                                                                                                                                              0.01))
        StateData.StateData.__init__(self, 'event-settings-done')
        self.setBin('gui-popup', 0)
        self.initialiseoptions(EventSettingsGUI)
        self.eventManager = eventManager
        self.textRolloverColor = Vec4(1, 1, 0, 1)
        self.textDownColor = Vec4(0.5, 0.9, 1, 1)
        self.textDisabledColor = Vec4(0.4, 0.8, 0.4, 1)
        return

    def unload(self):
        if self.isLoaded == 0:
            return
        self.isLoaded = 0
        self.exit()
        DirectFrame.destroy(self)

    def load(self):
        if self.isLoaded == 1:
            return
        self.isLoaded = 1
        gui = loader.loadModel('phase_3.5/models/gui/friendslist_gui')
        guiButton = loader.loadModel('phase_3/models/gui/quit_button')
        circleModel = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_nameShop')
        self.cancel = DirectButton(parent=self, relief=None, text=TTLocalizer.DisplaySettingsCancel, image=(
         guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), image_scale=(0.6,
                                                                                                                            1,
                                                                                                                            1), text_scale=TTLocalizer.DSDcancel, text_pos=TTLocalizer.DSDcancelPos, pos=(0.93,
                                                                                                                                                                                                          0,
                                                                                                                                                                                                          -0.65), command=self.__cancel)
        self.eventModeTitle = DirectLabel(parent=self, relief=None, pos=(0, 0, 0.35), text=TTLocalizer.EventManagerMode, text_scale=0.08)
        self.eventModeButton = DirectButton(parent=self, relief=None, text=TTLocalizer.EventManagerFreeMode, image=(
         guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), image_scale=(1,
                                                                                                                            1,
                                                                                                                            1), text_scale=TTLocalizer.DSDcancel, text_pos=TTLocalizer.DSDcancelPos, pos=(0,
                                                                                                                                                                                                          0,
                                                                                                                                                                                                          0.25), command=self.__toggleEventMode)
        self.eventModeDelay = DirectSlider(parent=self, text=TTLocalizer.EventManagerDelay, text_scale=0.08, text_pos=(0,
                                                                                                                       -0.12), pos=(0,
                                                                                                                                    0,
                                                                                                                                    0.1), value=1, range=(1,
                                                                                                                                                          10), pageSize=1.2, frameColor=(0.85,
                                                                                                                                                                                         0.95,
                                                                                                                                                                                         1,
                                                                                                                                                                                         1), thumb_geom=circleModel.find('**/tt_t_gui_mat_namePanelCircle'), thumb_relief=None, thumb_geom_scale=1, command=self.__changeDelay)
        self.eventMode = ToontownGlobals.EventManagerFreeMode
        self.eventDelay = 60
        gui.removeNode()
        guiButton.removeNode()
        circleModel.removeNode()
        self.hide()
        return

    def enter(self):
        if self.isEntered == 1:
            return
        self.isEntered = 1
        if self.isLoaded == 0:
            self.load()
        base.transitions.fadeScreen(0.5)
        self.show()

    def exit(self):
        if self.isEntered == 0:
            return
        self.isEntered = 0
        base.transitions.noTransitions()
        self.ignoreAll()
        self.hide()

    def __cancel(self):
        self.exit()

    def __toggleEventMode(self):
        if self.eventMode == ToontownGlobals.EventManagerFreeMode:
            self.eventMode = ToontownGlobals.EventManagerStrictMode
            self.eventModeButton['text'] = TTLocalizer.EventManagerStrictMode
        else:
            if self.eventMode == ToontownGlobals.EventManagerStrictMode:
                self.eventMode = ToontownGlobals.EventManagerFreeMode
                self.eventModeButton['text'] = TTLocalizer.EventManagerFreeMode

    def __changeDelay(self):
        delay = int(self.eventModeDelay['value'])
        if delay == 1:
            self.eventModeDelay['text'] = 'Delay (%s minute)' % delay
        else:
            self.eventModeDelay['text'] = 'Delay (%s minutes)' % delay
        self.eventDelay = delay * 60