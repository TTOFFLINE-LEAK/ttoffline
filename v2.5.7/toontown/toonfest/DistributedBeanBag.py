from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import *
import BeanBagGlobals
from toontown.safezone.DistributedTreasure import DistributedTreasure

class DistributedBeanBag(DistributedTreasure):
    notify = directNotify.newCategory('DistributedBeanBag')

    def __init__(self, cr):
        DistributedTreasure.__init__(self, cr)
        self.loadedModel = None
        self.value = 0
        self.animation = None
        self.modelPath = 'phase_6/models/events/ttr_m_ww_beanBag'
        self.grabSoundPath = 'phase_4/audio/sfx/SZ_DD_treasure.ogg'
        return

    def disable(self):
        DistributedTreasure.disable(self)
        if self.animation:
            self.animation.finish()
        self.animation = None
        return

    def setValue(self, value):
        self.value = value

    def loadModel(self):
        scale = 2 + self.value / 50.0
        self.scale = min(scale, 4.5)
        self.zOffset = 1.0
        self.grabSound = base.loader.loadSfx(self.grabSoundPath)
        self.rejectSound = base.loader.loadSfx(self.rejectSoundPath)
        if self.nodePath is None:
            self.makeNodePath()
        else:
            self.treasure.getChildren().detach()
        if self.loadedModel is not None:
            self.loadedModel.removeNode()
        self.loadedModel = loader.loadModel(self.modelPath)
        if self.value == BeanBagGlobals.TOKEN_BAG:
            alphaName = 'phase_6/maps/ttr_t_ww_beanBag_decal_token_a.rgb'
        else:
            alphaName = 'phase_6/maps/ttr_t_ww_beanBag_decal_a.rgb'
        texture = loader.loadTexture(BeanBagGlobals.Value2Texture[self.value], alphaName)
        self.loadedModel.find('**/beanBag_decal').setTexture(texture, 1)
        self.loadedModel.instanceTo(self.treasure)
        self.loadedModel.setScale(0.9 * self.scale)
        self.loadedModel.setZ(self.zOffset)
        self.loadedModel.setTransparency(True)
        return

    def startAnimation(self):
        x, y, z = self.treasure.getPos()
        self.animation = Parallel(Sequence(self.treasure.posInterval(2.0, (x, y, z + 1), startPos=(x, y, z), blendType='easeInOut'), self.treasure.posInterval(2.0, (x, y, z), startPos=(x, y, z + 1), blendType='easeInOut')), self.treasure.hprInterval(4.0, (360,
                                                                                                                                                                                                                                                                0,
                                                                                                                                                                                                                                                                0)))
        self.animation.loop()