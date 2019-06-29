from direct.gui import DirectGuiGlobals
from direct.gui.DirectGui import DirectButton
from direct.gui.DirectGui import DirectFrame
from direct.gui.DirectGui import DirectLabel
from panda3d.core import TextNode
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals

class TokenRewardGui(DirectFrame):
    notify = directNotify.newCategory('TokenRewardGui')
    PreCountdownDelay = 1.0
    CountDownRate = 0.2
    JarLabelTextColor = (0.95, 0.95, 0.0, 1.0)
    JarLabelMaxedTextColor = (1.0, 0.0, 0.0, 1.0)

    def __init__(self, doneEvent):
        self.doneEvent = doneEvent
        DirectFrame.__init__(self)
        self.reparentTo(aspect2d)
        self.setPos(0.0, 0.0, 0.16)
        self.stash()
        publicPartyGui = loader.loadModel('phase_4/models/parties/publicPartyGUI')
        self.frame = DirectFrame(parent=self, geom=publicPartyGui.find('**/activities_background'), geom_pos=(-0.8,
                                                                                                              0.0,
                                                                                                              0.2), geom_scale=2.0, relief=None)
        self.earnedLabel = DirectLabel(parent=self, relief=None, text=str(0), text_align=TextNode.ACenter, text_pos=(0.0,
                                                                                                                     -0.07), text_scale=0.2, text_fg=(0.95,
                                                                                                                                                      0.95,
                                                                                                                                                      0.0,
                                                                                                                                                      1.0), text_font=ToontownGlobals.getSignFont(), textMayChange=True, image=DirectGuiGlobals.getDefaultDialogGeom(), image_scale=(0.33,
                                                                                                                                                                                                                                                                                     1.0,
                                                                                                                                                                                                                                                                                     0.33), pos=(-0.3,
                                                                                                                                                                                                                                                                                                 0.0,
                                                                                                                                                                                                                                                                                                 0.2), scale=0.9)
        purchaseModels = loader.loadModel('phase_6/models/gui/ttr_m_tf_gui_tokens')
        jarImage = purchaseModels.find('**/jar')
        self.jarLabel = DirectLabel(parent=self, relief=None, text=str(0), text_align=TextNode.ACenter, text_pos=(0.0,
                                                                                                                  -0.07), text_scale=0.2, text_fg=TokenRewardGui.JarLabelTextColor, text_font=ToontownGlobals.getSignFont(), textMayChange=True, image=jarImage, scale=0.7, pos=(0.3,
                                                                                                                                                                                                                                                                                 0.0,
                                                                                                                                                                                                                                                                                 0.17))
        purchaseModels.removeNode()
        del purchaseModels
        jarImage.removeNode()
        del jarImage
        self.messageLabel = DirectLabel(parent=self, relief=None, text='', text_align=TextNode.ALeft, text_wordwrap=16.0, text_scale=0.07, pos=(-0.52,
                                                                                                                                                0.0,
                                                                                                                                                -0.1), textMayChange=True)
        self.doubledJellybeanLabel = DirectLabel(parent=self, relief=None, text=TTLocalizer.ToonFestRewardDoubledJellybean, text_align=TextNode.ACenter, text_wordwrap=12.0, text_scale=0.09, text_fg=(1.0,
                                                                                                                                                                                                       0.125,
                                                                                                                                                                                                       0.125,
                                                                                                                                                                                                       1.0), pos=(0.0,
                                                                                                                                                                                                                  0.0,
                                                                                                                                                                                                                  -0.465), textMayChange=False)
        self.doubledJellybeanLabel.hide()
        self.closeButton = DirectButton(parent=self, relief=None, text=TTLocalizer.PartyJellybeanRewardOK, text_align=TextNode.ACenter, text_scale=0.065, text_pos=(0.0,
                                                                                                                                                                    -0.625), geom=(
         publicPartyGui.find('**/startButton_up'),
         publicPartyGui.find('**/startButton_down'),
         publicPartyGui.find('**/startButton_rollover'),
         publicPartyGui.find('**/startButton_inactive')), geom_pos=(-0.39, 0.0, 0.125), command=self._close)
        publicPartyGui.removeNode()
        del publicPartyGui
        self.countSound = base.loader.loadSfx('phase_6/audio/sfx/ttr_tf_ara_ww_minigame_token.ogg')
        self.overMaxSound = base.loader.loadSfx('phase_6/audio/sfx/ttr_tf_ara_ww_minigame_token.ogg')
        return

    def showReward(self, earnedAmount, jarAmount, message):
        TokenRewardGui.notify.debug('showReward( earnedAmount=%d, jarAmount=%d, ...)' % (earnedAmount, jarAmount))
        self.earnedCount = earnedAmount
        self.earnedLabel['text'] = str(self.earnedCount)
        self.jarCount = jarAmount
        self.jarMax = base.localAvatar.getMaxMoney()
        self.jarLabel['text'] = str(self.jarCount)
        self.jarLabel['text_fg'] = TokenRewardGui.JarLabelTextColor
        self.messageLabel['text'] = message
        self.doubledJellybeanLabel.hide()
        self.unstash()
        taskMgr.doMethodLater(TokenRewardGui.PreCountdownDelay, self.transferOneJellybean, 'TokenRewardGuiTransferOneJellybean', extraArgs=[])

    def transferOneJellybean(self):
        if self.earnedCount == 0:
            return
        self.earnedCount -= 1
        self.earnedLabel['text'] = str(self.earnedCount)
        self.jarCount += 1
        if self.jarCount <= self.jarMax:
            self.jarLabel['text'] = str(self.jarCount)
        else:
            if self.jarCount > self.jarMax:
                self.jarLabel['text_fg'] = TokenRewardGui.JarLabelMaxedTextColor
        if self.jarCount <= self.jarMax:
            base.playSfx(self.countSound)
        else:
            base.playSfx(self.overMaxSound)
        taskMgr.doMethodLater(TokenRewardGui.CountDownRate, self.transferOneJellybean, 'TokenRewardGuiTransferOneJellybean', extraArgs=[])

    def _close(self):
        taskMgr.remove('TokenRewardGuiTransferOneJellybean')
        self.stash()
        messenger.send(self.doneEvent)

    def destroy(self):
        taskMgr.remove('TokenRewardGuiTransferOneJellybean')
        del self.countSound
        del self.overMaxSound
        self.frame.destroy()
        self.earnedLabel.destroy()
        self.jarLabel.destroy()
        self.messageLabel.destroy()
        self.closeButton.destroy()
        DirectFrame.destroy(self)