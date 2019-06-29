from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.actor.Actor import Actor
from otp.otpbase.PythonUtil import deprecated
from CogAnimations import *

@deprecated('Use toontown.avatar.ToontownAvatarUtils instead')
class CogMaker:

    def CogMaker(self, size, dept, head, hand, headT, scale):
        headPhase = 4
        headJoint = '**/to_head'
        if size == 'A':
            suitAnims = suitAAnims
            shadowScale = 0.5
        else:
            if size == 'B':
                suitAnims = suitBAnims
                shadowScale = 0.45
            else:
                if size == 'C':
                    suitAnims = suitCAnims
                    headPhase = 3.5
                    headJoint = '**/joint_head'
                    shadowScale = 0.55
        if head:
            suit = Actor('phase_3.5/models/char/suit%s-mod.bam' % size, suitAnims)
            suitBlazer = loader.loadTexture('phase_3.5/maps/%s_blazer.jpg' % dept)
            suitSleeve = loader.loadTexture('phase_3.5/maps/%s_sleeve.jpg' % dept)
            suitLeg = loader.loadTexture('phase_3.5/maps/%s_leg.jpg' % dept)
            suit.find('**/torso').setTexture(suitBlazer, 1)
            suit.find('**/arms').setTexture(suitSleeve, 1)
            suit.find('**/legs').setTexture(suitLeg, 1)
            suit.find('**/hands').setColor(hand)
            if head == 'flunky' and scale < 1:
                glasses = loader.loadModel('phase_3.5/models/char/suitC-heads.bam').find('**/glasses')
                glasses.reparentTo(suit.find('**/joint_head'))
            if head == 'beancounter' and size == 'A':
                head = loader.loadModel('phase_%s/models/char/suitB-heads.bam' % headPhase).find('**/%s' % head)
            else:
                if head == 'bigfish':
                    head = loader.loadModel('phase_%s/models/char/suitC-heads.egg' % headPhase).find('**/%s' % head)
                else:
                    head = loader.loadModel('phase_%s/models/char/suit%s-heads.bam' % (headPhase, size)).find('**/%s' % head)
            head.reparentTo(suit.find(headJoint))
            if headT:
                headT = loader.loadTexture('phase_%s/maps/%s.jpg' % (headPhase, headT))
                head.setTexture(headT, 1)
        else:
            suit = Actor('phase_5/models/char/cog%s_robot-zero.bam' % size, suitAnims)
            if dept == 'l':
                tie = 'legal'
            else:
                if dept == 'c':
                    tie = 'boss'
                else:
                    if dept == 'm':
                        tie = 'money'
                    else:
                        tie = 'sales'
            tieText = loader.loadTexture('phase_5/maps/cog_robot_tie_%s.jpg' % tie)
            suit.find('**/tie').setTexture(tieText, 1)
        shadow = loader.loadModel('phase_3/models/props/drop_shadow.bam')
        shadow.reparentTo(suit.find('**/joint_shadow'))
        shadow.setScale(shadowScale)
        shadow.setAlphaScale(0.89)
        suit.setScale(scale)
        self.healthMeter(suit, dept)
        suit.reparentTo(render)
        suit.node().setBounds(OmniBoundingVolume())
        suit.node().setFinal(1)
        suit.setBlend(frameBlend=True)
        self.suit = suit
        return self.suit

    def healthMeter(self, suit, dept):
        model = loader.loadModel('phase_3.5/models/gui/matching_game_gui.bam')
        button = model.find('**/minnieCircle')
        button.setScale(3.0)
        button.setH(180.0)
        button.setColor(0, 1, 0, 1)
        chestNull = suit.find('**/joint_attachMeter')
        button.reparentTo(chestNull)
        self.healthBar = button
        glow = loader.loadModel('phase_3.5/models/props/glow.bam')
        glow.reparentTo(self.healthBar)
        glow.setScale(0.28)
        glow.setPos(-0.005, 0.01, 0.015)
        glow.setColor(0.25, 1, 0.25, 0.5)
        button.flattenLight()
        self.healthBar.hide()
        if dept == 'l':
            icon = 'Legal'
        else:
            if dept == 'c' or dept == 'stone':
                icon = 'Corp'
            else:
                if dept == 'm':
                    icon = 'Money'
                else:
                    icon = 'Sales'
        c_icon = loader.loadModel('phase_3/models/gui/cog_icons.bam').find('**/%sIcon' % icon)
        c_icon.reparentTo(suit.find('**/joint_attachMeter'))
        c_icon.setScale(0.6)
        c_icon.setH(180.0)
        if dept == 'cm':
            c_icon.removeNode()

    def stoneCheese(self):
        headPhase = 4
        headJoint = '**/to_head'
        suitAnims = suitAAnims
        shadowScale = 0.5
        suit = Actor('phase_3.5/models/char/suitA-statue.bam', suitAnims)
        head = loader.loadModel('phase_%s/models/char/suitA-heads.bam' % headPhase).find('**/bigcheese')
        head.reparentTo(suit.find(headJoint))
        headT = loader.loadTexture('phase_4/maps/statue-tbc.jpg')
        head.setTexture(headT, 1)
        head.setColor(0.643, 0.643, 0.643, 1)
        shadow = loader.loadModel('phase_3/models/props/drop_shadow.bam')
        shadow.reparentTo(suit.find('**/joint_shadow'))
        shadow.setScale(shadowScale)
        shadow.setAlphaScale(0.89)
        suit.reparentTo(render)
        suit.node().setBounds(OmniBoundingVolume())
        suit.node().setFinal(1)
        suit.setBlend(frameBlend=True)
        self.suit = suit
        return self.suit