from toontown.avatar import ToontownAvatarUtils
from toontown.avatar.CogExtras import *
PROPS = [
 (
  5, 'modules', 'suit_walls', (0.0, 342.4, 0.0), (-10.5, 0.0, 0.0), (54.6, 54.6, 54.6), 'wall_suit_build5', None,
  None),
 (
  5, 'modules', 'suit_walls', (53.686, 332.45, 0.0), (-16.5, 0.0, 0.0), (54.6, 54.6, 54.6), 'wall_suit_build5', None,
  None),
 (
  5, 'modules', 'suit_walls', (106.037, 316.943, 0.0), (-24.0, 0.0, 0.0), (54.6, 54.6, 54.6), 'wall_suit_build5',
  None, None),
 (
  5, 'modules', 'suit_walls', (155.917, 294.735, 0.0), (-36.0, 0.0, 0.0), (54.6, 54.6, 54.6), 'wall_suit_build5',
  None, None),
 (
  4, 'modules', 'suit_landmark_corp', (196.307, 269.394, 0.0), (-49.5, 0.0, 0.0), (2.7, 2.7, 2.7), None, None, None),
 (
  5, 'modules', 'suit_walls', (247.652, 209.276, 0.0), (-54.0, 0.0, 0.0), (55.4, 55.4, 55.4), 'wall_suit_build4',
  None, None),
 (
  5, 'modules', 'suit_walls', (280.215, 164.456, 0.0), (-70.5, 0.0, 0.0), (55.4, 55.4, 55.4), 'wall_suit_build4',
  None, None),
 (
  5, 'modules', 'suit_walls', (298.708, 112.234, 0.0), (-81.0, 0.0, 0.0), (55.4, 55.4, 55.4), 'wall_suit_build4',
  None, None),
 (
  5, 'modules', 'suit_walls', (307.374, 57.516, 0.0), (-88.5, 0.0, 0.0), (55.4, 55.4, 55.4), 'wall_suit_build4',
  None,
  None),
 (
  5, 'modules', 'suit_walls', (308.824, 2.135, 0.0), (-96.0, 0.0, 0.0), (55.4, 55.4, 55.4), 'wall_suit_build3', None,
  None),
 (
  5, 'modules', 'suit_walls', (303.034, -52.961, 0.0), (-102.0, 0.0, 0.0), (55.4, 55.4, 55.4), 'wall_suit_build3',
  None, None),
 (
  5, 'modules', 'suit_walls', (291.515, -107.15, 0.0), (-115.5, 0.0, 0.0), (55.4, 55.4, 55.4), 'wall_suit_build3',
  None, None),
 (
  5, 'modules', 'suit_walls', (267.665, -157.153, 0.0), (-129.0, 0.0, 0.0), (55.4, 55.4, 55.4), 'wall_suit_build3',
  None, None),
 (
  5, 'modules', 'suit_walls', (232.801, -200.207, 0.0), (-142.5, 0.0, 0.0), (55.4, 55.4, 55.4), 'wall_suit_build3',
  None, None),
 (
  5, 'modules', 'suit_walls', (-78.657, -284.069, 0.0), (165.5, 0.0, 0.0), (55.4, 55.4, 55.4), 'wall_suit_build1',
  None, None),
 (
  5, 'modules', 'suit_walls', (-132.292, -270.198, 0.0), (149.0, 0.0, 0.0), (55.4, 55.4, 55.4), 'wall_suit_build1',
  None, None),
 (
  5, 'modules', 'suit_walls', (-179.779, -241.665, 0.0), (134.0, 0.0, 0.0), (55.4, 55.4, 55.4), 'wall_suit_build1',
  None, None),
 (
  5, 'modules', 'suit_walls', (-218.263, -201.813, 0.0), (123.5, 0.0, 0.0), (55.4, 55.4, 55.4), 'wall_suit_build2',
  None, None),
 (
  5, 'modules', 'suit_walls', (-248.84, -155.616, 0.0), (114.5, 0.0, 0.0), (55.4, 55.4, 55.4), 'wall_suit_build2',
  None, None),
 (
  5, 'modules', 'suit_walls', (-271.814, -105.204, 0.0), (96.5, 0.0, 0.0), (55.4, 55.4, 55.4), 'wall_suit_build2',
  None, None),
 (
  4, 'modules', 'suit_landmark_legal', (-278.086, -50.161, 0.0), (87.5, 0.0, 0.0), (2.7, 2.7, 2.7), None, None,
  None),
 (
  5, 'modules', 'suit_walls', (-274.513, 31.661, 0.0), (81.5, 0.0, 0.0), (54.5, 54.5, 54.5), 'wall_suit_build4',
  None,
  None),
 (
  5, 'modules', 'suit_walls', (-266.458, 85.563, 0.0), (66.5, 0.0, 0.0), (54.5, 54.5, 54.5), 'wall_suit_build4',
  None,
  None),
 (
  5, 'modules', 'suit_walls', (-244.726, 135.543, 0.0), (54.5, 0.0, 0.0), (54.5, 54.5, 54.5), 'wall_suit_build4',
  None, None),
 (
  5, 'modules', 'suit_walls', (-213.078, 179.912, 0.0), (65.0, 0.0, 0.0), (54.5, 54.5, 54.5), 'wall_suit_build4',
  None, None),
 (
  5, 'modules', 'suit_walls', (-190.045, 229.306, 0.0), (68.0, 0.0, 0.0), (54.5, 54.5, 54.5), 'wall_suit_build5',
  None, None),
 (
  5, 'modules', 'suit_walls', (-169.629, 279.838, 0.0), (54.5, 0.0, 0.0), (54.5, 54.5, 54.5), 'wall_suit_build5',
  None, None),
 (
  5, 'modules', 'suit_walls', (-137.98, 324.207, 0.0), (12.5, 0.0, 0.0), (54.5, 54.5, 54.5), 'wall_suit_build5',
  None,
  None),
 (
  4, 'modules', 'suit_landmark_sales', (-86.515, 338.143, 0.0), (5.0, 0.0, 0.0), (2.8, 2.8, 2.8), None, None, None),
 (
  6, 'cogHQ', 'WaterTowerSimple', (110.0, -140.0, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0), None, None, None),
 (
  6, 'cogHQ', 'WaterTowerSimple', (83.4, -175.2, 0.0), (0.0, 0.0, 0.0), (0.8, 0.8, 0.8), None, None, None),
 (
  6, 'cogHQ', 'WaterTowerSimple', (51.0, 131.8, 0.15), (54.0, 0.0, 0.0), (2.0, 2.0, 2.0), None, None, None),
 (
  6, 'cogHQ', 'WaterTowerSimple', (86.812, 209.566, 0.15), (-25.5, 0.0, 0.0), (1.4, 1.4, 1.4), None, None, None),
 (
  6, 'cogHQ', 'WaterTowerSimple', (125.888, 94.562, 0.15), (13.5, 0.0, 0.0), (1.4, 1.4, 1.4), None, None, None),
 (
  6, 'cogHQ', 'WaterTowerSimple', (167.643, -205.228, 0.15), (293.0, 0.0, 0.0), (1.1, 1.1, 1.1), None, None, None),
 (
  6, 'cogHQ', 'SmokeStack_simple', (-67.683, 76.087, 0.15), (293.0, 0.0, 0.0), (1.1, 1.1, 1.1), None, None, None),
 (
  6, 'cogHQ', 'SmokeStack_simple', (-76.301, 48.529, 0.15), (293.0, 0.0, 0.0), (1.025, 1.025, 1.025), None, None,
  None),
 (
  6, 'cogHQ', 'SmokeStack_simple', (-90.453, 37.979, 0.15), (293.0, 0.0, 0.0), (0.875, 0.875, 0.875), None, None,
  None),
 (
  6, 'cogHQ', 'SmokeStack_simple', (-96.849, 7.107, 0.15), (293.0, 0.0, 0.0), (0.775, 0.775, 0.775), None, None,
  None),
 (
  9, 'cogHQ', 'woodCrateB', (91.145, -154.239, 0.3), (403.5, 0.0, 0.0), (2.575, 2.575, 2.575), None, None, None),
 (
  9, 'cogHQ', 'metal_crateB', (241.218, 62.596, 0.3), (325.5, 0.0, 0.0), (3.975, 3.975, 3.975), None, None, None),
 (
  9, 'cogHQ', 'FactoryGearB', (215.457, -170.329, 3.15), (339.0, 0.0, 0.0), (12.975, 12.975, 12.975), None, None,
  None),
 (
  9, 'cogHQ', 'woodCrateB', (223.817, 70.637, 0.15), (348.0, 0.0, 0.0), (2.875, 2.875, 2.875), None, None, None),
 (
  10, 'cashbotHQ', 'CBWoodCrate', (148.604, -193.93, 0.25), (336.0, 0.0, 0.0), (2.875, 2.875, 2.875), None, None,
  None),
 (
  10, 'cashbotHQ', 'CBMetalCrate', (187.686, -190.44, 0.25), (364.5, 0.0, 0.0), (2.875, 2.875, 2.875), None, None,
  None),
 (
  10, 'cashbotHQ', 'CBMetalCrate', (159.86, -175.457, 0.25), (360.0, 0.0, 0.0), (2.425, 2.425, 2.425), None, None,
  None),
 (
  10, 'cashbotHQ', 'DoubleGoldStack', (130.958, 188.263, 0.25), (378.0, 0.0, 0.0), (2.425, 2.425, 2.425), None, None,
  None),
 (
  10, 'cashbotHQ', 'DoubleCoinStack', (16.991, 243.846, 0.25), (367.5, 0.0, 0.0), (2.425, 2.425, 2.425), None, None,
  None),
 (
  10, 'cashbotHQ', 'MoneyStackPallet', (94.762, 80.424, 0.25), (378.0, 0.0, 0.0), (2.425, 2.425, 2.425), None, None,
  None),
 (
  10, 'cashbotHQ', 'CashBotSafe', (152.787, 77.659, 0.25), (369.0, 0.0, 0.0), (1.0, 1.0, 1.0), None, None, None),
 (
  10, 'cashbotHQ', 'CashBotSafe', (167.633, 76.774, 0.25), (352.5, 0.0, 0.0), (1.0, 1.0, 1.0), None, None, None),
 (
  10, 'cashbotHQ', 'MoneyStackPallet', (232.506, -16.91, 0.25), (334.5, 0.0, 0.0), (2.4, 2.4, 2.4), None, None,
  None),
 (
  10, 'cashbotHQ', 'shelf_A1', (262.684, 171.426, 0.25), (312.0, 0.0, 0.0), (2.4, 2.4, 2.4), None, None, None),
 (
  10, 'cashbotHQ', 'shelf_A1MoneyBags', (280.169, 125.461, 0.25), (289.5, 0.0, 0.0), (2.4, 2.4, 2.4), None, None,
  None),
 (
  10, 'cashbotHQ', 'VaultDoorCover', (168.327, 284.185, 0.25), (328.5, 0.0, 0.0), (2.4, 2.4, 2.4), None, None, None),
 (
  10, 'cashbotHQ', 'shelf_A1Gold', (130.324, 297.732, 0.25), (337.5, 0.0, 0.0), (2.4, 2.4, 2.4), None, None, None),
 (
  10, 'cashbotHQ', 'shelf_A1Gold', (94.847, 312.427, 0.25), (340.5, 0.0, 0.0), (2.4, 2.4, 2.4), None, None, None),
 (
  10, 'cashbotHQ', 'shelf_A1Gold', (56.096, 316.298, 0.25), (345.0, 0.0, 0.0), (2.4, 2.4, 2.4), None, None, None),
 (
  6, 'cogHQ', 'WaterTowerSimple', (-43.383, -149.335, 0.0), (28.5, 0.0, 0.0), (1.0, 1.0, 1.0), None, None, None),
 (
  6, 'cogHQ', 'WaterTowerSimple', (-84.082, -125.941, 0.0), (-12.0, 0.0, 0.0), (1.2, 1.2, 1.2), None, None, None),
 (
  9, 'cogHQ', 'woodCrateB', (-106.023, -12.046, 0.0), (3.0, 0.0, 0.0), (2.5, 2.5, 2.5), None, None, None),
 (
  9, 'cogHQ', 'CogDoorHandShake', (-233.571, 146.487, 0.0), (58.5, 0.0, 0.0), (2.5, 2.5, 2.5), None, None, None),
 (
  10, 'cashbotHQ', 'CBWoodCrate', (-112.604, -121.894, 0.15), (31.5, 0.0, 0.0), (2.5, 2.5, 2.5), None, None, None),
 (
  10, 'cashbotHQ', 'crates_C1', (-152.706, 242.107, 0.15), (52.5, 0.0, 0.0), (2.5, 2.5, 2.5), None, None, None),
 (
  10, 'cashbotHQ', 'GoldBarStack', (-170.256, 215.103, 0.15), (48.0, 0.0, 0.0), (2.5, 2.5, 2.5), None, None, None),
 (
  10, 'cashbotHQ', 'MoneyStackPallet', (-186.041, 186.343, 0.15), (48.0, 0.0, 0.0), (2.5, 2.5, 2.5), None, None,
  None),
 (
  10, 'cashbotHQ', 'shelf_A1Gold', (-249.959, 76.956, 0.15), (67.5, 0.0, 0.0), (2.5, 2.5, 2.5), None, None, None),
 (
  11, 'lawbotHQ', 'LB_paper_stacks', (-159.375, 13.489, 0.15), (45.0, 0.0, 0.0), (1.875, 1.875, 1.875), None, None,
  None),
 (
  9, 'cogHQ', 'old_sky', (0.0, 0.0, 378.952), (15.5, 0.0, 0.0), (1.475, 1.475, 1.475), None, None, None)]

