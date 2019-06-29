from panda3d.core import *
from panda3d.toontown import *
import random, ToonInteriorColors
from toontown.hood import ZoneUtil
from toontown.building import DistributedToonInterior
from toontown.toonbase import ToontownGlobals
SIGN_LEFT = -4
SIGN_RIGHT = 4
SIGN_BOTTOM = -3.5
SIGN_TOP = 1.5
FrameScale = 1.4

class DistributedPizzeriaInterior(DistributedToonInterior.DistributedToonInterior):

    def setup(self):
        interior = loader.loadModel('phase_14/models/modules/pizzeria')
        self.interior = interior.copyTo(render)
        self.interior.find('**/floor').setBin('ground', -10)
        self.dnaStore = base.cr.playGame.dnaStore
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)
        hoodId = ZoneUtil.getCanonicalHoodId(self.zoneId)
        self.colors = ToonInteriorColors.colors[hoodId]
        door = self.dnaStore.findNode('door_double_round_ur')
        doorOrigin = self.interior.attachNewNode('door_origin')
        doorOrigin.setPos(0, 31.5, 0)
        doorOriginNPName = doorOrigin.getName()
        doorOriginIndexStr = doorOriginNPName[len('door_origin_'):]
        newNode = ModelNode('door_' + doorOriginIndexStr)
        newNodePath = NodePath(newNode)
        newNodePath.reparentTo(self.interior)
        doorNP = door.copyTo(newNodePath)
        doorOrigin.setScale(0.8, 0.8, 0.8)
        doorOrigin.setPos(doorOrigin, 0, -0.025, 0)
        color = self.randomGenerator.choice(self.colors['TI_door'])
        triggerId = str(self.block) + '_' + doorOriginIndexStr
        DNADoor.setupDoor(doorNP, newNodePath, doorOrigin, self.dnaStore, str(self.block), color)
        doorFrame = doorNP.find('door_*_flat')
        doorFrame.setColor(color)