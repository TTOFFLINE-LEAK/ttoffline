from panda3d.core import CollisionTube, CollisionNode
from libotp.nametag.NametagGroup import *
from toontown.pets import Pet
from toontown.suit import SuitDNA, Suit
from toontown.toon import NPCToons, Toon, ToonDNA
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals

def createToon(toonId, x=0, y=0, z=0, h=0, p=0, r=0, parent=render, anim='neutral', LOD=1000, isDisguised=False, suitType='f', coll=True):
    newToon = NPCToons.createLocalNPC(toonId)
    if not newToon:
        newToon = NPCToons.createLocalNPC(1)
    newToon.head = newToon.find('**/__Actor_head')
    if isDisguised:
        newToon.putOnSuit(suitType, False, False)
        if coll:
            collTube = CollisionTube(0, 0, 0.5, 0, 0, 4, 2)
            collNode = CollisionNode('suit')
            collNode.addSolid(collTube)
            newToon.attachNewNode(collNode)
    else:
        newToon.useLOD(LOD)
        if coll:
            newToon.initializeBodyCollisions('toon')
    newToon.setPosHpr(x, y, z, h, p, r)
    newToon.reparentTo(parent)
    newToon.loop(anim)
    return newToon


def createUniqueToon(name, dna, hat, glasses, backpack, shoes, x=0, y=0, z=0, h=0, p=0, r=0, parent=render, anim='neutral', LOD=1000, isDisguised=False, suitType='f', suitDept='c', isWaiter=False, isRental=False, coll=True, colorType=NametagGroup.CCNonPlayer, cogLevels=(0, 0, 0, 0, 0), cheesyEffect=ToontownGlobals.CENormal, nametagStyle=100):
    newToon = Toon.Toon()
    newToon.setName(name)
    newToon.setPickable(0)
    newToon.setPlayerType(colorType)
    if nametagStyle == 100:
        font = loader.loadFont(TTLocalizer.InterfaceFont)
    else:
        font = loader.loadFont(TTLocalizer.NametagFonts[nametagStyle])
    newToon.nametag.setFont(font)
    newDNA = ToonDNA.ToonDNA()
    newDNA.newToonFromProperties(*dna)
    newToon.setDNAString(newDNA.makeNetString())
    newToon.applyCheesyEffect(cheesyEffect, 0)
    newToon.head = newToon.find('**/__Actor_head')
    newToon.setHat(*hat)
    newToon.setBackpack(*backpack)
    newToon.setGlasses(*glasses)
    newToon.setShoes(*shoes)
    if isDisguised:
        if isWaiter:
            cogType = 4
        else:
            cogType = 0
        newToon.cogLevels = []
        for l in cogLevels:
            newToon.cogLevels.append(l)

        if cogType in ToontownGlobals.PutOnSuitRental or isRental:
            index = ToontownGlobals.CogDepts.index(suitDept)
            newToon.putOnSuit(index, cogType=cogType, rental=True)
        else:
            newToon.putOnSuit(suitType, cogType=cogType, rental=isRental)
        if coll:
            collTube = CollisionTube(0, 0, 0.5, 0, 0, 4, 2)
            collNode = CollisionNode('suit')
            collNode.addSolid(collTube)
            newToon.attachNewNode(collNode)
    else:
        newToon.useLOD(LOD)
        if coll:
            newToon.initializeBodyCollisions('toon')
    newToon.setPosHpr(x, y, z, h, p, r)
    newToon.reparentTo(parent)
    newToon.loop(anim)
    return newToon


def createCog(cogType, x=0, y=0, z=0, h=0, p=0, r=0, isSkelecog=False, isWaiter=False, isVirtual=False, isSkeleRevive=False, colorType=NametagGroup.CCSuit, anim='neutral', parent=render, name=None, dept=None, level=None, coll=True):
    newCog = Suit.Suit()
    newCog.dna = SuitDNA.SuitDNA()
    newCog.dna.newSuit(cogType)
    newCog.setDNA(newCog.dna)
    newCog.setPlayerType(colorType)
    newCog.setPickable(0)
    level = level if level != None else newCog.getActualLevel()
    if isWaiter:
        newCog.makeWaiter()
    if isSkelecog:
        newCog.makeSkeleton()
        newCog.setName(TTLocalizer.Skeleton)
    if isVirtual:
        newCog.makeVirtual()
    if isSkeleRevive:
        level = '%s%s' % (level, TTLocalizer.SkeleRevivePostFix)
    if name != None:
        newCog.setName(name)
    if dept is False:
        nameInfo = TTLocalizer.SuitBaseNameWithoutDept % {'name': newCog._name, 'level': level}
    else:
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': newCog._name, 'dept': dept if dept != None else newCog.getStyleDept(), 
           'level': level}
    newCog.setPosHpr(x, y, z, h, p, r)
    newCog.reparentTo(parent)
    newCog.loop(anim)
    newCog.setDisplayName(nameInfo)
    if coll:
        collTube = CollisionTube(0, 0, 0.5, 0, 0, 4, 2)
        collNode = CollisionNode('suit')
        collNode.addSolid(collTube)
        newCog.attachNewNode(collNode)
    return newCog


def createDoodle(name, head, ears, nose, tail, body, color, colorScale, eyes, gender, x=0, y=0, z=0, h=0, p=0, r=0, parent=render, coll=True):
    doodle = Pet.Pet()
    doodle.setDNA([head, ears, nose, tail, body, color, colorScale, eyes, gender])
    doodle.setName(name)
    doodle.setPickable(0)
    doodle.reparentTo(parent)
    doodle.setPosHpr(x, y, z, h, p, r)
    doodle.enterNeutralHappy()
    if coll:
        doodle.initializeBodyCollisions('pet')
    return doodle