import TTLocalizer
from otp.otpbase.OTPGlobals import *
from direct.showbase.PythonUtil import Enum, invertDict
from panda3d.core import BitMask32, Vec4
MapHotkeyOn = 'alt'
MapHotkeyOff = 'alt-up'
MapHotkey = 'alt'
AccountDatabaseChannelId = 4008
ToonDatabaseChannelId = 4021
DoodleDatabaseChannelId = 4023
DefaultDatabaseChannelId = AccountDatabaseChannelId
DatabaseIdFromClassName = {'Account': AccountDatabaseChannelId}
CogHQCameraFov = 60.0
BossBattleCameraFov = 72.0
MakeAToonCameraFov = 52.0
MakeAToonCameraFovRetro = 35.0
CeilingBitmask = BitMask32(256)
FloorEventBitmask = BitMask32(16)
PieBitmask = BitMask32(256)
PetBitmask = BitMask32(8)
CatchGameBitmask = BitMask32(16)
CashbotBossObjectBitmask = BitMask32(16)
FurnitureSideBitmask = BitMask32(32)
FurnitureTopBitmask = BitMask32(64)
FurnitureDragBitmask = BitMask32(128)
PetLookatPetBitmask = BitMask32(256)
PetLookatNonPetBitmask = BitMask32(512)
BanquetTableBitmask = BitMask32(1024)
FullPies = 65535
CogHQCameraFar = 1500.0
CogHQCameraNear = 1.0
CashbotHQCameraFar = 2000.0
CashbotHQCameraNear = 1.0
LawbotHQCameraFar = 3000.0
LawbotHQCameraNear = 1.0
BossbotHQCameraFar = 3000.0
BossbotHQCameraNear = 1.0
SpeedwayCameraFar = 8000.0
SpeedwayCameraNear = 1.0
SpecialHoodCameraFar = 8000.0
SpecialHoodCameraNear = 1.0
ToontownCentralBetaCameraFar = 2000.0
ToontownCentralBetaCameraNear = 1.0
DaisyGardensBetaCameraFar = 2000.0
DaisyGardensBetaCameraNear = 1.0
MaxMailboxContents = 30
MaxHouseItems = 45
MaxAccessories = 50
ExtraDeletedItems = 5
DeletedItemLifetime = 10080
CatalogNumWeeksPerSeries = 13
CatalogNumWeeks = 78
PetFloorCollPriority = 5
PetPanelProximityPriority = 6
P_NoTrunk = -28
P_AlreadyOwnBiggerCloset = -27
P_ItemAlreadyRented = -26
P_OnAwardOrderListFull = -25
P_AwardMailboxFull = -24
P_ItemInPetTricks = -23
P_ItemInMyPhrases = -22
P_ItemOnAwardOrder = -21
P_ItemInAwardMailbox = -20
P_ItemAlreadyWorn = -19
P_ItemInCloset = -18
P_ItemOnGiftOrder = -17
P_ItemOnOrder = -16
P_ItemInMailbox = -15
P_PartyNotFound = 14
P_WillNotFit = -13
P_NotAGift = -12
P_OnOrderListFull = -11
P_MailboxFull = -10
P_NoPurchaseMethod = -9
P_ReachedPurchaseLimit = -8
P_NoRoomForItem = -7
P_NotShopping = -6
P_NotAtMailbox = -5
P_NotInCatalog = -4
P_NotEnoughMoney = -3
P_InvalidIndex = -2
P_UserCancelled = -1
P_ItemAvailable = 1
P_ItemOnOrder = 2
P_ItemUnneeded = 3
GIFT_user = 0
GIFT_admin = 1
GIFT_RAT = 2
GIFT_mobile = 3
GIFT_cogs = 4
GIFT_partyrefund = 5
FM_InvalidItem = -7
FM_NondeletableItem = -6
FM_InvalidIndex = -5
FM_NotOwner = -4
FM_NotDirector = -3
FM_RoomFull = -2
FM_HouseFull = -1
FM_MovedItem = 1
FM_SwappedItem = 2
FM_DeletedItem = 3
FM_RecoveredItem = 4
SPDonaldsBoat = 3
SPMinniesPiano = 4
CEVirtual = 14
MaxHpLimit = 137
MaxCarryLimit = 80
MaxQuestCarryLimit = 4
GravityValue = 32.174
MaxCogSuitLevel = 49
CogSuitHPLevels = (14,
 19,
 29,
 39,
 49)
setInterfaceFont(TTLocalizer.InterfaceFont)
setSignFont(TTLocalizer.SignFont)
from toontown.toontowngui import TTDialog
setDialogClasses(TTDialog.TTDialog, TTDialog.TTGlobalDialog)
ToonFont = None
BuildingNametagFont = None
MinnieFont = None
SuitFont = None

def getToonFont():
    global ToonFont
    if ToonFont == None:
        ToonFont = loader.loadFont(TTLocalizer.ToonFont, lineHeight=1.0)
    return ToonFont


def getBuildingNametagFont():
    global BuildingNametagFont
    if BuildingNametagFont == None:
        BuildingNametagFont = loader.loadFont(TTLocalizer.BuildingNametagFont)
    return BuildingNametagFont


def getMinnieFont():
    global MinnieFont
    if MinnieFont == None:
        MinnieFont = loader.loadFont(TTLocalizer.MinnieFont)
    return MinnieFont


def getSuitFont():
    global SuitFont
    if SuitFont == None:
        SuitFont = loader.loadFont(TTLocalizer.SuitFont, pixelsPerUnit=40, spaceAdvance=0.25, lineHeight=1.0)
    return SuitFont


DonaldsDock = 1000
ToontownCentral = 2000
TheBrrrgh = 3000
MinniesMelodyland = 4000
DaisyGardens = 5000
OutdoorZone = 6000
FunnyFarm = 7000
GoofySpeedway = 8000
DonaldsDreamland = 9000
BarnacleBoulevard = 1100
SeaweedStreet = 1200
LighthouseLane = 1300
SillyStreet = 2100
LoopyLane = 2200
PunchlinePlace = 2300
WalrusWay = 3100
SleetStreet = 3200
PolarPlace = 3300
AltoAvenue = 4100
BaritoneBoulevard = 4200
TenorTerrace = 4300
ElmStreet = 5100
MapleStreet = 5200
OakStreet = 5300
LullabyLane = 9100
PajamaPlace = 9200
ToonHall = 2513
Kongdominium = 4656
Pizzeria = 19504
ToonyLab = 19505
PrivateServerCafe = 19513
GyrosLab = 22634
WelcomeValleyToken = 0
BossbotHQ = 10000
BossbotLobby = 10100
BossbotCountryClubIntA = 10500
BossbotCountryClubIntB = 10600
BossbotCountryClubIntC = 10700
SellbotHQ = 11000
SellbotLobby = 11100
SellbotFactoryExt = 11200
SellbotFactoryInt = 11500
CashbotHQ = 12000
CashbotLobby = 12100
CashbotMintIntA = 12500
CashbotMintIntB = 12600
CashbotMintIntC = 12700
LawbotHQ = 13000
LawbotLobby = 13100
LawbotOfficeExt = 13200
LawbotOfficeInt = 13300
LawbotStageIntA = 13300
LawbotStageIntB = 13400
LawbotStageIntC = 13500
LawbotStageIntD = 13600
Tutorial = 15000
MyEstate = 16000
GolfZone = 17000
PartyHood = 18000
ToontownOutskirts = 19000
TutorialTerrace = 19100
TutorialInterior = 19602
TutorialHood = 20000
ToontownCentralBeta = 21000
DaisyGardensBeta = 22000
OakStreetBeta = 22100
HoodsAlwaysVisited = [17000, 18000, 19000, 21000, 22000]
WelcomeValleyBegin = 30000
WelcomeValleyEnd = 61000
DynamicZonesBegin = 61000
DynamicZonesEnd = 1048576
HoodHierarchy = {ToontownCentral: (SillyStreet, LoopyLane, PunchlinePlace), DonaldsDock: (
               BarnacleBoulevard, SeaweedStreet, LighthouseLane), 
   TheBrrrgh: (
             WalrusWay, SleetStreet, PolarPlace), 
   MinniesMelodyland: (
                     AltoAvenue, BaritoneBoulevard, TenorTerrace), 
   DaisyGardens: (
                ElmStreet, MapleStreet, OakStreet), 
   DonaldsDreamland: (
                    LullabyLane, PajamaPlace), 
   GoofySpeedway: (), 
   ToontownOutskirts: (
                     TutorialTerrace,), 
   ToontownCentralBeta: (), 
   DaisyGardensBeta: (
                    OakStreetBeta,)}
cogDept2index = {'c': 0, 'l': 1, 
   'm': 2, 
   's': 3}
cogIndex2dept = invertDict(cogDept2index)
HQToSafezone = {SellbotHQ: DaisyGardens, CashbotHQ: DonaldsDreamland, 
   LawbotHQ: TheBrrrgh, 
   BossbotHQ: DonaldsDock}
CogDeptNames = [TTLocalizer.Bossbot,
 TTLocalizer.Lawbot,
 TTLocalizer.Cashbot,
 TTLocalizer.Sellbot]

def cogHQZoneId2deptIndex(zone):
    if zone >= 13000 and zone <= 13999:
        return 1
    else:
        if zone >= 12000:
            return 2
        if zone >= 11000:
            return 3
        return 0


def cogHQZoneId2dept(zone):
    return cogIndex2dept[cogHQZoneId2deptIndex(zone)]


def dept2cogHQ(dept):
    dept2hq = {'c': BossbotHQ, 'l': LawbotHQ, 
       'm': CashbotHQ, 
       's': SellbotHQ}
    return dept2hq[dept]


MockupFactoryId = 0
MintNumFloors = {CashbotMintIntA: 20, CashbotMintIntB: 20, 
   CashbotMintIntC: 20}
CashbotMintCogLevel = 10
CashbotMintSkelecogLevel = 11
CashbotMintBossLevel = 12
MintNumBattles = {CashbotMintIntA: 4, CashbotMintIntB: 6, 
   CashbotMintIntC: 8}
MintCogBuckRewards = {CashbotMintIntA: 8, CashbotMintIntB: 14, 
   CashbotMintIntC: 20}
