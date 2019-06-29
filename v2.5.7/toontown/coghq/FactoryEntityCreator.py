from otp.level import EntityCreator
import FactoryLevelMgr, PlatformEntity, ConveyorBelt, GearEntity, PaintMixer, GoonClipPlane, MintProduct, MintProductPallet, MintShelf, PathMasterEntity, RenderingEntity

class FactoryEntityCreator(EntityCreator.EntityCreator):

    def __init__(self, level):
        EntityCreator.EntityCreator.__init__(self, level)
        nothing = EntityCreator.nothing
        nonlocal = EntityCreator.nonlocal
        self.privRegisterTypes({'activeCell': nonlocal, 'crusherCell': nonlocal, 
           'battleBlocker': nonlocal, 
           'beanBarrel': nonlocal, 
           'button': nonlocal, 
           'conveyorBelt': ConveyorBelt.ConveyorBelt, 
           'crate': nonlocal, 
           'door': nonlocal, 
           'directionalCell': nonlocal, 
           'gagBarrel': nonlocal, 
           'gear': GearEntity.GearEntity, 
           'goon': nonlocal, 
           'gridGoon': nonlocal, 
           'golfGreenGame': nonlocal, 
           'goonClipPlane': GoonClipPlane.GoonClipPlane, 
           'grid': nonlocal, 
           'healBarrel': nonlocal, 
           'levelMgr': FactoryLevelMgr.FactoryLevelMgr, 
           'lift': nonlocal, 
           'mintProduct': MintProduct.MintProduct, 
           'mintProductPallet': MintProductPallet.MintProductPallet, 
           'mintShelf': MintShelf.MintShelf, 
           'mover': nonlocal, 
           'paintMixer': PaintMixer.PaintMixer, 
           'pathMaster': PathMasterEntity.PathMasterEntity, 
           'rendering': RenderingEntity.RenderingEntity, 
           'platform': PlatformEntity.PlatformEntity, 
           'sinkingPlatform': nonlocal, 
           'stomper': nonlocal, 
           'stomperPair': nonlocal, 
           'laserField': nonlocal, 
           'securityCamera': nonlocal, 
           'elevatorMarker': nonlocal, 
           'trigger': nonlocal, 
           'moleField': nonlocal, 
           'maze': nonlocal})