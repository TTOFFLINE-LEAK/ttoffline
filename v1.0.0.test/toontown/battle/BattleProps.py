from panda3d.core import *
from direct.actor import Actor
from direct.directnotify import DirectNotifyGlobal
from otp.otpbase import OTPGlobals
from toontown.toonbase import ToontownGlobals
import random

class PropPool:
    notify = DirectNotifyGlobal.directNotify.newCategory('PropPool')

    def __init__(self):
        self.props = {}
        self.propCache = []
        self.propStrings = {}
        self.propTypes = {}
        self.propScales = {}
        self.maxPoolSize = base.config.GetInt('prop-pool-size', 8)
        for p in ToontownGlobals.Props:
            phase = p[0]
            propName = p[1]
            modelName = p[2]
            if len(p) == 4:
                animName = p[3]
                propPath = self.getPath(phase, modelName)
                animPath = self.getPath(phase, animName)
                self.propTypes[propName] = 'actor'
                self.propStrings[propName] = (propPath, animPath)
                self.propScales[propName] = 1.0
            else:
                propPath = self.getPath(phase, modelName)
                self.propTypes[propName] = 'model'
                self.propStrings[propName] = (propPath,)
                self.propScales[propName] = 1.0

        for prop in ToontownGlobals.PropList:
            self.propTypes[prop[0]] = prop[1]
            self.propStrings[prop[0]] = prop[2]
            self.propScales[prop[0]] = prop[3]

    def getPath(self, phase, model):
        return 'phase_%s/models/props/%s' % (phase, model)

    def makeVariant(self, name):
        if name == 'tart':
            self.props[name].setScale(0.5)
        else:
            if name == 'fruitpie':
                self.props[name].setScale(0.75)
            else:
                if name == 'double-windsor':
                    self.props[name].setScale(1.5)
                else:
                    if name[:6] == 'splat-':
                        prop = self.props[name]
                        scale = prop.getScale() * ToontownGlobals.Splats[name[6:]][0]
                        prop.setScale(scale)
                        prop.setColor(ToontownGlobals.Splats[name[6:]][1])
                    else:
                        if name == 'splash-from-splat':
                            self.props[name].setColor(0.75, 0.75, 1.0, 1.0)
                        else:
                            if name == 'clip-on-tie':
                                tie = self.props[name]
                                tie.getChild(0).setHpr(23.86, -16.03, 9.18)
                            else:
                                if name == 'small-magnet':
                                    self.props[name].setScale(0.5)
                                else:
                                    if name == 'shredder-paper':
                                        paper = self.props[name]
                                        paper.setPosHpr(2.22, -0.95, 1.16, -48.61, 26.57, -111.51)
                                        paper.flattenMedium()
                                    else:
                                        if name == 'lips':
                                            lips = self.props[name]
                                            lips.setPos(0, 0, -3.04)
                                            lips.flattenMedium()
                                        else:
                                            if name == '5dollar':
                                                tex = loader.loadTexture('phase_5/maps/dollar_5.jpg')
                                                tex.setMinfilter(Texture.FTLinearMipmapLinear)
                                                tex.setMagfilter(Texture.FTLinear)
                                                self.props[name].setTexture(tex, 1)
                                            else:
                                                if name == '10dollar':
                                                    tex = loader.loadTexture('phase_5/maps/dollar_10.jpg')
                                                    tex.setMinfilter(Texture.FTLinearMipmapLinear)
                                                    tex.setMagfilter(Texture.FTLinear)
                                                    self.props[name].setTexture(tex, 1)
                                                else:
                                                    if name == 'dust':
                                                        bin = 110
                                                        for cloudNum in xrange(1, 12):
                                                            cloudName = '**/cloud' + str(cloudNum)
                                                            cloud = self.props[name].find(cloudName)
                                                            cloud.setBin('fixed', bin)
                                                            bin -= 10

                                                    else:
                                                        if name == 'kapow':
                                                            l = self.props[name].find('**/letters')
                                                            l.setBin('fixed', 20)
                                                            e = self.props[name].find('**/explosion')
                                                            e.setBin('fixed', 10)
                                                        else:
                                                            if name == 'suit_explosion':
                                                                joints = [
                                                                 '**/joint_scale_POW', '**/joint_scale_BLAM', '**/joint_scale_BOOM']
                                                                joint = random.choice(joints)
                                                                self.props[name].find(joint).hide()
                                                                joints.remove(joint)
                                                                joint = random.choice(joints)
                                                                self.props[name].find(joint).hide()
                                                            else:
                                                                if name == 'quicksand' or name == 'trapdoor':
                                                                    p = self.props[name]
                                                                    p.setBin('shadow', -5)
                                                                    p.setDepthWrite(0)
                                                                    p.getChild(0).setPos(0, 0, OTPGlobals.FloorOffset)
                                                                else:
                                                                    if name == 'traintrack' or name == 'traintrack2':
                                                                        prop = self.props[name]
                                                                        prop.find('**/tunnel3').hide()
                                                                        prop.find('**/tunnel2').hide()
                                                                        prop.find('**/tracksA').setPos(0, 0, OTPGlobals.FloorOffset)
                                                                    else:
                                                                        if name == 'geyser':
                                                                            p = self.props[name]
                                                                            s = SequenceNode('geyser')
                                                                            p.findAllMatches('**/Splash*').reparentTo(NodePath(s))
                                                                            s.loop(0)
                                                                            s.setFrameRate(12)
                                                                            p.attachNewNode(s)
                                                                        else:
                                                                            if name == 'ship':
                                                                                self.props[name] = self.props[name].find('**/ship_gag')
                                                                            else:
                                                                                if name == 'trolley':
                                                                                    self.props[name] = self.props[name].find('**/trolley_car')
                                                                                    self.props[name].setPosHpr(0, 0, 0, 0, 0, 0)
                                                                                else:
                                                                                    if name == 'streetlight':
                                                                                        self.props[name] = self.props[name].find('**/prop_post_sign')

    def unloadProps(self):
        for p in self.props.values():
            if type(p) != type(()):
                self.__delProp(p)

        self.props = {}
        self.propCache = []

    def getProp(self, name):
        return self.__getPropCopy(name)

    def __getPropCopy(self, name):
        if self.propTypes[name] == 'actor':
            if name not in self.props:
                prop = Actor.Actor()
                prop.loadModel(self.propStrings[name][0])
                animDict = {}
                animDict[name] = self.propStrings[name][1]
                prop.loadAnims(animDict)
                prop.setScale(self.propScales[name])
                prop.setName(name)
                prop.setBlend(frameBlend=base.settings.getBool('game', 'smooth-animations', False))
                self.storeProp(name, prop)
                if name in ToontownGlobals.Variants:
                    self.makeVariant(name)
            return Actor.Actor(other=self.props[name])
        if name not in self.props:
            prop = loader.loadModel(self.propStrings[name][0])
            prop.setScale(self.propScales[name])
            prop.setName(name)
            self.storeProp(name, prop)
            if name in ToontownGlobals.Variants:
                self.makeVariant(name)
        return self.props[name].copyTo(hidden)

    def storeProp(self, name, prop):
        self.props[name] = prop
        self.propCache.append(prop)
        if len(self.props) > self.maxPoolSize:
            oldest = self.propCache.pop(0)
            del self.props[oldest.getName()]
            self.__delProp(oldest)
        self.notify.debug('props = %s' % self.props)
        self.notify.debug('propCache = %s' % self.propCache)

    def getPropType(self, name):
        return self.propTypes[name]

    def __delProp(self, prop):
        if prop == None:
            self.notify.warning('tried to delete null prop!')
            return
        if isinstance(prop, Actor.Actor):
            prop.cleanup()
        else:
            prop.removeNode()
        return


globalPropPool = PropPool()