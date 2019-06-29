from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.distributed.MsgTypes import CLIENTAGENT_EJECT
from direct.distributed.PyDatagram import PyDatagram
from toontown.hood import ZoneUtil
from toontown.toonbase import ToontownGlobals

class DistributedEventManagerAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedEventManagerAI')

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.accept('avatarEntered', self.toonEntered)
        self.accept('avatarExited', self.toonExited)
        self.toons = []
        self.isElections = False
        self.eventDelay = 0
        self.eventMode = 0
        self.eventStarted = False
        self.timeLeft = 0

    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)
        self.determineEvent()

    def determineEvent(self):
        electionsActive = config.GetBool('want-doomsday', False)
        if electionsActive:
            self.isElections = True

    def toonEntered(self, toon):
        if not toon:
            return
        avId = toon.getDoId()
        if not avId:
            return
        if avId in self.toons:
            return
        self.toons.append(avId)
        if toon.getAdminAccess() >= 407:
            self.sendUpdateToAvatarId(avId, 'showAdminGui', [])

    def toonExited(self, toon):
        if not toon:
            return
        avId = toon.getDoId()
        if not avId:
            return
        if avId not in self.toons:
            return
        self.toons.remove(avId)

    def setEventDelay(self, eventDelay):
        self.eventDelay = eventDelay

    def setEventMode(self, eventMode):
        self.eventMode = eventMode

    def setEventStarted(self, eventStarted):
        self.eventStarted = eventStarted

    def d_setEventStarted(self, eventStarted):
        self.sendUpdate('setEventStarted', [eventStarted])

    def b_setEventStarted(self, eventStarted):
        self.setEventStarted(eventStarted)
        self.d_setEventStarted(eventStarted)

    def getEventStarted(self):
        return self.eventStarted

    def evaluateEvent(self):
        self.startEvent()
        return True

    def startEvent(self):
        if self.getEventStarted() is True:
            return
        self.b_setEventStarted(True)
        self.timeLeft = self.eventDelay
        if self.isElections:
            taskMgr.doMethodLater(0.1, self.announceTimeLeft, self.taskName('announce-time-left-task'))
            taskMgr.doMethodLater(1.5, self.teleportNotify, self.taskName('teleport-notify-task'))
            taskMgr.doMethodLater(self.eventDelay, self.performInitialPlayerCheck, self.taskName('initial-player-check-task'))
            taskMgr.doMethodLater(self.eventDelay + 30, self.performFinalPlayerCheck, self.taskName('final-player-check-task'))
            taskMgr.doMethodLater(self.eventDelay + 35, self.sendFinalAnnouncement, self.taskName('final-announcement-task'))
            taskMgr.doMethodLater(self.eventDelay + 45, self.handleEventStart, self.taskName('handle-event-start-task'))

    def announceTimeLeft(self, task):
        timeInMinutes = self.timeLeft / 60
        if timeInMinutes == 1:
            timeLeft = '%s minute' % timeInMinutes
        else:
            timeLeft = '%s minutes' % timeInMinutes
        if timeInMinutes > 0:
            if self.isElections:
                msg = 'Toon HQ: Attention Toons!\nThe Elections will begin in %s!' % timeLeft
            else:
                return task.done
        else:
            if self.isElections:
                msg = 'Toon HQ: Attention Toons!\nThe Elections will begin shortly!'
            else:
                return task.done
        for toonId in self.toons:
            toon = self.air.doId2do.get(toonId)
            if toon:
                toon.d_setSystemMessage(0, msg)

        self.timeLeft -= 60
        if self.timeLeft == -60:
            return task.done
        task.delayTime = 60
        return task.again

    def teleportNotify(self, task):
        if self.eventMode == ToontownGlobals.EventManagerStrictMode:
            msg = 'WARNING: You will automatically be teleported to Toontown Central when the event begins.'
            for toonId in self.toons:
                toon = self.air.doId2do.get(toonId)
                if toon:
                    if toon.zoneId != ToontownGlobals.ToontownCentral:
                        toon.d_setSystemMessage(0, msg)

        return task.done

    def performInitialPlayerCheck(self, task):
        if self.eventMode == ToontownGlobals.EventManagerStrictMode:
            for toonId in self.toons:
                toon = self.air.doId2do.get(toonId)
                if toon:
                    if toon.zoneId != ToontownGlobals.ToontownCentral:
                        self.sendUpdateToAvatarId(toonId, 'requestTeleport', [
                         '', '', ZoneUtil.getHoodId(ToontownGlobals.ToontownCentral),
                         ToontownGlobals.ToontownCentral, 0])

        return task.done

    def performFinalPlayerCheck(self, task):
        if self.eventMode == ToontownGlobals.EventManagerStrictMode:
            for toonId in self.toons:
                toon = self.air.doId2do.get(toonId)
                if toon:
                    if toon.zoneId != ToontownGlobals.ToontownCentral:
                        dg = PyDatagram()
                        dg.addServerHeader(toon.GetPuppetConnectionChannel(toon.doId), self.air.ourChannel, CLIENTAGENT_EJECT)
                        dg.addUint16(158)
                        dg.addString('Client took too long to enter TTC!')
                        self.air.send(dg)

        return task.done

    def sendFinalAnnouncement(self, task):
        if self.isElections:
            msg = 'Toon HQ: Attention Toons!\nThe Elections are about to begin!'
        else:
            return task.done
        for toonId in self.toons:
            toon = self.air.doId2do.get(toonId)
            if toon:
                toon.d_setSystemMessage(0, msg)

        return task.done

    def handleEventStart(self, task):
        if self.isElections:
            taskMgr.doMethodLater(0.1, self.gotoElectionEvent, self.taskName('goto-election-event-task'))
        return task.done

    def gotoElectionEvent(self, task):
        for toonId in self.toons:
            toon = self.air.doId2do.get(toonId)
            if toon:
                if toon.zoneId != ToontownGlobals.ToontownCentral:
                    return task.again

        event = self.air.doFind('ElectionEvent')
        if event:
            event.b_setState('Event')
        return task.done