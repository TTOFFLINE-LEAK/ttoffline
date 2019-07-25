from panda3d.core import *
from panda3d.toontown import *
from toontown.building import DistributedToonInterior
from toontown.hood import ZoneUtil
from toontown.suit.Chairman import Chairman
import ToonInteriorColors, random
SIGN_LEFT = -4
SIGN_RIGHT = 4
SIGN_BOTTOM = -3.5
SIGN_TOP = 1.5
FrameScale = 1.4

class DistributedGyrosLabInterior(DistributedToonInterior.DistributedToonInterior):

    def setup(self):
        interior = loader.loadModel('phase_14/models/modules/gyros_lab')
        self.interior = interior.copyTo(render)
        self.interior.find('**/entrance/**/Floor').setBin('ground', -10)
        self.interior.find('**/GyroGearhead_int_egg/**/Floor').setBin('ground', -10)
        self.interior.find('**/bulb_g').hide()
        self.interior.find('**/control_stand').setScale(1.25)
        self.interior.find('**/door').setH(-60)
        sky = loader.loadModel('phase_8/models/props/DL_sky')
        sky.setPos(0, 0, -50)
        sky.reparentTo(self.interior)
        self.chairman = Chairman()
        self.chairman.reparentTo(self.interior)
        self.chairman.setPosHpr(175.5, -24.5, 0.1, 90.0, 0.0, 0.0)
        self.chairman.pose('neutral', 0)
        self.chairman.find('**/left_eye').setColorScale(1, 1, 1, 0)
        self.chairman.find('**/right_eye').setColorScale(1, 1, 1, 0)
        self.chairman.getChild(0).setScale(1.3)
        self.chairman.addActive()
        chairmanNote = loader.loadModel('phase_14/models/char/chairmanSign-mod')
        chairmanNote.reparentTo(self.interior)
        chairmanNote.setPosHpr(175.25, -24.57, 0.0, -90.0, 0.0, 0.0)
        self.dnaStore = base.cr.playGame.dnaStore
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)
        hoodId = ZoneUtil.getCanonicalHoodId(self.zoneId)
        self.colors = ToonInteriorColors.colors[hoodId]
        door = self.dnaStore.findNode('door_double_round_ur')
        doorOrigin = self.interior.attachNewNode('door_origin')
        doorOrigin.setPosHpr(-49, -12, 0.02, 90, 0, 0)
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

    def disable(self):
        if self.chairman:
            self.chairman.cleanup()
            self.chairman.removeNode()
            del self.chairman
        DistributedToonInterior.DistributedToonInterior.disable(self)