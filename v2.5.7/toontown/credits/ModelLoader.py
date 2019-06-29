from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import ActorInterval
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import *

def addModels(PROPS, parent, children=False, strong=None):
    parent = parent.attachNewNode('parentNode')
    for prop in PROPS:
        if children:
            if prop[6]:
                if prop[0] == 'custom':
                    model = loader.loadModel('custom/models/%s/%s.egg' % (prop[1], prop[2])).find('**/%s' % prop[6])
                else:
                    model = loader.loadModel('phase_%s/models/%s/%s.bam' % (prop[0], prop[1], prop[2])).find('**/%s' % prop[6])
            elif prop[0] == 'custom':
                model = loader.loadModel('custom/models/%s/%s.egg' % (prop[1], prop[2]))
            else:
                model = loader.loadModel('phase_%s/models/%s/%s.bam' % (prop[0], prop[1], prop[2]))
        else:
            if prop[0] == 'custom':
                model = loader.loadModel('custom/models/%s/%s.egg' % (prop[1], prop[2]))
            else:
                model = loader.loadModel('phase_%s/models/%s/%s.bam' % (prop[0], prop[1], prop[2]))
        model.reparentTo(parent)
        model.setPos(prop[3])
        model.setHpr(prop[4])
        model.setScale(prop[5])
        if prop[7]:
            model.setColorScale(prop[7])
        if strong:
            model.flattenStrong()

    return parent


def addActors(ACTORS, parent):
    for prop in ACTORS:
        if prop[0] == 'custom':
            model = Actor('custom/models/%s/%s.egg' % (prop[1], prop[2]), prop[9])
        else:
            model = Actor('phase_%s/models/%s/%s.bam' % (prop[0], prop[1], prop[2]), prop[9])
        model.reparentTo(parent)
        model.setBlend(frameBlend=True)
        model.setPos(prop[3])
        model.setHpr(prop[4])
        model.setScale(prop[5])
        if prop[7]:
            model.setColorScale(prop[7])
        if prop[8]:
            texture = loader.loadTexture(prop[8])
            model.setTexture(texture, 1)
        actorTrack = Sequence()
        for anim in prop[9]:
            actorTrack.append(ActorInterval(model, anim))

        actorTrack.loop()


def addText(TEXT, parent):
    for text in TEXT:
        t = TextNode('')
        if text[1]:
            font = loader.loadFont(text[1])
            t.setFont(font)
        t.setText(text[0])
        t.setTextColor(text[2])
        t.setAlign(TextNode.ACenter)
        textNode = parent.attachNewNode(t)
        textNode.setPos(text[3])
        textNode.setHpr(text[4])
        textNode.setScale(text[5])