from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.fsm import StateData
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer

class InfoGUI(DirectFrame, StateData.StateData):
    notify = DirectNotifyGlobal.directNotify.newCategory('InfoGUI')

    def __init__(self, avChooser):
        DirectFrame.__init__(self, pos=(0, 0, 0.05), relief=None, image=DGG.getDefaultDialogGeom(), image_scale=(2.2,
                                                                                                                 1,
                                                                                                                 1.4), image_pos=(0,
                                                                                                                                  0,
                                                                                                                                  -0.05), image_color=ToontownGlobals.GlobalDialogColor, text=TTLocalizer.AvatarChooserInfo, text_scale=0.12, text_pos=(0,
                                                                                                                                                                                                                                                        0.5), borderWidth=(0.01,
                                                                                                                                                                                                                                                                           0.01))
        StateData.StateData.__init__(self, 'info-gui-done')
        self.isLoaded = False
        self.setBin('gui-popup', 0)
        self.initialiseoptions(InfoGUI)
        self.avChooser = avChooser
        self.textRolloverColor = Vec4(1, 1, 0, 1)
        self.textDownColor = Vec4(0.5, 0.9, 1, 1)
        self.textDisabledColor = Vec4(0.4, 0.8, 0.4, 1)
        self.descPos = (0.485, 0, -0.2)
        self.halloweenMiniserver = None
        self.halloweenMiniserverSeq = None
        return

    def unload(self):
        if not self.isLoaded:
            return
        self.isLoaded = False
        self.exit()
        DirectFrame.destroy(self)

    def load(self):
        if self.isLoaded:
            return
        self.isLoaded = True
        gui = loader.loadModel('phase_3.5/models/gui/friendslist_gui')
        guiButton = loader.loadModel('phase_3/models/gui/quit_button')
        if base.cr.holidayValue == 1:
            ImagePath = 'phase_14.5/maps/halloween_server_1.png'
        else:
            if base.cr.holidayValue == 2:
                ImagePath = 'phase_14.5/maps/halloween_server_3.png'
            else:
                if base.cr.holidayValue == 3:
                    ImagePath = 'phase_14.5/maps/halloween_server_5.png'
                else:
                    if base.cr.holidayValue == 4:
                        ImagePath = 'phase_14.5/maps/halloween_server_2.png'
                    else:
                        if base.cr.holidayValue == 5:
                            ImagePath = 'phase_14.5/maps/halloween_server_4.png'
                        else:
                            if base.cr.holidayValue == 6:
                                ImagePath = 'phase_14.5/maps/halloween_server_4.png'
        self.sname = DirectLabel(parent=self, text=TTLocalizer.ServerPageName % base.cr.serverName, relief=None, pos=(0.0,
                                                                                                                      0.0,
                                                                                                                      0.35), scale=0.079, text_fg=Vec4(0, 0, 0, 1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getToonFont())
        self.description = DirectLabel(parent=self, text=TTLocalizer.InfoDescription + base.cr.serverDescription, relief=None, pos=(0.0,
                                                                                                                                    0.0,
                                                                                                                                    0.25), scale=0.069, text_fg=Vec4(0, 0, 0, 1), text_wordwrap=24, text_align=TextNode.ACenter, text_font=ToontownGlobals.getToonFont())
        self.cancel = DirectButton(parent=self, relief=None, text=TTLocalizer.DisplaySettingsCancel, image=(guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), image_scale=(0.6,
                                                                                                                                                                                                                               1,
                                                                                                                                                                                                                               1), text_scale=TTLocalizer.DSDcancel, text_pos=TTLocalizer.DSDcancelPos, pos=(0.93,
                                                                                                                                                                                                                                                                                                             0,
                                                                                                                                                                                                                                                                                                             -0.65), command=self.__cancel)
        if base.cr.isHalloween and base.cr.holidayValue != 0:
            self.halloweenMiniserver = OnscreenImage(image=ImagePath, pos=(0.0, 0,
                                                                           -0.13), scale=(0.3125,
                                                                                          0.3125,
                                                                                          0.25))
            self.halloweenMiniserver.reparentTo(self)
            self.halloweenMiniserver.setTransparency(TransparencyAttrib.MAlpha)
            self.halloweenMiniserverSeq = Sequence(self.halloweenMiniserver.scaleInterval(3, (0.5,
                                                                                              0.5,
                                                                                              0.4), blendType='easeInOut'), self.halloweenMiniserver.scaleInterval(3, (0.3125,
                                                                                                                                                                       0.3125,
                                                                                                                                                                       0.25), blendType='easeInOut'))
            self.halloweenMiniserverSeq.loop()
            self.event = DirectLabel(text='A unqiue Halloween event is\nactive on this Mini-Server!', relief=None, pos=(0.0,
                                                                                                                        0.0,
                                                                                                                        -0.6), scale=0.069, text_fg=Vec4(0, 0, 0, 1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getToonFont())
            self.event.reparentTo(self)
            self.eventSeq = Sequence(Wait(1.4), Func(self.event.setColorScale, 1, 1, 1, 0), Wait(1.4), Func(self.event.setColorScale, 1, 1, 1, 1))
            self.eventSeq.loop()
        gui.removeNode()
        guiButton.removeNode()
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