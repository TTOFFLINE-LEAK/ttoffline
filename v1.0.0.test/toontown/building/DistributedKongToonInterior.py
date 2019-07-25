from panda3d.core import *
from panda3d.toontown import *
import random, ToonInteriorColors
from toontown.hood import ZoneUtil
from toontown.building import DistributedToonInterior
from toontown.toonbase import ToontownGlobals, TTLocalizer
SIGN_LEFT = -4
SIGN_RIGHT = 4
SIGN_BOTTOM = -3.5
SIGN_TOP = 1.5
FrameScale = 1.4

class DistributedKongToonInterior(DistributedToonInterior.DistributedToonInterior):

    def setup(self):
        self.dnaStore = base.cr.playGame.dnaStore
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)
        interior = self.randomDNAItem('TI_room', self.dnaStore.findNode)
        self.interior = interior.copyTo(render)
        hoodId = ZoneUtil.getCanonicalHoodId(self.zoneId)
        self.colors = ToonInteriorColors.colors[hoodId]
        self.replaceRandomInModel(self.interior)
        doorModelName = 'door_double_round_ul'
        if doorModelName[-1:] == 'r':
            doorModelName = doorModelName[:-1] + 'l'
        else:
            doorModelName = doorModelName[:-1] + 'r'
        door = self.dnaStore.findNode(doorModelName)
        door_origin = render.find('**/door_origin;+s')
        doorNP = door.copyTo(door_origin)
        door_origin.setScale(0.8, 0.8, 0.8)
        door_origin.setPos(door_origin, 0, -0.025, 0)
        color = self.randomGenerator.choice(self.colors['TI_door'])
        DNADoor.setupDoor(doorNP, self.interior, door_origin, self.dnaStore, str(self.block), color)
        doorFrame = doorNP.find('door_*_flat')
        doorFrame.wrtReparentTo(self.interior)
        doorFrame.setColor(color)
        sign = hidden.find('**/tb%s:*_landmark_*_DNARoot/**/sign;+s' % (self.block,))
        if not sign.isEmpty():
            signOrigin = self.interior.find('**/sign_origin;+s')
            newSignNP = sign.copyTo(signOrigin)
            mat = self.dnaStore.getSignTransformFromBlockNumber(int(self.block))
            inv = Mat4(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            inv.invertFrom(mat)
            newSignNP.setMat(inv)
            newSignNP.flattenLight()
            ll = Point3()
            ur = Point3()
            newSignNP.calcTightBounds(ll, ur)
            width = ur[0] - ll[0]
            height = ur[2] - ll[2]
            if width != 0 and height != 0:
                xScale = (SIGN_RIGHT - SIGN_LEFT) / width
                zScale = (SIGN_TOP - SIGN_BOTTOM) / height
                scale = min(xScale, zScale)
                xCenter = (ur[0] + ll[0]) / 2.0
                zCenter = (ur[2] + ll[2]) / 2.0
                newSignNP.setPosHprScale((SIGN_RIGHT + SIGN_LEFT) / 2.0 - xCenter * scale, -0.1, (SIGN_TOP + SIGN_BOTTOM) / 2.0 - zCenter * scale, 0.0, 0.0, 0.0, scale, scale, scale)
                newSignNP.setZ(newSignNP.getZ() + 2.3)
                memorialNP = signOrigin.attachNewNode(TextNode('memorialText'))
                memorialNP.node().setFont(ToontownGlobals.getSignFont())
                memorialNP.node().setText('Dedicated to Random Toon. Rest in peace.')
                memorialNP.setDepthWrite(1, 1)
                memorialNP.flattenLight()
                memorialNP.setX(memorialNP.getX() - 3.95)
                memorialNP.setZ(memorialNP.getZ() + 3.85)
                memorialNP.setScale(0.35)
                nowPlayingNP = signOrigin.attachNewNode(TextNode('nowPlayingText'))
                nowPlayingNP.node().setFont(ToontownGlobals.getSignFont())
                nowPlayingNP.node().setText(TTLocalizer.TributeSongPlaying)
                nowPlayingNP.setDepthWrite(1, 1)
                nowPlayingNP.flattenLight()
                nowPlayingNP.setX(nowPlayingNP.getX() - 2.35)
                nowPlayingNP.setZ(nowPlayingNP.getZ() - 1.35)
                nowPlayingNP.setScale(0.65)
                albumNP = signOrigin.attachNewNode(TextNode('albumText'))
                albumNP.node().setFont(ToontownGlobals.getSignFont())
                albumNP.node().setText('Your Own Little World')
                albumNP.setDepthWrite(1, 1)
                albumNP.flattenLight()
                albumNP.setX(nowPlayingNP.getX() - 0.55)
                albumNP.setZ(nowPlayingNP.getZ() - 1.75)
                albumNP.setScale(0.45)
        trophyOrigin = self.interior.find('**/trophy_origin')
        pos = 1.25 - 5.0
        imageFrames = hidden.attachNewNode('imageFrames')
        cm = CardMaker('card')
        for i in xrange(4):
            frame = loader.loadModel('phase_3.5/models/modules/trophy_frame')
            frame.setScale(FrameScale, 1.0, FrameScale)
            frame.reparentTo(imageFrames)
            frame.setPos(pos, 0, 0)
            imageCard = frame.attachNewNode(cm.generate())
            imageTex = loader.loadTexture('phase_14/maps/kongdo%s.jpg' % (i + 1))
            imageCard.setTexture(imageTex)
            imageCard.setX(imageCard.getX() - 0.5)
            imageCard.setZ(imageCard.getZ() - 0.5)
            imageCard.setDepthOffset(1000)
            imageCard.flattenLight()
            pos += 2.5

        if imageFrames:
            imageFrames.reparentTo(trophyOrigin)
        del self.colors
        del self.dnaStore
        del self.randomGenerator
        self.interior.flattenMedium()