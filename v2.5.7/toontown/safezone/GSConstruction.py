from panda3d.core import CollisionSphere, CollisionNode, CollisionTube
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.interval.IntervalGlobal import Parallel, LerpHprInterval
from otp.margins.WhisperPopup import *
from toontown.toonbase import ToontownGlobals
from toontown.toon import NPCToons
import random

class GSConstruction:

    def __init__(self):
        self.toon = None
        self.shovel = None
        self.shovelModelPath = 'phase_5.5/models/estate/shovels.bam'
        self.coneModelPath = 'phase_6/models/karting/cone.bam'
        self.wheelBarrelModelPath = 'phase_5.5/models/estate/wheelbarrel.bam'
        self.barrelModelPath = 'phase_6/models/props/small_round_barrel.bam'
        self.creamPieSliceModelPath = 'phase_5/models/props/cream-pie-slice.bam'
        self.clipboardModelPath = 'phase_4/models/props/tt_m_prp_acs_clipboard.bam'
        self.constructionSignModelPath = 'phase_6/models/golf/golf_construction_sign.bam'
        self.props = None
        return

    def generate(self):
        self.toon = NPCToons.createLocalNPC(2222)
        self.toon.useLOD(1000)
        self.toon.head = self.toon.find('**/__Actor_head')
        self.toon.initializeBodyCollisions('toon')
        self.toon.setPosHpr(64.03, 12.352, 0.095, 274.359, 0, 0)
        self.toon.reparentTo(render)
        self.toon.loop('loop-dig')
        self.toon.addActive()
        self.shovel = loader.loadModel(self.shovelModelPath).find('**/shovelD')
        self.shovel.reparentTo(self.toon.find('**/rightHand'))
        self.shovel.setH(-90)
        self.shovel.setP(216)
        self.shovel.setX(0.2)
        self.cone = loader.loadModel(self.coneModelPath)
        self.cone.reparentTo(render)
        self.cone.setPosHpr(57.029, 18.531, 0.095, 45, 0, 0)
        self.cone2 = loader.loadModel(self.coneModelPath)
        self.cone2.reparentTo(render)
        self.cone2.setPosHpr(57.015, 12.556, 0.095, 135, 0, 0)
        self.cone3 = loader.loadModel(self.coneModelPath)
        self.cone3.reparentTo(render)
        self.cone3.setPosHpr(57.029, 5.055, 0.095, -45, 0, 0)
        self.barrel = loader.loadModel(self.barrelModelPath)
        self.barrel.setPosHpr(59.654, 18.275, 0.095, 167.548, 0, 0)
        self.barrel.reparentTo(render)
        self.barrel2 = loader.loadModel(self.barrelModelPath)
        self.barrel2.setPosHpr(61.975, 18.16, 0.095, 219.01, 0, 0)
        self.barrel2.reparentTo(render)
        self.barrel3 = loader.loadModel(self.barrelModelPath)
        self.barrel3.setPosHpr(60.456, 19.654, 0.095, 363.297, 0, 0)
        self.barrel3.reparentTo(render)
        self.wheelbarrel = loader.loadModel(self.wheelBarrelModelPath)
        self.wheelbarrel.reparentTo(render)
        self.wheelbarrel.setPosHpr(60.08, 4.339, 0.095, -29.058, 0, 0)
        self.creampieslice = loader.loadModel(self.creamPieSliceModelPath)
        self.creampieslice.setPosHpr(59.654, 18.275, 2.095, -514.649, 0, 0)
        self.creampieslice.reparentTo(render)
        self.clipboard = loader.loadModel(self.clipboardModelPath)
        self.clipboard.setPosHpr(60.456, 19.654, 2.095, -506.554, 0, 90)
        self.clipboard.reparentTo(render)
        self.construction = loader.loadModel(self.constructionSignModelPath)
        self.construction.setPosHpr(55.872, 9.394, 0.095, -448.917, 0, 0)
        self.construction.reparentTo(render)
        self.construction1 = loader.loadModel(self.constructionSignModelPath)
        self.construction1.setPosHpr(55.753, 15.855, 0.095, -450.165, 0, 0)
        self.construction1.reparentTo(render)
        self.props = [
         self.shovel, self.cone, self.cone2, self.cone3, self.barrel, self.barrel2, self.barrel3, self.wheelbarrel, self.creampieslice, self.clipboard, self.construction, self.construction1]

    def toonPhrase(self):
        toonChat = [
         'One, two! One, two! One, two!',
         'Come on, you can do it!!',
         'What are they planning to make here anyhow?',
         'Why has it taken this long just for a little bit of fence?',
         'All this just for some silly stand- the nerve!',
         'At least I have a Golden Shovel!',
         'Are you just gonna sit there and watch?',
         'Who knew the Toon Council were cheapskates?!']
        self.toon.setChatAbsolute(random.choice(toonChat), CFSpeech | CFTimeout)

    def disable(self):
        self.shovelModelPath = None
        if self.toon:
            self.toon.removeActive()
            self.toon.hide()
            self.toon = None
        for prop in self.props:
            if prop:
                prop.removeNode()
                prop = None

        return