MintNumRooms = {CashbotMintIntA: 2 * (6, ) + 5 * (7, ) + 5 * (8, ) + 5 * (9, ) + 3 * (10, ), CashbotMintIntB: 3 * (8, ) + 6 * (9, ) + 6 * (10, ) + 5 * (11, ), 
   CashbotMintIntC: 4 * (10, ) + 10 * (11, ) + 6 * (12, )}
BossbotCountryClubCogLevel = 11
BossbotCountryClubSkelecogLevel = 12
BossbotCountryClubBossLevel = 12
CountryClubNumRooms = {BossbotCountryClubIntA: (4, ), BossbotCountryClubIntB: 3 * (8, ) + 6 * (9, ) + 6 * (10, ) + 5 * (11, ), 
   BossbotCountryClubIntC: 4 * (10, ) + 10 * (11, ) + 6 * (12, )}
CountryClubNumBattles = {BossbotCountryClubIntA: 3, BossbotCountryClubIntB: 2, 
   BossbotCountryClubIntC: 3}
CountryClubCogBuckRewards = {BossbotCountryClubIntA: 8, BossbotCountryClubIntB: 14, 
   BossbotCountryClubIntC: 20}
LawbotStageCogLevel = 10
LawbotStageSkelecogLevel = 11
LawbotStageBossLevel = 12
StageNumBattles = {LawbotStageIntA: 0, LawbotStageIntB: 0, 
   LawbotStageIntC: 0, 
   LawbotStageIntD: 0}
StageNoticeRewards = {LawbotStageIntA: 75, LawbotStageIntB: 150, 
   LawbotStageIntC: 225, 
   LawbotStageIntD: 300}
StageNumRooms = {LawbotStageIntA: 2 * (6, ) + 5 * (7, ) + 5 * (8, ) + 5 * (9, ) + 3 * (10, ), LawbotStageIntB: 3 * (8, ) + 6 * (9, ) + 6 * (10, ) + 5 * (11, ), 
   LawbotStageIntC: 4 * (10, ) + 10 * (11, ) + 6 * (12, ), 
   LawbotStageIntD: 4 * (10, ) + 10 * (11, ) + 6 * (12, )}
FT_FullSuit = 'fullSuit'
FT_Leg = 'leg'
FT_Arm = 'arm'
FT_Torso = 'torso'
factoryId2factoryType = {MockupFactoryId: FT_FullSuit, SellbotFactoryInt: FT_FullSuit, 
   LawbotOfficeInt: FT_FullSuit}
StreetNames = TTLocalizer.GlobalStreetNames
StreetBranchZones = StreetNames.keys()
Hoods = (DonaldsDock,
 ToontownCentral,
 TheBrrrgh,
 MinniesMelodyland,
 DaisyGardens,
 OutdoorZone,
 FunnyFarm,
 GoofySpeedway,
 DonaldsDreamland,
 BossbotHQ,
 SellbotHQ,
 CashbotHQ,
 LawbotHQ,
 GolfZone,
 ToontownOutskirts,
 ToontownCentralBeta,
 DaisyGardensBeta)
HoodsForTeleportAll = (DonaldsDock,
 ToontownCentral,
 TheBrrrgh,
 MinniesMelodyland,
 DaisyGardens,
 OutdoorZone,
 GoofySpeedway,
 DonaldsDreamland,
 BossbotHQ,
 SellbotHQ,
 CashbotHQ,
 LawbotHQ,
 GolfZone,
 ToontownOutskirts,
 ToontownCentralBeta,
 DaisyGardensBeta)
HoodsWithMinigames = (DonaldsDock,
 ToontownCentral,
 TheBrrrgh,
 MinniesMelodyland,
 DaisyGardens,
 DonaldsDreamland,
 ToontownCentralBeta,
 DaisyGardensBeta)
NoPreviousGameId = 0
RaceGameId = 1
CannonGameId = 2
TagGameId = 3
PatternGameId = 4
RingGameId = 5
MazeGameId = 6
TugOfWarGameId = 7
CatchGameId = 8
DivingGameId = 9
TargetGameId = 10
PairingGameId = 11
VineGameId = 12
IceGameId = 13
CogThiefGameId = 14
TwoDGameId = 15
PhotoGameId = 16
TravelGameId = 100
MinigameNames = {'race': RaceGameId, 'cannon': CannonGameId, 
   'tag': TagGameId, 
   'pattern': PatternGameId, 
   'minnie': PatternGameId, 
   'match': PatternGameId, 
   'matching': PatternGameId, 
   'ring': RingGameId, 
   'maze': MazeGameId, 
   'tug': TugOfWarGameId, 
   'catch': CatchGameId, 
   'diving': DivingGameId, 
   'target': TargetGameId, 
   'pairing': PairingGameId, 
   'vine': VineGameId, 
   'ice': IceGameId, 
   'thief': CogThiefGameId, 
   '2d': TwoDGameId, 
   'photo': PhotoGameId, 
   'travel': TravelGameId}
MinigameTemplateId = -1
MinigameIDs = (RaceGameId,
 CannonGameId,
 TagGameId,
 PatternGameId,
 RingGameId,
 MazeGameId,
 TugOfWarGameId,
 CatchGameId,
 DivingGameId,
 TargetGameId,
 PairingGameId,
 VineGameId,
 IceGameId,
 CogThiefGameId,
 TwoDGameId,
 PhotoGameId,
 TravelGameId)
MinigamePlayerMatrix = {1: (CannonGameId,
     RingGameId,
     MazeGameId,
     TugOfWarGameId,
     CatchGameId,
     DivingGameId,
     TargetGameId,
     PairingGameId,
     VineGameId,
     CogThiefGameId,
     TwoDGameId), 
   2: (
     CannonGameId,
     PatternGameId,
     RingGameId,
     TagGameId,
     MazeGameId,
     TugOfWarGameId,
     CatchGameId,
     DivingGameId,
     TargetGameId,
     PairingGameId,
     VineGameId,
     IceGameId,
     CogThiefGameId,
     TwoDGameId), 
   3: (
     CannonGameId,
     PatternGameId,
     RingGameId,
     TagGameId,
     RaceGameId,
     MazeGameId,
     TugOfWarGameId,
     CatchGameId,
     DivingGameId,
     TargetGameId,
     PairingGameId,
     VineGameId,
     IceGameId,
     CogThiefGameId,
     TwoDGameId), 
   4: (
     CannonGameId,
     PatternGameId,
     RingGameId,
     TagGameId,
     RaceGameId,
     MazeGameId,
     TugOfWarGameId,
     CatchGameId,
     DivingGameId,
     TargetGameId,
     PairingGameId,
     VineGameId,
     IceGameId,
     CogThiefGameId,
     TwoDGameId)}
MinigameReleaseDates = {IceGameId: (2008, 8, 5), PhotoGameId: (2008, 8, 13), 
   TwoDGameId: (2008, 8, 20), 
   CogThiefGameId: (2008, 8, 27)}
KeyboardTimeout = 300
phaseMap = {Tutorial: 4, ToontownCentral: 4, 
   MyEstate: 5.5, 
   DonaldsDock: 6, 
   MinniesMelodyland: 6, 
   GoofySpeedway: 6, 
   TheBrrrgh: 8, 
   DaisyGardens: 8, 
   FunnyFarm: 8, 
   DonaldsDreamland: 8, 
   OutdoorZone: 8, 
   BossbotHQ: 12, 
   SellbotHQ: 9, 
   CashbotHQ: 10, 
   LawbotHQ: 11, 
   GolfZone: 8, 
   PartyHood: 13, 
   ToontownOutskirts: 14, 
   ToontownCentralBeta: 14, 
   DaisyGardensBeta: 14}
streetPhaseMap = {ToontownCentral: 5, DonaldsDock: 6, 
   MinniesMelodyland: 6, 
   GoofySpeedway: 6, 
   TheBrrrgh: 8, 
   DaisyGardens: 8, 
   FunnyFarm: 8, 
   DonaldsDreamland: 8, 
   OutdoorZone: 8, 
   BossbotHQ: 12, 
   SellbotHQ: 9, 
   CashbotHQ: 10, 
   LawbotHQ: 11, 
   PartyHood: 13, 
   ToontownOutskirts: 14, 
   ToontownCentralBeta: 14, 
   DaisyGardensBeta: 14}
dnaMap = {Tutorial: 'toontown_central', ToontownCentral: 'toontown_central', 
   DonaldsDock: 'donalds_dock', 
   MinniesMelodyland: 'minnies_melody_land', 
   GoofySpeedway: 'goofy_speedway', 
   TheBrrrgh: 'the_burrrgh', 
   DaisyGardens: 'daisys_garden', 
   FunnyFarm: 'not done yet', 
   DonaldsDreamland: 'donalds_dreamland', 
   OutdoorZone: 'outdoor_zone', 
   BossbotHQ: 'cog_hq_bossbot', 
   SellbotHQ: 'cog_hq_sellbot', 
   CashbotHQ: 'cog_hq_cashbot', 
   LawbotHQ: 'cog_hq_lawbot', 
   GolfZone: 'golf_zone', 
   ToontownOutskirts: 'special_hood', 
   ToontownCentralBeta: 'toontown_central_beta', 
   DaisyGardensBeta: 'daisys_garden_beta'}
hoodNameMap = {DonaldsDock: TTLocalizer.DonaldsDock, ToontownCentral: TTLocalizer.ToontownCentral, 
   TheBrrrgh: TTLocalizer.TheBrrrgh, 
   MinniesMelodyland: TTLocalizer.MinniesMelodyland, 
   DaisyGardens: TTLocalizer.DaisyGardens, 
   OutdoorZone: TTLocalizer.OutdoorZone, 
   FunnyFarm: TTLocalizer.FunnyFarm, 
   GoofySpeedway: TTLocalizer.GoofySpeedway, 
   DonaldsDreamland: TTLocalizer.DonaldsDreamland, 
   BossbotHQ: TTLocalizer.BossbotHQ, 
   SellbotHQ: TTLocalizer.SellbotHQ, 
   CashbotHQ: TTLocalizer.CashbotHQ, 
   LawbotHQ: TTLocalizer.LawbotHQ, 
   Tutorial: TTLocalizer.Tutorial, 
   MyEstate: TTLocalizer.MyEstate, 
   GolfZone: TTLocalizer.GolfZone, 
   PartyHood: TTLocalizer.PartyHood, 
   ToontownOutskirts: TTLocalizer.SpecialHood, 
   ToontownCentralBeta: TTLocalizer.ToontownCentralBeta, 
   DaisyGardensBeta: TTLocalizer.DaisyGardensBeta}