class MoneybinTakeover:

    def __init__(self):
        base.camLens.setFov(60)
        self.modelList = []
        self.moneyBinTheme = None
        self.moneyBinTakeOver = None
        self.moneybin = None
        self.cogbin = None
        self.cogArea = None
        self.cogSky = None
        return

    def generate(self):

        def addModels(PROPS, parent, children=False, strong=None):
            for prop in PROPS:
                if children:
                    if prop[6]:
                        if prop[0] == 'custom':
                            model = loader.loadModel('custom/models/%s/%s.egg' % (prop[1], prop[2])).find('**/%s' % prop[6])
                        else:
                            model = loader.loadModel('phase_%s/models/%s/%s' % (prop[0], prop[1], prop[2])).find('**/%s' % prop[6])
                    elif prop[0] == 'custom':
                        model = loader.loadModel('custom/models/%s/%s.egg' % (prop[1], prop[2]))
                    else:
                        model = loader.loadModel('phase_%s/models/%s/%s' % (prop[0], prop[1], prop[2]))
                else:
                    if prop[0] == 'custom':
                        model = loader.loadModel('custom/models/%s/%s.egg' % (prop[1], prop[2]))
                    else:
                        model = loader.loadModel('phase_%s/models/%s/%s' % (prop[0], prop[1], prop[2]))
                model.reparentTo(parent)
                model.setPos(prop[3])
                model.setHpr(prop[4])
                model.setScale(prop[5])
                self.modelList.append(model)
                if prop[7]:
                    model.setColorScale(prop[7])
                if prop[8]:
                    texture = loader.loadTexture(prop[8])
                    model.setTexture(texture, 1)
                if strong:
                    model.flattenStrong()

        self.moneyBinTheme = loader.loadMusic('phase_14.5/audio/bgm/SB_hub.ogg')
        self.moneyBinTakeOver = loader.loadMusic('phase_14.5/audio/sfx/SB_Takeover.ogg')
        self.cogArea = render.attachNewNode('cogArea')
        self.cogArea.setZ(150)
        self.cogArea.hide()
        self.cogArea.setColorScale(1, 0.912, 0.863, 1)
        self.cogSky = loader.loadModel('phase_9/models/cogHQ/old_sky')
        self.cogSky.reparentTo(render)
        self.cogSky.setPosHprScale(0, 0, 378.952, 15.5, 0, 0, 1.475, 1.475, 1.475)
        self.cogSky.hide()
        self.modelList.append(self.cogSky)
        self.modelList.append(self.cogArea)
        addModels(PROPS, self.cogArea, children=True)
        self.setUpStreet()
        loader.loadDNAFile(base.cr.playGame.hood.dnaStore, 'phase_8/dna/storage_ODG.jazz')
        loader.loadDNAFile(base.cr.playGame.hood.dnaStore, 'phase_4/dna/storage.jazz')
        loader.loadDNAFile(base.cr.playGame.hood.dnaStore, 'phase_4/dna/storage_TT_sz.jazz')
        self.moneybin = loader.loadDNAFile(base.cr.playGame.hood.dnaStore, 'phase_14/dna/tt_dg_moneybin_area.jazz')
        self.moneybin = NodePath(self.moneybin)
        self.moneybin.setH(90)
        self.moneybin.reparentTo(render)
        self.modelList.append(self.moneybin)
        self.sky = loader.loadModel('phase_3.5/models/props/TT_sky')
        self.sky.setScale(2.42)
        self.sky.reparentTo(render)
        self.cogbin = loader.loadModel('phase_14/models/modules/cogbin')
        self.cogbin.reparentTo(render)
        self.cogbin.setPosHprScale(0.0, 2.16, 150, 0.0, 0.0, 0.0, 1.38, 1.38, 1.38)
        self.cogbin.hide()
        self.modelList.append(self.cogbin)
        groundTexture = loader.loadTexture('phase_9/maps/ground7.jpg')
        sidewalkTexture = loader.loadTexture('phase_9/maps/CementFloorx4Warm.jpg')
        self.robberbaron = ToontownAvatarUtils.createDistributedCog('rb', 0.0, -48.43, 16.999, 0.0, 0.0, 0.0, level=12)
        streetTrack = Parallel()
        for street in ['street_80x40_sidewalk', 'street_80x40_curb', 'street_80x40_street', 'street_25x40_street',
         'street_25x40_sidewalk', 'street_25x40_curb']:
            for node in render.findAllMatches('**/%s' % street):
                streetTrack.append(Func(node.setTexture, groundTexture, 1))
                streetTrack.append(Func(node.setTexture, sidewalkTexture, 1))
                streetTrack.append(Func(node.setTexture, sidewalkTexture, 1))

        moneybinTrack = Parallel(self.moneybin.find('**/moneybin1').colorScaleInterval(4.2, (0,
                                                                                             0,
                                                                                             0,
                                                                                             1)), self.moneybin.find('**/moneybin1').colorScaleInterval(4.2, (0,
                                                                                                                                                              0,
                                                                                                                                                              0,
                                                                                                                                                              1)), Sequence(Wait(1.75), Parallel(Sequence(Parallel(self.moneybin.find('**/moneybin1').scaleInterval(3.75, (1,
                                                                                                                                                                                                                                                                           1,
                                                                                                                                                                                                                                                                           0.001)), self.moneybin.find('**/flowers').scaleInterval(3.75, (1,
                                                                                                                                                                                                                                                                                                                                          1,
                                                                                                                                                                                                                                                                                                                                          0.001)), self.moneybin.find('**/trees').scaleInterval(3.75, (1,
                                                                                                                                                                                                                                                                                                                                                                                                       1,
                                                                                                                                                                                                                                                                                                                                                                                                       0.001)), self.moneybin.find('**/tag_arena_wall').scaleInterval(3.75, (1,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                             1,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                             0.001)), self.moneybin.find('**/out_arena_trees_1').scaleInterval(3.75, (1,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      1,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      0.001)), self.moneybin.find('**/out_arena_trees_2').scaleInterval(3.75, (1,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               1,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               0.001))), Func(self.moneybin.find('**/moneybin1').removeNode), Func(self.moneybin.find('**/flowers').removeNode), Func(self.moneybin.find('**/trees').removeNode), Func(self.moneybin.find('**/tag_arena_wall').removeNode), Func(self.moneybin.find('**/out_arena_trees_1').removeNode), Func(self.moneybin.find('**/out_arena_trees_2').removeNode)))))
        cogBinTrack = Parallel(Func(self.cogbin.show), Func(self.cogArea.show), Func(self.sky.removeNode), Func(self.cogSky.show), Func(self.songRateChange, self.moneyBinTheme), Sequence(Parallel(self.cogbin.posInterval(5.0, (0.0,
                                                                                                                                                                                                                                  2.16,
                                                                                                                                                                                                                                  16.3)), self.cogArea.posInterval(5.0, (0.0,
                                                                                                                                                                                                                                                                         2.16,
                                                                                                                                                                                                                                                                         0.0))), Parallel(Sequence(LerpScaleInterval(self.cogbin, 0.45, (1.38,
                                                                                                                                                                                                                                                                                                                                         1.38,
                                                                                                                                                                                                                                                                                                                                         1.1), blendType='easeInOut'), LerpScaleInterval(self.cogbin, 0.6, (1.38,
                                                                                                                                                                                                                                                                                                                                                                                                            1.38,
                                                                                                                                                                                                                                                                                                                                                                                                            1.6), blendType='easeInOut'), LerpScaleInterval(self.cogbin, 0.7, (1.38,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                               1.38,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                               1.28), blendType='easeInOut'), LerpScaleInterval(self.cogbin, 0.75, (1.38,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    1.38,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    1.38), blendType='easeInOut')), Sequence(LerpScaleInterval(self.cogArea, 0.45, (1.0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    1.0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    0.7), blendType='easeInOut'), LerpScaleInterval(self.cogArea, 0.6, (1.0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        1.0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        1.3), blendType='easeInOut'), LerpScaleInterval(self.cogArea, 0.7, (1.0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            1.0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            0.9), blendType='easeInOut'), LerpScaleInterval(self.cogArea, 0.75, (1.0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 1.0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 1.0), blendType='easeInOut')))))
        self.cameraTrack = Sequence(Func(self.robberbaron.setPosHpr, 0.0, -48.43, 16.999, 0.0, 0.0, 0.0), Func(base.camera.setPosHpr, -90.37, -95.11, 20.3, -154, 0.0, 0.0), Parallel(Sequence(Wait(1.0), self.robberbaron.beginSupaFlyMove(VBase3(0.0, -48.43, 16.999), 1, 'flyIn', walkAfterLanding=False)), LerpPosHprInterval(base.camera, 8.0, (-34.39,
                                                                                                                                                                                                                                                                                                                                                     -28.71,
                                                                                                                                                                                                                                                                                                                                                     25.038), (-130,
                                                                                                                                                                                                                                                                                                                                                               -0.6,
                                                                                                                                                                                                                                                                                                                                                               0.0), blendType='easeInOut')), Func(base.camera.setPosHpr, 27.945, -83.46, 17.402, 34.5, 8.24, 4.5), Func(self.robberbaron.loop, 'walk'), self.robberbaron.posHprInterval(2.5, (0.0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               -27.43,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               21.398), (0.0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         0.0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         0.0)), self.robberbaron.posHprInterval(1.5, (0.0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      -9,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      21.398), (0.0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                0.0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                0.0)), Func(base.camera.setPosHpr, 2.4331, -238.5, 20.352, -1.7, 11.8, 9.0), Func(self.robberbaron.delete), Wait(5.0), Func(base.localAvatar.brickLay, 'cog'), Func(self.moneybin.find('**/ground').setTexture, groundTexture, 1), Func(self.moneybin.find('**/moneybin_hill').setTexture, groundTexture, 1), Func(self.moneybin.find('**/ground').setColor, 1, 1, 1, 1), Func(self.moneybin.find('**/moneybin_hill').setColor, 1, 1, 1, 1), Func(self.moneyBinTheme.stop), Func(self.moneyBinTakeOver.play), Func(base.camera.setPosHpr, 131.27, -382.0, 78.261, 19.1, -5.1, 0.0), streetTrack)
        self.buildingTrack = Sequence(Wait(12.0), Parallel(moneybinTrack, cogBinTrack, Sequence(Wait(8.0), Func(base.transitions.fadeOut, 2.0), Wait(2.0), Func(self.cleanupScene))))
        self.animation = Parallel(Func(self.moneyBinTheme.play), self.cameraTrack, self.buildingTrack)
        self.animation.start()
        return

    def songRateChange(self, song):
        rateTrack = Sequence()
        playRate = 1.0
        for rate in xrange(0, 101):
            rateTrack.append(Func(song.setPlayRate, playRate))
            rateTrack.append(Wait(0.05))
            playRate -= 0.01

        rateTrack.append(Func(song.stop))
        rateTrack.start()

    def setUpStreet(self):
        for dept in ['sales', 'money', 'corp', 'legal']:
            for spot in render.findAllMatches('**/suit_landmark_new_%s_door_origin' % dept):
                elevator = loader.loadModel('phase_4/models/modules/elevator')
                elevator.reparentTo(spot)
                randomFloor = random.randint(3, 5)
                hideList = 5
                for light in range(1, 6):
                    elevator.find('**/floor_light_%s' % light).setColor(0.5, 0.5, 0.5, 1)
                    if hideList != randomFloor:
                        elevator.find('**/floor_light_%s' % hideList).hide()
                        hideList = hideList - 1

                sign = loader.loadModel('phase_5/models/modules/suit_sign')
                sign.reparentTo(spot)
                sign.setPos(0, -0.1, 12.5)
                sign.setScale(5)

            for spot in render.findAllMatches('**/suit_landmark_money2_door_origin'):
                elevator = loader.loadModel('phase_4/models/modules/elevator')
                elevator.reparentTo(spot)
                randomFloor = random.randint(2, 5)
                hideList = 5
                for light in range(1, 6):
                    elevator.find('**/floor_light_%s' % light).setColor(0.5, 0.5, 0.5, 1)
                    if hideList != randomFloor:
                        elevator.find('**/floor_light_%s' % hideList).hide()
                        hideList = hideList - 1

                sign = loader.loadModel('phase_5/models/modules/suit_sign')
                sign.reparentTo(spot)
                sign.setPos(0, -0.1, 11.5)
                sign.setScale(5)

    def cleanupScene(self):
        for model in self.modelList:
            model.removeNode()
            del model