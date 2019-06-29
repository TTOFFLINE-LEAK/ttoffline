from panda3d.core import CollisionTube, CollisionNode
from otp.nametag.NametagGroup import *
from toontown.pets import Pet
from toontown.suit import DistributedSuitBase, SuitDNA, Suit
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
            collNodePath = newToon.attachNewNode(collNode)
    else:
        newToon.useLOD(LOD)
        if coll:
            newToon.initializeBodyCollisions('toon')
    newToon.setPosHpr(x, y, z, h, p, r)
    newToon.reparentTo(parent)
    newToon.loop(anim)
    return newToon


def createUniqueToon(name, dna, hat, glasses, backpack, shoes, x=0, y=0, z=0, h=0, p=0, r=0, parent=render, anim='neutral', LOD=1000, isDisguised=False, suitType='f', isWaiter=False, coll=True, isRental=False, colorType=NametagGroup.CCNonPlayer, cogLevels=[0, 0, 0, 0, 0], cheesyEffect=ToontownGlobals.CENormal, nametagStyle=100):
    newToon = Toon.Toon()
    newToon.setName(name)
    newToon.setPickable(0)
    newToon.setPlayerType(colorType)
    if nametagStyle == 100:
        font = loader.loadFont('phase_3/models/fonts/ImpressBT.ttf')
    else:
        font = loader.loadFont(TTLocalizer.NametagFonts[nametagStyle])
    newToon.nametag.setFont(font)
    coolDNA = ToonDNA.ToonDNA()
    coolDNA.newToonFromProperties(*dna)
    newToon.setDNAString(coolDNA.makeNetString())
    newToon.applyCheesyEffect(cheesyEffect, 0)
    newToon.head = newToon.find('**/__Actor_head')
    a, b, c = hat
    newToon.setHat(a, b, c)
    a, b, c = backpack
    newToon.setBackpack(a, b, c)
    a, b, c = glasses
    newToon.setGlasses(a, b, c)
    a, b, c = shoes
    newToon.setShoes(a, b, c)
    if isDisguised:
        if isWaiter:
            becomeCog = 5
        else:
            becomeCog = 0
        newToon.cogLevels = []
        for l in cogLevels:
            newToon.cogLevels.append(l)

        newToon.putOnSuit(suitType, rental=isRental, becomeCog=becomeCog)
        if coll:
            collTube = CollisionTube(0, 0, 0.5, 0, 0, 4, 2)
            collNode = CollisionNode('suit')
            collNode.addSolid(collTube)
            collNodePath = newToon.attachNewNode(collNode)
    else:
        newToon.useLOD(LOD)
        if coll:
            newToon.initializeBodyCollisions('toon')
    newToon.setPosHpr(x, y, z, h, p, r)
    newToon.reparentTo(parent)
    newToon.loop(anim)
    return newToon


def createCog(cogType, x=0, y=0, z=0, h=0, p=0, r=0, isSkelecog=False, isWaiter=False, anim='neutral', parent=render, name=None, dept=None, level=None, coll=True):
    newCog = Suit.Suit()
    newCog.dna = SuitDNA.SuitDNA()
    newCog.dna.newSuit(cogType)
    newCog.setDNA(newCog.dna)
    newCog.setPickable(0)
    if isWaiter:
        newCog.makeWaiter()
    if isSkelecog:
        newCog.makeSkeleton(True)
        newCog.setName(TTLocalizer.Skeleton)
    if name != None:
        newCog.setName(name)
    if dept is False:
        nameInfo = TTLocalizer.SuitBaseNameWithoutDept % {'name': newCog._name, 'level': level if level != None else newCog.getActualLevel()}
    else:
        if cogType == 'sj':
            nameInfo = 'Shadow Justice'
        else:
            if cogType == 'ph':
                nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': newCog._name, 'dept': 'Crazybot', 
                   'level': level if level != None else newCog.getActualLevel()}
            else:
                nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': newCog._name, 'dept': dept if dept != None else newCog.getStyleDept(), 
                   'level': level if level != None else newCog.getActualLevel()}
    newCog.reparentTo(parent)
    newCog.setPosHpr(x, y, z, h, p, r)
    newCog.loop(anim)
    newCog.setDisplayName(nameInfo)
    if coll:
        collTube = CollisionTube(0, 0, 0.5, 0, 0, 4, 2)
        collNode = CollisionNode('suit')
        collNode.addSolid(collTube)
        collNodePath = newCog.attachNewNode(collNode)
    return newCog


def createDistributedCog(cogType, x=0, y=0, z=0, h=0, p=0, r=0, isSkelecog=False, isWaiter=False, anim='neutral', parent=render, name=None, dept=None, level=None, coll=True, isVirtual=False, colorType=NametagGroup.CCSuit):
    newCog = DistributedSuitBase.DistributedSuitBase(base.cr)
    newCog.dna = SuitDNA.SuitDNA()
    newCog.dna.newSuit(cogType)
    newCog.setDNA(newCog.dna)
    newCog.setPlayerType(colorType)
    if isWaiter:
        newCog.makeWaiter()
    if isSkelecog:
        newCog.makeSkeleton()
    if isVirtual:
        newCog.virtualify()
    newCog.setPickable(0)
    newCog.doId = id(newCog)
    if name != None:
        newCog.setName(name)
    if dept is False:
        nameInfo = TTLocalizer.SuitBaseNameWithoutDept % {'name': newCog._name, 'level': level if level != None else newCog.getActualLevel()}
    else:
        if cogType == 'sj':
            nameInfo = 'Shadow Justice'
        else:
            if cogType == 'ph':
                nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': newCog._name, 'dept': 'Crazybot', 
                   'level': level if level != None else newCog.getActualLevel()}
            else:
                nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': newCog._name, 'dept': dept if dept != None else newCog.getStyleDept(), 
                   'level': level if level != None else newCog.getActualLevel()}
    newCog.setDisplayName(nameInfo)
    newCog.reparentTo(parent)
    newCog.setPosHpr(x, y, z, h, p, r)
    newCog.loop(anim)
    if coll:
        collTube = CollisionTube(0, 0, 0.5, 0, 0, 4, 2)
        collNode = CollisionNode('suit')
        collNode.addSolid(collTube)
        collNodePath = newCog.attachNewNode(collNode)
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