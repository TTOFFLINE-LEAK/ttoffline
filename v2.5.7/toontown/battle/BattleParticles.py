from direct.particles.ParticleEffect import *
import os
from direct.directnotify import DirectNotifyGlobal
from direct.showbase import AppRunnerGlobal
import ParticleDefs
notify = DirectNotifyGlobal.directNotify.newCategory('BattleParticles')
TutorialParticleEffects = ('gearExplosionBig.ptf', 'gearExplosionSmall.ptf', 'gearExplosion.ptf')
ParticleNames = ('audit-div', 'audit-five', 'audit-four', 'audit-minus', 'audit-mult',
                 'audit-one', 'audit-plus', 'audit-six', 'audit-three', 'audit-two',
                 'blah', 'brainstorm-box', 'brainstorm-env', 'brainstorm-track',
                 'buzzwords-crash', 'buzzwords-inc', 'buzzwords-main', 'buzzwords-over',
                 'buzzwords-syn', 'confetti', 'doubletalk-double', 'doubletalk-dup',
                 'doubletalk-good', 'filibuster-cut', 'filibuster-fiscal', 'filibuster-impeach',
                 'filibuster-inc', 'jargon-brow', 'jargon-deep', 'jargon-hoop', 'jargon-ipo',
                 'legalese-hc', 'legalese-qpq', 'legalese-vd', 'mumbojumbo-boiler',
                 'mumbojumbo-creative', 'mumbojumbo-deben', 'mumbojumbo-high', 'mumbojumbo-iron',
                 'poundsign', 'schmooze-genius', 'schmooze-instant', 'schmooze-master',
                 'schmooze-viz', 'roll-o-dex', 'rollodex-card', 'dagger', 'fire',
                 'snow-particle', 'raindrop', 'gear', 'checkmark', 'dollar-sign',
                 'spark')
particleModel = None
particleSearchPath = None

def loadParticles():
    global particleModel
    if particleModel == None:
        particleModel = loader.loadModel('phase_3.5/models/props/suit-particles')
    return


def unloadParticles():
    global particleModel
    if particleModel != None:
        particleModel.removeNode()
    del particleModel
    particleModel = None
    return


def getParticle(name):
    if name in ParticleNames:
        particle = particleModel.find('**/' + str(name))
        return particle
    notify.warning('getParticle() - no name: %s' % name)
    return
    return


def loadParticleFile(name):
    name = name[:-4]
    particleFunc = ParticleDefs.ParticleTable[name]
    effect = ParticleEffect()
    particleFunc(effect)
    return effect


def createParticleEffect(name=None, file=None, numParticles=None, color=None):
    if not name:
        fileName = file + '.ptf'
        return loadParticleFile(fileName)
    if name == 'GearExplosion':
        return __makeGearExplosion(numParticles)
    if name == 'BigGearExplosion':
        return __makeGearExplosion(numParticles, 'Big')
    if name == 'WideGearExplosion':
        return __makeGearExplosion(numParticles, 'Wide')
    if name == 'BrainStorm':
        return loadParticleFile('brainStorm.ptf')
    if name == 'BuzzWord':
        return loadParticleFile('buzzWord.ptf')
    if name == 'Calculate':
        return loadParticleFile('calculate.ptf')
    if name == 'Confetti':
        return loadParticleFile('confetti.ptf')
    if name == 'DemotionFreeze':
        return loadParticleFile('demotionFreeze.ptf')
    if name == 'DemotionSpray':
        return loadParticleFile('demotionSpray.ptf')
    if name == 'DoubleTalkLeft':
        return loadParticleFile('doubleTalkLeft.ptf')
    if name == 'DoubleTalkRight':
        return loadParticleFile('doubleTalkRight.ptf')
    if name == 'FingerWag':
        return loadParticleFile('fingerwag.ptf')
    if name == 'FiredFlame':
        return loadParticleFile('firedFlame.ptf')
    if name == 'FreezeAssets':
        return loadParticleFile('freezeAssets.ptf')
    if name == 'GlowerPower':
        return loadParticleFile('glowerPowerKnives.ptf')
    if name == 'HotAir':
        return loadParticleFile('hotAirSpray.ptf')
    if name == 'PoundKey':
        return loadParticleFile('poundkey.ptf')
    if name == 'ShiftSpray':
        return loadParticleFile('shiftSpray.ptf')
    if name == 'ShiftLift':
        return __makeShiftLift()
    if name == 'Shred':
        return loadParticleFile('shred.ptf')
    if name == 'Smile':
        return loadParticleFile('smile.ptf')
    if name == 'SpriteFiredFlecks':
        return loadParticleFile('spriteFiredFlecks.ptf')
    if name == 'Synergy':
        return loadParticleFile('synergy.ptf')
    if name == 'Waterfall':
        return loadParticleFile('waterfall.ptf')
    if name == 'PoundKey':
        return loadParticleFile('poundkey.ptf')
    if name == 'RubOut':
        return __makeRubOut(color)
    if name == 'SplashLines':
        return loadParticleFile('splashlines.ptf')
    if name == 'Withdrawal':
        return loadParticleFile('withdrawal.ptf')
    notify.warning('createParticleEffect() - no name: %s' % name)
    return


def setEffectTexture(effect, name, color=None):
    particles = effect.getParticlesNamed('particles-1')
    np = getParticle(name)
    if color:
        particles.renderer.setColor(color)
    particles.renderer.setFromNode(np)


def __makeGearExplosion(numParticles=None, style='Normal'):
    if style == 'Normal':
        effect = loadParticleFile('gearExplosion.ptf')
    else:
        if style == 'Big':
            effect = loadParticleFile('gearExplosionBig.ptf')
        else:
            if style == 'Wide':
                effect = loadParticleFile('gearExplosionWide.ptf')
    if numParticles:
        particles = effect.getParticlesNamed('particles-1')
        particles.setPoolSize(numParticles)
    return effect


def __makeRubOut(color=None):
    effect = loadParticleFile('demotionUnFreeze.ptf')
    loadParticles()
    setEffectTexture(effect, 'snow-particle')
    particles = effect.getParticlesNamed('particles-1')
    particles.renderer.setInitialXScale(0.03)
    particles.renderer.setFinalXScale(0.0)
    particles.renderer.setInitialYScale(0.02)
    particles.renderer.setFinalYScale(0.0)
    if color:
        particles.renderer.setColor(color)
    else:
        particles.renderer.setColor(Vec4(0.54, 0.92, 0.32, 0.7))
    return effect


def __makeShiftLift():
    effect = loadParticleFile('pixieDrop.ptf')
    particles = effect.getParticlesNamed('particles-1')
    particles.renderer.setCenterColor(Vec4(1, 1, 0, 0.9))
    particles.renderer.setEdgeColor(Vec4(1, 1, 0, 0.6))
    particles.emitter.setRadius(0.01)
    effect.setHpr(0, 180, 0)
    effect.setPos(0, 0, 0)
    return effect