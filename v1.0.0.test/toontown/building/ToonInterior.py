from panda3d.core import *
from toontown.toonbase.ToonBaseGlobal import *
from direct.directnotify import DirectNotifyGlobal
from toontown.hood import Place
from toontown.hood import ZoneUtil
from direct.showbase import DirectObject
from direct.fsm import StateData
from direct.fsm import ClassicFSM, State
from direct.fsm import State
from direct.task import Task
from otp.distributed.TelemetryLimiter import RotationLimitToH, TLGatherAllAvs
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.toon import NPCForceAcknowledge
from toontown.toon import HealthForceAcknowledge
import random

class ToonInterior(Place.Place):
    notify = DirectNotifyGlobal.directNotify.newCategory('ToonInterior')

    def __init__(self, loader, parentFSMState, doneEvent):
        Place.Place.__init__(self, loader, doneEvent)
        self.dnaFile = 'phase_7/models/modules/toon_interior'
        self.isInterior = 1
        self.tfaDoneEvent = 'tfaDoneEvent'
        self.hfaDoneEvent = 'hfaDoneEvent'
        self.npcfaDoneEvent = 'npcfaDoneEvent'
        self.fsm = ClassicFSM.ClassicFSM('ToonInterior', [State.State('start', self.enterStart, self.exitStart, ['doorIn', 'teleportIn', 'tutorial']),
         State.State('walk', self.enterWalk, self.exitWalk, ['sit',
          'stickerBook',
          'doorOut',
          'DFA',
          'trialerFA',
          'teleportOut',
          'quest',
          'purchase',
          'phone',
          'stopped',
          'pet',
          'died']),
         State.State('sit', self.enterSit, self.exitSit, ['walk']),
         State.State('stickerBook', self.enterStickerBook, self.exitStickerBook, ['walk',
          'DFA',
          'trialerFA',
          'sit',
          'doorOut',
          'teleportOut',
          'quest',
          'purchase',
          'phone',
          'stopped',
          'pet',
          'died']),
         State.State('trialerFA', self.enterTrialerFA, self.exitTrialerFA, ['trialerFAReject', 'DFA']),
         State.State('trialerFAReject', self.enterTrialerFAReject, self.exitTrialerFAReject, ['walk']),
         State.State('DFA', self.enterDFA, self.exitDFA, ['DFAReject',
          'HFA',
          'NPCFA',
          'teleportOut',
          'doorOut']),
         State.State('DFAReject', self.enterDFAReject, self.exitDFAReject, ['walk']),
         State.State('NPCFA', self.enterNPCFA, self.exitNPCFA, ['NPCFAReject', 'HFA', 'teleportOut']),
         State.State('NPCFAReject', self.enterNPCFAReject, self.exitNPCFAReject, ['walk']),
         State.State('HFA', self.enterHFA, self.exitHFA, ['HFAReject', 'teleportOut', 'tunnelOut']),
         State.State('HFAReject', self.enterHFAReject, self.exitHFAReject, ['walk']),
         State.State('doorIn', self.enterDoorIn, self.exitDoorIn, ['walk']),
         State.State('doorOut', self.enterDoorOut, self.exitDoorOut, ['walk']),
         State.State('teleportIn', self.enterTeleportIn, self.exitTeleportIn, ['walk']),
         State.State('teleportOut', self.enterTeleportOut, self.exitTeleportOut, ['teleportIn']),
         State.State('quest', self.enterQuest, self.exitQuest, ['walk', 'doorOut']),
         State.State('tutorial', self.enterTutorial, self.exitTutorial, ['walk', 'quest']),
         State.State('purchase', self.enterPurchase, self.exitPurchase, ['walk', 'doorOut']),
         State.State('pet', self.enterPet, self.exitPet, ['walk']),
         State.State('phone', self.enterPhone, self.exitPhone, ['walk', 'doorOut']),
         State.State('stopped', self.enterStopped, self.exitStopped, ['walk', 'doorOut']),
         State.State('died', self.enterDied, self.exitDied, ['walk', 'stickerBook', 'final']),
         State.State('final', self.enterFinal, self.exitFinal, ['start'])], 'start', 'final')
        self.parentFSMState = parentFSMState

    def load(self):
        Place.Place.load(self)
        self.parentFSMState.addChild(self.fsm)

    def unload(self):
        Place.Place.unload(self)
        self.parentFSMState.removeChild(self.fsm)
        del self.parentFSMState
        del self.fsm
        ModelPool.garbageCollect()
        TexturePool.garbageCollect()

    def enter(self, requestStatus):
        self.zoneId = requestStatus['zoneId']
        self.fsm.enterInitialState()
        messenger.send('enterToonInterior')
        self.accept('doorDoneEvent', self.handleDoorDoneEvent)
        self.accept('DistributedDoor_doorTrigger', self.handleDoorTrigger)
        volume = requestStatus.get('musicVolume', 0.7)
        if self.zoneId == ToontownGlobals.Kongdominium:
            taskMgr.add(self.kongdoMusicTask, 'kongdo-music-task', extraArgs=[volume], appendTask=True)
        else:
            base.playMusic(self.loader.activityMusic, looping=1, volume=volume)
        self._telemLimiter = TLGatherAllAvs('ToonInterior', RotationLimitToH)
        NametagGlobals.setMasterArrowsOn(1)
        self.fsm.request(requestStatus['how'], [requestStatus])
        zoneId = self.zoneId
        if not base.localAvatar.tutorialAck:
            zoneId = 20002
        base.cr.discordManager.setInfo(base.cr.discordManager.getState(), None, ToontownGlobals.Zone2String.get(ZoneUtil.getHoodId(zoneId)), None, None, None, zoneId)
        return

    def exit(self):
        self.ignoreAll()
        messenger.send('exitToonInterior')
        self._telemLimiter.destroy()
        del self._telemLimiter
        NametagGlobals.setMasterArrowsOn(0)
        if self.zoneId == ToontownGlobals.Kongdominium and self.activityMusicOverride:
            taskMgr.remove('kongdo-music-task')
            self.activityMusicOverride.stop()
        else:
            self.loader.activityMusic.stop()

    def setState(self, state):
        self.fsm.request(state)

    def enterTutorial(self, requestStatus):
        self.fsm.request('walk')
        base.localAvatar.b_setParent(ToontownGlobals.SPRender)
        globalClock.tick()
        base.transitions.irisIn()
        messenger.send('enterTutorialInterior')

    def exitTutorial(self):
        pass

    def doRequestLeave(self, requestStatus):
        self.fsm.request('trialerFA', [requestStatus])

    def enterDFACallback(self, requestStatus, doneStatus):
        self.dfa.exit()
        del self.dfa
        ds = doneStatus['mode']
        if ds == 'complete':
            self.fsm.request('NPCFA', [requestStatus])
        else:
            if ds == 'incomplete':
                self.fsm.request('DFAReject')
            else:
                self.notify.error('Unknown done status for DownloadForceAcknowledge: ' + `doneStatus`)

    def enterNPCFA(self, requestStatus):
        self.acceptOnce(self.npcfaDoneEvent, self.enterNPCFACallback, [requestStatus])
        self.npcfa = NPCForceAcknowledge.NPCForceAcknowledge(self.npcfaDoneEvent)
        self.npcfa.enter()

    def exitNPCFA(self):
        self.ignore(self.npcfaDoneEvent)

    def enterNPCFACallback(self, requestStatus, doneStatus):
        self.npcfa.exit()
        del self.npcfa
        if doneStatus['mode'] == 'complete':
            outHow = {'teleportIn': 'teleportOut', 'tunnelIn': 'tunnelOut', 'doorIn': 'doorOut'}
            self.fsm.request(outHow[requestStatus['how']], [requestStatus])
        else:
            if doneStatus['mode'] == 'incomplete':
                self.fsm.request('NPCFAReject')
            else:
                self.notify.error('Unknown done status for NPCForceAcknowledge: ' + `doneStatus`)

    def enterNPCFAReject(self):
        self.fsm.request('walk')

    def exitNPCFAReject(self):
        pass

    def enterHFA(self, requestStatus):
        self.acceptOnce(self.hfaDoneEvent, self.enterHFACallback, [requestStatus])
        self.hfa = HealthForceAcknowledge.HealthForceAcknowledge(self.hfaDoneEvent)
        self.hfa.enter(1)

    def exitHFA(self):
        self.ignore(self.hfaDoneEvent)

    def enterHFACallback(self, requestStatus, doneStatus):
        self.hfa.exit()
        del self.hfa
        if doneStatus['mode'] == 'complete':
            outHow = {'teleportIn': 'teleportOut', 'tunnelIn': 'tunnelOut', 'doorIn': 'doorOut'}
            self.fsm.request(outHow[requestStatus['how']], [requestStatus])
        else:
            if doneStatus['mode'] == 'incomplete':
                self.fsm.request('HFAReject')
            else:
                self.notify.error('Unknown done status for HealthForceAcknowledge: ' + `doneStatus`)

    def enterHFAReject(self):
        self.fsm.request('walk')

    def exitHFAReject(self):
        pass

    def enterTeleportIn(self, requestStatus):
        if ZoneUtil.isPetshop(self.zoneId):
            base.localAvatar.setPosHpr(0, 0, ToontownGlobals.FloorOffset, 45.0, 0.0, 0.0)
        else:
            base.localAvatar.setPosHpr(2.5, 11.5, ToontownGlobals.FloorOffset, 45.0, 0.0, 0.0)
        Place.Place.enterTeleportIn(self, requestStatus)

    def enterTeleportOut(self, requestStatus):
        Place.Place.enterTeleportOut(self, requestStatus, self.__teleportOutDone)

    def __teleportOutDone(self, requestStatus):
        hoodId = requestStatus['hoodId']
        zoneId = requestStatus['zoneId']
        shardId = requestStatus['shardId']
        if hoodId == self.loader.hood.id and zoneId == self.zoneId and shardId == None:
            self.fsm.request('teleportIn', [requestStatus])
        else:
            if hoodId == ToontownGlobals.MyEstate:
                self.getEstateZoneAndGoHome(requestStatus)
            else:
                self.doneStatus = requestStatus
                messenger.send(self.doneEvent)
        return

    def goHomeFailed(self, task):
        self.notifyUserGoHomeFailed()
        self.ignore('setLocalEstateZone')
        self.doneStatus['avId'] = -1
        self.doneStatus['zoneId'] = self.getZoneId()
        self.fsm.request('teleportIn', [self.doneStatus])
        return Task.done

    def exitTeleportOut(self):
        Place.Place.exitTeleportOut(self)

    def getKongdoSongs(self):
        return ToontownGlobals.KongdominiumSongs

    def kongdoMusicTask(self, volume, task):
        kongdoSongs = self.getKongdoSongs()
        songName = random.choice(kongdoSongs.keys())
        songChoice = kongdoSongs[songName]
        self.activityMusicOverride = base.loader.loadMusic(songChoice)
        base.playMusic(self.activityMusicOverride, looping=0, volume=volume)
        signOrigin = render.find('**/sign_origin;+s')
        if not signOrigin.isEmpty():
            songNameNP = render.find('**/songName')
            if not songNameNP.isEmpty():
                songNameNP.removeNode()
            songNameNP = signOrigin.attachNewNode(TextNode('songName'))
            songNameNP.node().setFont(ToontownGlobals.getSignFont())
            songNameNP.node().setText(songName)
            songNameNP.setDepthWrite(1, 1)
            songNameNP.flattenLight()
            ll = Point3()
            ur = Point3()
            songNameNP.calcTightBounds(ll, ur)
            width = ur[0] - ll[0]
            height = ur[2] - ll[2]
            if width != 0 and height != 0:
                xScale = 8 / width
                zScale = 5.0 / height
                scale = min(xScale, zScale)
                if len(songName) < 15:
                    scale = scale - 0.85
                xCenter = (ur[0] + ll[0]) / 2.0
                songNameNP.setZ(songNameNP.getZ() - 2.25)
                songNameNP.setX(0 / 2.0 - xCenter * scale)
                songNameNP.setScale(scale)
        task.delayTime = self.activityMusicOverride.length() + 2.0
        return task.again