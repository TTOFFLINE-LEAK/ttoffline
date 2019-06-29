from panda3d.core import CollisionSphere, CollisionNode, CollisionTube
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.interval.IntervalGlobal import Parallel, LerpHprInterval
from otp.margins.WhisperPopup import *
from toontown.suit import Suit, SuitDNA
from toontown.toonbase import ToontownGlobals, TTLocalizer
import random

class HolidayCar:

    def __init__(self):
        self.swag = None
        self.cart = None
        self.cartModelPath = 'phase_12/models/bossbotHQ/Coggolf_cart3.bam'
        return

    def generate(self):
        self.cart = loader.loadModel(self.cartModelPath)
        self.cart.reparentTo(render)
        self.cartBody = self.cart.find('**/main_body')
        self.cartBase = self.cart.find('**/cart_base*')
        self.cartBody.setColorScale(0.8, 0.1, 0.1, 1)
        self.cartBase.setColorScale(0.1, 0.8, 0.1, 1)
        self.swag = Suit.Suit()
        self.swag.dna = SuitDNA.SuitDNA()
        self.swag.dna.newSuit('sf')
        self.swag.setDNA(self.swag.dna)
        self.swag.setName("Smokin' Claus")
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': "Smokin' Claus", 'dept': TTLocalizer.Sellbot, 
           'level': 50}
        self.swag.setDisplayName(nameInfo)
        self.swag.setPickable(False)
        self.swag.addActive()
        self.collTube = CollisionTube(0, 0, 0.5, 0, 0, 4, 4)
        self.collNode = CollisionNode('suit')
        self.collNode.addSolid(self.collTube)
        self.collNodePath = self.swag.attachNewNode(self.collNode)
        self.swag.loop('sit')
        self.swag.setScale(0.7)
        self.swag.setH(180)
        self.swag.setPos(0, -1, -1.5)
        self.swag.reparentTo(self.cart.find('**/seat1'))

    def swagPhrase(self):
        swagChat = [
         'Bing bong. Bing bing bong. Bing bong bing bong.',
         'Now look at this Kart, which I just found! When I say go, be ready to throw!',
         'Ho ho ho! Merry Mememas!',
         "The staff caught a case of the Scrooge this year and couldn't afford a proper Sleigh.",
         "I'm supposed to be getting Jury Notices, but this one duck keeps greening my rear.",
         "I may be a Cog, but I'm not interested in this 'Duck Hunt' you speak of.",
         "It's the Holiday Season in Toontown Offline! Host a miniserver, grab some friends, and have fun!"]
        self.swag.setChatAbsolute(random.choice(swagChat), CFSpeech | CFTimeout)

    def disable(self):
        self.cartModelPath = None
        if self.swag:
            self.swag.removeActive()
            self.swag.hide()
            self.swag = None
        if self.cart:
            self.cart.removeNode()
            self.cart = None
        return