safeZoneCountMap = {MyEstate: 8, Tutorial: 6, 
   ToontownCentral: 6, 
   DonaldsDock: 10, 
   MinniesMelodyland: 5, 
   GoofySpeedway: 500, 
   TheBrrrgh: 8, 
   DaisyGardens: 9, 
   FunnyFarm: 500, 
   DonaldsDreamland: 5, 
   OutdoorZone: 500, 
   GolfZone: 500, 
   PartyHood: 500, 
   ToontownOutskirts: 500, 
   ToontownCentralBeta: 500, 
   DaisyGardensBeta: 500}
townCountMap = {MyEstate: 8, Tutorial: 40, 
   ToontownCentral: 37, 
   DonaldsDock: 40, 
   MinniesMelodyland: 40, 
   GoofySpeedway: 40, 
   TheBrrrgh: 40, 
   DaisyGardens: 40, 
   FunnyFarm: 40, 
   DonaldsDreamland: 40, 
   OutdoorZone: 40, 
   PartyHood: 20, 
   ToontownOutskirts: 40, 
   ToontownCentralBeta: 40, 
   DaisyGardensBeta: 40}
hoodCountMap = {MyEstate: 2, Tutorial: 2, 
   ToontownCentral: 2, 
   DonaldsDock: 2, 
   MinniesMelodyland: 2, 
   GoofySpeedway: 2, 
   TheBrrrgh: 2, 
   DaisyGardens: 2, 
   FunnyFarm: 2, 
   DonaldsDreamland: 2, 
   OutdoorZone: 2, 
   BossbotHQ: 2, 
   SellbotHQ: 43, 
   CashbotHQ: 2, 
   LawbotHQ: 2, 
   GolfZone: 2, 
   PartyHood: 2, 
   ToontownOutskirts: 2, 
   ToontownCentralBeta: 2, 
   DaisyGardensBeta: 2}
TrophyStarLevels = (10, 20, 30, 50, 75, 100)
TrophyStarColors = (Vec4(0.9, 0.6, 0.2, 1),
 Vec4(0.9, 0.6, 0.2, 1),
 Vec4(0.8, 0.8, 0.8, 1),
 Vec4(0.8, 0.8, 0.8, 1),
 Vec4(1, 1, 0, 1),
 Vec4(1, 1, 0, 1))
MickeySpeed = 5.0
VampireMickeySpeed = 1.15
MinnieSpeed = 3.2
WitchMinnieSpeed = 1.8
DonaldSpeed = 3.68
FrankenDonaldSpeed = 0.9
DaisySpeed = 2.3
GoofySpeed = 5.2
SuperGoofySpeed = 1.6
PlutoSpeed = 5.5
WesternPlutoSpeed = 3.2
ChipSpeed = 3
DaleSpeed = 3.5
DaleOrbitDistance = 3
SuitWalkSpeed = 4.8
PieCodeBossCog = 1
PieCodeNotBossCog = 2
PieCodeToon = 3
PieCodeBossInsides = 4
PieCodeDefensePan = 5
PieCodeProsecutionPan = 6
PieCodeLawyer = 7
PieCodeColors = {PieCodeBossCog: None, PieCodeNotBossCog: (0.8, 0.8, 0.8, 1), 
   PieCodeToon: None}
BossCogRollSpeed = 7.5
BossCogTurnSpeed = 20
BossCogTreadSpeed = 3.5
BossCogDizzy = 0
BossCogElectricFence = 1
BossCogSwatLeft = 2
BossCogSwatRight = 3
BossCogAreaAttack = 4
BossCogFrontAttack = 5
BossCogRecoverDizzyAttack = 6
BossCogDirectedAttack = 7
BossCogStrafeAttack = 8
BossCogNoAttack = 9
BossCogGoonZap = 10
BossCogSlowDirectedAttack = 11
BossCogDizzyNow = 12
BossCogGavelStomp = 13
BossCogGavelHandle = 14
BossCogLawyerAttack = 15
BossCogMoveAttack = 16
BossCogGolfAttack = 17
BossCogGolfAreaAttack = 18
BossCogGearDirectedAttack = 19
BossCogOvertimeAttack = 20
BossCogAttackTimes = {BossCogElectricFence: 0, BossCogSwatLeft: 5.5, 
   BossCogSwatRight: 5.5, 
   BossCogAreaAttack: 4.21, 
   BossCogFrontAttack: 2.65, 
   BossCogRecoverDizzyAttack: 5.1, 
   BossCogDirectedAttack: 4.84, 
   BossCogNoAttack: 6, 
   BossCogSlowDirectedAttack: 7.84, 
   BossCogMoveAttack: 3, 
   BossCogGolfAttack: 6, 
   BossCogGolfAreaAttack: 7, 
   BossCogGearDirectedAttack: 4.84, 
   BossCogOvertimeAttack: 5}
BossCogDamageLevels = {BossCogElectricFence: 1, BossCogSwatLeft: 5, 
   BossCogSwatRight: 5, 
   BossCogAreaAttack: 10, 
   BossCogFrontAttack: 3, 
   BossCogRecoverDizzyAttack: 3, 
   BossCogDirectedAttack: 3, 
   BossCogStrafeAttack: 2, 
   BossCogGoonZap: 5, 
   BossCogSlowDirectedAttack: 10, 
   BossCogGavelStomp: 20, 
   BossCogGavelHandle: 2, 
   BossCogLawyerAttack: 5, 
   BossCogMoveAttack: 20, 
   BossCogGolfAttack: 15, 
   BossCogGolfAreaAttack: 15, 
   BossCogGearDirectedAttack: 15, 
   BossCogOvertimeAttack: 10}
BossCogBattleAPosHpr = (0, -25, 0, 0, 0, 0)
BossCogBattleBPosHpr = (0, 25, 0, 180, 0, 0)
SellbotBossMaxDamage = 100
SellbotBossMaxDamageNerfed = 100
SellbotBossBattleOnePosHpr = (0, -35, 0, -90, 0, 0)
SellbotBossBattleTwoPosHpr = (0, 60, 18, -90, 0, 0)
SellbotBossBattleThreeHpr = (180, 0, 0)
SellbotBossBottomPos = (0, -110, -6.5)
SellbotBossDeathPos = (0, -175, -6.5)
SellbotBossDooberTurnPosA = (-20, -50, 0)
SellbotBossDooberTurnPosB = (20, -50, 0)
SellbotBossDooberTurnPosDown = (0, -50, 0)
SellbotBossDooberFlyPos = (0, -135, -6.5)
SellbotBossTopRampPosA = (-80, -35, 18)
SellbotBossTopRampTurnPosA = (-80, 10, 18)
SellbotBossP3PosA = (-50, 40, 18)
SellbotBossTopRampPosB = (80, -35, 18)
SellbotBossTopRampTurnPosB = (80, 10, 18)
SellbotBossP3PosB = (50, 60, 18)
CashbotBossMaxDamage = 500
CashbotBossOffstagePosHpr = (120, -195, 0, 0, 0, 0)
CashbotBossBattleOnePosHpr = (120, -230, 0, 90, 0, 0)
CashbotRTBattleOneStartPosHpr = (94, -220, 0, 110, 0, 0)
CashbotBossBattleThreePosHpr = (120, -315, 0, 180, 0, 0)
CashbotToonsBattleThreeStartPosHpr = [
 (105, -285, 0, 208, 0, 0),
 (136, -342, 0, 398, 0, 0),
 (105, -342, 0, 333, 0, 0),
 (135, -292, 0, 146, 0, 0),
 (93, -303, 0, 242, 0, 0),
 (144, -327, 0, 64, 0, 0),
 (145, -302, 0, 117, 0, 0),
 (93, -327, 0, -65, 0, 0)]
CashbotBossSafePosHprs = [
 (120, -315, 30, 0, 0, 0),
 (77.2, -329.3, 0, -90, 0, 0),
 (77.1, -302.7, 0, -90, 0, 0),
 (165.7, -326.4, 0, 90, 0, 0),
 (165.5, -302.4, 0, 90, 0, 0),
 (107.8, -359.1, 0, 0, 0, 0),
 (133.9, -359.1, 0, 0, 0, 0),
 (107.0, -274.7, 0, 180, 0, 0),
 (134.2, -274.7, 0, 180, 0, 0)]
CashbotBossCranePosHprs = [
 (97.4, -337.6, 0, -45, 0, 0),
 (97.4, -292.4, 0, -135, 0, 0),
 (142.6, -292.4, 0, 135, 0, 0),
 (142.6, -337.6, 0, 45, 0, 0)]
