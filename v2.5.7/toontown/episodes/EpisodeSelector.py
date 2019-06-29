from direct.directnotify import DirectNotifyGlobal
from direct.fsm import StateData
from direct.gui.DirectGui import *
from panda3d.core import Vec4, TextNode
from toontown.episodes import EpisodeConfig
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals

class EpisodeSelector(DirectFrame, StateData.StateData):
    notify = DirectNotifyGlobal.directNotify.newCategory('EpisodeSelector')

    def __init__(self, avChooser):
        DirectFrame.__init__(self, pos=(0, 0, 0.05), relief=None, image=DGG.getDefaultDialogGeom(), image_scale=(2.2,
                                                                                                                 1,
                                                                                                                 1.4), image_pos=(0,
                                                                                                                                  0,
                                                                                                                                  -0.05), image_color=ToontownGlobals.GlobalDialogColor, text=TTLocalizer.AvatarChooserEpisodes, text_scale=0.12, text_pos=(0,
                                                                                                                                                                                                                                                            0.5), borderWidth=(0.01,
                                                                                                                                                                                                                                                                               0.01))
        StateData.StateData.__init__(self, 'episode-selector-done')
        self.isLoaded = False
        self.setBin('gui-popup', 0)
        self.initialiseoptions(EpisodeSelector)
        self.avChooser = avChooser
        self.textRolloverColor = Vec4(1, 1, 0, 1)
        self.textDownColor = Vec4(0.5, 0.9, 1, 1)
        self.textDisabledColor = Vec4(0.4, 0.8, 0.4, 1)
        self.descPos = (0.485, 0, -0.2)
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
        self.episodes = []
        self.descriptions = []
        self.thumbnails = []
        for episode in EpisodeConfig.episodes:
            episodeName = DirectButton(parent=self, relief=None, text=EpisodeConfig.episodes[episode].get('name'), text_align=TextNode.ACenter, text_pos=(0.19,
                                                                                                                                                          0,
                                                                                                                                                          0), text_scale=0.05, text1_bg=self.textDownColor, text2_bg=self.textRolloverColor, text3_fg=self.textDisabledColor, textMayChange=0, command=self.selectEpisode, extraArgs=[
             episode])
            self.episodes.append(episodeName)
            setattr(self, ('{0}Name').format(episode), episodeName)
            episodeDesc = DirectLabel(parent=hidden, relief=None, text=EpisodeConfig.episodes[episode].get('desc'), text_align=TextNode.ACenter, text_scale=0.06, text_wordwrap=15, pos=self.descPos)
            self.descriptions.append(episodeDesc)
            setattr(self, ('{0}Desc').format(episode), episodeDesc)
            episodeThumb = OnscreenImage(image=('phase_3/maps/episodes/{0}').format(EpisodeConfig.episodes[episode].get('thumbnail', 'mystery_episode_thumbnail.jpg')), scale=(0.45,
                                                                                                                                                                               0.25,
                                                                                                                                                                               0.25), pos=(0.5,
                                                                                                                                                                                           0,
                                                                                                                                                                                           0.15), parent=hidden)
            self.thumbnails.append(episodeThumb)
            setattr(self, ('{0}Thumbnail').format(episode), episodeThumb)

        gui = loader.loadModel('phase_3.5/models/gui/friendslist_gui')
        guiButton = loader.loadModel('phase_3/models/gui/quit_button')
        self.scrollList = DirectScrolledList(parent=self, relief=None, forceHeight=0.07, pos=(-0.5,
                                                                                              0,
                                                                                              -0.05), incButton_image=(
         gui.find('**/FndsLst_ScrollUp'),
         gui.find('**/FndsLst_ScrollDN'),
         gui.find('**/FndsLst_ScrollUp_Rllvr'),
         gui.find('**/FndsLst_ScrollUp')), incButton_relief=None, incButton_scale=(1.3,
                                                                                   1.3,
                                                                                   -1.3), incButton_pos=(-0.05,
                                                                                                         0,
                                                                                                         -0.6), incButton_image3_color=Vec4(1, 1, 1, 0.2), decButton_image=(
         gui.find('**/FndsLst_ScrollUp'),
         gui.find('**/FndsLst_ScrollDN'),
         gui.find('**/FndsLst_ScrollUp_Rllvr'),
         gui.find('**/FndsLst_ScrollUp')), decButton_relief=None, decButton_scale=(1.3,
                                                                                   1.3,
                                                                                   1.3), decButton_pos=(-0.05,
                                                                                                        0,
                                                                                                        0.52), decButton_image3_color=Vec4(1, 1, 1, 0.2), itemFrame_pos=(-0.237,
                                                                                                                                                                         0,
                                                                                                                                                                         0.41), itemFrame_scale=1.0, itemFrame_relief=DGG.SUNKEN, itemFrame_frameSize=(-0.3,
                                                                                                                                                                                                                                                       0.66,
                                                                                                                                                                                                                                                       -0.98,
                                                                                                                                                                                                                                                       0.07), itemFrame_frameColor=(0.85,
                                                                                                                                                                                                                                                                                    0.95,
                                                                                                                                                                                                                                                                                    1,
                                                                                                                                                                                                                                                                                    1), itemFrame_borderWidth=(0.01,
                                                                                                                                                                                                                                                                                                               0.01), numItemsVisible=14, items=self.episodes)
        self.cancel = DirectButton(parent=self, relief=None, text=TTLocalizer.DisplaySettingsCancel, image=(
         guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), image_scale=(0.6,
                                                                                                                            1,
                                                                                                                            1), text_scale=TTLocalizer.DSDcancel, text_pos=TTLocalizer.DSDcancelPos, pos=(0.93,
                                                                                                                                                                                                          0,
                                                                                                                                                                                                          -0.65), command=self.__cancel)
        self.play = DirectButton(parent=hidden, relief=None, text=TTLocalizer.EpisodePlay, image=(
         guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), image_scale=(0.6,
                                                                                                                            1,
                                                                                                                            1), text_scale=TTLocalizer.DSDcancel, text_pos=TTLocalizer.DSDcancelPos, pos=(0.5,
                                                                                                                                                                                                          0,
                                                                                                                                                                                                          -0.55))
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
        self.scrollList.destroy()
        del self.scrollList
        base.transitions.noTransitions()
        self.ignoreAll()
        self.hide()

    def __cancel(self):
        self.exit()

    def selectEpisode(self, episode):
        for episodeName in self.episodes:
            if episodeName['state'] != DGG.NORMAL:
                episodeName['state'] = DGG.NORMAL

        for description in self.descriptions:
            if description.getParent() != hidden:
                description.reparentTo(hidden)

        for thumbnail in self.thumbnails:
            if thumbnail:
                thumbnail.reparentTo(hidden)

        getattr(self, ('{0}Name').format(episode))['state'] = DGG.DISABLED
        getattr(self, ('{0}Desc').format(episode)).reparentTo(self)
        getattr(self, ('{0}Thumbnail').format(episode)).reparentTo(self)
        self.play['text'] = TTLocalizer.EpisodePlay
        self.play['command'] = self.__handleEpisode
        self.play['extraArgs'] = [episode]
        self.play.reparentTo(self)

    def __handleEpisode(self, episode):
        self.unload()
        self.avChooser.playEpisode(episode)