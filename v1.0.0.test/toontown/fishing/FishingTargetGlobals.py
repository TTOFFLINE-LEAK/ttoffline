from toontown.toonbase import ToontownGlobals
OFF = 0
MOVING = 1
StepTime = 5.0
MinimumHunger = 1.0
NUM_TARGETS_INDEX = 0
POS_START_INDEX = 1
POS_END_INDEX = 4
RADIUS_INDEX = 4
WATER_LEVEL_INDEX = 5
__targetInfoDict = {ToontownGlobals.ToontownCentral: (2, -81, 31, -4.8, 14, -1.4), 
   ToontownGlobals.SillyStreet: (
                               2,
                               20,
                               -664,
                               -1.4,
                               14,
                               -1.8379999999999999), 
   ToontownGlobals.LoopyLane: (
                             2,
                             -234,
                             175,
                             -1.4,
                             14,
                             -1.8619999999999999), 
   ToontownGlobals.PunchlinePlace: (
                                  2,
                                  529,
                                  -70,
                                  -1.4,
                                  13,
                                  -1.886), 
   ToontownGlobals.DonaldsDock: (
                               2,
                               -17,
                               130,
                               1.73,
                               15,
                               -1.8850000000000002), 
   ToontownGlobals.BarnacleBoulevard: (
                                     2,
                                     381,
                                     -350,
                                     -2,
                                     14,
                                     -2.482), 
   ToontownGlobals.SeaweedStreet: (
                                 2,
                                 -395,
                                 -226,
                                 -2,
                                 14,
                                 -2.482), 
   ToontownGlobals.LighthouseLane: (
                                  2,
                                  350,
                                  100,
                                  -2,
                                  14,
                                  -2.482), 
   ToontownGlobals.DaisyGardens: (
                                2,
                                50,
                                47,
                                -1.48,
                                13,
                                -1.825), 
   ToontownGlobals.ElmStreet: (
                             2,
                             149,
                             44,
                             -1.43,
                             13,
                             -2.048), 
   ToontownGlobals.MapleStreet: (
                               2,
                               176,
                               100,
                               -1.43,
                               13,
                               -2.048), 
   ToontownGlobals.OakStreet: (
                             2,
                             134,
                             -70.5,
                             -1.5,
                             13,
                             -1.877), 
   ToontownGlobals.MinniesMelodyland: (
                                     2,
                                     -0.2,
                                     -20.2,
                                     -14.65,
                                     14,
                                     -2.6500000000000004), 
   ToontownGlobals.AltoAvenue: (
                              2,
                              -580,
                              -90,
                              -0.87,
                              14,
                              -2.714), 
   ToontownGlobals.BaritoneBoulevard: (
                                     2,
                                     -214,
                                     250,
                                     -0.87,
                                     14,
                                     -2.714), 
   ToontownGlobals.TenorTerrace: (
                                2,
                                715,
                                -15,
                                -0.87,
                                14,
                                -2.714), 
   ToontownGlobals.TheBrrrgh: (2, -58, -26, 1.7, 10, -0.8), 
   ToontownGlobals.WalrusWay: (
                             2,
                             460,
                             29,
                             -2,
                             13,
                             -2.4), 
   ToontownGlobals.SleetStreet: (
                               2,
                               340,
                               480,
                               -2,
                               13,
                               -2.4), 
   ToontownGlobals.PolarPlace: (
                              2,
                              45.5,
                              90.86,
                              -2,
                              13,
                              -2.4), 
   ToontownGlobals.DonaldsDreamland: (
                                    2,
                                    159,
                                    0.2,
                                    -17.1,
                                    14,
                                    -2.5000000000000018), 
   ToontownGlobals.LullabyLane: (
                               2,
                               118,
                               -185,
                               -2.1,
                               14,
                               -2.478), 
   ToontownGlobals.PajamaPlace: (
                               2,
                               241,
                               -348,
                               -2.1,
                               14,
                               -2.478), 
   ToontownGlobals.MyEstate: (3, 30, -126, -0.3, 16, -0.83)}

def getNumTargets(zone):
    info = __targetInfoDict.get(zone)
    if info:
        return info[NUM_TARGETS_INDEX]
    return 2


def getTargetCenter(zone):
    info = __targetInfoDict.get(zone)
    if info:
        return info[POS_START_INDEX:POS_END_INDEX]
    return (0, 0, 0)


def getTargetRadius(zone):
    info = __targetInfoDict.get(zone)
    if info:
        return info[RADIUS_INDEX]
    return 10


def getWaterLevel(zone):
    info = __targetInfoDict.get(zone)
    if info:
        return info[WATER_LEVEL_INDEX]
    return 0