CashbotBossToMagnetTime = 0.2
CashbotBossFromMagnetTime = 1
CashbotBossSafeKnockImpact = 0.5
CashbotBossSafeNewImpact = 0.0
CashbotBossGoonImpact = 0.1
CashbotBossKnockoutDamage = 15
TTWakeWaterHeight = -4.79
DDWakeWaterHeight = 1.669
EstateWakeWaterHeight = -0.3
OZWakeWaterHeight = -0.5
WakeRunDelta = 0.1
WakeWalkDelta = 0.2
NoItems = 0
NewItems = 1
OldItems = 2
SuitInvasionBegin = 0
SuitInvasionUpdate = 1
SuitInvasionEnd = 2
SuitInvasionBulletin = 3
NO_HOLIDAY = 0
JULY4_FIREWORKS = 1
NEWYEARS_FIREWORKS = 2
HALLOWEEN = 3
WINTER_DECORATIONS = 4
SKELECOG_INVASION = 5
MR_HOLLYWOOD_INVASION = 6
FISH_BINGO_NIGHT = 7
ELECTION_PROMOTION = 8
BLACK_CAT_DAY = 9
RESISTANCE_EVENT = 10
KART_RECORD_DAILY_RESET = 11
KART_RECORD_WEEKLY_RESET = 12
TRICK_OR_TREAT = 13
CIRCUIT_RACING = 14
POLAR_PLACE_EVENT = 15
CIRCUIT_RACING_EVENT = 16
TROLLEY_HOLIDAY = 17
TROLLEY_WEEKEND = 18
SILLY_SATURDAY_BINGO = 19
SILLY_SATURDAY_CIRCUIT = 20
SILLY_SATURDAY_TROLLEY = 21
ROAMING_TRIALER_WEEKEND = 22
BOSSCOG_INVASION = 23
MARCH_INVASION = 24
MORE_XP_HOLIDAY = 25
HALLOWEEN_PROPS = 26
HALLOWEEN_COSTUMES = 27
DECEMBER_INVASION = 28
APRIL_FOOLS_COSTUMES = 29
CRASHED_LEADERBOARD = 30
OCTOBER31_FIREWORKS = 31
NOVEMBER19_FIREWORKS = 32
SELLBOT_SURPRISE_1 = 33
SELLBOT_SURPRISE_2 = 34
SELLBOT_SURPRISE_3 = 35
SELLBOT_SURPRISE_4 = 36
CASHBOT_CONUNDRUM_1 = 37
CASHBOT_CONUNDRUM_2 = 38
CASHBOT_CONUNDRUM_3 = 39
CASHBOT_CONUNDRUM_4 = 40
LAWBOT_GAMBIT_1 = 41
LAWBOT_GAMBIT_2 = 42
LAWBOT_GAMBIT_3 = 43
LAWBOT_GAMBIT_4 = 44
TROUBLE_BOSSBOTS_1 = 45
TROUBLE_BOSSBOTS_2 = 46
TROUBLE_BOSSBOTS_3 = 47
TROUBLE_BOSSBOTS_4 = 48
JELLYBEAN_DAY = 49
FEBRUARY14_FIREWORKS = 51
JULY14_FIREWORKS = 52
JUNE22_FIREWORKS = 53
BIGWIG_INVASION = 54
COLD_CALLER_INVASION = 53
BEAN_COUNTER_INVASION = 54
DOUBLE_TALKER_INVASION = 55
DOWNSIZER_INVASION = 56
WINTER_CAROLING = 57
HYDRANT_ZERO_HOLIDAY = 58
VALENTINES_DAY = 59
SILLYMETER_HOLIDAY = 60
MAILBOX_ZERO_HOLIDAY = 61
TRASHCAN_ZERO_HOLIDAY = 62
SILLY_SURGE_HOLIDAY = 63
HYDRANTS_BUFF_BATTLES = 64
MAILBOXES_BUFF_BATTLES = 65
TRASHCANS_BUFF_BATTLES = 66
SILLY_CHATTER_ONE = 67
SILLY_CHATTER_TWO = 68
SILLY_CHATTER_THREE = 69
SILLY_CHATTER_FOUR = 70
SILLY_TEST = 71
YES_MAN_INVASION = 72
TIGHTWAD_INVASION = 73
TELEMARKETER_INVASION = 74
HEADHUNTER_INVASION = 75
SPINDOCTOR_INVASION = 76
MONEYBAGS_INVASION = 77
TWOFACES_INVASION = 78
MINGLER_INVASION = 79
LOANSHARK_INVASION = 80
CORPORATE_RAIDER_INVASION = 81
ROBBER_BARON_INVASION = 82
LEGAL_EAGLE_INVASION = 83
BIG_WIG_INVASION = 84
BIG_CHEESE_INVASION = 85
DOWN_SIZER_INVASION = 86
MOVER_AND_SHAKER_INVASION = 87
DOUBLETALKER_INVASION = 88
PENNY_PINCHER_INVASION = 89
NAME_DROPPER_INVASION = 90
AMBULANCE_CHASER_INVASION = 91
MICROMANAGER_INVASION = 92
NUMBER_CRUNCHER_INVASION = 93
SILLY_CHATTER_FIVE = 94
VICTORY_PARTY_HOLIDAY = 95
SELLBOT_NERF_HOLIDAY = 96
JELLYBEAN_TROLLEY_HOLIDAY = 97
JELLYBEAN_FISHING_HOLIDAY = 98
JELLYBEAN_PARTIES_HOLIDAY = 99
BANK_UPGRADE_HOLIDAY = 100
TOP_TOONS_MARATHON = 101
SELLBOT_INVASION = 102
SELLBOT_FIELD_OFFICE = 103
SELLBOT_INVASION_MOVER_AND_SHAKER = 104
IDES_OF_MARCH = 105
EXPANDED_CLOSETS = 106
TAX_DAY_INVASION = 107
KARTING_TICKETS_HOLIDAY = 109
PRE_JULY_4_DOWNSIZER_INVASION = 110
PRE_JULY_4_BIGWIG_INVASION = 111
COMBO_FIREWORKS = 112
JELLYBEAN_TROLLEY_HOLIDAY_MONTH = 113
JELLYBEAN_FISHING_HOLIDAY_MONTH = 114
JELLYBEAN_PARTIES_HOLIDAY_MONTH = 115
SILLYMETER_EXT_HOLIDAY = 116
SPOOKY_BLACK_CAT = 117
SPOOKY_TRICK_OR_TREAT = 118
SPOOKY_PROPS = 119
SPOOKY_COSTUMES = 120
WACKY_WINTER_DECORATIONS = 121
WACKY_WINTER_CAROLING = 122
TOT_REWARD_JELLYBEAN_AMOUNT = 100
TOT_REWARD_END_OFFSET_AMOUNT = 0
LawbotBossMaxDamage = 2700
LawbotBossWinningTilt = 40
LawbotBossInitialDamage = 1350
LawbotBossStartPosHpr = (-3.0, 140, 21, 0, 0, 0)
LawbotBossBattleOnePosHpr = (-3.0, 15, 0, 0, 0, 0)
LawbotBossBattleTwoPosHpr = (-2.798, 89, 19.145, 0, 0, 0)
LawbotBossTopRampPosA = (-80, -35, 18)
LawbotBossTopRampTurnPosA = (-80, 10, 18)
LawbotBossP3PosA = (55, -9, 0)
LawbotBossTopRampPosB = (80, -35, 18)
LawbotBossTopRampTurnPosB = (80, 10, 18)
LawbotBossP3PosB = (55, -9, 0)
LawbotBossBattleThreePosHpr = LawbotBossBattleTwoPosHpr
LawbotBossBottomPos = (50, 39, 0)
LawbotBossDeathPos = (50, 40, 0)
LawbotBossGavelPosHprs = [
 (35, 78.328, 0, -135, 0, 0),
 (68.5, 78.328, 0, 135, 0, 0),
 (47, -33, 0, 45, 0, 0),
 (-50, -39, 0, -45, 0, 0),
 (-9, -37, 0, 0, 0, 0),
 (-9, 49, 0, -180, 0, 0),
 (32, 0, 0, 45, 0, 0),
 (33, 56, 0, 135, 0, 0)]
LawbotBossGavelTimes = [(0.2, 0.9, 0.6),
 (0.25, 1, 0.5),
 (1.0, 6, 0.5),
 (0.3, 3, 1),
 (0.26, 0.9, 0.45),
 (0.24, 1.1, 0.65),
 (0.27, 1.2, 0.45),
 (0.25, 0.95, 0.5)]
LawbotBossGavelHeadings = [
 (0,
  -15,
  4,
  -115,
  5,
  45),
 (0, -45, -4, -35, -45, -16, 32),
 (0, -8, 19, -7, 5, 23),
 (0, -4, 8, -16, 32, -45, 7, 7, -30, 19, -13, 25),
 (0, -45, -90, 45, 90),
 (0, -45, -90, 45, 90),
 (0, -45, 45),
 (0, -45, 45)]
LawbotBossCogRelBattleAPosHpr = (-25, -10, 0, 0, 0, 0)
LawbotBossCogRelBattleBPosHpr = (-25, 10, 0, 0, 0, 0)
LawbotBossCogAbsBattleAPosHpr = (-5, -2, 0, 0, 0, 0)
LawbotBossCogAbsBattleBPosHpr = (-5, 0, 0, 0, 0, 0)
LawbotBossWitnessStandPosHpr = (54, 100, 0, -90, 0, 0)
LawbotBossInjusticePosHpr = (-3, 12, 0, 90, 0, 0)
LawbotBossInjusticeScale = (1.75, 1.75, 1.5)
LawbotBossDefensePanDamage = 1
LawbotBossLawyerPosHprs = [
 (-57, -24, 0, -90, 0, 0),
 (-57, -12, 0, -90, 0, 0),
 (-57, 0, 0, -90, 0, 0),
 (-57, 12, 0, -90, 0, 0),
 (-57, 24, 0, -90, 0, 0),
 (-57, 36, 0, -90, 0, 0),
 (-57, 48, 0, -90, 0, 0),
 (-57, 60, 0, -90, 0, 0),
 (-3, -37.3, 0, 0, 0, 0),
 (-3, 53, 0, -180, 0, 0)]
LawbotBossLawyerCycleTime = 6
LawbotBossLawyerToPanTime = 2.5
LawbotBossLawyerChanceToAttack = 50
LawbotBossLawyerHeal = 2
LawbotBossLawyerStunTime = 5
LawbotBossDifficultySettings = [
 (38, 4, 8, 1, 0, 0),
 (36, 5, 8, 1, 0, 0),
 (34, 5, 8, 1, 0, 0),
 (32, 6, 8, 2, 0, 0),
 (30, 6, 8, 2, 0, 0),
 (28, 7, 8, 3, 0, 0),
 (26, 7, 9, 3, 1, 1),
 (24, 8, 9, 4, 1, 1),
 (22, 8, 10, 4, 1, 0)]
LawbotBossCannonPosHprs = [
 (-40, -12, 0, -90, 0, 0),
 (-40, 0, 0, -90, 0, 0),
 (-40, 12, 0, -90, 0, 0),
 (-40, 24, 0, -90, 0, 0),
 (-40, 36, 0, -90, 0, 0),
 (-40, 48, 0, -90, 0, 0),
 (-40, 60, 0, -90, 0, 0),
 (-40, 72, 0, -90, 0, 0)]
LawbotBossCannonPosA = (-80, -51.48, 0)
LawbotBossCannonPosB = (-80, 70.73, 0)
LawbotBossChairPosHprs = [
 (60, 72, 0, -90, 0, 0),
 (60, 62, 0, -90, 0, 0),
 (60, 52, 0, -90, 0, 0),
 (60, 42, 0, -90, 0, 0),
 (60, 32, 0, -90, 0, 0),
 (60, 22, 0, -90, 0, 0),
 (70, 72, 5, -90, 0, 0),
 (70, 62, 5, -90, 0, 0),
 (70, 52, 5, -90, 0, 0),
 (70, 42, 5, -90, 0, 0),
 (70, 32, 5, -90, 0, 0),
 (70, 22, 5, -90, 0, 0)]
