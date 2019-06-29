from direct.actor import Actor
from panda3d.core import *
from direct.interval.IntervalGlobal import *
from ChatBalloon import *
from direct.task import Task
import random
playRate = 1

class CogExtras:

    def __init__(self):
        pass

    def flyIn(self, suit, duration):
        self.flyIn = loader.loadSfx('phase_5/audio/sfx/ENC_propeller_in.ogg')
        self.flyOut = loader.loadSfx('phase_5/audio/sfx/ENC_propeller_out.ogg')
        self.propeller = Actor.Actor('phase_4/models/props/propeller-mod.bam', {'chan': 'phase_4/models/props/propeller-chan.bam'})
        self.propeller.reparentTo(suit.find('**/to_head'))
        spin = ActorInterval(self.propeller, 'chan', startTime=0, endTime=0.3)
        return Sequence(Func(suit.pose, 'landing', 0), Func(spin.loop), Wait(duration), Func(self.flyIn.play), Parallel(Sequence(ActorInterval(suit, 'landing'), Func(suit.loop, 'neutral')), Sequence(ActorInterval(self.propeller, 'chan'), Func(self.propeller.delete))))

    def healthColor(self, suit, button, glow, showMeter=False):
        if showMeter:
            suit.icon.show()
            suit.button.hide()
            suit.glow.hide()
            return
        suit.button.show()
        suit.button.setColor(button)
        suit.glow.setColor(glow)
        suit.glow.show()
        suit.icon.hide()

    def cogTalk(self, text, suit, height, size=0.3, duration=3, noise=None, cog=True, boss=False, x=0, y=0, Bin=True, smallCaps=False):
        suitChatBalloon = loader.loadModel('phase_3/models/props/chatbox.bam')
        suitChat = ChatBalloon(suitChatBalloon)
        cogFont = loader.loadFont('phase_3/models/fonts/vtRemingtonPortable.ttf')
        bubble = suitChat.generate(text, cogFont)[0]
        bubble.setScale(0.001)
        bubble.setPos(x, y, height)
        bubble.reparentTo(suit)
        bubble.setBillboardPointEye()
        if Bin:
            bubble.setBin('fixed', 0, 1)
        if noise:
            pass
        else:
            if len(text) > 50:
                noise = 'murmur'
            else:
                if len(text) > 40:
                    noise = random.choice(['murmur', 'statement'])
                else:
                    if len(text) > 30:
                        noise = random.choice(['statement', 'question'])
                    else:
                        if len(text) > 20:
                            noise = random.choice(['statement', 'grunt'])
                        else:
                            noise = 'grunt'
        if boss:
            talk = loader.loadSfx('phase_9/audio/sfx/Boss_COG_VO_%s.ogg' % noise)
        else:
            if cog:
                talk = loader.loadSfx('phase_3.5/audio/dial/COG_VO_%s.ogg' % noise)
            else:
                talk = loader.loadSfx('phase_5/audio/sfx/Skel_COG_VO_%s.ogg' % noise)
        sfx = SoundInterval(talk)
        Sequence(bubble.scaleInterval(0.35, size + 0.1), bubble.scaleInterval(0.1, size), Parallel(sfx, Wait(duration)), Func(bubble.removeNode)).start(playRate=playRate)