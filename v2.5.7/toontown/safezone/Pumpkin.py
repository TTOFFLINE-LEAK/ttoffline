from panda3d.core import *
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from otp.avatar import Avatar
from direct.distributed import DistributedNode
from toontown.toonbase import ToontownGlobals
from panda3d.core import *
from toontown.toonbase import TTLocalizer
import math
AnimDict = {'s': (('neutral', 'neutral'), ('float', 'float'), ('grow', 'grow'), ('spin', 'spin')), 'l': (('neutral', 'neutral'), ('fly', 'fly'), ('jump', 'jump'), ('laugh', 'laugh'))}
ModelDict = {'s': 'phase_14/models/char/pumpkin_short-', 'l': 'phase_14/models/char/pumpkin_tall-'}
PumpkinDNA = ['s', 'l']

class Pumpkin(Avatar.Avatar):

    def __init__(self):
        try:
            self.Pump_init
        except:
            self.Pump_init = 1
            Avatar.Avatar.__init__(self)

    def delete(self):
        try:
            self.Pump_del
        except:
            self.Pump_del = 1
            filePrefix = ModelDict[self.size]
            loader.unloadModel(filePrefix + 'mod')
            animList = AnimDict[self.size]
            for anim in animList:
                loader.unloadModel(filePrefix + anim[1])

            Avatar.Avatar.delete(self)

        return

    def setSize(self, size):
        if size in PumpkinDNA:
            self.size = size
        else:
            self.notify.warning("Pumpkin DNA isn't valid! Defaulting to 's'.")
            self.size = 's'

    def getSize(self):
        return self.size

    def generatePumpkin(self):
        filePrefix = ModelDict[self.size]
        self.loadModel(filePrefix + 'mod')
        animDict = {}
        animList = AnimDict[self.size]
        for anim in animList:
            animDict[anim[0]] = filePrefix + anim[1]

        self.loadAnims(animDict)
        self.setBlend(frameBlend=config.GetBool('interpolate-animations', True))

    def getAnim(self, id=None):
        if id:
            if id == 0 and self.size == 's':
                if self.size == 's':
                    loop = Sequence(Wait(1), ActorInterval(self, 'grow'), Func(self.loop, 'neutral'), Wait(12), ActorInterval(self, 'spin'), Func(self.loop, 'neutral'), Wait(12), ActorInterval(self, 'float'), Func(self.loop, 'neutral'), Wait(11))
                elif self.size == 'l':
                    loop = Sequence(Wait(5), ActorInterval(self, 'laugh'), Func(self.loop, 'neutral'), Wait(12), ActorInterval(self, 'jump'), Func(self.loop, 'neutral'), Wait(12), ActorInterval(self, 'fly'), Func(self.loop, 'neutral'), Wait(7))
                else:
                    loop = Sequence(ActorInterval(self, 'neutral'))
            elif id == 1:
                if self.size == 's':
                    loop = Sequence(Wait(2), ActorInterval(self, 'float'), Func(self.loop, 'neutral'), Wait(12), ActorInterval(self, 'grow'), Func(self.loop, 'neutral'), Wait(12), ActorInterval(self, 'spin'), Func(self.loop, 'neutral'), Wait(10))
                elif self.size == 'l':
                    loop = Sequence(Wait(6), ActorInterval(self, 'fly'), Func(self.loop, 'neutral'), Wait(12), ActorInterval(self, 'laugh'), Func(self.loop, 'neutral'), Wait(12), ActorInterval(self, 'jump'), Func(self.loop, 'neutral'), Wait(6))
                else:
                    loop = Sequence(ActorInterval(self, 'neutral'))
            elif id == 2:
                if self.size == 's':
                    loop = Sequence(Wait(3), ActorInterval(self, 'spin'), Func(self.loop, 'neutral'), Wait(12), ActorInterval(self, 'float'), Func(self.loop, 'neutral'), Wait(12), ActorInterval(self, 'grow'), Func(self.loop, 'neutral'), Wait(9))
                elif self.size == 'l':
                    loop = Sequence(Wait(7), ActorInterval(self, 'jump'), Func(self.loop, 'neutral'), Wait(12), ActorInterval(self, 'fly'), Func(self.loop, 'neutral'), Wait(12), ActorInterval(self, 'laugh'), Func(self.loop, 'neutral'), Wait(5))
                else:
                    loop = Sequence(ActorInterval(self, 'neutral'))
            elif id == 3:
                if self.size == 's':
                    loop = Sequence(Wait(4), ActorInterval(self, 'float'), Func(self.loop, 'neutral'), Wait(12), ActorInterval(self, 'float'), Func(self.loop, 'neutral'), Wait(12), ActorInterval(self, 'grow'), Func(self.loop, 'neutral'), Wait(8))
                elif self.size == 'l':
                    loop = Sequence(Wait(8), ActorInterval(self, 'fly'), Func(self.loop, 'neutral'), Wait(12), ActorInterval(self, 'fly'), Func(self.loop, 'neutral'), Wait(12), ActorInterval(self, 'laugh'), Func(self.loop, 'neutral'), Wait(4))
                else:
                    loop = Sequence(ActorInterval(self, 'neutral'))
            else:
                loop = Sequence(ActorInterval(self, 'neutral'))
        else:
            loop = Sequence(ActorInterval(self, 'neutral'))
        return loop