LawbotBossChairRow1PosB = (59.3, 48, 14.05)
LawbotBossChairRow1PosA = (59.3, -18.2, 14.05)
LawbotBossChairRow2PosB = (75.1, 48, 28.2)
LawbotBossChairRow2PosA = (75.1, -18.2, 28.2)
LawbotBossCannonBallMax = 12
LawbotBossJuryBoxStartPos = (94, -8, 5)
LawbotBossJuryBoxRelativeEndPos = (30, 0, 12.645)
LawbotBossJuryBoxMoveTime = 70
LawbotBossJurorsForBalancedScale = 8
LawbotBossDamagePerJuror = 68
LawbotBossCogJurorFlightTime = 10
LawbotBossCogJurorDistance = 75
LawbotBossBaseJurorNpcId = 2001
LawbotBossWitnessEpiloguePosHpr = (-3, 0, 0, 180, 0, 0)
LawbotBossChanceForTaunt = 25
LawbotBossBonusWaitTime = 60
LawbotBossBonusDuration = 20
LawbotBossBonusToonup = 10
LawbotBossBonusWeightMultiplier = 2
LawbotBossChanceToDoAreaAttack = 11
MIN_POP = 1
LOW_POP = 48
MID_POP = 96
HIGH_POP = 128
PinballCannonBumper = 0
PinballCloudBumperLow = 1
PinballCloudBumperMed = 2
PinballCloudBumperHigh = 3
PinballTarget = 4
PinballRoof = 5
PinballHouse = 6
PinballFence = 7
PinballBridge = 8
PinballStatuary = 9
PinballScoring = [(100, 1),
 (150, 1),
 (200, 1),
 (250, 1),
 (350, 1),
 (100, 1),
 (50, 1),
 (25, 1),
 (100, 1),
 (10, 1)]
PinballCannonBumperInitialPos = (0, -20, 40)
RentalCop = 0
RentalCannon = 1
RentalGameTable = 2
GlitchKillerZones = [13300,
 13400,
 13500,
 13600]
ColorPlayer = (0.3, 0.7, 0.3, 1)
ColorAvatar = (0.3, 0.3, 0.7, 1)
ColorPet = (0.6, 0.4, 0.2, 1)
ColorFreeChat = (0.3, 0.3, 0.8, 1)
ColorSpeedChat = (0.2, 0.6, 0.4, 1)
ColorNoChat = (0.8, 0.5, 0.1, 1)
FactoryLaffMinimums = [(0, 31),
 (0, 66, 71),
 (0, 81, 86, 96),
 (0, 101, 106)]
PICNIC_COUNTDOWN_TIME = 60
BossbotRTIntroStartPosHpr = (0, -64, 0, 180, 0, 0)
BossbotRTPreTwoPosHpr = (0, -20, 0, 180, 0, 0)
BossbotRTEpiloguePosHpr = (0, 90, 0, 180, 0, 0)
BossbotBossBattleOnePosHpr = (0, 355, 0, 0, 0, 0)
BossbotBossPreTwoPosHpr = (0, 20, 0, 0, 0, 0)
BossbotElevCamPosHpr = (0, -100.544, 7.18258, 0, 0, 0)
BossbotFoodModelScale = 0.75
BossbotNumFoodToExplode = 3
BossbotBossServingDuration = 300
BossbotPrepareBattleThreeDuration = 20
WaiterBattleAPosHpr = (20, -400, 0, 0, 0, 0)
WaiterBattleBPosHpr = (-20, -400, 0, 0, 0, 0)
BossbotBossBattleThreePosHpr = (0, 355, 0, 0, 0, 0)
DinerBattleAPosHpr = (20, -240, 0, 0, 0, 0)
DinerBattleBPosHpr = (-20, -240, 0, 0, 0, 0)
BossbotBossMaxDamage = 500
BossbotMaxSpeedDamage = 90
BossbotSpeedRecoverRate = 20
BossbotBossDifficultySettings = [
 (8, 4, 11, 3, 30, 25),
 (9, 5, 12, 6, 28, 26),
 (10, 6, 11, 7, 26, 27),
 (8, 8, 12, 8, 24, 28),
 (13, 5, 12, 9, 22, 29)]
BossbotRollSpeedMax = 22
BossbotRollSpeedMin = 7.5
BossbotTurnSpeedMax = 60
BossbotTurnSpeedMin = 20
BossbotTreadSpeedMax = 10.5
BossbotTreadSpeedMin = 3.5
CalendarFilterShowAll = 0
CalendarFilterShowOnlyHolidays = 1
CalendarFilterShowOnlyParties = 2
TTC = 1
DD = 2
MM = 3
GS = 4
DG = 5
BR = 6
OZ = 7
DL = 8
DefaultWantNewsPageSetting = 1
gmMagicWordList = ['restock',
 'restockUber',
 'autoRestock',
 'resistanceRestock',
 'restockSummons',
 'uberDrop',
 'rich',
 'maxBankMoney',
 'toonUp',
 'rod',
 'cogPageFull',
 'pinkSlips',
 'Tickets',
 'newSummons',
 'who',
 'who all']
NewsPageScaleAdjust = 0.85
AnimPropTypes = Enum(('Unknown', 'Hydrant', 'Mailbox', 'Trashcan'), start=-1)
EmblemTypes = Enum(('Silver', 'Gold'))
NumEmblemTypes = 2
DefaultMaxBankMoney = 12000
MaxJarMoney = 9999
DefaultBankItemId = 1350
ToonAnimStates = set(['off',
 'neutral',
 'victory',
 'Happy',
 'Sad',
 'Catching',
 'CatchEating',
 'Sleep',
 'walk',
 'jumpSquat',
 'jump',
 'jumpAirborne',
 'jumpLand',
 'run',
 'swim',
 'swimhold',
 'dive',
 'cringe',
 'OpenBook',
 'ReadBook',
 'CloseBook',
 'TeleportOut',
 'Died',
 'TeleportedOut',
 'TeleportIn',
 'Emote',
 'SitStart',
 'Sit',
 'Push',
 'Squish',
 'FallDown',
 'GolfPuttLoop',
 'GolfRotateLeft',
 'GolfRotateRight',
 'GolfPuttSwing',
 'GolfGoodPutt',
 'GolfBadPutt',
 'Flattened',
 'CogThiefRunning',
 'ScientistJealous',
 'ScientistEmcee',
 'ScientistWork',
 'ScientistLessWork',
 'ScientistPlay',
 'PortalOut',
 'PortaledOut',
 'PortalIn'])
AV_FLAG_REASON_TOUCH = 1
AV_FLAG_HISTORY_LEN = 500
AV_TOUCH_CHECK_DELAY_AI = 3.0
AV_TOUCH_CHECK_DELAY_CL = 1.0
AV_TOUCH_CHECK_DIST = 2.0
AV_TOUCH_CHECK_DIST_Z = 5.0
AV_TOUCH_CHECK_TIMELIMIT_CL = 0.002
AV_TOUCH_COUNT_LIMIT = 5
AV_TOUCH_COUNT_TIME = 300
HQEventStinkLifetime = 60
HQEventStinkThreshold = 100
hood2Id = {'TTC': (
         ToontownCentral,), 
   'DD': (
        DonaldsDock,), 
   'MML': (
         MinniesMelodyland,), 
   'DG': (
        DaisyGardens,), 
   'TB': (
        TheBrrrgh,), 
   'DDL': (
         DonaldsDreamland,), 
   'GZ': (
        GolfZone,), 
   'GSW': (
         GoofySpeedway,), 
   'GS': (
        GoofySpeedway,), 
   'OZ': (
        OutdoorZone,), 
   'CEO': (
         BossbotHQ,), 
   'CJ': (
        LawbotHQ,), 
   'CFO': (
         CashbotHQ,), 
   'VP': (
        SellbotHQ,), 
   'BBHQ': (
          BossbotHQ,), 
   'LBHQ': (
          LawbotHQ,), 
   'CBHQ': (
          CashbotHQ,), 
   'SBHQ': (
          SellbotHQ,), 
   'FACTORY': (
             SellbotHQ, SellbotFactoryExt), 
   'FRONTENTRY': (
                SellbotHQ, SellbotFactoryExt), 
   'SIDEENTRY': (
               SellbotHQ, SellbotFactoryExt), 
   'BULLION': (
             CashbotHQ,), 
   'DOLLAR': (
            CashbotHQ,), 
   'COIN': (
          CashbotHQ,), 
   'OFFICEA': (
             LawbotHQ, LawbotOfficeExt), 
   'OFFICEB': (
             LawbotHQ, LawbotOfficeExt), 
   'OFFICEC': (
             LawbotHQ, LawbotOfficeExt), 
   'OFFICED': (
             LawbotHQ, LawbotOfficeExt), 
   'BACK': (
          BossbotHQ,), 
   'MIDDLE': (
            BossbotHQ,), 
   'FRONT': (
           BossbotHQ,), 
   'SP': (
        ToontownOutskirts,), 
   'TT': (
        ToontownOutskirts, TutorialTerrace), 
   'TTCB': (
          ToontownCentralBeta,), 
   'DGB': (
         DaisyGardensBeta,)}
