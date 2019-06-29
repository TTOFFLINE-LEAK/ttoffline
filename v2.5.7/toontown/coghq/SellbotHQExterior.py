from direct.directnotify import DirectNotifyGlobal
from direct.fsm import ClassicFSM, State
from toontown.building import Elevator
from toontown.coghq import CogHQExterior
from toontown.dna.DNAStorage import DNAStorage
from toontown.dna.DNAParser import loadDNAFileAI
from toontown.hood import ZoneUtil

class SellbotHQExterior(CogHQExterior.CogHQExterior):
    notify = DirectNotifyGlobal.directNotify.newCategory('SellbotHQExterior')

    def __init__(self, loader, parentFSM, doneEvent):
        CogHQExterior.CogHQExterior.__init__(self, loader, parentFSM, doneEvent)
        self.elevatorDoneEvent = 'elevatorDone'
        self.trains = None
        self.fsm.addState(State.State('elevator', self.enterElevator, self.exitElevator, ['walk', 'stopped', 'golfKartBlock']))
        state = self.fsm.getStateNamed('walk')
        state.addTransition('elevator')
        state = self.fsm.getStateNamed('stopped')
        state.addTransition('elevator')
        state = self.fsm.getStateNamed('stickerBook')
        state.addTransition('elevator')
        return

    def enter(self, requestStatus):
        CogHQExterior.CogHQExterior.enter(self, requestStatus)
        self.loader.hood.startSky()
        self.loader.factGeom.reparentTo(render)
        dnaStore = DNAStorage()
        dnaFileName = self.genDNAFileName(self.zoneId)
        loadDNAFileAI(dnaStore, dnaFileName)
        self.zoneVisDict = {}
        for i in xrange(dnaStore.getNumDNAVisGroupsAI()):
            groupFullName = dnaStore.getDNAVisGroupName(i)
            visGroup = dnaStore.getDNAVisGroupAI(i)
            visZoneId = int(base.cr.hoodMgr.extractGroupName(groupFullName))
            visZoneId = ZoneUtil.getTrueZoneId(visZoneId, self.zoneId)
            visibles = []
            for i in xrange(visGroup.getNumVisibles()):
                visibles.append(int(visGroup.visibles[i]))

            visibles.append(ZoneUtil.getBranchZone(visZoneId))
            self.zoneVisDict[visZoneId] = visibles

        base.cr.sendSetZoneMsg(self.zoneId, self.zoneVisDict.values()[0])

    def exit(self):
        self.loader.hood.stopSky()
        CogHQExterior.CogHQExterior.exit(self)

    def enterElevator(self, distElevator, skipDFABoard=0):
        self.accept(self.elevatorDoneEvent, self.handleElevatorDone)
        self.elevator = Elevator.Elevator(self.fsm.getStateNamed('elevator'), self.elevatorDoneEvent, distElevator)
        if skipDFABoard:
            self.elevator.skipDFABoard = 1
        distElevator.elevatorFSM = self.elevator
        self.elevator.setReverseBoardingCamera(True)
        self.elevator.load()
        self.elevator.enter()

    def exitElevator(self):
        self.ignore(self.elevatorDoneEvent)
        self.elevator.unload()
        self.elevator.exit()
        del self.elevator

    def detectedElevatorCollision(self, distElevator):
        if self.fsm.getCurrentState().getName() == 'walk':
            self.fsm.request('elevator', [distElevator])

    def handleElevatorDone(self, doneStatus):
        self.notify.debug('handling elevator done event')
        where = doneStatus['where']
        if where == 'reject':
            if hasattr(base.localAvatar, 'elevatorNotifier') and base.localAvatar.elevatorNotifier.isNotifierOpen():
                pass
            else:
                self.fsm.request('walk')
        else:
            if where == 'exit':
                self.fsm.request('walk')
            else:
                if where == 'factoryExterior':
                    self.doneStatus = doneStatus
                    messenger.send(self.doneEvent)
                else:
                    self.notify.error('Unknown mode: %s in handleElevatorDone' % where)