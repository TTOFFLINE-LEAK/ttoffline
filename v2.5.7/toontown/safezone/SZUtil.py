from panda3d.core import CompassEffect, Fog, NodePath
from direct.task.Task import Task
from toontown.battle import BattleParticles
from toontown.dna.DNAParser import *
from toontown.toonbase import ToontownGlobals
import colorsys

def createParticle(geom, pos, particleName, renderName):
    part = BattleParticles.loadParticleFile(particleName)
    part.setPos(*pos)
    partRender = geom.attachNewNode(renderName)
    partRender.setDepthWrite(2)
    partRender.setBin('fixed', 1)
    return (
     part, partRender)


def createSnow(geom):
    return createParticle(geom, (0, 0, 5), 'snowdisk.ptf', 'snowRender')


def createRain(geom):
    return createParticle(geom, (0, 30, 10), 'rain.ptf', 'rainRender')


def startUnderwaterFog():
    if not base.wantFog:
        return
    stopUnderwaterFog()
    taskMgr.add(__updateUnderwaterFog, 'underwaterFog')


def stopUnderwaterFog():
    taskMgr.remove('underwaterFog')


def __updateUnderwaterFog(task):
    fog = base.cr.playGame.hood.fog if hasattr(base.cr.playGame.hood, 'fog') else base.cr.playGame.place.fog
    saturation = min(max(base.localAvatar.getZ() / -12.3, 0.51), 1)
    fog.setColor(*colorsys.hsv_to_rgb(0.616, saturation, 0.5))
    return task.cont


def cloudSkyTrack(task):
    task.h += globalClock.getDt() * 0.25
    if task.cloud1.isEmpty() or task.cloud2.isEmpty():
        return
    task.cloud1.setH(task.h)
    task.cloud2.setH(-task.h * 0.8)
    return task.cont


def startCloudSky(hood, parent=camera, effects=CompassEffect.PRot | CompassEffect.PZ):
    startClouds(hood.sky, hood.skyTrack, parent, effects)


def startClouds(sky, skyTrack, parent=camera, effects=CompassEffect.PRot | CompassEffect.PZ):
    sky.setDepthTest(0)
    sky.setDepthWrite(0)
    sky.setBin('background', 100)
    if sky.find('**/Sky').isEmpty():
        sky.reparentTo(render)
        return
    sky.reparentTo(parent)
    sky.find('**/Sky').reparentTo(sky, -1)
    if effects:
        ce = CompassEffect.make(NodePath(), effects)
        sky.node().setEffect(ce)
    skyTrackTask = Task(skyTrack)
    skyTrackTask.h = 0
    skyTrackTask.cloud1 = sky.find('**/cloud1')
    skyTrackTask.cloud2 = sky.find('**/cloud2')
    if not skyTrackTask.cloud1.isEmpty() and not skyTrackTask.cloud2.isEmpty():
        taskMgr.add(skyTrackTask, 'skyTrack')


def loadPlayground(playground):
    dna = ToontownGlobals.getSafezoneDNA(playground)
    if not dna:
        return None
    dnaStorage = DNAStorage()
    prop, node = loadDNAFile(dnaStorage, dna)
    for frame in node.findAllMatches('**/*doorFrame*'):
        frame.removeNode()

    node.flattenMedium()
    sky = loader.loadModel(ToontownGlobals.SZ_SKY[playground])
    startClouds(sky, lambda task: cloudSkyTrack(task))
    if playground == ToontownGlobals.TheBrrrgh:
        snow, snowRender = createSnow(node)
        snow.start(camera, snowRender)
    else:
        if playground == ToontownGlobals.CogtownCentral:
            snow, snowRender = createRain(node)
            snow.start(camera, snowRender)
        else:
            snow, snowRender = (None, None)
    return (dnaStorage, node, sky, snow, snowRender)