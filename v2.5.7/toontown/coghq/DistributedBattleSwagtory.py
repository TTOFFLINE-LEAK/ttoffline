import random
from direct.directnotify import DirectNotifyGlobal
from otp.margins.WhisperPopup import *
from toontown.battle import SuitBattleGlobals
from toontown.suit import SuitDNA
from toontown.toonbase import TTLocalizer
import DistributedBattleFactory

class DistributedBattleSwagtory(DistributedBattleFactory.DistributedBattleFactory):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedBattleSwagtory')

    def getSuitName(self, dept):
        if base.localAvatar.cogCounts[((dept + 1) * SuitDNA.suitsPerDept - 1)] != 0:
            return SuitBattleGlobals.SuitAttributes[SuitDNA.suitHeadTypes[((dept + 1) * SuitDNA.suitsPerDept - 1)]]['name']
        return TTLocalizer.RankNineUnknown.format(SuitDNA.suitDeptFullnames.get(SuitDNA.suitDepts[dept], None))
        return

    def informAboutReward(self, summonType, deptIndex):
        if summonType == 'single':
            summonType = 'Cog'
        if summonType == -1 or deptIndex == -1:
            base.localAvatar.setSystemMessage(0, TTLocalizer.SwagtoryNoReward, WhisperPopup.WTSwagForeman)
        else:
            base.localAvatar.setSystemMessage(0, random.choice(TTLocalizer.SwagtoryReward).format(self.getSuitName(deptIndex), summonType), WhisperPopup.WTSwagForeman)