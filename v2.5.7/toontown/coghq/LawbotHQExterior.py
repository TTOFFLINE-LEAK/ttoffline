from direct.directnotify import DirectNotifyGlobal
from toontown.battle import BattlePlace
from direct.fsm import ClassicFSM, State
from direct.fsm import State
from toontown.toonbase import ToontownGlobals
from toontown.building import Elevator
from panda3d.core import *
from toontown.coghq import CogHQExterior
from toontown.dna.DNAStorage import DNAStorage
from toontown.dna.DNAParser import loadDNAFileAI
from toontown.hood import ZoneUtil

class LawbotHQExterior(CogHQExterior.CogHQExterior):
    notify = DirectNotifyGlobal.directNotify.newCategory('LawbotHQExterior')

    def enter(self, requestStatus):
        CogHQExterior.CogHQExterior.enter(self, requestStatus)
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