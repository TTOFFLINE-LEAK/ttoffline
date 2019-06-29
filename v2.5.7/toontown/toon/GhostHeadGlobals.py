from panda3d.core import *

def makeCard(book=False):
    cardMaker = CardMaker('ghost-head-cm')
    cardMaker.setHasUvs(1)
    cardMaker.setFrame(-0.5, 0.5, -0.5, 0.5)
    nodePath = NodePath('ghost-head')
    nodePath.setBillboardPointEye()
    ghostHead = nodePath.attachNewNode(cardMaker.generate())
    ghostHead.setTexture(loader.loadTexture('phase_3/maps/GhostHead.png'))
    ghostHead.setY(-0.3)
    ghostHead.setTransparency(True)
    return nodePath


def addHeadEffect(head, book=False):
    card = makeCard(book=book)
    card.setScale(1.45 if book else 1.8)
    card.setZ(0.05 if book else 0.5)
    for nodePath in head.getChildren():
        nodePath.removeNode()

    card.instanceTo(head)


def addToonEffect(toon):
    toon.getDialogueArray = lambda *args, **kwargs: []
    for lod in toon.getLODNames():
        addHeadEffect(toon.getPart('head', lod))