hood2Coords = {'CEO': [
         (61.044, 119.014, 0.025, -4.68, 0, 0)], 
   'CJ': [
        (333.7, -179.869, -42.932, -807.174, 0, 0)], 
   'CFO': [
         (125.155, 546.084, 32.246, 360.056, 0, 0)], 
   'VP': [
        (25.512, -51.193, 10.095, 40.868, 0, 0)], 
   'FACTORY': [
             (62.204, -89.739, 0.025, -7.144, 0, 0)], 
   'FRONTENTRY': [
                (62.204, -89.739, 0.025, -7.144, 0, 0)], 
   'SIDEENTRY': [
               (-165.94, 26.804, 0.025, -97.144, 0, 0)], 
   'BULLION': [
             (-118.641, 64.131, -23.434, 449.182, 0, 0)], 
   'DOLLAR': [
            (178.612, -175.786, -63.244, 274.225, 0, 0)], 
   'COIN': [
          (-122.43, -428.856, -23.439, 450.141, 0, 0)], 
   'OFFICE': [
            (-170.371, -191.902, -16.28, -633.031, 0, 0)], 
   'OFFICEA': [
             (47.594, 78.874, 51.692, -35, 0, 0)], 
   'OFFICEB': [
             (94.816, 78.874, 51.692, -15, 0, 0)], 
   'OFFICEC': [
             (137.586, 78.874, 51.692, 15, 0, 0)], 
   'OFFICED': [
             (178.331, 78.874, 51.692, 35, 0, 0)], 
   'BACK': [
          (-73.911, 87.426, 11.803, 10.17, 0, 0)], 
   'MIDDLE': [
            (-98.805, 39.18, 11.364, -253.35, 0, 0)], 
   'FRONT': [
           (-105.626, -33.441, 9.777, -211.885, 0, 0)], 
   'WESTWING': [
              (-102.431, 6.703, 0.565, -38.212, 0, 0)], 
   'WW': [
        (-102.431, 6.703, 0.565, -38.212, 0, 0)], 
   'AA': [
        (3044.39, 12.72, 199.19, 69.83, 0.0, 0.0)], 
   'TT': [
        (107.85, -49.32, 0.03, 40.58, 0.0, 0.0)]}
SuitLevels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 20, 30, 40, 50]
MoleHillPositions = [
 (136.542, 98.415, -1.212),
 (121.312, 8.031, -0.904),
 (104.776, -36.965, -0.904),
 (80.159, -64.127, -0.904),
 (7.309, -15.04, -0.433),
 (29.393, 30.864, -1.025),
 (-84.014, -89.77, 10.586),
 (220.143, -6.165, -1.792)]
KongdominiumSongs = {'One Day, Everything Will Be Okay': 'phase_14.5/audio/bgm/mpg/mpg_yolw_onedayeverythingwillbeokay.ogg', 
   'Mayday': 'phase_14.5/audio/bgm/mpg/mpg_yolw_mayday.ogg', 
   'I Wrote You a Chiptune': 'phase_14.5/audio/bgm/mpg/mpg_yolw_iwroteyouachiptune.ogg', 
   'How to Win a World War, Somewhere': 'phase_14.5/audio/bgm/mpg/mpg_yolw_howtowinaworldwarsomewhere.ogg', 
   "It's Love": 'phase_14.5/audio/bgm/mpg/mpg_yolw_itslove.ogg'}
PrivateServerCafeSongs = {'The Toontown Rewritten Theme': 'phase_14.5/audio/bgm/tribute/ttr_theme.ogg', 
   'The Toontown House Theme': 'phase_14.5/audio/bgm/tribute/tth_theme.ogg', 
   'The Toontown Infinite Theme': 'phase_14.5/audio/bgm/tribute/tti_theme.ogg', 
   'The Operation: Dessert Storm Theme': 'phase_14.5/audio/bgm/tribute/ods_theme.ogg'}
Phrase2Location = {1131: ToontownOutskirts, 
   1004: ToontownOutskirts, 
   1106: DonaldsDock, 
   1107: MinniesMelodyland, 
   1108: DaisyGardens, 
   1109: TheBrrrgh, 
   1110: DonaldsDreamland, 
   1111: GoofySpeedway, 
   1114: SellbotHQ, 
   1115: SellbotHQ, 
   1116: SellbotFactoryExt, 
   1119: CashbotHQ, 
   1120: CashbotHQ, 
   1121: CashbotHQ, 
   1122: LawbotHQ, 
   1123: LawbotHQ, 
   1124: LawbotOfficeExt, 
   1125: OutdoorZone, 
   1126: GolfZone, 
   1127: BossbotHQ, 
   1128: BossbotHQ, 
   1129: BossbotHQ, 
   1206: SellbotFactoryExt, 
   1207: SellbotFactoryExt, 
   1210: CashbotHQ, 
   1211: LawbotOfficeExt, 
   1212: BossbotHQ}
Location2Hood = {SellbotFactoryExt: SellbotHQ, 
   LawbotOfficeExt: LawbotHQ}
MeetHereNpcIds = [
 7100,
 7101,
 7102,
 7103,
 7104,
 7105,
 7106,
 7107]
TextToSpeechLink = 'http://sourceforge.net/projects/espeak/files/latest/download'
Species2Voice = {'dog': 'Alex', 
   'cat': 'Samantha', 
   'horse': 'Daniel', 
   'mouse': 'Junior', 
   'rabbit': 'Princess', 
   'duck': 'Fred', 
   'monkey': 'Deranged', 
   'bear': 'Bruce', 
   'Pig': 'Albert'}
Species2Pitch = {'dog': 50, 
   'cat': 80, 
   'horse': 30, 
   'mouse': 99, 
   'rabbit': 95, 
   'duck': 35, 
   'monkey': 85, 
   'bear': 20, 
   'Pig': 25}
DefaultVoice = 'Alex'
DefaultVoiceSuit = 'Thomas'
DefaultVoiceCogBoss = 'Albert'
DefaultVoiceClassicChar = 'Princess'
DefaultPitch = 50
Props = (
 (5, 'partyBall', 'partyBall'),
 (5, 'feather', 'feather-mod', 'feather-chan'),
 (5, 'lips', 'lips'),
 (5, 'lipstick', 'lipstick'),
 (5, 'hat', 'hat'),
 (5, 'cane', 'cane'),
 (5, 'cubes', 'cubes-mod', 'cubes-chan'),
 (5, 'ladder', 'ladder2'),
 (4, 'fishing-pole', 'fishing-pole-mod', 'fishing-pole-chan'),
 (5, '1dollar', '1dollar-bill-mod', '1dollar-bill-chan'),
 (5, 'big-magnet', 'magnet'),
 (5, 'hypno-goggles', 'hypnotize-mod', 'hypnotize-chan'),
 (5, 'slideshow', 'av_screen'),
 (5, 'banana', 'banana-peel-mod', 'banana-peel-chan'),
 (5, 'rake', 'rake-mod', 'rake-chan'),
 (5, 'marbles', 'marbles-mod', 'marbles-chan'),
 (5, 'tnt', 'tnt-mod', 'tnt-chan'),
 (5, 'trapdoor', 'trapdoor'),
 (5, 'quicksand', 'quicksand'),
 (5, 'traintrack', 'traintrack2'),
 (5, 'train', 'train'),
 (5, 'megaphone', 'megaphone'),
 (5, 'aoogah', 'aoogah'),
 (5, 'bikehorn', 'bikehorn'),
 (5, 'bugle', 'bugle'),
 (5, 'elephant', 'elephant'),
 (5, 'fog_horn', 'fog_horn'),
 (5, 'whistle', 'whistle'),
 (5, 'singing', 'singing'),
 (3.5, 'creampie', 'tart'),
 (5, 'fruitpie-slice', 'fruit-pie-slice'),
 (5, 'creampie-slice', 'cream-pie-slice'),
 (5, 'birthday-cake', 'birthday-cake-mod', 'birthday-cake-chan'),
 (5, 'wedding-cake', 'wedding_cake'),
 (3.5, 'squirting-flower', 'squirting-flower'),
 (5, 'glass', 'glass-mod', 'glass-chan'),
 (4, 'water-gun', 'water-gun'),
 (3.5, 'bottle', 'bottle'),
 (5, 'firehose', 'firehose-mod', 'firehose-chan'),
 (5, 'hydrant', 'battle_hydrant'),
 (4, 'stormcloud', 'stormcloud-mod', 'stormcloud-chan'),
 (5, 'geyser', 'geyser'),
 (3.5, 'button', 'button'),
 (5, 'flowerpot', 'flowerpot-mod', 'flowerpot-chan'),
 (5, 'sandbag', 'sandbag-mod', 'sandbag-chan'),
 (4, 'anvil', 'anvil-mod', 'anvil-chan'),
 (5, 'weight', 'weight-mod', 'weight-chan'),
 (5, 'safe', 'safe-mod', 'safe-chan'),
 (5, 'piano', 'piano-mod', 'piano-chan'),
 (5, 'rake-react', 'rake-step-mod', 'rake-step-chan'),
 (5, 'pad', 'pad'),
 (4, 'propeller', 'propeller-mod', 'propeller-chan'),
 (5, 'calculator', 'calculator-mod', 'calculator-chan'),
 (5, 'rollodex', 'roll-o-dex'),
 (5, 'rubber-stamp', 'rubber-stamp'),
 (5, 'rubber-stamp-pad', 'rubber-stamp-pad-mod', 'rubber-stamp-pad-chan'),
 (5, 'smile', 'smile-mod', 'smile-chan'),
 (5, 'golf-club', 'golf-club'),
 (5, 'golf-ball', 'golf-ball'),
 (5, 'redtape', 'redtape'),
 (5, 'redtape-tube', 'redtape-tube'),
 (5, 'bounced-check', 'bounced-check'),
 (5, 'calculator', 'calculator-mod', 'calculator-chan'),
 (3.5, 'clip-on-tie', 'clip-on-tie-mod', 'clip-on-tie-chan'),
 (5, 'pen', 'pen'),
 (5, 'pencil', 'pencil'),
 (3.5, 'phone', 'phone'),
 (3.5, 'receiver', 'receiver'),
 (5, 'sharpener', 'sharpener'),
 (3.5, 'shredder', 'shredder'),
 (3.5, 'shredder-paper', 'shredder-paper-mod', 'shredder-paper-chan'),
 (5, 'watercooler', 'watercooler'),
 (5, 'dagger', 'dagger'),
 (5, 'card', 'card'),
 (5, 'baseball', 'baseball'),
 (5, 'bird', 'bird'),
 (5, 'can', 'can'),
 (5, 'cigar', 'cigar'),
 (5, 'evil-eye', 'evil-eye'),
 (5, 'gavel', 'gavel'),
 (5, 'half-windsor', 'half-windsor'),
 (5, 'lawbook', 'lawbook'),
 (5, 'newspaper', 'newspaper'),
 (5, 'pink-slip', 'pink-slip'),
 (5, 'teeth', 'teeth-mod', 'teeth-chan'),
 (5, 'power-tie', 'power-tie'),
 (3.5, 'spray', 'spray'),
 (3.5, 'splat', 'splat-mod', 'splat-chan'),
 (3.5, 'stun', 'stun-mod', 'stun-chan'),
 (3.5, 'glow', 'glow'),
 (3.5, 'suit_explosion', 'suit_explosion-mod', 'suit_explosion-chan'),
 (3.5, 'suit_explosion_dust', 'dust_cloud'),
 (4, 'ripples', 'ripples'),
 (4, 'wake', 'wake'),
 (4, 'splashdown', 'SZ_splashdown-mod', 'SZ_splashdown-chan'))
CreampieColor = VBase4(250.0 / 255.0, 241.0 / 255.0, 24.0 / 255.0, 1.0)
FruitpieColor = VBase4(55.0 / 255.0, 40.0 / 255.0, 148.0 / 255.0, 1.0)
BirthdayCakeColor = VBase4(253.0 / 255.0, 119.0 / 255.0, 220.0 / 255.0, 1.0)
Splats = {'tart': (0.3, FruitpieColor), 'fruitpie-slice': (
                    0.5, FruitpieColor), 
   'creampie-slice': (
                    0.5, CreampieColor), 
   'fruitpie': (
              0.7, FruitpieColor), 
   'creampie': (
              0.7, CreampieColor), 
   'birthday-cake': (
                   0.9, BirthdayCakeColor), 
   'wedding-cake': (
                  1, CreampieColor)}
Variants = ('tart', 'fruitpie', 'splat-tart', 'dust', 'kapow', 'double-windsor', 'splat-fruitpie-slice',
            'splat-creampie-slice', 'splat-fruitpie', 'splat-creampie', 'splat-birthday-cake',
            'splat-wedding-cakesplash-from-splat', 'clip-on-tie', 'lips', 'small-magnet',
            '5dollar', '10dollar', 'suit_explosion', 'quicksand', 'trapdoor', 'geyser',
            'ship', 'trolley', 'traintrack')

def getPath(phase, model):
    return 'phase_%s/models/props/%s' % (phase, model)


PropList = [
 (
  'tart', 'model', (getPath(3.5, 'tart'),), 1.0),
 (
  'fruitpie', 'model', (getPath(3.5, 'tart'),), 1.0),
 (
  'double-windsor', 'model', (getPath(5, 'half-windsor'),), 1.0),
 (
  'splat-tart', 'actor', (getPath(3.5, 'splat-mod'), getPath(3.5, 'splat-chan')), 1.0),
 (
  'splat-fruitpie-slice', 'actor', (getPath(3.5, 'splat-mod'), getPath(3.5, 'splat-chan')), 1.0),
 (
  'splat-creampie-slice', 'actor', (getPath(3.5, 'splat-mod'), getPath(3.5, 'splat-chan')), 1.0),
 (
  'splat-fruitpie', 'actor', (getPath(3.5, 'splat-mod'), getPath(3.5, 'splat-chan')), 1.0),
 (
  'splat-creampie', 'actor', (getPath(3.5, 'splat-mod'), getPath(3.5, 'splat-chan')), 1.0),
 (
  'splat-birthday-cake', 'actor', (getPath(3.5, 'splat-mod'), getPath(3.5, 'splat-chan')), 1.0),
 (
  'splat-wedding-cake', 'actor', (getPath(3.5, 'splat-mod'), getPath(3.5, 'splat-chan')), 1.0),
 (
  'splash-from-splat', 'actor', (getPath(3.5, 'splat-mod'), getPath(3.5, 'splat-chan')), 1.0),
 (
  'small-magnet', 'model', (getPath(5, 'magnet'),), 1.0),
 (
  '5dollar', 'actor', (getPath(5, '1dollar-bill-mod'), getPath(5, '1dollar-bill-chan')), 1.0),
 (
  '10dollar', 'actor', (getPath(5, '1dollar-bill-mod'), getPath(5, '1dollar-bill-chan')), 1.0),
 (
  'dust', 'actor', (getPath(5, 'dust-mod'), getPath(5, 'dust-chan')), 1.0),
 (
  'kapow', 'actor', (getPath(5, 'kapow-mod'), getPath(5, 'kapow-chan')), 1.0),
 (
  'ship', 'model', (getPath(5, 'ship'),), 1.0),
 (
  'trolley', 'model', ('phase_4/models/modules/trolley_station_TT', ), 1.0),
 (
  'clipboard', 'model', (getPath(4, 'tt_m_prp_acs_clipboard'),), 1.0),
 (
  'sillyreader', 'model', (getPath(4, 'tt_m_prp_acs_sillyReader'),), 1.0),
 (
  'ffc', 'model', (getPath(14, 'kfc'),), 1.0),
 (
  'sillymeter', 'actor', (getPath(4, 'tt_a_ara_ttc_sillyMeter_default'), getPath(4, 'tt_a_ara_ttc_sillyMeter_phaseFour')), 0.25),
 (
  'periscope', 'actor', (getPath(3.5, 'HQ_periscope-base-mod'), getPath(3.5, 'HQ_periscope-base-chan')), 1.0),
 (
  'rocket', 'actor', ('phase_13/models/parties/rocket_model', 'phase_13/models/parties/rocket_launch'), 1.0),
 (
  'globe', 'actor', ('phase_13/models/parties/tt_m_ara_pty_gagGlobe_model', 'phase_13/models/parties/tt_m_ara_pty_gagGlobe'), 1.0),
 (
  'botcam', 'actor', ('phase_9/models/char/BotCam-zero', 'phase_9/models/char/BotCam-neutral'), 1.0),
 (
  'foot', 'actor', ('phase_9/models/char/BotFoot-zero', 'phase_9/models/char/BotFoot-kick'), 1.0),
 (
  'surlee', 'model', ('phase_3.5/models/modules/tt_m_ara_int_scientistMonkeyFlat', ), 1.0),
 (
  'dimm', 'model', ('phase_3.5/models/modules/tt_m_ara_int_scientistDuckFlat', ), 1.0),
 (
  'prepostera', 'model', ('phase_3.5/models/modules/tt_m_ara_int_scientistHorseFlat', ), 1.0),
 (
  'flatsillymeter', 'model', ('phase_3.5/models/modules/tt_m_ara_int_sillyMeterFlat', ), 0.25),
 (
  'bluepen', 'model', (getPath(5, 'pen'),), 1.0),
 (
  'smashball', 'model', (getPath(14, 'smashball'),), 5.0),
 (
  'logo', 'model', (getPath(14, 'logo'),), 1.0),
 (
  'cube', 'model', (getPath(3.5, 'cube'),), 1.0),
 (
  'laughbarrel', 'model', ('phase_5/models/cogdominium/tt_m_ara_cbr_laughBarrel', ), 1.0),
 (
  'safes', 'model', ('phase_5/models/cogdominium/tt_m_ara_ccg_safesA', ), 1.0),
 (
  'streamer', 'model', ('phase_5/models/cogdominium/tt_m_ara_cfg_streamer', ), 1.0),
 (
  'toonpropeller', 'model', ('phase_5/models/cogdominium/tt_m_ara_cfg_toonPropeller', ), 1.0),
 (
  'whirlwind', 'model', ('phase_5/models/cogdominium/tt_m_ara_cfg_whirlwind', ), 1.0),
 (
  'waterballoon', 'model', ('phase_5/models/cogdominium/tt_m_ara_cmg_waterBalloon', ), 1.0),
 (
  'locomotive', 'model', ('phase_10/models/cogHQ/CashBotLocomotive', ), 0.25),
 (
  'flatcar', 'model', ('phase_10/models/cogHQ/CashBotFlatCar', ), 0.25),
 (
  'boxcar', 'model', ('phase_10/models/cogHQ/CashBotBoxCar', ), 0.25),
 (
  'tankcar', 'model', ('phase_10/models/cogHQ/CashBotTankCar', ), 0.25),
 (
  'moneystack', 'model', ('phase_10/models/cogHQ/DoubleMoneyStack', ), 1.0),
 (
  'metalcrate', 'model', ('phase_10/models/cogHQ/CBMetalCrate2', ), 1.0),
 (
  'cogsafe', 'model', ('phase_10/models/cogHQ/CBSafe', ), 1.0),
 (
  'coinstack', 'model', ('phase_10/models/cashbotHQ/DoubleCoinStack', ), 1.0),
 (
  'goldstack', 'model', ('phase_10/models/cashbotHQ/DoubleGoldStack', ), 1.0),
 (
  'register', 'model', ('phase_10/models/cashbotHQ/CashBotHQCshRegister', ), 1.0),
 (
  'cognationcrate', 'model', ('phase_10/models/cashbotHQ/CBWoodCrate', ), 1.0),
 (
  'goldstack', 'model', ('phase_10/models/cashbotHQ/DoubleGoldStack', ), 1.0),
 (
  'moneystacksmall', 'model', ('phase_10/models/cashbotHQ/MoneyStackPallet', ), 1.0),
 (
  'moneybag', 'model', ('phase_10/models/cashbotHQ/MoneyBag', ), 1.0),
 (
  'goldstacksmall', 'model', ('phase_10/models/cashbotHQ/GoldBarStack', ), 1.0),
 (
  'gold', 'model', ('phase_10/models/cashbotHQ/GoldBar', ), 1.0),
 (
  'money', 'model', ('phase_10/models/cashbotHQ/MoneyStack', ), 1.0),
 (
  'sillysigns1', 'model', ('phase_4/models/props/tt_m_ara_ttc_sillyMeterSign_groupA', ), 1.0),
 (
  'sillysigns2', 'model', ('phase_4/models/props/tt_m_ara_ttc_sillyMeterSign_groupB', ), 1.0),
 (
  'mickeyhorse', 'model', ('phase_4/models/props/mickey_on_horse', ), 1.0),
 (
  'wintertree', 'model', ('phase_4/models/props/winter_tree_Christmas', ), 1.0),
 (
  'fishies', 'actor', ('phase_4/models/props/interiorfish-zero', 'phase_4/models/props/interiorfish-swim'), 0.5),
 (
  'fountain', 'model', ('phase_4/models/props/toontown_central_fountain', ), 0.25),
 (
  'streetlight', 'model', ('phase_3.5/models/props/streetlight_TT', ), 1.0),
 (
  'paintmixer', 'model', ('phase_9/models/cogHQ/PaintMixer', ), 1.0),
 (
  'stomper', 'model', ('phase_9/models/cogHQ/square_stomper', ), 1.0),
 (
  'cogdoor', 'model', ('phase_9/models/cogHQ/CogDoorHandShake', ), 1.0),
 (
  'factoryelevator', 'model', ('phase_9/models/cogHQ/Elevator', ), 1.0),
 (
  'joke', 'model', ('phase_5/models/cogdominium/tt_m_ara_csa_joke', ), 1.0),
 (
  'memo', 'model', ('phase_5/models/cogdominium/tt_m_ara_csa_memo', ), 1.0),
 (
  'cabinet', 'model', ('phase_5/models/cogdominium/tt_m_ara_cmg_cabinetSmFalling', ), 1.0),
 (
  'redtapering', 'model', ('phase_5/models/cogdominium/tt_m_ara_cfg_redTapeRing', ), 1.0),
 (
  'trolleybed', 'model', ('phase_5.5/models/estate/trolley_bed', ), 1.0),
 (
  'cogtube', 'actor', ('phase_5.5/models/estate/tt_a_ara_pty_tubeCogVictory_default', 'phase_5.5/models/estate/tt_a_ara_pty_tubeCogVictory_wave'), 0.5),
 (
  'bank', 'model', ('phase_5.5/models/estate/jellybeanBank', ), 1.0),
 (
  'panda3d', 'actor', ('phase_3/models/char/panda', 'phase_3/models/char/panda-walk'), 0.25),
 (
  'dummycog', 'actor', ('phase_13/models/parties/cogPinata_actor', 'phase_13/models/parties/cogPinata_idle_anim'), 1.0),
 (
  'cannon', 'model', ('phase_4/models/minigames/toon_cannon', ), 1.0),
 (
  'smalltrampoline', 'model', ('phase_4/models/minigames/slingshot_game_tramp', ), 0.25),
 (
  'trampoline', 'model', ('phase_13/models/parties/trampoline_model', ), 0.5),
 (
  'trolleyhole', 'model', ('phase_4/models/minigames/trolley_game_turntable', ), 0.5),
 (
  'watertower', 'model', ('phase_4/models/minigames/toon_cannon_water_tower', ), 0.25),
 (
  'brokenleaderboard', 'model', ('phase_6/models/karting/tt_m_ara_gfs_leaderBoardCrashed', ), 0.25),
 (
  'krate', 'model', ('phase_6/models/karting/krate', ), 1.0),
 (
  'wrenches', 'model', ('phase_6/models/karting/KartArea_WrenchJack', ), 0.25),
 (
  'tires', 'model', ('phase_6/models/karting/KartArea_Tires', ), 0.25),
 (
  'cone', 'model', ('phase_6/models/karting/cone', ), 1.0),
 (
  'announcerpost', 'model', ('phase_6/models/karting/announcer', ), 1.0),
 (
  'giftbox', 'model', ('phase_6/models/karting/qbox', ), 1.0),
 (
  'lawgavel', 'model', ('phase_11/models/lawbotHQ/lawbot_gavel', ), 1.0),
 (
  'gazebo', 'model', ('phase_4/models/modules/gazebo', ), 0.25),
 (
  'partystage', 'actor', ('phase_13/models/parties/tt_a_ara_pty_hydra_default', 'phase_13/models/parties/tt_a_ara_pty_hydra_dance'), 0.5),
 (
  'cogkart', 'model', ('phase_12/models/bossbotHQ/Coggolf_cart3', ), 1.0),
 (
  'icetire', 'model', ('phase_4/models/minigames/ice_game_tire', ), 1.0),
 (
  'cogbin', 'model', ('phase_14/models/props/cogbin', ), 0.1),
 (
  'dancefloor', 'model', ('phase_13/models/parties/danceFloor', ), 0.1),
 (
  'dancingbuilding', 'actor', ('phase_5/models/char/tt_r_ara_ttc_B2', 'phase_5/models/char/tt_a_ara_ttc_B2_dance'), 0.25),
 (
  'apple', 'model', ('phase_4/models/minigames/apple', ), 1.0),
 (
  'orange', 'model', ('phase_4/models/minigames/orange', ), 1.0),
 (
  'pear', 'model', ('phase_4/models/minigames/pear', ), 1.0),
 (
  'coconut', 'model', ('phase_4/models/minigames/coconut', ), 1.0),
 (
  'watermelon', 'model', ('phase_4/models/minigames/watermelon', ), 1.0),
 (
  'pineapple', 'model', ('phase_4/models/minigames/pineapple', ), 1.0),
 (
  'bookshelf', 'model', ('phase_11/models/lawbotHQ/LB_bookshelfB', ), 1),
 (
  'chair', 'model', ('phase_11/models/lawbotHQ/LB_chairA', ), 1),
 (
  'couch', 'model', ('phase_11/models/lawbotHQ/LB_couchA', ), 1),
 (
  'desk', 'model', ('phase_11/models/lawbotHQ/LB_deskA', ), 1),
 (
  'paperstack', 'model', ('phase_11/models/lawbotHQ/LB_paper_stacks', ), 1),
 (
  'paperstacksmall', 'model', ('phase_11/models/lawbotHQ/LB_paper_twist_stacks', ), 1),
 (
  'lampA', 'model', ('phase_11/models/lawbotHQ/LB_torch_lampA', ), 1),
 (
  'lampB', 'model', ('phase_11/models/lawbotHQ/LB_torch_lampB', ), 0.5),
 (
  'lampC', 'model', ('phase_11/models/lawbotHQ/LB_torch_lampC', ), 1),
 (
  'pottedplant', 'model', ('phase_11/models/lawbotHQ/LB_pottedplantA', ), 5),
 (
  'coggun', 'model', ('phase_14/models/props/cog-gun', ), 1),
 (
  'dankgun', 'model', ('phase_14/models/props/dank-gun', ), 1),
 (
  'fidgetspinner', 'model', ('phase_14/models/props/fidget-spinner', ), 1),
 (
  'greenox', 'model', ('phase_14/models/props/greenox', ), 1),
 (
  'guitar', 'model', ('phase_14/models/props/guitar', ), 1),
 (
  'witnesstand', 'model', ('phase_14/models/props/witness-stand', ), 1),
 (
  'sandwich', 'model', ('phase_6/models/golf/picnic_sandwich', ), 1),
 (
  'cupcake', 'model', ('phase_6/models/golf/picnic_cupcake', ), 1),
 (
  'cake', 'model', ('phase_6/models/golf/picnic_chocolate_cake', ), 1),
 (
  'basket', 'model', ('phase_6/models/golf/picnic_basket', ), 1),
 (
  'table', 'model', ('phase_6/models/golf/picnic_table', ), 0.5),
 (
  'cogmole', 'model', ('phase_12/models/bossbotHQ/mole_cog', ), 1),
 (
  'toonmole', 'model', ('phase_12/models/bossbotHQ/mole_norm', ), 1),
 (
  'umbrella', 'model', ('phase_4/models/minigames/slingshot_game_umbrellas', ), 1),
 (
  'treasure', 'model', ('phase_4/models/minigames/treasure', ), 0.05),
 (
  'organ', 'model', ('phase_5.5/models/estate/Organ', ), 1),
 (
  'jurychair', 'model', ('phase_11/models/lawbotHQ/JuryBoxChair', ), 0.25),
 (
  'banquettable', 'model', ('phase_12/models/bossbotHQ/BanquetTableChairs', ), 0.5),
 (
  'cogcan', 'model', ('phase_12/models/bossbotHQ/canoffood', ), 0.5),
 (
  'cogbutton', 'model', ('phase_9/models/cogHQ/CogDoor_Button', ), 1),
 (
  'statue', 'model', ('phase_14/models/props/LB_statue', ), 0.1),
 (
  'godshark', 'model', ('phase_14/models/props/god-shark', ), 1),
 (
  'goofystatue', 'model', ('phase_4/models/props/goofy_statue', ), 1)]
