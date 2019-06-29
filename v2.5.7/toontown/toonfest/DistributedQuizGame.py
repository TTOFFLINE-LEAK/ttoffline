from direct.distributed import DistributedObject
from direct.distributed.ClockDelta import *
from direct.fsm import ClassicFSM
from direct.fsm import State
from direct.interval.IntervalGlobal import *
from panda3d.core import *
import QuizGui
from otp.nametag.NametagConstants import *
from otp.otpbase import PythonUtil
from toontown.toon import NPCToons
from toontown.toonbase import ToontownGlobals

class DistributedQuizGame(DistributedObject.DistributedObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedQuizGame')

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        self.geom = base.cr.playGame.hood.loader.geom
        self.grounds = None
        self.quizzer = None
        self.idleSeq = None
        self.beanBag = None
        self.fenceDoor = None
        self.collider = None
        self.gui = None
        self.colEventName = ''
        self.round = 0
        self.fsm = ClassicFSM.ClassicFSM('DistributedQuizGame', [
         State.State('Off', self.enterOff, self.exitOff, ['Idle',
          'Start',
          'Question',
          'Answer',
          'Final']),
         State.State('Idle', self.enterIdle, self.exitIdle, ['Start']),
         State.State('Start', self.enterStart, self.exitStart, ['Question']),
         State.State('Question', self.enterQuestion, self.exitQuestion, ['Answer']),
         State.State('Answer', self.enterAnswer, self.exitAnswer, [
          'Question', 'Final']),
         State.State('Final', self.enterFinal, self.exitFinal, ['Idle'])], 'Off', 'Off')
        self.fsm.enterInitialState()
        return

    def generate(self):
        DistributedObject.DistributedObject.generate(self)
        self.grounds = loader.loadModel('phase_6/models/events/ttr_m_tf_quizStage')
        self.grounds.reparentTo(self.geom)
        self.grounds.setPosHpr(247.54, 74.37, 4.6, 345, 0, 0)
        if base.cr.newsManager.isHolidayRunning(ToontownGlobals.TRICK_OR_TREAT) or base.cr.newsManager.isHolidayRunning(ToontownGlobals.HALLOWEEN_PROPS) or base.cr.newsManager.isHolidayRunning(ToontownGlobals.HALLOWEEN):
            self.quizzer = NPCToons.createLocalNPC(14108)
        else:
            self.quizzer = NPCToons.createLocalNPC(14008)
            self.quizzer.setHat(24, 0, 0)
            self.quizzer.setGlasses(17, 0, 0)
        self.quizzer.useLOD(1000)
        self.quizzer.addActive()
        npcOrigin = self.grounds.find('**/NPC_origin')
        self.quizzer.reparentTo(npcOrigin)
        self.quizzer.setH(180)
        self.quizzer.setBlend(animBlend=True)
        self.quizzer.setControlEffect('neutral', 1.0)
        self.beanBag = loader.loadModel('phase_6/models/events/ttr_m_ww_beanBag')
        self.beanBag.reparentTo(self.quizzer.rightHand)
        self.beanBag.setScale(0)
        self.beanBag.setPosHpr(0.38, -0.28, 0.29, 90, 180, 90)
        self.collider = self.grounds.find('**/ww_stage_trigger')
        self.colEventName = 'enter' + self.collider.getName()
        self.accept(self.colEventName, self.handleEnter)
        self.fenceDoor = self.grounds.find('**/fenceDoor')
        self.fenceDoor.setZ(-2.25)
        self.gui = QuizGui.QuizGui(self)
        self.fsm.request('Idle')

    def disable(self):
        self.gui.unload()
        self.fsm.request('Off')

    def delete(self):
        self.grounds.removeNode()
        self.beanBag.removeNode()
        self.quizzer.delete()
        del self.gui
        DistributedObject.DistributedObject.delete(self)

    def enterIdle(self):
        if not self.idleSeq:
            self.idleSeq = Sequence(Func(self.quizzer.setChatAbsolute, 'Hello, hello, everyone!', CFSpeech | CFTimeout), Wait(5), Func(self.quizzer.play, 'scientistGame', fromFrame=409), PythonUtil.blendAnimation(0.5, 'neutral', 'scientistGame', self.quizzer), Func(self.quizzer.setChatAbsolute, "A lot of you've come out today, eh?", CFSpeech | CFTimeout), Wait(3), PythonUtil.blendAnimation(0.5, 'scientistGame', 'neutral', self.quizzer), Func(self.quizzer.stop, 'scientistGame'), Wait(3.5), Func(self.quizzer.setChatAbsolute, 'Step right up and play this amazing quiz...', CFSpeech | CFTimeout), Wait(7), Func(self.quizzer.setChatAbsolute, '...and win fantabulous prizes!', CFSpeech | CFTimeout), Func(self.quizzer.play, 'scientistJealous', fromFrame=468), Parallel(PythonUtil.blendAnimation(0.5, 'neutral', 'scientistJealous', self.quizzer), self.beanBag.scaleInterval(0.5, 1.0)), Wait(4), Parallel(PythonUtil.blendAnimation(0.5, 'scientistJealous', 'neutral', self.quizzer), self.beanBag.scaleInterval(0.5, 0.0)), Func(self.quizzer.stop, 'scientistJealous'), Wait(1.5), Func(self.quizzer.setChatAbsolute, 'What are you waiting for? Come over and try your luck!', CFSpeech | CFTimeout), Wait(7))
        self.idleSeq.loop()

    def exitIdle(self):
        self.idleSeq.finish()

    def enterStart(self):
        pass

    def exitStart(self):
        pass

    def enterQuestion(self):
        pass

    def exitQuestion(self):
        pass

    def enterAnswer(self):
        pass

    def exitAnswer(self):
        pass

    def enterFinal(self):
        pass

    def exitFinal(self):
        self.round = 0

    def enterOff(self):
        if self.grounds:
            self.grounds.stash()
            self.quizzer.removeActive()

    def exitOff(self):
        if self.grounds:
            self.grounds.unstash()
            self.quizzer.addActive()

    def handleEnter(self, collEntry):
        self.notify.info('Local avatar trying to join us.')
        self.sendUpdate('addParticipant', [])
        base.localAvatar.disableAvatarControls()
        self.gui.load()

    def handleExit(self):
        self.notify.info('Local avatar trying to leave us.')
        self.sendUpdate('removeParticipant', [])
        base.localAvatar.enableAvatarControls()
        self.gui.unload()