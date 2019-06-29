from panda3d.core import *
import datetime
from direct.distributed.ClockDelta import *
from direct.interval.IntervalGlobal import *
from direct.distributed import DistributedObject
from direct.fsm import ClassicFSM, State
from direct.fsm import State
from otp.nametag.NametagConstants import *
from toontown.suit import SuitDNA, Suit
from toontown.toonbase import ToontownGlobals

class DistributedPumpkinCog(DistributedObject.DistributedObject):

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)

    def generate(self):
        DistributedObject.DistributedObject.generate(self)
        self.pumpkin = loader.loadModel('phase_4/models/estate/pumpkin_tall')
        self.spookyCog = Suit.Suit()
        self.spookyCog.dna = SuitDNA.SuitDNA()
        self.spookyCog.dna.newSuit('mh')
        self.spookyCog.setDNA(self.spookyCog.dna)
        self.spookyCog.makeSkeleton(skipName=True)
        head = self.spookyCog.find('**/joint_head')
        self.pumpkin.reparentTo(head)
        self.pumpkin.setPosHprScale(0, 0, -0.125, 180, 0, 0, 0.5, 0.5, 0.5)
        self.pumpkin.find('**/floorShadow_plane').removeNode()
        self.pumpkin.setScale(0.4)
        self.spookyCog.setName('Spooky Skelecog')
        self.spookyCog.setDisplayName('Spooky Skelecog\nLevel 31')
        self.spookyCog.spookify()
        self.spookyCog.setPickable(False)
        self.spookyCog.addActive()
        self.spookyCog.reparentTo(render)
        self.spookyCog.setPos(-23.076, -83.587, 0.525)
        self.spookyCog.loop('neutral')
        cs = CollisionSphere(0, 0, 0, 3)
        self.spookNode = self.spookyCog.attachNewNode(CollisionNode('spookycog'))
        self.spookNode.node().addSolid(cs)
        self.colEventName = 'enter' + self.spookNode.node().getName()
        self.accept(self.colEventName, self.handleSpookyCog)

    def disable(self):
        self.ignore(self.colEventName)
        self.spookyCog.stash()
        self.spookyCog.removeActive()

    def delete(self):
        self.pumpkin.removeNode()
        self.spookyCog.delete()
        DistributedObject.DistributedObject.delete(self)

    def handleSpookyCog(self, collEntry):
        serverPhrases = [
         "Get out of here before I take you down to Bill's Hell!", 'Hey, I already gave you a pumpkin. Do you want me to take away your clothing as well?', "Welcome to Nickdoge's Server!", "Something about this place reminds me of a 'cheezy' joke.", "Welcome to Jamie's Server #1!", "Welcome to Jamie's Server #2!"]
        now = datetime.datetime.now()
        endDate = datetime.datetime(now.year, 10, 31, 23, 59)
        if now > endDate:
            self.spookyCog.setChatAbsolute('Looks like the spook is over. See you in 2018!', CFSpeech | CFTimeout)
            return
        if base.localAvatar.getCheesyEffect()[0] == ToontownGlobals.CEPumpkin:
            if base.cr.holidayValue != 0:
                for x in xrange(5):
                    if base.cr.holidayValue == x:
                        self.spookyCog.setChatAbsolute(serverPhrases[(x - 1)], CFSpeech | CFTimeout)

            else:
                self.spookyCog.setChatAbsolute('Happy Halloween!', CFSpeech | CFTimeout)
            return
        self.sendUpdate('giveRewardToAv')
        self.spookyCog.setChatAbsolute("Here's your pumpkin head, Toon. It will last until Halloween ends.", CFSpeech | CFTimeout)

    def startSpookyCog(self):
        if self.spookNode:
            self.accept(self.colEventName, self.handleSpookyCog)

    def stopSpookyCog(self):
        if self.spookNode:
            self.ignore(self.colEventName)