from direct.gui.DirectGui import *
from panda3d.core import *
from toontown.toonbase import TTLocalizer

class QuizGui:

    def __init__(self, quiz):
        self.quiz = quiz
        self.gui = None
        self.answer1 = None
        self.answer2 = None
        self.answer3 = None
        self.answer4 = None
        self.quitButton = None
        self.openButton = None
        self.open = True
        self.moveSeq = None
        return

    def load(self):
        self.unload()
        self.gui = loader.loadModel('phase_6/models/gui/ttr_m_tf_gui_quizGui')
        self.answer1 = self.gui.find('**/answerPanel0')
        self.answer2 = self.gui.find('**/answerPanel1')
        self.answer3 = self.gui.find('**/answerPanel2')
        self.answer4 = self.gui.find('**/answerPanel3')
        arrowUp = self.gui.find('**/arrowClose')
        arrowOver = self.gui.find('**/arrowClose_rollover')
        arrowClick = self.gui.find('**/arrowClose_pressed')
        arrowUp.reparentTo(hidden)
        arrowOver.reparentTo(hidden)
        arrowClick.reparentTo(hidden)
        self.gui.reparentTo(base.a2dLeftCenter)
        self.gui.setScale(0.85)
        self.gui.setPos(0.625, 0, 0)
        base.tfq = self.gui
        guiButton = loader.loadModel('phase_3/models/gui/quit_button.bam')
        imageSet = (guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR'))
        self.quitButton = DirectButton(relief=None, text=TTLocalizer.QuizLeaveButton, text_fg=(0,
                                                                                               0,
                                                                                               0,
                                                                                               1), text_scale=0.06, text_pos=(0,
                                                                                                                              -0.02), image=imageSet, image_color=(1,
                                                                                                                                                                   1,
                                                                                                                                                                   1,
                                                                                                                                                                   1), image_scale=(1.1,
                                                                                                                                                                                    1.1,
                                                                                                                                                                                    1.1), pos=(0,
                                                                                                                                                                                               0,
                                                                                                                                                                                               0.9), command=self.exitQuiz)
        self.openButton = DirectButton(image=(arrowUp, arrowOver, arrowClick), relief=None, command=self.toggleOpen)
        self.openButton.reparentTo(base.a2dLeftCenter)
        self.openButton.setScale(0.85)
        self.openButton.setPos(0.6, 0, 0)
        return

    def unload(self):
        if self.moveSeq:
            self.moveSeq.finish()
            self.moveSeq = None
        if self.gui:
            self.gui.removeNode()
        if self.openButton:
            self.quitButton.destroy()
        if self.openButton:
            self.openButton.destroy()
        return

    def toggleOpen(self):
        if self.moveSeq:
            self.moveSeq.finish()
        if self.open:
            x = -1
        else:
            x = 0.625
        self.open = not self.open
        self.moveSeq = self.gui.posInterval(0.25, (x, 0, 0), (
         self.gui.getX(), 0, 0))
        self.moveSeq.start()

    def exitQuiz(self):
        self.quiz.handleExit()