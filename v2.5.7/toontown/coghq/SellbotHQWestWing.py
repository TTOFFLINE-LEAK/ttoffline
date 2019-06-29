import random
from direct.directnotify import DirectNotifyGlobal
from panda3d.core import *
import FactoryExterior
from toontown.battle import BattlePlace
DROP_POINTS = [
 (54, -110, 0.998, -5, 0, 0),
 (64, -105, 0.998, 27, 0, 0),
 (49, -87, 0.998, 17, 0, 0),
 (25, -103, 0.998, 5, 0, 0),
 (-34, -176, 0.998, 340, 0, 0),
 (-105, -161, 0.998, 340, 0, 0),
 (-112, -84, 0.557, 330, 0, 0)]

class SellbotHQWestWing(FactoryExterior.FactoryExterior):
    notify = DirectNotifyGlobal.directNotify.newCategory('SellbotHQWestWing')

    def enterTeleportIn(self, requestStatus):
        dropPoint = random.choice(DROP_POINTS)
        base.localAvatar.setPosHpr(dropPoint[0], dropPoint[1], dropPoint[2], dropPoint[3], dropPoint[4], dropPoint[5])
        BattlePlace.BattlePlace.enterTeleportIn(self, requestStatus)