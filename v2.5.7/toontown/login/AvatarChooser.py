from panda3d.core import *
from toontown.toonbase import ToontownGlobals
from direct.filter.CommonFilters import CommonFilters
from direct.fsm import StateData
from direct.fsm import ClassicFSM, State
from direct.fsm import State
from toontown.launcher import DownloadForceAcknowledge
from direct.gui.DirectGui import *
from toontown.toonbase import TTLocalizer
from toontown.toonbase import DisplayOptions
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from toontown.toon import ToonDNA
from toontown.episodes.EpisodeSelector import EpisodeSelector
from toontown.toontowngui import TTDialog
from toontown.toonbase import TTLocalizer
from toontown.login.InfoGUI import InfoGUI
import AvatarChoice, random, time
MAX_AVATARS = 6
if config.GetBool('want-retro-mode', False):
    POSITIONS = (
     Vec3(-0.82, 0, 0.35), Vec3(0, 0, 0.35),
     Vec3(0.82, 0, 0.35), Vec3(-0.82, 0, -0.47),
     Vec3(0, 0, -0.47), Vec3(0.82, 0, -0.47))
    COLORS = (
     Vec4(0.917, 0.164, 0.164, 1), Vec4(0.152, 0.75, 0.258, 1),
     Vec4(0.598, 0.402, 0.875, 1),
     Vec4(0.133, 0.59, 0.977, 1),
     Vec4(0.895, 0.348, 0.602, 1),
     Vec4(0.977, 0.816, 0.133, 1))
else:
    POSITIONS = (
     Vec3(-0.840167, 0, 0.359333),
     Vec3(0.00933349, 0, 0.306533),
     Vec3(0.862, 0, 0.3293),
     Vec3(-0.863554, 0, -0.445659),
     Vec3(0.00999999, 0, -0.5181),
     Vec3(0.864907, 0, -0.445659))
    COLORS = (Vec4(0.917, 0.164, 0.164, 1),
     Vec4(0.152, 0.75, 0.258, 1),
     Vec4(0.598, 0.402, 0.875, 1),
     Vec4(0.133, 0.59, 0.977, 1),
     Vec4(0.895, 0.348, 0.602, 1),
     Vec4(0.977, 0.816, 0.133, 1))
chooser_notify = DirectNotifyGlobal.directNotify.newCategory('AvatarChooser')

class AvatarChooser(StateData.StateData):

    def __init__(self, avatarList, parentFSM, doneEvent):
        StateData.StateData.__init__(self, doneEvent)
        self.choice = None
        self.avatarList = avatarList
        self.displayOptions = None
        self.fsm = ClassicFSM.ClassicFSM('AvatarChooser', [State.State('Choose', self.enterChoose, self.exitChoose, ['CheckDownload']), State.State('CheckDownload', self.enterCheckDownload, self.exitCheckDownload, ['Choose'])], 'Choose', 'Choose')
        self.fsm.enterInitialState()
        self.parentFSM = parentFSM
        self.parentFSM.getCurrentState().addChild(self.fsm)
        self.episodeToonExists = False
        self.choseEpisodeToon = False
        self.blur = None
        return

    def enter(self):
        self.notify.info('AvatarChooser.enter')
        if not self.displayOptions:
            self.displayOptions = DisplayOptions.DisplayOptions()
        self.notify.info('calling self.displayOptions.restrictToEmbedded(False)')
        if base.appRunner:
            self.displayOptions.loadFromSettings()
            self.displayOptions.restrictToEmbedded(False)
        if self.isLoaded == 0:
            self.load()
        base.disableMouse()
        self.title.reparentTo(aspect2d)
        self.quitButton.show()
        if config.GetBool('want-episodes', False):
            self.episodesButton.show()
        if config.GetBool('want-info-gui', False):
            self.infoButton.show()
        if base.cr.supportsRelogin():
            self.logoutButton.show()
        base.setBackgroundColor(Vec4(0.145, 0.368, 0.78, 1))
        self.pickAToonBG.setBin('background', 1)
        self.pickAToonBG.reparentTo(aspect2d)
        choice = config.GetInt('auto-avatar-choice', -1)
        for panel in self.panelList:
            panel.show()
            self.accept(panel.doneEvent, self.__handlePanelDone)
            if panel.position == choice and panel.mode == AvatarChoice.AvatarChoice.MODE_CHOOSE:
                self.__handlePanelDone('chose', panelChoice=choice)

        if loader.loadingScreen.coolRender:
            loader.loadingScreen.coolRender.removeNode()
            loader.loadingScreen.coolRender = None
        return

    def exit(self):
        if self.isLoaded == 0:
            return
        for panel in self.panelList:
            panel.hide()

        self.ignoreAll()
        self.title.reparentTo(hidden)
        self.episodesButton.hide()
        self.logoutButton.hide()
        self.infoButton.hide()
        self.quitButton.hide()
        self.pickAToonBG.reparentTo(hidden)
        base.setBackgroundColor(ToontownGlobals.DefaultBackgroundColor)
        return

    def load(self, isPaid):
        if self.isLoaded == 1:
            return
        self.isPaid = isPaid
        gui = loader.loadModel('phase_3/models/gui/pick_a_toon_gui')
        gui2 = loader.loadModel('phase_3/models/gui/quit_button')
        guiClose = loader.loadModel('phase_3.5/models/gui/avatar_panel_gui')
        if config.GetBool('want-retro-mode', False):
            newGui = loader.loadModel('phase_3/models/gui/tt_m_gui_pat_mainGui_retro')
        else:
            if config.GetBool('want-doomsday', False):
                newGui = loader.loadModel('phase_3/models/gui/tt_m_gui_pat_mainGui_elections')
            else:
                if base.cr.isHalloween:
                    gui = loader.loadModel('phase_3/models/gui/pick_a_toon_gui_halloween')
                    newGui = loader.loadModel('phase_3/models/gui/tt_m_gui_pat_mainGui_halloween')
                else:
                    if base.cr.isWinter:
                        newGui = loader.loadModel('phase_3/models/gui/tt_m_gui_pat_mainGui_christmas')
                    else:
                        newGui = loader.loadModel('phase_3/models/gui/tt_m_gui_pat_mainGui')
        self.pickAToonBG = newGui.find('**/tt_t_gui_pat_background')
        self.pickAToonBG.reparentTo(hidden)
        self.pickAToonBG.setPos(0.0, 2.73, 0.0)
        self.pickAToonBG.setScale(1, 1, 1)
        if config.GetBool('want-retro-mode', False):
            self.title = OnscreenText(TTLocalizer.AvatarChooserPickAToon, scale=0.125, parent=hidden, font=ToontownGlobals.getSignFont(), fg=(1,
                                                                                                                                              0.9,
                                                                                                                                              0.1,
                                                                                                                                              1), pos=(0.0,
                                                                                                                                                       0.82))
        else:
            if base.cr.isHalloween:
                self.title = OnscreenText(TTLocalizer.AvatarChooserPickAToon, scale=TTLocalizer.ACtitle, parent=hidden, font=ToontownGlobals.getSignFont(), fg=(0.4,
                                                                                                                                                                0,
                                                                                                                                                                0.8,
                                                                                                                                                                1), shadow=(0,
                                                                                                                                                                            0,
                                                                                                                                                                            0,
                                                                                                                                                                            1), pos=(0.0,
                                                                                                                                                                                     0.78))
            else:
                if base.cr.isWinter:
                    self.title = OnscreenText(TTLocalizer.AvatarChooserPickAToon, scale=TTLocalizer.ACtitle, parent=hidden, font=ToontownGlobals.getSignFont(), fg=(0.8,
                                                                                                                                                                    0.1,
                                                                                                                                                                    0.1,
                                                                                                                                                                    1), shadow=(0,
                                                                                                                                                                                0,
                                                                                                                                                                                0,
                                                                                                                                                                                1), pos=(0.0,
                                                                                                                                                                                         0.78))
                else:
                    self.title = OnscreenText(TTLocalizer.AvatarChooserPickAToon, scale=TTLocalizer.ACtitle, parent=hidden, font=ToontownGlobals.getSignFont(), fg=(1,
                                                                                                                                                                    0.9,
                                                                                                                                                                    0.1,
                                                                                                                                                                    1), pos=(0.0,
                                                                                                                                                                             0.82))
        quitHover = gui.find('**/QuitBtn_RLVR')
        if config.GetBool('want-retro-mode', False):
            self.quitButton = DirectButton(image=(gui.find('**/QuitBtn_UP'), gui.find('**/QuitBtn_DN'), gui.find('**/QuitBtn_RLVR')), relief=None, text=TTLocalizer.AvatarChooserQuit, text_font=ToontownGlobals.getSignFont(), text0_fg=(0.152,
                                                                                                                                                                                                                                          0.75,
                                                                                                                                                                                                                                          0.258,
                                                                                                                                                                                                                                          1), text1_fg=(0.152,
                                                                                                                                                                                                                                                        0.75,
                                                                                                                                                                                                                                                        0.258,
                                                                                                                                                                                                                                                        1), text2_fg=(0.977,
                                                                                                                                                                                                                                                                      0.816,
                                                                                                                                                                                                                                                                      0.133,
                                                                                                                                                                                                                                                                      1), text_pos=(0,
                                                                                                                                                                                                                                                                                    -0.035), text_scale=0.1, scale=1.05, pos=(0,
                                                                                                                                                                                                                                                                                                                              0,
                                                                                                                                                                                                                                                                                                                              -0.924), command=self.__handleQuit)
        else:
            if base.cr.isHalloween:
                self.quitButton = DirectButton(image=(quitHover, quitHover, quitHover), relief=None, text=TTLocalizer.AvatarChooserQuit, text_font=ToontownGlobals.getSignFont(), text_fg=(0.8,
                                                                                                                                                                                           0.4,
                                                                                                                                                                                           0,
                                                                                                                                                                                           1), text_pos=TTLocalizer.ACquitButtonPos, text_scale=TTLocalizer.ACquitButton, image_scale=1, image1_scale=1.05, image2_scale=1.05, scale=1.05, pos=(-0.253,
                                                                                                                                                                                                                                                                                                                                                0,
                                                                                                                                                                                                                                                                                                                                                0.093), command=self.__handleQuit)
            else:
                if base.cr.isWinter:
                    self.quitButton = DirectButton(image=(quitHover, quitHover, quitHover), relief=None, text=TTLocalizer.AvatarChooserQuit, text_font=ToontownGlobals.getSignFont(), text_fg=(0.8,
                                                                                                                                                                                               0.1,
                                                                                                                                                                                               0.1,
                                                                                                                                                                                               1), text_pos=TTLocalizer.ACquitButtonPos, text_scale=TTLocalizer.ACquitButton, image_scale=1, image1_scale=1.05, image2_scale=1.05, scale=1.05, pos=(-0.253,
                                                                                                                                                                                                                                                                                                                                                    0,
                                                                                                                                                                                                                                                                                                                                                    0.093), command=self.__handleQuit)
                else:
                    self.quitButton = DirectButton(image=(quitHover, quitHover, quitHover), relief=None, text=TTLocalizer.AvatarChooserQuit, text_font=ToontownGlobals.getSignFont(), text_fg=(0.977,
                                                                                                                                                                                               0.816,
                                                                                                                                                                                               0.133,
                                                                                                                                                                                               1), text_pos=TTLocalizer.ACquitButtonPos, text_scale=TTLocalizer.ACquitButton, image_scale=1, image1_scale=1.05, image2_scale=1.05, scale=1.05, pos=(-0.253,
                                                                                                                                                                                                                                                                                                                                                    0,
                                                                                                                                                                                                                                                                                                                                                    0.093), command=self.__handleQuit)
        if not config.GetBool('want-retro-mode', False):
            self.quitButton.reparentTo(base.a2dBottomRight)
        self.quitButton.flattenMedium()
        self.quitButton.hide()
        if config.GetBool('want-retro-mode', False):
            if base.cr.supportsRelogin():
                self.episodesButton = DirectButton(relief=None, image=(gui2.find('**/QuitBtn_UP'), gui2.find('**/QuitBtn_DN'), gui2.find('**/QuitBtn_RLVR')), image_scale=(1.4,
                                                                                                                                                                           0,
                                                                                                                                                                           1.15), text=TTLocalizer.AvatarChooserEpisodes, text_font=ToontownGlobals.getSignFont(), text0_fg=(0.152,
                                                                                                                                                                                                                                                                             0.75,
                                                                                                                                                                                                                                                                             0.258,
                                                                                                                                                                                                                                                                             1), text1_fg=(0.152,
                                                                                                                                                                                                                                                                                           0.75,
                                                                                                                                                                                                                                                                                           0.258,
                                                                                                                                                                                                                                                                                           1), text2_fg=(0.977,
                                                                                                                                                                                                                                                                                                         0.816,
                                                                                                                                                                                                                                                                                                         0.133,
                                                                                                                                                                                                                                                                                                         1), text_scale=0.1, text_pos=(0,
                                                                                                                                                                                                                                                                                                                                       -0.035), pos=(0.805,
                                                                                                                                                                                                                                                                                                                                                     0,
                                                                                                                                                                                                                                                                                                                                                     -0.924), scale=0.5, command=self.openEpisodeSelector)
            else:
                self.episodesButton = DirectButton(relief=None, image=(gui2.find('**/QuitBtn_UP'), gui2.find('**/QuitBtn_DN'), gui2.find('**/QuitBtn_RLVR')), image_scale=(1.4,
                                                                                                                                                                           0,
                                                                                                                                                                           1.15), text=TTLocalizer.AvatarChooserEpisodes, text_font=ToontownGlobals.getSignFont(), text0_fg=(0.152,
                                                                                                                                                                                                                                                                             0.75,
                                                                                                                                                                                                                                                                             0.258,
                                                                                                                                                                                                                                                                             1), text1_fg=(0.152,
                                                                                                                                                                                                                                                                                           0.75,
                                                                                                                                                                                                                                                                                           0.258,
                                                                                                                                                                                                                                                                                           1), text2_fg=(0.977,
                                                                                                                                                                                                                                                                                                         0.816,
                                                                                                                                                                                                                                                                                                         0.133,
                                                                                                                                                                                                                                                                                                         1), text_scale=0.1, text_pos=(0,
                                                                                                                                                                                                                                                                                                                                       -0.035), pos=(1.105,
                                                                                                                                                                                                                                                                                                                                                     0,
                                                                                                                                                                                                                                                                                                                                                     -0.924), scale=0.5, command=self.openEpisodeSelector)
            self.episodesButton.flattenMedium()
            self.episodesButton.hide()
        else:
            if base.cr.isHalloween:
                self.episodesButton = DirectButton(image=(quitHover, quitHover, quitHover), relief=None, text=TTLocalizer.AvatarChooserEpisodes, text_font=ToontownGlobals.getSignFont(), text_fg=(0.8,
                                                                                                                                                                                                   0.4,
                                                                                                                                                                                                   0,
                                                                                                                                                                                                   1), text_pos=TTLocalizer.ACepisodesButtonPos, text_scale=TTLocalizer.ACepisodesButton, image_scale=1, image1_scale=1.05, image2_scale=1.05, scale=1.05, pos=(-0.725,
                                                                                                                                                                                                                                                                                                                                                                0,
                                                                                                                                                                                                                                                                                                                                                                0.093), command=self.openEpisodeSelector)
                self.episodesButton.flattenMedium()
                self.episodesButton.reparentTo(base.a2dBottomRight)
                self.episodesButton.hide()
            else:
                if base.cr.isWinter:
                    self.episodesButton = DirectButton(image=(quitHover, quitHover, quitHover), relief=None, text=TTLocalizer.AvatarChooserEpisodes, text_font=ToontownGlobals.getSignFont(), text_fg=(0.8,
                                                                                                                                                                                                       0.1,
                                                                                                                                                                                                       0.1,
                                                                                                                                                                                                       1), text_pos=TTLocalizer.ACepisodesButtonPos, text_scale=TTLocalizer.ACepisodesButton, image_scale=1, image1_scale=1.05, image2_scale=1.05, scale=1.05, pos=(-0.725,
                                                                                                                                                                                                                                                                                                                                                                    0,
                                                                                                                                                                                                                                                                                                                                                                    0.093), command=self.openEpisodeSelector)
                    self.episodesButton.flattenMedium()
                    self.episodesButton.reparentTo(base.a2dBottomRight)
                    self.episodesButton.hide()
                else:
                    self.episodesButton = DirectButton(image=(quitHover, quitHover, quitHover), relief=None, text=TTLocalizer.AvatarChooserEpisodes, text_font=ToontownGlobals.getSignFont(), text_fg=(0.977,
                                                                                                                                                                                                       0.816,
                                                                                                                                                                                                       0.133,
                                                                                                                                                                                                       1), text_pos=TTLocalizer.ACepisodesButtonPos, text_scale=TTLocalizer.ACepisodesButton, image_scale=1, image1_scale=1.05, image2_scale=1.05, scale=1.05, pos=(-0.725,
                                                                                                                                                                                                                                                                                                                                                                    0,
                                                                                                                                                                                                                                                                                                                                                                    0.093), command=self.openEpisodeSelector)
                    self.episodesButton.flattenMedium()
                    self.episodesButton.reparentTo(base.a2dBottomRight)
                    self.episodesButton.hide()
        if config.GetBool('want-retro-mode', False):
            self.logoutButton = DirectButton(relief=None, image=(gui2.find('**/QuitBtn_UP'), gui2.find('**/QuitBtn_DN'), gui2.find('**/QuitBtn_RLVR')), image_scale=1.15, text=TTLocalizer.OptionsPageLogout, text_font=ToontownGlobals.getSignFont(), text0_fg=(0.152,
                                                                                                                                                                                                                                                                 0.75,
                                                                                                                                                                                                                                                                 0.258,
                                                                                                                                                                                                                                                                 1), text1_fg=(0.152,
                                                                                                                                                                                                                                                                               0.75,
                                                                                                                                                                                                                                                                               0.258,
                                                                                                                                                                                                                                                                               1), text2_fg=(0.977,
                                                                                                                                                                                                                                                                                             0.816,
                                                                                                                                                                                                                                                                                             0.133,
                                                                                                                                                                                                                                                                                             1), text_scale=TTLocalizer.AClogoutButton, text_pos=(0,
                                                                                                                                                                                                                                                                                                                                                  -0.035), pos=(1.105,
                                                                                                                                                                                                                                                                                                                                                                0,
                                                                                                                                                                                                                                                                                                                                                                -0.924), scale=0.5, command=self.__handleLogoutWithoutConfirm)
            self.logoutButton.flattenMedium()
            self.logoutButton.hide()
        else:
            if base.cr.isHalloween:
                self.logoutButton = DirectButton(relief=None, image=(quitHover, quitHover, quitHover), text=TTLocalizer.OptionsPageLogout, text_font=ToontownGlobals.getSignFont(), text_fg=(0.8,
                                                                                                                                                                                             0.4,
                                                                                                                                                                                             0,
                                                                                                                                                                                             1), text_scale=TTLocalizer.AClogoutButton, text_pos=(0,
                                                                                                                                                                                                                                                  -0.035), pos=(0.163,
                                                                                                                                                                                                                                                                0,
                                                                                                                                                                                                                                                                0.086), image_scale=1.15, image1_scale=1.15, image2_scale=1.18, scale=0.5, command=self.__handleLogoutWithoutConfirm)
                self.logoutButton.reparentTo(base.a2dBottomLeft)
                self.logoutButton.flattenMedium()
                self.logoutButton.hide()
            else:
                if base.cr.isWinter:
                    self.logoutButton = DirectButton(relief=None, image=(quitHover, quitHover, quitHover), text=TTLocalizer.OptionsPageLogout, text_font=ToontownGlobals.getSignFont(), text_fg=(0.8,
                                                                                                                                                                                                 0.1,
                                                                                                                                                                                                 0.1,
                                                                                                                                                                                                 1), text_scale=TTLocalizer.AClogoutButton, text_pos=(0,
                                                                                                                                                                                                                                                      -0.035), pos=(0.163,
                                                                                                                                                                                                                                                                    0,
                                                                                                                                                                                                                                                                    0.086), image_scale=1.15, image1_scale=1.15, image2_scale=1.18, scale=0.5, command=self.__handleLogoutWithoutConfirm)
                    self.logoutButton.reparentTo(base.a2dBottomLeft)
                    self.logoutButton.flattenMedium()
                    self.logoutButton.hide()
                else:
                    self.logoutButton = DirectButton(relief=None, image=(quitHover, quitHover, quitHover), text=TTLocalizer.OptionsPageLogout, text_font=ToontownGlobals.getSignFont(), text_fg=(0.977,
                                                                                                                                                                                                 0.816,
                                                                                                                                                                                                 0.133,
                                                                                                                                                                                                 1), text_scale=TTLocalizer.AClogoutButton, text_pos=(0,
                                                                                                                                                                                                                                                      -0.035), pos=(0.163,
                                                                                                                                                                                                                                                                    0,
                                                                                                                                                                                                                                                                    0.086), image_scale=1.15, image1_scale=1.15, image2_scale=1.18, scale=0.5, command=self.__handleLogoutWithoutConfirm)
                    self.logoutButton.reparentTo(base.a2dBottomLeft)
                    self.logoutButton.flattenMedium()
                    self.logoutButton.hide()
        if not config.GetBool('want-retro-mode', False):
            if base.cr.supportsRelogin():
                infoButtonPos = (0.42, 0, 0.086)
            else:
                infoButtonPos = (0.163, 0, 0.086)
        if config.GetBool('want-retro-mode', False):
            self.infoButton = DirectButton(relief=None, image=(gui2.find('**/QuitBtn_UP'), gui2.find('**/QuitBtn_DN'), gui2.find('**/QuitBtn_RLVR')), image_scale=1.15, text=TTLocalizer.OptionsPageInfo, text_font=ToontownGlobals.getSignFont(), text0_fg=(0.152,
                                                                                                                                                                                                                                                             0.75,
                                                                                                                                                                                                                                                             0.258,
                                                                                                                                                                                                                                                             1), text1_fg=(0.152,
                                                                                                                                                                                                                                                                           0.75,
                                                                                                                                                                                                                                                                           0.258,
                                                                                                                                                                                                                                                                           1), text2_fg=(0.977,
                                                                                                                                                                                                                                                                                         0.816,
                                                                                                                                                                                                                                                                                         0.133,
                                                                                                                                                                                                                                                                                         1), text_scale=0.1, text_pos=(0,
                                                                                                                                                                                                                                                                                                                       -0.035), pos=(-1.105,
                                                                                                                                                                                                                                                                                                                                     0,
                                                                                                                                                                                                                                                                                                                                     -0.924), scale=0.5, command=self.openInfoGUI)
            self.infoButton.flattenMedium()
            self.infoButton.hide()
        else:
            if base.cr.isHalloween:
                self.infoButton = DirectButton(relief=None, image=(quitHover, quitHover, quitHover), text=TTLocalizer.OptionsPageInfo, text_font=ToontownGlobals.getSignFont(), text_fg=(0.8,
                                                                                                                                                                                         0.4,
                                                                                                                                                                                         0,
                                                                                                                                                                                         1), text_scale=TTLocalizer.AClogoutButton, text_pos=(0,
                                                                                                                                                                                                                                              -0.035), pos=infoButtonPos, image_scale=1.15, image1_scale=1.15, image2_scale=1.18, scale=0.5, command=self.openInfoGUI)
                self.infoButton.reparentTo(base.a2dBottomLeft)
                self.infoButton.flattenMedium()
                self.infoButton.hide()
            else:
                if base.cr.isWinter:
                    self.infoButton = DirectButton(relief=None, image=(quitHover, quitHover, quitHover), text=TTLocalizer.OptionsPageInfo, text_font=ToontownGlobals.getSignFont(), text_fg=(0.8,
                                                                                                                                                                                             0.1,
                                                                                                                                                                                             0.1,
                                                                                                                                                                                             1), text_scale=TTLocalizer.AClogoutButton, text_pos=(0,
                                                                                                                                                                                                                                                  -0.035), pos=infoButtonPos, image_scale=1.15, image1_scale=1.15, image2_scale=1.18, scale=0.5, command=self.openInfoGUI)
                    self.infoButton.reparentTo(base.a2dBottomLeft)
                    self.infoButton.flattenMedium()
                    self.infoButton.hide()
                else:
                    self.infoButton = DirectButton(relief=None, image=(quitHover, quitHover, quitHover), text=TTLocalizer.OptionsPageInfo, text_font=ToontownGlobals.getSignFont(), text_fg=(0.977,
                                                                                                                                                                                             0.816,
                                                                                                                                                                                             0.133,
                                                                                                                                                                                             1), text_scale=TTLocalizer.AClogoutButton, text_pos=(0,
                                                                                                                                                                                                                                                  -0.035), pos=infoButtonPos, image_scale=1.15, image1_scale=1.15, image2_scale=1.18, scale=0.5, command=self.openInfoGUI)
                    self.infoButton.reparentTo(base.a2dBottomLeft)
                    self.infoButton.flattenMedium()
                    self.infoButton.hide()
        gui.removeNode()
        gui2.removeNode()
        guiClose.removeNode()
        newGui.removeNode()
        self.panelList = []
        used_position_indexs = []
        for av in self.avatarList:
            if av.position != 6:
                if base.cr.isPaid():
                    okToLockout = 0
                else:
                    okToLockout = 1
                panel = AvatarChoice.AvatarChoice(av, position=av.position, paid=isPaid, okToLockout=okToLockout)
                panel.setPos(POSITIONS[av.position])
                if config.GetBool('want-retro-mode', False):
                    panel['image_color'] = COLORS[av.position]
                used_position_indexs.append(av.position)
                self.panelList.append(panel)

        for panelNum in range(0, MAX_AVATARS):
            if panelNum not in used_position_indexs:
                panel = AvatarChoice.AvatarChoice(position=panelNum, paid=isPaid)
                panel.setPos(POSITIONS[panelNum])
                if config.GetBool('want-retro-mode', False):
                    panel['image_color'] = COLORS[panelNum]
                self.panelList.append(panel)

        if len(self.avatarList) > 0:
            self.initLookAtInfo()
        self.isLoaded = 1
        return

    def getLookAtPosition(self, toonHead, toonidx):
        lookAtChoice = random.random()
        if len(self.used_panel_indexs) == 1:
            lookFwdPercent = 0.33
            lookAtOthersPercent = 0
        else:
            lookFwdPercent = 0.2
            if len(self.used_panel_indexs) == 2:
                lookAtOthersPercent = 0.4
            else:
                lookAtOthersPercent = 0.65
        lookRandomPercent = 1.0 - lookFwdPercent - lookAtOthersPercent
        if lookAtChoice < lookFwdPercent:
            self.IsLookingAt[toonidx] = 'f'
            return Vec3(0, 1.5, 0)
        if lookAtChoice < lookRandomPercent + lookFwdPercent or len(self.used_panel_indexs) == 1:
            self.IsLookingAt[toonidx] = 'r'
            return toonHead.getRandomForwardLookAtPoint()
        other_toon_idxs = []
        for i in range(len(self.IsLookingAt)):
            if self.IsLookingAt[i] == toonidx:
                other_toon_idxs.append(i)

        if len(other_toon_idxs) == 1:
            IgnoreStarersPercent = 0.4
        else:
            IgnoreStarersPercent = 0.2
        NoticeStarersPercent = 0.5
        bStareTargetTurnsToMe = 0
        if len(other_toon_idxs) == 0 or random.random() < IgnoreStarersPercent:
            other_toon_idxs = []
            for i in self.used_panel_indexs:
                if i != toonidx:
                    other_toon_idxs.append(i)

            if random.random() < NoticeStarersPercent:
                bStareTargetTurnsToMe = 1
        if len(other_toon_idxs) == 0:
            return toonHead.getRandomForwardLookAtPoint()
        lookingAtIdx = random.choice(other_toon_idxs)
        if bStareTargetTurnsToMe:
            self.IsLookingAt[lookingAtIdx] = toonidx
            otherToonHead = None
            for panel in self.panelList:
                if panel.position == lookingAtIdx:
                    otherToonHead = panel.headModel

            otherToonHead.doLookAroundToStareAt(otherToonHead, self.getLookAtToPosVec(lookingAtIdx, toonidx))
        self.IsLookingAt[toonidx] = lookingAtIdx
        return self.getLookAtToPosVec(toonidx, lookingAtIdx)
        return

    def getLookAtToPosVec(self, fromIdx, toIdx):
        x = -(POSITIONS[toIdx][0] - POSITIONS[fromIdx][0])
        y = POSITIONS[toIdx][1] - POSITIONS[fromIdx][1]
        z = POSITIONS[toIdx][2] - POSITIONS[fromIdx][2]
        return Vec3(x, y, z)

    def initLookAtInfo(self):
        self.used_panel_indexs = []
        for panel in self.panelList:
            if panel.dna != None:
                self.used_panel_indexs.append(panel.position)

        if len(self.used_panel_indexs) == 0:
            return
        self.IsLookingAt = []
        for i in range(MAX_AVATARS):
            self.IsLookingAt.append('f')

        for panel in self.panelList:
            if panel.dna != None:
                panel.headModel.setLookAtPositionCallbackArgs((self, panel.headModel, panel.position))

        return

    def unload(self):
        if self.isLoaded == 0:
            return
        cleanupDialog('globalDialog')
        for panel in self.panelList:
            panel.destroy()

        del self.panelList
        self.title.removeNode()
        del self.title
        self.episodesButton.destroy()
        del self.episodesButton
        self.logoutButton.destroy()
        del self.logoutButton
        self.infoButton.destroy()
        del self.infoButton
        self.quitButton.destroy()
        del self.quitButton
        self.pickAToonBG.removeNode()
        del self.pickAToonBG
        del self.avatarList
        self.parentFSM.getCurrentState().removeChild(self.fsm)
        del self.parentFSM
        del self.fsm
        self.ignoreAll()
        self.isLoaded = 0
        ModelPool.garbageCollect()
        TexturePool.garbageCollect()
        base.setBackgroundColor(ToontownGlobals.DefaultBackgroundColor)
        return

    def __handlePanelDone(self, panelDoneStatus, panelChoice=0):
        self.doneStatus = {}
        self.doneStatus['mode'] = panelDoneStatus
        self.choice = panelChoice
        if panelDoneStatus == 'chose':
            self.__handleChoice()
        else:
            if panelDoneStatus == 'nameIt':
                self.__handleCreate()
            else:
                if panelDoneStatus == 'delete':
                    self.__handleDelete()
                else:
                    if panelDoneStatus == 'create':
                        self.__handleCreate()

    def getChoice(self):
        return self.choice

    def __handleChoice(self):
        self.fsm.request('CheckDownload')

    def __handleCreate(self):
        base.transitions.fadeOut(finishIval=EventInterval(self.doneEvent, [self.doneStatus]))

    def __handleDelete(self):
        messenger.send(self.doneEvent, [self.doneStatus])

    def __handleQuit(self):
        cleanupDialog('globalDialog')
        self.doneStatus = {'mode': 'exit'}
        messenger.send(self.doneEvent, [self.doneStatus])

    def __handleEpisode(self, episode):
        base.cr.currentEpisode = episode
        for av in self.avatarList:
            if av.position == 6:
                self.episodeToonExists = True
                break

        if self.episodeToonExists:
            self.__handlePanelDone('chose', panelChoice=6)
        else:
            self.choseEpisodeToon = True
            base.cr.skipTutorialRequest = True
            dna = ToonDNA.ToonDNA()
            dna.newToonFromProperties('dss', 'ms', 'm', 'm', 0, 0, 0, 0, 0, 27, 0, 27, 0, 27)
            dna.makeFromNetString(dna.makeNetString())
            self.episodeToonSeq = Sequence(Func(base.transitions.fadeOut), Func(base.cr.csm.sendCreateAvatar, dna, '', 6, True), Wait(1), Func(base.cr.loginFSM.request, 'waitForAvatarList'), Wait(1), Func(self.__handleEpisodeEnter, episode))
            self.episodeToonSeq.start()

    def enterChoose(self):
        pass

    def exitChoose(self):
        pass

    def enterCheckDownload(self):
        self.accept('downloadAck-response', self.__handleDownloadAck)
        self.downloadAck = DownloadForceAcknowledge.DownloadForceAcknowledge('downloadAck-response')
        self.downloadAck.enter(4)

    def exitCheckDownload(self):
        self.downloadAck.exit()
        self.downloadAck = None
        self.ignore('downloadAck-response')
        return

    def __handleDownloadAck(self, doneStatus):
        if doneStatus['mode'] == 'complete':
            if self.choseEpisodeToon:
                messenger.send(self.doneEvent, [self.doneStatus])
            else:
                base.transitions.fadeOut(finishIval=EventInterval(self.doneEvent, [self.doneStatus]))
        else:
            self.fsm.request('Choose')

    def __handleLogoutWithoutConfirm(self):
        base.cr.loginFSM.request('login')

    def openInfoGUI(self):
        infoGUI = InfoGUI(self)
        infoGUI.enter()

    def __handleEpisodeEnter(self, episode):
        if not hasattr(self, 'fsm'):
            self.fsm = ClassicFSM.ClassicFSM('AvatarChooser', [State.State('Choose', self.enterChoose, self.exitChoose, ['CheckDownload']), State.State('CheckDownload', self.enterCheckDownload, self.exitCheckDownload, ['Choose'])], 'Choose', 'Choose')
            self.fsm.enterInitialState()
        self.__handlePanelDone('chose', panelChoice=6)

    def openEpisodeSelector(self):
        if config.GetBool('want-mini-server', False):
            self.nopenoepisodes = TTDialog.TTGlobalDialog(doneEvent='confirmDone', message='Sorry, you cannot play episodes on a Mini-Server!', style=TTDialog.Acknowledge)
            self.nopenoepisodes.show()
            self.accept('confirmDone', self.handleConfirm)
        else:
            if config.GetBool('want-doomsday', False):
                self.nopenoepisodes = TTDialog.TTGlobalDialog(doneEvent='confirmDone', message='Sorry, you cannot play episodes during the Elections!', style=TTDialog.Acknowledge)
                self.nopenoepisodes.show()
                self.accept('confirmDone', self.handleConfirm)
            else:
                episodeSelector = EpisodeSelector(self)
                episodeSelector.enter()

    def handleConfirm(self):
        status = self.nopenoepisodes.doneStatus
        self.ignore('confirmDone')
        self.nopenoepisodes.cleanup()
        del self.nopenoepisodes

    def playEpisode(self, episode):
        base.cr.inEpisode = True
        base.cr.currentEpisode = episode
        self.__handleEpisode(episode)

    def getPickAToonSequenceOrder(self):
        loginSequences = [
         'Sellbot', 'Cashbot', 'Lawbot', 'Bossbot']
        randomOrder = [0, 1, 2, 3]
        deptOrder = {}
        for dept in loginSequences:
            order = random.choice(randomOrder)
            randomOrder.remove(order)
            deptOrder[order] = dept

        return [deptOrder[0], deptOrder[1], deptOrder[2], deptOrder[3]]