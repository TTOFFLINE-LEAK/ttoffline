from panda3d.core import *
from direct.interval.IntervalGlobal import *
from toontown.suit import DistributedCashbotBoss
from direct.directnotify import DirectNotifyGlobal
from toontown.coghq import CogHQBossBattle

class CashbotHQBossBattle(CogHQBossBattle.CogHQBossBattle):
    notify = DirectNotifyGlobal.directNotify.newCategory('CashbotHQBossBattle')

    def __init__(self, loader, parentFSM, doneEvent):
        CogHQBossBattle.CogHQBossBattle.__init__(self, loader, parentFSM, doneEvent)
        self.teleportInPosHpr = (88, -214, 0, 210, 0, 0)

    def load(self):
        CogHQBossBattle.CogHQBossBattle.load(self)

    def unload(self):
        CogHQBossBattle.CogHQBossBattle.unload(self)

    def enter(self, requestStatus):
        CogHQBossBattle.CogHQBossBattle.enter(self, requestStatus, DistributedCashbotBoss.OneBossCog)

    def exit(self):
        CogHQBossBattle.CogHQBossBattle.exit(self)

    def exitCrane(self):
        CogHQBossBattle.CogHQBossBattle.exitCrane(self)
        messenger.send('exitCrane')

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
                    self.notify.error('Unknown mode: ' + where + ' in handleElevatorDone')