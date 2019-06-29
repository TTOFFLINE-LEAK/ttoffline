from panda3d.core import *
from direct.interval.IntervalGlobal import *
import random, math
from otp.nametag.NametagConstants import *
from toontown.avatar import ToontownAvatarUtils
from toontown.toonbase import ToontownGlobals
from SafeZoneLoader import SafeZoneLoader
from Playground import Playground
from TFPlayground import TFPlayground
from toontown.battle import BattleParticles

class TFSafeZoneLoader(SafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playgroundClass = TFPlayground
        self.musicFile = 'phase_6/audio/bgm/TF_SZ_1.ogg'
        self.activityMusicFile = 'phase_3.5/audio/bgm/TC_SZ_activity.ogg'
        self.dnaFile = 'phase_6/dna/toonfest_sz.jazz'
        self.safeZoneStorageDNAFile = 'phase_6/dna/storage_TF.jazz'
        self.clouds = []
        self.cloudSwitch = 0
        self.cloudTrack = None
        self.flippyBlatherSequence = Sequence()
        self.fluffy = None
        self.flippy = None
        return

    def createSafeZone(self, dnaFile):
        SafeZoneLoader.createSafeZone(self, dnaFile)
        binMgr = CullBinManager.getGlobalPtr()
        binMgr.addBin('water', CullBinManager.BTFixed, 29)
        water = self.geom.find('**/pond_water')
        water.setTransparency(1)
        water.setColorScale(1.0, 1.0, 1.0, 1.0)
        water.setBin('water', 51, 1)

    def load(self):
        SafeZoneLoader.load(self)
        self.flippy = ToontownAvatarUtils.createToon(2001, 188, -260, 4.597, 108.411)
        self.flippy.addActive()
        self.flippy.startBlink()
        self.flippyBlatherSequence = Sequence(Wait(10), Func(self.flippy.setChatAbsolute, 'Welcome Toons, far and wide!', CFSpeech | CFTimeout), ActorInterval(self.flippy, 'wave'), Func(self.flippy.loop, 'neutral'), Wait(5), Func(self.flippy.setChatAbsolute, "It's been an amazing year at Toontown, and we're glad you could join us!", CFSpeech | CFTimeout), Wait(8), Func(self.flippy.setChatAbsolute, "Oh, don't mind the little guy back there. That's my new pet, Fluffy.", CFSpeech | CFTimeout), Wait(8), Func(self.flippy.setChatAbsolute, "He's a real rascal, but he already has the Cog-fighting down to a science!", CFSpeech | CFTimeout), Wait(8), Func(self.flippy.setChatAbsolute, 'Doctor Surlee says he\'s some sort of creature called a "Doodle". Funny name, right?', CFSpeech | CFTimeout), Wait(8), Func(self.flippy.setChatAbsolute, 'Anyway, what are you waiting for?', CFSpeech | CFTimeout), ActorInterval(self.flippy, 'shrug'), Func(self.flippy.loop, 'neutral'), Wait(4), Func(self.flippy.setChatAbsolute, 'Grab some pies, catch some fish, and go for a spin. ToonFest is in full swing!', CFSpeech | CFTimeout))
        self.flippyBlatherSequence.loop()
        self.fluffy = ToontownAvatarUtils.createDoodle('Fluffy', -1, 0, 0, -1, 4, 0, 0, 5, 1, 191, -263, 4.597, 109)
        self.fluffy.addActive()
        self.fluffy.startBlink()
        self.tower = self.geom.find('**/toonfest_tower_DNARoot')
        self.base1 = self.tower.find('**/base1')
        self.base2 = self.tower.find('**/base2')
        self.base3 = self.tower.find('**/base3')
        self.body = self.tower.find('**/tf_tower_mid')
        self.sign = self.tower.find('**/tf_sign')

    def unload(self):
        del self.tower
        del self.base1
        del self.base2
        del self.base3
        self.flippyBlatherSequence.finish()
        if self.flippy:
            self.flippy.stopBlink()
            self.flippy.removeActive()
            self.flippy.delete()
        if self.fluffy:
            self.fluffy.stopBlink()
            self.fluffy.removeActive()
            self.fluffy.enterOff()
            self.fluffy.delete()
        SafeZoneLoader.unload(self)

    def enter(self, requestStatus):
        SafeZoneLoader.enter(self, requestStatus)

    def exit(self):
        SafeZoneLoader.exit(self)

    def startCloudPlatforms(self):
        return
        if len(self.clouds):
            self.cloudTrack = self.__cloudTrack()
            self.cloudTrack.loop()

    def stopCloudPlatforms(self):
        if self.cloudTrack:
            self.cloudTrack.pause()
            del self.cloudTrack
            self.cloudTrack = None
        return

    def loadClouds(self):
        self.loadCloudPlatforms()
        if base.cloudPlatformsEnabled and 0:
            self.setCloudSwitch(1)
        if self.cloudSwitch:
            self.setCloudSwitch(self.cloudSwitch)

    def loadCloud(self, version, radius, zOffset):
        self.notify.debug('loadOnePlatform version=%d' % version)
        cloud = NodePath('cloud-%d%d' % (radius, version))
        cloudModel = loader.loadModel('phase_5.5/models/estate/bumper_cloud')
        cc = cloudModel.copyTo(cloud)
        colCube = cc.find('**/collision')
        colCube.setName('cloudSphere-0')
        dTheta = 2.0 * math.pi / self.numClouds
        cloud.reparentTo(self.cloudOrigin)
        axes = [Vec3(1, 0, 0), Vec3(0, 1, 0), Vec3(0, 0, 1)]
        cloud.setPos(radius * math.cos(version * dTheta), radius * math.sin(version * dTheta), 4 * random.random() + zOffset)
        cloud.setScale(4.0)
        cloud.setTag('number', '%d%d' % (radius, version))
        x, y, z = cloud.getPos()
        cloudIval = Parallel(cloud.hprInterval(4.0, (360, 0, 0)))
        if version % 2 == 0:
            cloudIval.append(Sequence(cloud.posInterval(2.0, (x, y, z + 4), startPos=(x, y, z), blendType='easeInOut'), cloud.posInterval(2.0, (x, y, z), startPos=(x, y, z + 4), blendType='easeInOut')))
        else:
            cloudIval.append(Sequence(cloud.posInterval(2.0, (x, y, z), startPos=(x, y, z + 4), blendType='easeInOut'), cloud.posInterval(2.0, (x, y, z + 4), startPos=(x, y, z), blendType='easeInOut')))
        cloudIval.loop()
        self.clouds.append([cloud, random.choice(axes)])

    def loadSkyCollision(self):
        plane = CollisionPlane(Plane(Vec3(0, 0, -1), Point3(0, 0, 350)))
        plane.setTangible(0)
        planeNode = CollisionNode('sky_collision')
        planeNode.addSolid(plane)
        self.cloudOrigin.attachNewNode(planeNode)

    def loadCloudPlatforms(self):
        self.cloudOrigin = self.geom.attachNewNode('cloudOrigin')
        self.cloudOrigin.setPos(216, -68, 55)
        self.loadSkyCollision()
        self.numClouds = 18
        for i in range(self.numClouds):
            self.loadCloud(i, 110, 0)

        for i in range(self.numClouds):
            self.loadCloud(i, 130, 30)

        for i in range(self.numClouds):
            self.loadCloud(i, 110, 60)

        self.cloudOrigin.stash()

    def __cleanupCloudFadeInterval(self):
        if hasattr(self, 'cloudFadeInterval'):
            self.cloudFadeInterval.pause()
            self.cloudFadeInterval = None
        return

    def fadeClouds(self, on):
        self.__cleanupCloudFadeInterval()
        self.cloudOrigin.setTransparency(1)
        self.cloudFadeInterval = self.cloudOrigin.colorInterval(0.5, Vec4(1, 1, 1, int(on)), blendType='easeIn')
        if on:
            self.cloudOrigin.setColor(Vec4(1, 1, 1, 0))
            self.setCloudSwitch(1)
        else:
            self.cloudFadeInterval = Sequence(self.cloudFadeInterval, Func(self.setCloudSwitch, 0), Func(self.cloudOrigin.setTransparency, 0))
        self.cloudFadeInterval.start()

    def setCloudSwitch(self, on):
        self.cloudSwitch = on
        if hasattr(self, 'cloudOrigin'):
            if on:
                self.cloudOrigin.unstash()
            else:
                self.cloudOrigin.stash()