PropNames = []
for prop in Props:
    PropNames.append(prop[1])

for prop in PropList:
    PropNames.append(prop[0])

MaxPropCount = 2048
GreenEffectMassFlyPositions = [(-4, 0), (-4, -4), (-4, 4), (0, -4), (0, 4), (4, 4), (4, -4), (4, 0)]
GreenEffectMassFlyCogs = [('cc', 'tm', 'nd', 'gh', 'ms', 'tf', 'm', 'mh'),
 ('sc', 'pp', 'tw', 'bc', 'nc', 'mb', 'ls', 'rb'),
 ('bf', 'b', 'dt', 'ac', 'bs', 'sd', 'le', 'bw'),
 ('f', 'p', 'ym', 'mm', 'ds', 'hh', 'cr', 'tbc')]
PutOnSuitRentalDept2Cog = {'s': 'cc', 'm': 'sc', 'l': 'bf', 'c': 'f'}
PutOnSuitToonHead = [0, 3, 9]
PutOnSuitCogs = [1, 2, 4, 5, 8]
PutOnSuitSkeleRevive = [2, 5]
PutOnSuitWaiter = [3, 4, 5]
PutOnSuitSkelecog = [6, 7]
PutOnSuitVirtual = [7, 8]
PutOnSuitRental = [9]
PutOnSuitCustom = [50, 51]
PutOnSuitCustomExclusions = [50]
NPCTailorCost = 1000
DefaultIcon = 'ttoff'
Zone2String = {ToontownCentral: 'ttc', 
   DonaldsDock: 'dd', 
   DaisyGardens: 'dg', 
   MinniesMelodyland: 'mml', 
   TheBrrrgh: 'tb', 
   DonaldsDreamland: 'ddl', 
   GoofySpeedway: 'gs', 
   OutdoorZone: 'oz', 
   GolfZone: 'gz', 
   SellbotHQ: 'sbhq', 
   SellbotFactoryExt: 'sbhq-f', 
   CashbotHQ: 'cbhq', 
   LawbotHQ: 'lbhq', 
   LawbotOfficeExt: 'lbhq-o', 
   BossbotHQ: 'bbhq', 
   ToontownOutskirts: 'ttc-sz', 
   MyEstate: 'estate', 
   Tutorial: 'ttc', 
   ToontownCentralBeta: 'ttcb', 
   DaisyGardensBeta: 'dgb'}
Dept2Zone = {'s': 11000, 
   'm': 12000, 
   'l': 13000, 
   'c': 10000}
Dept2Dept = {'s': 'Sellbot', 
   'm': 'Cashbot', 
   'l': 'Lawbot', 
   'c': 'Bossbot'}
CogDepts = [
 'c', 'l', 'm', 's']
TransformationCog = 0
TransformationClassicChar = 1