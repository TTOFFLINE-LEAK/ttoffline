from direct.actor.Actor import Actor
from direct.task.Task import Task
from direct.distributed.DistributedObject import DistributedObject
from panda3d.core import *
from otp.otpbase.OTPBase import OTPBase
from otp.otpbase import OTPGlobals
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.parties.PartyGlobals import ActivityIds, ActivityTypes, ActivityRequestStatus, PhaseToMusicData60, JUKEBOX_TIMEOUT
from toontown.parties.PartyGlobals import getMusicRepeatTimes, MUSIC_PATH, sanitizePhase
from toontown.parties.JukeboxGui import JukeboxGui
from toontown.toontowngui import TTDialog

class DistributedSafezoneJukebox(DistributedObject):
    notify = directNotify.newCategory('DistributedSafezoneJukebox')

    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        self.activityName = TTLocalizer.SafezoneJukeboxTitle
        self.phaseToMusicData = PhaseToMusicData60
        self.jukebox = None
        self.gui = None
        self.tunes = []
        self.music = None
        self.messageGui = None
        self.currentSongData = None
        self.localQueuedSongInfo = None
        self.localQueuedSongListItem = None
        self._localToonRequestStatus = None
        self.toonIds = []
        self._toonId2ror = {}
        self.root = NodePath('root')
        return

    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        self.load()

    def disable(self):
        self.notify.debug('BASE: disable')
        DistributedObject.disable(self)
        rorToonIds = self._toonId2ror.keys()
        for toonId in rorToonIds:
            self.cr.relatedObjectMgr.abortRequest(self._toonId2ror[toonId])
            del self._toonId2ror[toonId]

        self.ignore(self.messageDoneEvent)
        if self.messageGui is not None and not self.messageGui.isEmpty():
            self.messageGui.cleanup()
            self.messageGui = None
        return

    def delete(self):
        self.notify.debug('BASE: delete')
        self.unload()
        self.ignoreAll()
        DistributedObject.delete(self)

    def generateInit(self):
        self.gui = JukeboxGui(self.phaseToMusicData)

    def load(self):
        self.jukebox = Actor('phase_13/models/parties/jukebox_model', {'dance': 'phase_13/models/parties/jukebox_dance'})
        self.jukebox.reparentTo(self.root)
        self.collNode = CollisionNode(self.getCollisionName())
        self.collNode.setCollideMask(ToontownGlobals.CameraBitmask | ToontownGlobals.WallBitmask)
        collTube = CollisionTube(0, 0, 0, 0.0, 0.0, 4.25, 2.25)
        collTube.setTangible(1)
        self.collNode.addSolid(collTube)
        self.collNodePath = self.jukebox.attachNewNode(self.collNode)
        self.loadSign()
        self.sign.setPos(-5.0, 0, 0)
        self.messageDoneEvent = self.uniqueName('messageDoneEvent')
        self.root.reparentTo(render)
        self.activate()

    def loadSign(self):
        self.sign = self.root.attachNewNode('%sSign' % self.activityName)
        self.defaultSignModel = loader.loadModel('phase_13/models/parties/eventSign')
        self.signModel = self.defaultSignModel.copyTo(self.sign)
        self.signFlat = self.signModel.find('**/sign_flat')
        self.signFlatWithNote = self.signModel.find('**/sign_withNote')
        self.signTextLocator = self.signModel.find('**/signText_locator')
        self.activityIconsModel = loader.loadModel('phase_4/models/parties/eventSignIcons')
        textureNodePath = self.activityIconsModel.find('**/PartyJukebox40Icon')
        textureNodePath.setPos(0.0, -0.02, 2.2)
        textureNodePath.setScale(2.35)
        textureNodePath.copyTo(self.signFlat)
        textureNodePath.copyTo(self.signFlatWithNote)
        text = TextNode('noteText')
        text.setTextColor(0.2, 0.1, 0.7, 1.0)
        text.setAlign(TextNode.ACenter)
        text.setFont(OTPGlobals.getInterfaceFont())
        text.setWordwrap(10.0)
        text.setText('')
        self.noteText = self.signFlatWithNote.attachNewNode(text)
        self.noteText.setPosHpr(self.signTextLocator, 0.0, 0.0, 0.2, 0.0, 0.0, 0.0)
        self.noteText.setScale(0.2)
        self.signFlatWithNote.stash()
        self.signTextLocator.stash()

    def unload(self):
        self.gui.unload()
        if self.music is not None:
            self.music.stop()
        self.jukebox.stop()
        self.jukebox.delete()
        self.jukebox = None
        self.signModel.removeNode()
        del self.signModel
        self.sign.removeNode()
        del self.sign
        self.ignoreAll()
        self.root.removeNode()
        del self.root
        del self.activityName
        del self.messageGui
        if hasattr(self, 'toonIds'):
            del self.toonIds
        self.ignoreAll()
        return

    def getCollisionName(self):
        return self.uniqueName('jukeboxCollision')

    def activate(self):
        self.accept('enter' + self.getCollisionName(), self.__handleEnterCollision)

    def __handleEnterCollision(self, collisionEntry):
        if base.cr.playGame.getPlace().fsm.getCurrentState().getName() == 'walk':
            base.cr.playGame.getPlace().fsm.request('activity')
            self.d_toonJoinRequest()

    def localToonExiting(self):
        self._localToonRequestStatus = ActivityRequestStatus.Exiting

    def localToonJoining(self):
        self._localToonRequestStatus = ActivityRequestStatus.Joining

    def d_toonJoinRequest(self):
        if self._localToonRequestStatus is None:
            self.localToonJoining()
            self.sendUpdate('toonJoinRequest')
        return

    def d_toonExitRequest(self):
        if self._localToonRequestStatus is None:
            self.localToonExiting()
            self.sendUpdate('toonExitRequest')
        return

    def d_toonExitDemand(self):
        self.localToonExiting()
        self.sendUpdate('toonExitDemand')

    def joinRequestDenied(self, reason):
        self._localToonRequestStatus = None
        self.showMessage(TTLocalizer.PartyJukeboxOccupied)
        return

    def handleToonJoined(self, toonId):
        toon = base.cr.doId2do.get(toonId)
        if toon:
            self.jukebox.lookAt(base.cr.doId2do[toonId])
            self.jukebox.setHpr(self.jukebox.getH() + 180.0, 0, 0)
        if toonId == base.localAvatar.doId:
            self.__localUseJukebox()

    def handleToonExited(self, toonId):
        if toonId == base.localAvatar.doId and self.gui.isLoaded():
            self.__deactivateGui()

    def handleToonDisabled(self, toonId):
        self.notify.warning('handleToonDisabled no implementation yet')

    def setToonsPlaying(self, toonIds):
        exitedToons, joinedToons = self.getToonsPlayingChanges(self.toonIds, toonIds)
        self.setToonIds(toonIds)
        self._processExitedToons(exitedToons)
        self._processJoinedToons(joinedToons)

    def _processExitedToons(self, exitedToons):
        for toonId in exitedToons:
            if toonId != base.localAvatar.doId or toonId == base.localAvatar.doId and self.isLocalToonRequestStatus(ActivityRequestStatus.Exiting):
                toon = self.getAvatar(toonId)
                if toon is not None:
                    self.ignore(toon.uniqueName('disable'))
                self.handleToonExited(toonId)
                if toonId == base.localAvatar.doId:
                    self._localToonRequestStatus = None
                if toonId in self._toonId2ror:
                    self.cr.relatedObjectMgr.abortRequest(self._toonId2ror[toonId])
                    del self._toonId2ror[toonId]

        return

    def _processJoinedToons(self, joinedToons):
        for toonId in joinedToons:
            if toonId != base.localAvatar.doId or toonId == base.localAvatar.doId and self.isLocalToonRequestStatus(ActivityRequestStatus.Joining):
                if toonId not in self._toonId2ror:
                    request = self.cr.relatedObjectMgr.requestObjects([toonId], allCallback=self._handlePlayerPresent)
                    if toonId in self._toonId2ror:
                        del self._toonId2ror[toonId]
                    else:
                        self._toonId2ror[toonId] = request

    def _handlePlayerPresent(self, toons):
        toon = toons[0]
        toonId = toon.doId
        if toonId in self._toonId2ror:
            del self._toonId2ror[toonId]
        else:
            self._toonId2ror[toonId] = None
        self._enableHandleToonDisabled(toonId)
        self.handleToonJoined(toonId)
        if toonId == base.localAvatar.doId:
            self._localToonRequestStatus = None
        return

    def _enableHandleToonDisabled(self, toonId):
        toon = self.getAvatar(toonId)
        if toon is not None:
            self.acceptOnce(toon.uniqueName('disable'), self.handleToonDisabled, [toonId])
        else:
            self.notify.warning('BASE: unable to get handle to toon with toonId:%d. Hook for handleToonDisabled not set.' % toonId)
        return

    def isLocalToonRequestStatus(self, requestStatus):
        return self._localToonRequestStatus == requestStatus

    def setToonIds(self, toonIds):
        self.toonIds = toonIds

    def getToonsPlayingChanges(self, oldToonIds, newToonIds):
        oldToons = set(oldToonIds)
        newToons = set(newToonIds)
        exitedToons = oldToons.difference(newToons)
        joinedToons = newToons.difference(oldToons)
        return (
         list(exitedToons), list(joinedToons))

    def getAvatar(self, toonId):
        if toonId in self.cr.doId2do:
            return self.cr.doId2do[toonId]
        self.notify.warning('BASE: getAvatar: No avatar in doId2do with id: ' + str(toonId))
        return
        return

    def __localUseJukebox(self):
        base.localAvatar.disableAvatarControls()
        base.localAvatar.stopPosHprBroadcast()
        self.__activateGui()
        self.accept(JukeboxGui.CLOSE_EVENT, self.__handleGuiClose)
        taskMgr.doMethodLater(0.5, self.__localToonWillExitTask, self.uniqueName('toonWillExitJukeboxOnTimeout'), extraArgs=None)
        self.accept(JukeboxGui.ADD_SONG_CLICK_EVENT, self.__handleQueueSong)
        if self.isUserHost():
            self.accept(JukeboxGui.MOVE_TO_TOP_CLICK_EVENT, self.__handleMoveSongToTop)
        return

    def __localToonWillExitTask(self, task):
        self.localToonExiting()
        return Task.done

    def __activateGui(self):
        self.gui.enable(timer=JUKEBOX_TIMEOUT)
        self.gui.disableAddSongButton()
        if self.currentSongData is not None:
            self.gui.setSongCurrentlyPlaying(self.currentSongData[0], self.currentSongData[1])
        self.d_queuedSongsRequest()
        return

    def __deactivateGui(self):
        self.ignore(JukeboxGui.CLOSE_EVENT)
        self.ignore(JukeboxGui.SONG_SELECT_EVENT)
        self.ignore(JukeboxGui.MOVE_TO_TOP_CLICK_EVENT)
        base.cr.playGame.getPlace().setState('walk')
        base.localAvatar.startPosHprBroadcast()
        base.localAvatar.enableAvatarControls()
        self.gui.unload()
        self.__localClearQueuedSong()

    def isUserHost(self):
        return base.localAvatar.getAccessLevel() >= 200

    def d_queuedSongsRequest(self):
        self.sendUpdate('queuedSongsRequest')

    def queuedSongsResponse(self, songInfoList, index):
        if self.gui.isLoaded():
            for i in xrange(len(songInfoList)):
                songInfo = songInfoList[i]
                self.__addSongToQueue(songInfo, isLocalQueue=index >= 0 and i == index)

            self.gui.enableAddSongButton()

    def __handleGuiClose(self):
        self.__deactivateGui()
        self.d_toonExitDemand()

    def __handleQueueSong(self, name, values):
        self.d_setNextSong(values[0], values[1])

    def d_setNextSong(self, phase, filename):
        self.sendUpdate('setNextSong', [(phase, filename)])

    def setSongInQueue(self, songInfo):
        if self.gui.isLoaded():
            phase = sanitizePhase(songInfo[0])
            filename = songInfo[1]
            data = self.getMusicData(phase, filename)
            if data:
                if self.localQueuedSongListItem is not None:
                    self.localQueuedSongListItem['text'] = data[0]
                else:
                    self.__addSongToQueue(songInfo, isLocalQueue=True)
        return

    def __addSongToQueue(self, songInfo, isLocalQueue=False):
        isHost = isLocalQueue and self.isUserHost()
        data = self.getMusicData(sanitizePhase(songInfo[0]), songInfo[1])
        if data:
            listItem = self.gui.addSongToQueue(data[0], highlight=isLocalQueue, moveToTopButton=isHost)
            if isLocalQueue:
                self.localQueuedSongInfo = songInfo
                self.localQueuedSongListItem = listItem

    def __localClearQueuedSong(self):
        self.localQueuedSongInfo = None
        self.localQueuedSongListItem = None
        return

    def __play(self, phase, filename, length):
        self.music = base.loader.loadMusic((MUSIC_PATH + '%s') % (phase, filename))
        if self.music:
            if self.__checkPartyValidity() and hasattr(base.cr.playGame.getPlace().loader, 'music') and base.cr.playGame.getPlace().loader.music:
                base.cr.playGame.getPlace().loader.music.stop()
            self.music.setTime(0.0)
            self.music.setLoopCount(int(getMusicRepeatTimes(length)))
            self.music.play()
            jukeboxAnimControl = self.jukebox.getAnimControl('dance')
            if not jukeboxAnimControl.isPlaying():
                self.jukebox.loop('dance', fromFrame=0, toFrame=48)
            self.currentSongData = (
             phase, filename)

    def __stop(self):
        self.jukebox.stop()
        self.currentSongData = None
        if self.music:
            self.music.stop()
        if self.gui.isLoaded():
            self.gui.clearSongCurrentlyPlaying()
        return

    def setSongPlaying(self, songInfo, toonId):
        phase = sanitizePhase(songInfo[0])
        filename = songInfo[1]
        if not filename:
            self.__stop()
            return
        data = self.getMusicData(phase, filename)
        if data:
            self.__play(phase, filename, data[1])
            self.setSignNote(data[0])
            if self.gui.isLoaded():
                item = self.gui.popSongFromQueue()
                self.gui.setSongCurrentlyPlaying(phase, filename)
                if item == self.localQueuedSongListItem:
                    self.__localClearQueuedSong()
        if toonId == localAvatar.doId:
            localAvatar.setSystemMessage(0, TTLocalizer.PartyJukeboxNowPlaying)

    def setSignNote(self, note):
        self.noteText.node().setText(note)
        if len(note.strip()) > 0:
            self.signFlat.stash()
            self.signFlatWithNote.unstash()
            self.signTextLocator.unstash()
        else:
            self.signFlat.unstash()
            self.signFlatWithNote.stash()
            self.signTextLocator.stash()

    def __handleMoveSongToTop(self):
        if self.isUserHost() and self.localQueuedSongListItem is not None:
            self.d_moveHostSongToTopRequest()
        return

    def d_moveHostSongToTopRequest(self):
        self.notify.debug('d_moveHostSongToTopRequest')
        self.sendUpdate('moveHostSongToTopRequest')

    def moveHostSongToTop(self):
        self.notify.debug('moveHostSongToTop')
        if self.gui.isLoaded():
            self.gui.pushQueuedItemToTop(self.localQueuedSongListItem)

    def getMusicData(self, phase, filename):
        data = []
        phase = sanitizePhase(phase)
        phase = self.phaseToMusicData.get(phase)
        if phase:
            data = phase.get(filename, [])
        return data

    def __checkPartyValidity(self):
        if hasattr(base.cr.playGame, 'getPlace') and base.cr.playGame.getPlace() and hasattr(base.cr.playGame.getPlace(), 'loader') and base.cr.playGame.getPlace().loader:
            return True
        return False

    def showMessage(self, message, endState='walk'):
        base.cr.playGame.getPlace().fsm.request('activity')
        self.acceptOnce(self.messageDoneEvent, self.__handleMessageDone)
        self.messageGui = TTDialog.TTGlobalDialog(doneEvent=self.messageDoneEvent, message=message, style=TTDialog.Acknowledge)
        self.messageGui.endState = endState

    def __handleMessageDone(self):
        self.ignore(self.messageDoneEvent)
        if hasattr(base.cr.playGame.getPlace(), 'fsm'):
            if self.messageGui and hasattr(self.messageGui, 'endState'):
                self.notify.info('__handleMessageDone (endState=%s)' % self.messageGui.endState)
                base.cr.playGame.getPlace().fsm.request(self.messageGui.endState)
            else:
                self.notify.warning("messageGui has no endState, defaulting to 'walk'")
                base.cr.playGame.getPlace().fsm.request('walk')
        if self.messageGui is not None and not self.messageGui.isEmpty():
            self.messageGui.cleanup()
            self.messageGui = None
        return