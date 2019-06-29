from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.actor import Actor
from toontown.toonbase import ToontownGlobals
import random
from toontown.parties import PartyGlobals
from toontown.parties.PartyUtils import getCenterPosFromGridSize
from toontown.safezone import HolidayCar

class Decoration(NodePath):
    notify = directNotify.newCategory('Decoration')

    def __init__(self, name, x, y, h):
        NodePath.__init__(self, name)
        self.name = name
        decorId = PartyGlobals.DecorationIds.fromString(name)
        centerX, centerY = getCenterPosFromGridSize(x, y, PartyGlobals.DecorationInformationDict[decorId]['gridsize'])
        self.setPos(centerX, centerY, 0.0)
        self.setH(h)
        if self.name == 'CakeTower':
            self.partyCake = loader.loadModel('phase_13/models/parties/tt_m_ara_pty_cakeTower')
            tntSeqNode = self.partyCake.find('**/seqNode_tnt').node()
            tntSeqNode.setFrameRate(20)
            self.partyCake.reparentTo(self)
        else:
            if self.name == 'BannerJellyBean':
                partyBannerModel = loader.loadModel('phase_13/models/parties/tt_m_ara_pty_bannerJellybean_model')
                banner = []
                banner1 = partyBannerModel.find('**/banner1')
                banner2 = partyBannerModel.find('**/banner2')
                temp = NodePath('Empty')
                banner1.reparentTo(temp)
                banner2.reparentTo(temp)
                banner.append(banner1)
                banner.append(banner2)
                self.partyBanner = Actor.Actor(partyBannerModel, {'float': 'phase_13/models/parties/tt_m_ara_pty_bannerJellybean'})
                self.partyBanner.setBlend(frameBlend=config.GetBool('interpolate-animations', True))
                bannerSeqNodeParent = self.partyBanner.find('**/bannerJoint')
                bannerSeqNode = SequenceNode('banner')
                for bannerNode in banner:
                    bannerSeqNode.addChild(bannerNode.node())

                temp.detachNode()
                del temp
                bannerSeqNodeParent.attachNewNode(bannerSeqNode)
                bannerSeqNode.setFrameRate(4)
                bannerSeqNode.loop(True)
                bannerSeqNode.setPlayRate(1)
                balloonLeft = self.partyBanner.find('**/balloonsLMesh')
                balloonRight = self.partyBanner.find('**/balloonsRMesh')
                balloonLeft.setBillboardAxis()
                balloonRight.setBillboardAxis()
                balloonLeftLocator = self.partyBanner.find('**/balloonJointL')
                balloonRightLocator = self.partyBanner.find('**/balloonJointR')
                balloonLeft.reparentTo(balloonLeftLocator)
                balloonRight.reparentTo(balloonRightLocator)
                self.partyBanner.loop('float')
                self.partyBanner.reparentTo(self)
            else:
                if self.name == 'GagGlobe':
                    self.partyGlobe = Actor.Actor('phase_13/models/parties/tt_m_ara_pty_gagGlobe_model', {'idle': 'phase_13/models/parties/tt_m_ara_pty_gagGlobe'})
                    self.partyGlobe.setBlend(frameBlend=config.GetBool('interpolate-animations', True))
                    self.partyGlobe.setBillboardAxis()
                    confettiLocator = self.partyGlobe.find('**/uvj_confetti')
                    confettiMesh = self.partyGlobe.find('**/innerGlobeMesh')
                    confettiMesh.setTexProjector(confettiMesh.findTextureStage('default'), confettiLocator, self.partyGlobe)
                    collisionMesh = self.partyGlobe.find('**/collisionMesh')
                    collisionMesh.hide()
                    self.globeSphere = CollisionSphere(confettiMesh.getBounds().getCenter(), confettiMesh.getBounds().getRadius())
                    self.globeSphere.setTangible(1)
                    self.globeSphereNode = CollisionNode('gagGlobe' + str(self.getPos()))
                    self.globeSphereNode.setIntoCollideMask(ToontownGlobals.WallBitmask)
                    self.globeSphereNode.addSolid(self.globeSphere)
                    self.globeSphereNodePath = self.partyGlobe.attachNewNode(self.globeSphereNode)
                    self.partyGlobe.loop('idle')
                    self.partyGlobe.reparentTo(self)
                else:
                    if self.name == 'FlyingHeart':
                        flyingHeartModel = loader.loadModel('phase_13/models/parties/tt_m_ara_pty_heartWing_model')
                        self.flyingHeart = Actor.Actor(flyingHeartModel, {'idle': 'phase_13/models/parties/tt_m_ara_pty_heartWing'})
                        self.flyingHeart.setBlend(frameBlend=config.GetBool('interpolate-animations', True))
                        wingsSeqNodeParent = self.flyingHeart.find('**/heartWingJoint')
                        collisionMesh = self.flyingHeart.find('**/collision_heartWing')
                        collisionMesh.hide()
                        self.globeSphere = CollisionSphere(collisionMesh.getBounds().getCenter(), collisionMesh.getBounds().getRadius())
                        self.globeSphere.setTangible(1)
                        self.globeSphereNode = CollisionNode('flyingHeart' + str(self.getPos()))
                        self.globeSphereNode.setIntoCollideMask(ToontownGlobals.WallBitmask)
                        self.globeSphereNode.addSolid(self.globeSphere)
                        self.globeSphereNodePath = self.flyingHeart.attachNewNode(self.globeSphereNode)
                        self.globeSphereNodePath.reparentTo(wingsSeqNodeParent)
                        wings = []
                        wingsSeqNode = SequenceNode('wingsSeqNode')
                        temp = NodePath('Empty')
                        wing1 = self.flyingHeart.find('**/wing1')
                        wing2 = self.flyingHeart.find('**/wing2')
                        wing3 = self.flyingHeart.find('**/wing3')
                        wing4 = self.flyingHeart.find('**/wing4')
                        wing1.reparentTo(temp)
                        wing2.reparentTo(temp)
                        wing3.reparentTo(temp)
                        wing4.reparentTo(temp)
                        wings.append(wing1)
                        wings.append(wing2)
                        wings.append(wing3)
                        wings.append(wing4)
                        wingsSeqNode.addChild(wing1.node())
                        wingsSeqNode.addChild(wing2.node())
                        wingsSeqNode.addChild(wing3.node())
                        wingsSeqNode.addChild(wing4.node())
                        wingsSeqNode.addChild(wing3.node())
                        wingsSeqNode.addChild(wing2.node())
                        temp.detachNode()
                        del temp
                        wingsSeqNodeParent.attachNewNode(wingsSeqNode)
                        wingsSeqNode.setFrameRate(12)
                        wingsSeqNode.loop(True)
                        wingsSeqNode.setPlayRate(1)
                        self.flyingHeart.loop('idle')
                        self.flyingHeart.reparentTo(self)
                    else:
                        if self.name == 'HeartBanner':
                            self.heartBanner = Actor.Actor('phase_13/models/parties/tt_m_ara_pty_bannerValentine_model', {'idle': 'phase_13/models/parties/tt_m_ara_pty_bannerValentine'})
                            self.heartBanner.setBlend(frameBlend=config.GetBool('interpolate-animations', True))
                            balloonLeft = self.heartBanner.find('**/balloonsL')
                            balloonRight = self.heartBanner.find('**/balloonsR')
                            balloonLeft.setBillboardAxis()
                            balloonRight.setBillboardAxis()
                            balloonLeftLocator = self.heartBanner.find('**/balloonJointL')
                            balloonRightLocator = self.heartBanner.find('**/balloonJointR')
                            balloonLeft.reparentTo(balloonLeftLocator)
                            balloonRight.reparentTo(balloonRightLocator)
                            self.heartBanner.loop('idle')
                            self.heartBanner.reparentTo(self)
                        else:
                            if self.name == 'Hydra' or self.name == 'StageWinter':
                                if self.name == 'StageWinter':
                                    self.hydra = Actor.Actor('phase_13/models/parties/tt_r_ara_pty_winterProps', {'dance': 'phase_13/models/parties/tt_a_ara_pty_hydra_dance'})
                                else:
                                    self.hydra = Actor.Actor('phase_13/models/parties/tt_a_ara_pty_hydra_default', {'dance': 'phase_13/models/parties/tt_a_ara_pty_hydra_dance'})
                                st = random.randint(0, 10)
                                animIval = ActorInterval(self.hydra, 'dance')
                                animIvalDur = animIval.getDuration()
                                self.decSfx = loader.loadSfx('phase_13/audio/sfx/tt_s_ara_pty_propsShow_dance.ogg')
                                soundIval = SoundInterval(self.decSfx, node=self.hydra, listenerNode=base.localAvatar, volume=PartyGlobals.DECORATION_VOLUME, cutOff=PartyGlobals.DECORATION_CUTOFF, duration=animIvalDur)
                                self.animSeq = Parallel(animIval, soundIval)
                                self.animSeq.loop(st)
                                collisions = self.hydra.find('**/*collision*')
                                collisions.setPos(0, 0, -5)
                                self.hydra.setBlend(frameBlend=config.GetBool('interpolate-animations', True))
                                self.hydra.flattenStrong()
                                self.hydra.reparentTo(self)
                                if self.name == 'StageWinter':
                                    stageBounds = self.hydra.find('**/stage').node().getBounds()
                                    self.hydra.node().setBounds(stageBounds)
                                    self.hydra.node().setFinal(1)
                            else:
                                if self.name == 'TubeCogVictory':
                                    self.tubeCog = Actor.Actor('phase_5.5/models/estate/tt_a_ara_pty_tubeCogVictory_default', {'wave': 'phase_5.5/models/estate/tt_a_ara_pty_tubeCogVictory_wave'})
                                    st = random.randint(0, 10)
                                    animIval = ActorInterval(self.tubeCog, 'wave')
                                    animIvalDur = animIval.getDuration()
                                    self.decSfx = loader.loadSfx('phase_13/audio/sfx/tt_s_ara_pty_tubeCogVictory_wave.ogg')
                                    soundIval = SoundInterval(self.decSfx, node=self.tubeCog, listenerNode=base.localAvatar, volume=PartyGlobals.DECORATION_VOLUME, cutOff=PartyGlobals.DECORATION_CUTOFF, duration=animIvalDur)
                                    self.animSeq = Parallel(animIval, soundIval)
                                    self.animSeq.loop()
                                    self.animSeq.setT(st)
                                    self.tubeCog.setBlend(frameBlend=config.GetBool('interpolate-animations', True))
                                    self.tubeCog.flattenStrong()
                                    self.tubeCog.reparentTo(self)
                                else:
                                    if self.name == 'BannerVictory':
                                        self.bannerVictory = Actor.Actor('phase_13/models/parties/tt_m_ara_pty_bannerVictory_model', {'idle': 'phase_13/models/parties/tt_m_ara_pty_bannerVictory'})
                                        self.bannerVictory.setBlend(frameBlend=config.GetBool('interpolate-animations', True))
                                        balloonLeft = self.bannerVictory.find('**/balloonsLMesh')
                                        balloonRight = self.bannerVictory.find('**/balloonsRMesh')
                                        balloonLeft.setBillboardAxis()
                                        balloonRight.setBillboardAxis()
                                        balloonLeftLocator = self.bannerVictory.find('**/balloonJointL')
                                        balloonRightLocator = self.bannerVictory.find('**/balloonJointR')
                                        balloonLeft.reparentTo(balloonLeftLocator)
                                        balloonRight.reparentTo(balloonRightLocator)
                                        self.bannerVictory.loop('idle')
                                        self.bannerVictory.reparentTo(self)
                                    else:
                                        if self.name == 'CannonVictory':
                                            self.cannonVictory = Actor.Actor('phase_13/models/parties/tt_m_ara_pty_cannonVictory_model', {'idle': 'phase_13/models/parties/tt_m_ara_pty_cannonVictory'})
                                            self.cannonVictory.setBlend(frameBlend=config.GetBool('interpolate-animations', True))
                                            confettiLocator = self.cannonVictory.findAllMatches('**/uvj_confetties')[1]
                                            confettiMesh = self.cannonVictory.find('**/confettis')
                                            confettiMesh.setTexProjector(confettiMesh.findTextureStage('default'), self.cannonVictory, confettiLocator)
                                            self.cannonVictory.flattenStrong()
                                            self.cannonVictory.loop('idle')
                                            self.cannonVictory.reparentTo(self)
                                        else:
                                            if self.name == 'CogStatueVictory':
                                                self.decorationModel = loader.loadModel('phase_13/models/parties/tt_m_ara_pty_cogDoodleVictory')
                                                self.decorationModel.reparentTo(self)
                                                self.decorationShadow = self.setupAnimSeq()
                                            else:
                                                if self.name == 'CogIceCreamVictory':
                                                    self.decorationModel = loader.loadModel('phase_13/models/parties/tt_m_ara_pty_cogIceCreamVictory')
                                                    self.decorationModel.reparentTo(self)
                                                    self.decorationShadow = self.setupAnimSeq()
                                                else:
                                                    if self.name == 'cogIceCreamWinter':
                                                        self.decorationModel = loader.loadModel('phase_13/models/parties/tt_m_ara_pty_cogIceCreamWinter')
                                                        self.decorationModel.reparentTo(self)
                                                        self.decorationShadow = self.setupAnimSeq()
                                                    else:
                                                        if self.name == 'CogStatueWinter':
                                                            self.decorationModel = loader.loadModel('phase_13/models/parties/tt_m_ara_pty_cogDoodleWinter')
                                                            self.decorationModel.reparentTo(self)
                                                            self.decorationShadow = self.setupAnimSeq()
                                                        else:
                                                            if self.name == 'ToonHall':
                                                                self.decorationModel = loader.loadModel('phase_4/models/modules/toonhall')
                                                                self.decorationModel.reparentTo(self)
                                                            else:
                                                                if self.name == 'Bank':
                                                                    self.decorationModel = loader.loadModel('phase_4/models/modules/bank')
                                                                    self.decorationModel.reparentTo(self)
                                                                else:
                                                                    if self.name == 'Gazebo':
                                                                        self.decorationModel = loader.loadModel('phase_4/models/modules/gazebo')
                                                                        self.decorationModel.reparentTo(self)
                                                                    else:
                                                                        if self.name == 'Trolley':
                                                                            self.decorationModel = loader.loadModel('phase_4/models/modules/trolley_station_TT')
                                                                            self.decorationModel.reparentTo(self)
                                                                        else:
                                                                            if self.name == 'PetShop':
                                                                                self.decorationModel = loader.loadModel('phase_4/models/modules/PetShopExterior_TT')
                                                                                self.decorationModel.reparentTo(self)
                                                                            else:
                                                                                if self.name == 'School':
                                                                                    self.decorationModel = loader.loadModel('phase_4/models/modules/school_house')
                                                                                    self.decorationModel.reparentTo(self)
                                                                                else:
                                                                                    if self.name == 'Library':
                                                                                        self.decorationModel = loader.loadModel('phase_4/models/modules/library')
                                                                                        self.decorationModel.reparentTo(self)
                                                                                    else:
                                                                                        if self.name == 'GagTank':
                                                                                            self.decorationModel = loader.loadModel('phase_4/models/cogHQ/gagTank')
                                                                                            self.decorationModel.reparentTo(self)
                                                                                        else:
                                                                                            if self.name == 'MickeyHorse':
                                                                                                self.decorationModel = loader.loadModel('phase_4/models/props/mickey_on_horse')
                                                                                                self.decorationModel.reparentTo(self)
                                                                                            else:
                                                                                                if self.name == 'GoofyStatue':
                                                                                                    self.decorationModel = loader.loadModel('phase_4/models/props/goofy_statue')
                                                                                                    self.decorationModel.reparentTo(self)
                                                                                                else:
                                                                                                    if self.name == 'SillyMeter':
                                                                                                        self.decorationModel = loader.loadModel('phase_4/models/props/tt_a_ara_ttc_sillyMeter_default')
                                                                                                        self.decorationModel.reparentTo(self)
                                                                                                    else:
                                                                                                        if self.name == 'Fountain':
                                                                                                            self.decorationModel = loader.loadModel('phase_4/models/props/toontown_central_fountain')
                                                                                                            self.decorationModel.reparentTo(self)
                                                                                                        else:
                                                                                                            if self.name == 'XmasTree':
                                                                                                                self.decorationModel = loader.loadModel('phase_4/models/props/winter_tree_Christmas')
                                                                                                                self.decorationModel.reparentTo(self)
                                                                                                            else:
                                                                                                                if self.name == 'FlippyStand':
                                                                                                                    self.decorationModel = loader.loadModel('phase_4/models/events/election_flippyStand-static')
                                                                                                                    self.decorationModel.reparentTo(self)
                                                                                                                else:
                                                                                                                    if self.name == 'Podium':
                                                                                                                        self.decorationModel = loader.loadModel('phase_4/models/events/election_stagePodium')
                                                                                                                        self.decorationModel.reparentTo(self)
                                                                                                                    else:
                                                                                                                        if self.name == 'Stage':
                                                                                                                            self.decorationModel = loader.loadModel('phase_4/models/events/election_stage')
                                                                                                                            self.decorationModel.reparentTo(self)
                                                                                                                        else:
                                                                                                                            if self.name == 'SlappyStand':
                                                                                                                                self.decorationModel = loader.loadModel('phase_4/models/events/election_slappyStand-mod')
                                                                                                                                self.decorationModel.reparentTo(self)
                                                                                                                            else:
                                                                                                                                if self.name == 'CogdoSafes':
                                                                                                                                    self.decorationModel = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_ccg_safesA')
                                                                                                                                    self.decorationModel.reparentTo(self)
                                                                                                                                else:
                                                                                                                                    if self.name == 'Train':
                                                                                                                                        self.decorationModel = loader.loadModel('phase_5/models/props/train')
                                                                                                                                        self.decorationModel.reparentTo(self)
                                                                                                                                    else:
                                                                                                                                        if self.name == 'Hydrant':
                                                                                                                                            self.decorationModel = loader.loadModel('phase_5/models/props/TT_hydrant')
                                                                                                                                            self.decorationModel.reparentTo(self)
                                                                                                                                        else:
                                                                                                                                            if self.name == 'BeanBank':
                                                                                                                                                self.decorationModel = loader.loadModel('phase_5.5/models/estate/jellybeanBank')
                                                                                                                                                self.decorationModel.reparentTo(self)
                                                                                                                                            else:
                                                                                                                                                if self.name == 'Organ':
                                                                                                                                                    self.decorationModel = loader.loadModel('phase_5.5/models/estate/Organ')
                                                                                                                                                    self.decorationModel.reparentTo(self)
                                                                                                                                                else:
                                                                                                                                                    if self.name == 'PopcornCart':
                                                                                                                                                        self.decorationModel = loader.loadModel('phase_5.5/models/estate/popcornCart')
                                                                                                                                                        self.decorationModel.reparentTo(self)
                                                                                                                                                    else:
                                                                                                                                                        if self.name == 'House':
                                                                                                                                                            self.decorationModel = loader.loadModel('phase_5.5/models/estate/test_houseA')
                                                                                                                                                            self.decorationModel.reparentTo(self)
                                                                                                                                                        else:
                                                                                                                                                            if self.name == 'CastleHouse':
                                                                                                                                                                self.decorationModel = loader.loadModel('phase_5.5/models/estate/tt_m_ara_est_house_castle')
                                                                                                                                                                self.decorationModel.reparentTo(self)
                                                                                                                                                            else:
                                                                                                                                                                if self.name == 'Tiki':
                                                                                                                                                                    self.decorationModel = loader.loadModel('phase_5.5/models/estate/tt_m_ara_est_house_tiki')
                                                                                                                                                                    self.decorationModel.reparentTo(self)
                                                                                                                                                                else:
                                                                                                                                                                    if self.name == 'Tepee':
                                                                                                                                                                        self.decorationModel = loader.loadModel('phase_5.5/models/estate/tt_m_ara_est_house_tepee')
                                                                                                                                                                        self.decorationModel.reparentTo(self)
                                                                                                                                                                    else:
                                                                                                                                                                        if self.name == 'GagShop':
                                                                                                                                                                            self.decorationModel = loader.loadModel('phase_6/models/modules/gagShop_DD')
                                                                                                                                                                            self.decorationModel.reparentTo(self)
                                                                                                                                                                        else:
                                                                                                                                                                            if self.name == 'snowman':
                                                                                                                                                                                self.decorationModel = loader.loadModel('phase_13/models/estate/tt_m_prp_ext_snowman')
                                                                                                                                                                                self.decorationModel.reparentTo(self)
                                                                                                                                                                                self.decorationModel.find('**/growthStage_1').hide()
                                                                                                                                                                                self.decorationModel.find('**/growthStage_2').hide()
                                                                                                                                                                            else:
                                                                                                                                                                                if self.name == 'snowDoodle':
                                                                                                                                                                                    self.decorationModel = loader.loadModel('phase_5.5/models/estate/tt_m_prp_ext_snowDoodle')
                                                                                                                                                                                    self.decorationModel.reparentTo(self)
                                                                                                                                                                                    self.decorationModel.find('**/growthStage_1').hide()
                                                                                                                                                                                    self.decorationModel.find('**/growthStage_2').hide()
                                                                                                                                                                                else:
                                                                                                                                                                                    if self.name == 'HolidaySwag':
                                                                                                                                                                                        self.swagtaClaus = HolidayCar.HolidayCar()
                                                                                                                                                                                        self.swagtaClaus.generate()
                                                                                                                                                                                        self.saySwag = Sequence(Func(self.swagtaClaus.swagPhrase), Wait(25))
                                                                                                                                                                                        self.saySwag.loop()
                                                                                                                                                                                    else:
                                                                                                                                                                                        if self.name == 'NormalSky':
                                                                                                                                                                                            self.sky = loader.loadModel('phase_3.5/models/props/TT_sky')
                                                                                                                                                                                            self.sky.setTag('sky', 'Regular')
                                                                                                                                                                                            self.sky.setScale(1.0)
                                                                                                                                                                                            self.sky.setFogOff()
                                                                                                                                                                                            self.sky.reparentTo(camera)
                                                                                                                                                                                            self.sky.setPosHpr(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
                                                                                                                                                                                            ce = CompassEffect.make(NodePath(), CompassEffect.PRot | CompassEffect.PZ)
                                                                                                                                                                                            self.sky.node().setEffect(ce)
                                                                                                                                                                                        else:
                                                                                                                                                                                            if self.name == 'Dreamland':
                                                                                                                                                                                                self.sky = loader.loadModel('phase_8/models/props/DL_sky')
                                                                                                                                                                                                self.sky.setTag('sky', 'Regular')
                                                                                                                                                                                                self.sky.setScale(1.0)
                                                                                                                                                                                                self.sky.setFogOff()
                                                                                                                                                                                                self.sky.reparentTo(camera)
                                                                                                                                                                                                self.sky.setPosHpr(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
                                                                                                                                                                                                ce = CompassEffect.make(NodePath(), CompassEffect.PRot | CompassEffect.PZ)
                                                                                                                                                                                                self.sky.node().setEffect(ce)
                                                                                                                                                                                            else:
                                                                                                                                                                                                if self.name == 'Melodyland':
                                                                                                                                                                                                    self.sky = loader.loadModel('phase_6/models/props/MM_sky')
                                                                                                                                                                                                    self.sky.setTag('sky', 'Regular')
                                                                                                                                                                                                    self.sky.setScale(1.0)
                                                                                                                                                                                                    self.sky.setFogOff()
                                                                                                                                                                                                    self.sky.reparentTo(camera)
                                                                                                                                                                                                    self.sky.setPosHpr(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
                                                                                                                                                                                                    ce = CompassEffect.make(NodePath(), CompassEffect.PRot | CompassEffect.PZ)
                                                                                                                                                                                                    self.sky.node().setEffect(ce)
                                                                                                                                                                                                else:
                                                                                                                                                                                                    if self.name == 'FoggySky':
                                                                                                                                                                                                        self.sky = loader.loadModel('phase_3.5/models/props/BR_sky')
                                                                                                                                                                                                        self.sky.setTag('sky', 'Regular')
                                                                                                                                                                                                        self.sky.setScale(1.0)
                                                                                                                                                                                                        self.sky.setFogOff()
                                                                                                                                                                                                        self.sky.reparentTo(camera)
                                                                                                                                                                                                        self.sky.setPosHpr(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
                                                                                                                                                                                                        ce = CompassEffect.make(NodePath(), CompassEffect.PRot | CompassEffect.PZ)
                                                                                                                                                                                                        self.sky.node().setEffect(ce)
                                                                                                                                                                                                    else:
                                                                                                                                                                                                        if self.name == 'SpookySky':
                                                                                                                                                                                                            self.sky = loader.loadModel('phase_3.5/models/props/HW_2016_Sky')
                                                                                                                                                                                                            self.sky.setTag('sky', 'Regular')
                                                                                                                                                                                                            self.sky.setScale(1.0)
                                                                                                                                                                                                            self.sky.setFogOff()
                                                                                                                                                                                                            self.sky.reparentTo(camera)
                                                                                                                                                                                                            self.sky.setPosHpr(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
                                                                                                                                                                                                            ce = CompassEffect.make(NodePath(), CompassEffect.PRot | CompassEffect.PZ)
                                                                                                                                                                                                            self.sky.node().setEffect(ce)
                                                                                                                                                                                                        else:
                                                                                                                                                                                                            if self.name == 'CogSky':
                                                                                                                                                                                                                self.sky = loader.loadModel('phase_9/models/cogHQ/cog_sky')
                                                                                                                                                                                                                self.sky.setTag('sky', 'Regular')
                                                                                                                                                                                                                self.sky.setScale(1.0)
                                                                                                                                                                                                                self.sky.setFogOff()
                                                                                                                                                                                                                self.sky.reparentTo(camera)
                                                                                                                                                                                                                self.sky.setPosHpr(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
                                                                                                                                                                                                                ce = CompassEffect.make(NodePath(), CompassEffect.PRot | CompassEffect.PZ)
                                                                                                                                                                                                                self.sky.node().setEffect(ce)
                                                                                                                                                                                                            else:
                                                                                                                                                                                                                if self.name == 'OldCogSky':
                                                                                                                                                                                                                    self.sky = loader.loadModel('phase_9/models/cogHQ/old_sky')
                                                                                                                                                                                                                    self.sky.setTag('sky', 'Regular')
                                                                                                                                                                                                                    self.sky.setScale(1.0)
                                                                                                                                                                                                                    self.sky.setFogOff()
                                                                                                                                                                                                                    self.sky.reparentTo(camera)
                                                                                                                                                                                                                    self.sky.setPosHpr(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
                                                                                                                                                                                                                    ce = CompassEffect.make(NodePath(), CompassEffect.PRot | CompassEffect.PZ)
                                                                                                                                                                                                                    self.sky.node().setEffect(ce)
                                                                                                                                                                                                                else:
                                                                                                                                                                                                                    if self.name == 'BBHQCogSky':
                                                                                                                                                                                                                        self.sky = loader.loadModel('phase_12/models/bossbotHQ/ttr_m_bossbothq_sky')
                                                                                                                                                                                                                        self.sky.setTag('sky', 'Regular')
                                                                                                                                                                                                                        self.sky.setScale(1.0)
                                                                                                                                                                                                                        self.sky.setFogOff()
                                                                                                                                                                                                                        self.sky.reparentTo(camera)
                                                                                                                                                                                                                        self.sky.setPosHpr(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
                                                                                                                                                                                                                        ce = CompassEffect.make(NodePath(), CompassEffect.PRot | CompassEffect.PZ)
                                                                                                                                                                                                                        self.sky.node().setEffect(ce)
                                                                                                                                                                                                                        base.camLens.setNearFar(ToontownGlobals.BossbotHQCameraNear, ToontownGlobals.BossbotHQCameraFar)
                                                                                                                                                                                                                    else:
                                                                                                                                                                                                                        self.decorationModels = loader.loadModel('phase_4/models/parties/partyDecorations')
                                                                                                                                                                                                                        self.decorationModels.copyTo(self)
                                                                                                                                                                                                                        decors = self.findAllMatches('**/partyDecoration_*')
                                                                                                                                                                                                                        for i in xrange(decors.getNumPaths()):
                                                                                                                                                                                                                            decPiece = decors.getPath(i)
                                                                                                                                                                                                                            n = decPiece.getName()
                                                                                                                                                                                                                            if n.endswith('shadow') or n.endswith('base') or n.endswith('collision') or n.endswith(name):
                                                                                                                                                                                                                                pass
                                                                                                                                                                                                                            else:
                                                                                                                                                                                                                                decPiece.reparentTo(hidden)

        self.reparentTo(base.cr.playGame.hood.loader.geom)

    def setupAnimSeq(self):
        self.startAnim = 1
        self.animSeq = None
        shadow = self.find('**/*shadow*;+i')
        shadow.wrtReparentTo(base.cr.playGame.hood.loader.geom)
        self.startAnimSeq()
        return shadow

    def startAnimSeq(self):
        if self.animSeq:
            self.animSeq.finish()
        if self.startAnim == 1:
            self.animSeq = Sequence(LerpHprInterval(self.decorationModel, 3.0, Vec3(random.randint(0, 5), random.randint(0, 5), random.randint(0, 5))), Wait(0.05), Func(self.startAnimSeq))
            self.animSeq.start()

    def cleanUpAnimSequences(self):
        self.startAnim = 0
        if hasattr(self, 'animSeq'):
            self.animSeq.pause()
            self.animSeq.finish()
            if self.animSeq:
                del self.animSeq

    def unload(self):
        self.notify.debug('Unloading')
        if self.name == 'GagGlobe':
            self.globeSphereNodePath.removeNode()
            del self.globeSphereNodePath
            del self.globeSphereNode
            del self.globeSphere
            self.partyGlobe.removeNode()
            del self.partyGlobe
        else:
            if self.name == 'Hydra' or self.name == 'StageWinter':
                self.cleanUpAnimSequences()
                self.hydra.removeNode()
                del self.hydra
                if hasattr(self, 'decSfx'):
                    del self.decSfx
            else:
                if self.name == 'TubeCogVictory':
                    self.cleanUpAnimSequences()
                    self.tubeCog.removeNode()
                    del self.tubeCog
                    if hasattr(self, 'decSfx'):
                        del self.decSfx
                else:
                    if self.name == 'BannerJellyBean':
                        self.partyBanner.removeNode()
                    else:
                        if self.name == 'CakeTower':
                            self.partyCake.removeNode()
                        else:
                            if self.name == 'FlyingHeart':
                                self.globeSphereNodePath.removeNode()
                                del self.globeSphereNodePath
                                del self.globeSphereNode
                                del self.globeSphere
                                self.flyingHeart.removeNode()
                            else:
                                if self.name == 'HeartBanner':
                                    self.heartBanner.removeNode()
                                else:
                                    if self.name == 'CannonVictory':
                                        self.cannonVictory.removeNode()
                                        del self.cannonVictory
                                    else:
                                        if self.name == 'CogIceCreamVictory' or self.name == 'CogStatueVictory' or self.name == 'cogIceCreamWinter' or self.name == 'CogStatueWinter':
                                            self.cleanUpAnimSequences()
                                            self.decorationModel.removeNode()
                                            self.decorationShadow.removeNode()
                                            del self.decorationShadow
                                        else:
                                            if self.name == 'snowman' or self.name == 'snowDoodle':
                                                self.decorationModel.removeNode()
                                            else:
                                                if self.name == 'BannerVictory':
                                                    self.bannerVictory.removeNode()
                                                    del self.bannerVictory
                                                else:
                                                    if self.name == 'ToonHall' or self.name == 'Bank' or self.name == 'Gazebo' or self.name == 'Trolley' or self.name == 'PetShop' or self.name == 'School' or self.name == 'Library' or self.name == 'GagTank' or self.name == 'MickeyHorse' or self.name == 'GoofyStatue' or self.name == 'SillyMeter' or self.name == 'Fountain' or self.name == 'XmasTree' or self.name == 'FlippyStand' or self.name == 'Podium' or self.name == 'Stage' or self.name == 'SlappyStand' or self.name == 'CogdoSafes' or self.name == 'Train' or self.name == 'Hydrant' or self.name == 'BeanBank' or self.name == 'Organ' or self.name == 'PopcornCart' or self.name == 'House' or self.name == 'CastleHouse' or self.name == 'Tiki' or self.name == 'Tepee' or self.name == 'GagShop':
                                                        self.decorationModel.removeNode()
                                                        del self.decorationModel
                                                    else:
                                                        if self.name == 'CannonVictory':
                                                            self.decorationModel.removeNode()
                                                            del self.decorationModel
                                                        else:
                                                            if self.name == 'HolidaySwag':
                                                                if self.saySwag:
                                                                    self.saySwag.finish()
                                                                if self.swagtaClaus:
                                                                    self.swagtaClaus.disable()
                                                            else:
                                                                if self.name == 'NormalSky' or self.name == 'Dreamland' or self.name == 'Melodyland' or self.name == 'FoggySky' or self.name == 'SpookySky' or self.name == 'CogSky' or self.name == 'OldCogSky' or self.name == 'BBHQCogSky':
                                                                    if self.name == 'BBHQCogSky':
                                                                        base.camLens.setNearFar(ToontownGlobals.DefaultCameraNear, ToontownGlobals.DefaultCameraFar)
                                                                    self.sky.removeNode()
                                                                    del self.sky
                                                                else:
                                                                    self.decorationModels.removeNode()