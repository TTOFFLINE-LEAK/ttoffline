from direct.directnotify import DirectNotifyGlobal
from toontown.battle.DistributedBattleAI import DistributedBattleAI

class DistributedBattleSquirtingFlowerAI(DistributedBattleAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedBattleSquirtingFlowerAI')