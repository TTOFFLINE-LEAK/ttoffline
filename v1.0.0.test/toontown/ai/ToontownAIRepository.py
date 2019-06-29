import time, json, ssl, urllib, urllib2
from direct.directnotify import DirectNotifyGlobal
from direct.distributed.PyDatagram import *
from direct.task import Task
from panda3d.core import *
from panda3d.toontown import *
from libotp import WhisperPopup
from otp.ai.AIZoneData import AIZoneDataStore
from otp.ai.TimeManagerAI import TimeManagerAI
from otp.distributed.OtpDoGlobals import *
from otp.friends.FriendManagerAI import FriendManagerAI
from otp.avatar.DistributedPlayerAI import DistributedPlayerAI
from otp.otpbase import OTPGlobals
from toontown.ai.DistributedPolarPlaceEffectMgrAI import DistributedPolarPlaceEffectMgrAI
from toontown.ai.DistributedResistanceEmoteMgrAI import DistributedResistanceEmoteMgrAI
from toontown.ai.HolidayManagerAI import HolidayManagerAI
from toontown.ai.NewsManagerAI import NewsManagerAI
from toontown.ai.WelcomeValleyManagerAI import WelcomeValleyManagerAI
from toontown.building.DistributedTrophyMgrAI import DistributedTrophyMgrAI
from toontown.catalog.CatalogManagerAI import CatalogManagerAI
from toontown.coghq.CogSuitManagerAI import CogSuitManagerAI
from toontown.coghq.CountryClubManagerAI import CountryClubManagerAI
from toontown.coghq.FactoryManagerAI import FactoryManagerAI
from toontown.coghq.LawOfficeManagerAI import LawOfficeManagerAI
from toontown.coghq.MintManagerAI import MintManagerAI
from toontown.coghq.PromotionManagerAI import PromotionManagerAI
from toontown.distributed.ToontownDistrictAI import ToontownDistrictAI
from toontown.distributed.ToontownDistrictStatsAI import ToontownDistrictStatsAI
from toontown.distributed.ToontownInternalRepository import ToontownInternalRepository
from toontown.estate.EstateManagerAI import EstateManagerAI
from toontown.fishing.FishManagerAI import FishManagerAI
from toontown.hood import ZoneUtil
from toontown.hood.BRHoodDataAI import BRHoodDataAI
from toontown.hood.BossbotHQDataAI import BossbotHQDataAI
from toontown.hood.CSHoodDataAI import CSHoodDataAI
from toontown.hood.CashbotHQDataAI import CashbotHQDataAI
from toontown.hood.DDHoodDataAI import DDHoodDataAI
from toontown.hood.DGHoodDataAI import DGHoodDataAI
from toontown.hood.DLHoodDataAI import DLHoodDataAI
from toontown.hood.GSHoodDataAI import GSHoodDataAI
from toontown.hood.GZHoodDataAI import GZHoodDataAI
from toontown.hood.LawbotHQDataAI import LawbotHQDataAI
from toontown.hood.MMHoodDataAI import MMHoodDataAI
from toontown.hood.OZHoodDataAI import OZHoodDataAI
from toontown.hood.TTHoodDataAI import TTHoodDataAI
from toontown.hood.SpecialHoodDataAI import SpecialHoodDataAI
from toontown.hood.TTBetaHoodDataAI import TTBetaHoodDataAI
from toontown.hood.DGBetaHoodDataAI import DGBetaHoodDataAI
from toontown.parties.ToontownTimeManager import ToontownTimeManager
from toontown.pets.PetManagerAI import PetManagerAI
from toontown.quest.QuestManagerAI import QuestManagerAI
from toontown.racing import RaceGlobals
from toontown.racing.DistributedLeaderBoardAI import DistributedLeaderBoardAI
from toontown.racing.DistributedRacePadAI import DistributedRacePadAI
from toontown.racing.DistributedStartingBlockAI import DistributedStartingBlockAI, DistributedViewingBlockAI
from toontown.racing.DistributedViewPadAI import DistributedViewPadAI
from toontown.racing.RaceManagerAI import RaceManagerAI
from toontown.safezone.SafeZoneManagerAI import SafeZoneManagerAI
from toontown.shtiker.CogPageManagerAI import CogPageManagerAI
from toontown.spellbook.TTOffMagicWordManagerAI import TTOffMagicWordManagerAI
from toontown.suit.SuitInvasionManagerAI import SuitInvasionManagerAI
from toontown.toon import NPCToons
from toontown.toonbase import ToontownGlobals, TTLocalizer
from toontown.tutorial.TutorialManagerAI import TutorialManagerAI
from toontown.uberdog.DistributedInGameNewsMgrAI import DistributedInGameNewsMgrAI
from toontown.uberdog.DistributedPartyManagerAI import DistributedPartyManagerAI
from toontown.uberdog.ModdingManagerAI import ModdingManagerAI
from toontown.uberdog.TTOffChatManagerAI import TTOffChatManagerAI
from toontown.uberdog.DiscordManagerAI import DiscordManagerAI

class ToontownAIRepository(ToontownInternalRepository):
    notify = DirectNotifyGlobal.directNotify.newCategory('ToontownAIRepository')

    def __init__(self, baseChannel, serverId, districtName, districtLimit, districtDescription, districtWebsiteId, eventId, defaultAccessLevel):
        ToontownInternalRepository.__init__(self, baseChannel, serverId, dcSuffix='AI')
        self.districtName = districtName
        self.districtLimit = districtLimit
        if self.districtLimit < ToontownGlobals.MIN_POP:
            self.districtLimit = ToontownGlobals.MIN_POP
        else:
            if self.districtLimit > ToontownGlobals.HIGH_POP:
                self.districtLimit = ToontownGlobals.HIGH_POP
        self.districtDescription = districtDescription
        self.districtWebsiteId = districtWebsiteId
        self.eventId = eventId
        self.defaultAccessLevel = defaultAccessLevel
        self.doLiveUpdates = self.config.GetBool('want-live-updates', True)
        self.wantCogdominiums = self.config.GetBool('want-cogdominiums', True)
        self.wantEmblems = self.config.GetBool('want-emblems', True)
        self.useAllMinigames = self.config.GetBool('want-all-minigames', True)
        self.wantEmblems = self.config.GetBool('want-emblems', True)
        self.districtId = None
        self.district = None
        self.districtStats = None
        self.districtFull = False
        self.timeManager = None
        self.newsManager = None
        self.holidayManager = None
        self.welcomeValleyManager = None
        self.catalogManager = None
        self.zoneDataStore = None
        self.inGameNewsMgr = None
        self.trophyMgr = None
        self.petMgr = None
        self.dnaStoreMap = {}
        self.dnaDataMap = {}
        self.zoneTable = {}
        self.hoods = []
        self.buildingManagers = {}
        self.suitPlanners = {}
        self.suitInvasionManager = None
        self.zoneAllocator = None
        self.zoneId2owner = {}
        self.questManager = None
        self.cogPageManager = None
        self.fishManager = None
        self.factoryMgr = None
        self.mintMgr = None
        self.lawMgr = None
        self.countryClubMgr = None
        self.promotionMgr = None
        self.cogSuitMgr = None
        self.partyManager = None
        self.safeZoneManager = None
        self.raceMgr = None
        self.polarPlaceEffectMgr = None
        self.resistanceEmoteMgr = None
        self.tutorialManager = None
        self.friendManager = None
        self.chatManager = None
        self.toontownTimeManager = None
        self.estateMgr = None
        self.magicWordManager = None
        self.deliveryManager = None
        self.cogSuitMessageSent = False
        self.propGenerators = {}
        self.propGeneratorsLocked = False
        self.moddingManager = None
        self.discordManager = None
        return

    def getTrackClsends(self):
        return False

    def handleConnected(self):
        ToontownInternalRepository.handleConnected(self)
        self.districtId = self.allocateChannel()
        self.notify.info('Creating district (%d)...' % self.districtId)
        self.district = ToontownDistrictAI(self)
        self.district.setName(self.districtName)
        self.district.setDescription(self.districtDescription)
        self.district.generateWithRequiredAndId(self.districtId, self.getGameDoId(), OTP_ZONE_ID_MANAGEMENT)
        self.notify.info('Claiming ownership of district (%d)...' % self.districtId)
        datagram = PyDatagram()
        datagram.addServerHeader(self.districtId, self.ourChannel, STATESERVER_OBJECT_SET_AI)
        datagram.addChannel(self.ourChannel)
        self.send(datagram)
        self.notify.info('Creating local objects...')
        self.createLocals()
        self.notify.info('Creating global objects...')
        self.createGlobals()
        self.notify.info('Creating zones (Playgrounds and Cog HQs)...')
        self.createZones()
        self.notify.info('Making district available...')
        self.district.b_setAvailable(1)
        self.notify.info('District is now ready. Have fun in Toontown Offline!')

    def createLocals(self):
        self.holidayManager = HolidayManagerAI(self)
        self.zoneDataStore = AIZoneDataStore()
        self.petMgr = PetManagerAI(self)
        self.suitInvasionManager = SuitInvasionManagerAI(self)
        self.zoneAllocator = UniqueIdAllocator(ToontownGlobals.DynamicZonesBegin, ToontownGlobals.DynamicZonesEnd)
        self.questManager = QuestManagerAI(self)
        self.cogPageManager = CogPageManagerAI(self)
        self.fishManager = FishManagerAI(self)
        self.factoryMgr = FactoryManagerAI(self)
        self.mintMgr = MintManagerAI(self)
        self.lawMgr = LawOfficeManagerAI(self)
        self.countryClubMgr = CountryClubManagerAI(self)
        self.promotionMgr = PromotionManagerAI(self)
        self.cogSuitMgr = CogSuitManagerAI(self)
        self.raceMgr = RaceManagerAI(self)
        self.toontownTimeManager = ToontownTimeManager(serverTimeUponLogin=int(time.time()), globalClockRealTimeUponLogin=globalClock.getRealTime())

    def createGlobals(self):
        districtStatsId = self.allocateChannel()
        self.notify.info('Creating district stats AI (%d)...' % districtStatsId)
        self.districtStats = ToontownDistrictStatsAI(self)
        self.districtStats.settoontownDistrictId(self.districtId)
        self.districtStats.generateWithRequiredAndId(districtStatsId, self.getGameDoId(), OTP_ZONE_ID_DISTRICTS)
        self.timeManager = TimeManagerAI(self)
        self.timeManager.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)
        self.newsManager = NewsManagerAI(self)
        self.newsManager.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)
        self.catalogManager = CatalogManagerAI(self)
        self.catalogManager.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)
        self.inGameNewsMgr = DistributedInGameNewsMgrAI(self)
        self.inGameNewsMgr.setLatestIssueStr('2013-08-22 23:49:46')
        self.inGameNewsMgr.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)
        self.trophyMgr = DistributedTrophyMgrAI(self)
        self.trophyMgr.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)
        self.partyManager = DistributedPartyManagerAI(self)
        self.partyManager.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)
        self.safeZoneManager = SafeZoneManagerAI(self)
        self.safeZoneManager.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)
        self.polarPlaceEffectMgr = DistributedPolarPlaceEffectMgrAI(self)
        self.polarPlaceEffectMgr.generateWithRequired(3821)
        self.resistanceEmoteMgr = DistributedResistanceEmoteMgrAI(self)
        self.resistanceEmoteMgr.generateWithRequired(9720)
        self.tutorialManager = TutorialManagerAI(self)
        self.tutorialManager.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)
        self.friendManager = FriendManagerAI(self)
        self.friendManager.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)
        self.chatManager = TTOffChatManagerAI(self)
        self.chatManager.generateWithRequiredAndId(OTP_DO_ID_CHAT_MANAGER, self.getGameDoId(), OTP_ZONE_ID_MANAGEMENT)
        self.estateMgr = EstateManagerAI(self)
        self.estateMgr.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)
        self.magicWordManager = TTOffMagicWordManagerAI(self)
        self.magicWordManager.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)
        self.deliveryManager = self.generateGlobalObject(OTP_DO_ID_TOONTOWN_DELIVERY_MANAGER, 'DistributedDeliveryManager')
        self.banManager = self.generateGlobalObject(OTP_DO_ID_BAN_MANAGER, 'BanManager')
        self.moddingManager = ModdingManagerAI(self)
        self.moddingManager.generateWithRequiredAndId(OTP_DO_ID_MODDING_MANAGER, self.getGameDoId(), OTP_ZONE_ID_MANAGEMENT)
        self.moddingManager.setColorsAiToUd(self.moddingManager.getColors())
        self.moddingManager.setCardsAiToUd(self.moddingManager.getCards())
        self.discordManager = DiscordManagerAI(self)
        self.discordManager.generateWithRequiredAndId(OTP_DO_ID_DISCORD_MANAGER, self.getGameDoId(), OTP_ZONE_ID_MANAGEMENT)

    def createHood(self, hoodCtr, zoneId):
        if zoneId != ToontownGlobals.BossbotHQ:
            self.dnaStoreMap[zoneId] = DNAStorage()
            self.dnaDataMap[zoneId] = self.loadDNAFileAI(self.dnaStoreMap[zoneId], self.genDNAFileName(zoneId))
            if zoneId in ToontownGlobals.HoodHierarchy:
                for streetId in ToontownGlobals.HoodHierarchy[zoneId]:
                    self.dnaStoreMap[streetId] = DNAStorage()
                    self.dnaDataMap[streetId] = self.loadDNAFileAI(self.dnaStoreMap[streetId], self.genDNAFileName(streetId))

        hood = hoodCtr(self, zoneId)
        hood.startup()
        self.hoods.append(hood)

    def createZones(self):
        NPCToons.generateZone2NpcDict()
        self.zoneTable[ToontownGlobals.ToontownCentral] = (
         (
          ToontownGlobals.ToontownCentral, 1, 0), (ToontownGlobals.SillyStreet, 1, 1),
         (
          ToontownGlobals.LoopyLane, 1, 1),
         (
          ToontownGlobals.PunchlinePlace, 1, 1))
        self.createHood(TTHoodDataAI, ToontownGlobals.ToontownCentral)
        self.zoneTable[ToontownGlobals.DonaldsDock] = (
         (
          ToontownGlobals.DonaldsDock, 1, 0), (ToontownGlobals.BarnacleBoulevard, 1, 1),
         (
          ToontownGlobals.SeaweedStreet, 1, 1), (ToontownGlobals.LighthouseLane, 1, 1))
        self.createHood(DDHoodDataAI, ToontownGlobals.DonaldsDock)
        self.zoneTable[ToontownGlobals.DaisyGardens] = (
         (
          ToontownGlobals.DaisyGardens, 1, 0), (ToontownGlobals.ElmStreet, 1, 1),
         (
          ToontownGlobals.MapleStreet, 1, 1), (ToontownGlobals.OakStreet, 1, 1))
        self.createHood(DGHoodDataAI, ToontownGlobals.DaisyGardens)
        self.zoneTable[ToontownGlobals.MinniesMelodyland] = (
         (
          ToontownGlobals.MinniesMelodyland, 1, 0), (ToontownGlobals.AltoAvenue, 1, 1),
         (
          ToontownGlobals.BaritoneBoulevard, 1, 1), (ToontownGlobals.TenorTerrace, 1, 1))
        self.createHood(MMHoodDataAI, ToontownGlobals.MinniesMelodyland)
        self.zoneTable[ToontownGlobals.TheBrrrgh] = (
         (
          ToontownGlobals.TheBrrrgh, 1, 0), (ToontownGlobals.WalrusWay, 1, 1),
         (
          ToontownGlobals.SleetStreet, 1, 1), (ToontownGlobals.PolarPlace, 1, 1))
        self.createHood(BRHoodDataAI, ToontownGlobals.TheBrrrgh)
        self.zoneTable[ToontownGlobals.DonaldsDreamland] = (
         (
          ToontownGlobals.DonaldsDreamland, 1, 0), (ToontownGlobals.LullabyLane, 1, 1),
         (
          ToontownGlobals.PajamaPlace, 1, 1))
        self.createHood(DLHoodDataAI, ToontownGlobals.DonaldsDreamland)
        self.zoneTable[ToontownGlobals.SellbotHQ] = (
         (
          ToontownGlobals.SellbotHQ, 0, 1), (ToontownGlobals.SellbotFactoryExt, 0, 1))
        self.createHood(CSHoodDataAI, ToontownGlobals.SellbotHQ)
        self.zoneTable[ToontownGlobals.CashbotHQ] = (
         (
          ToontownGlobals.CashbotHQ, 0, 1),)
        self.createHood(CashbotHQDataAI, ToontownGlobals.CashbotHQ)
        self.zoneTable[ToontownGlobals.LawbotHQ] = (
         (
          ToontownGlobals.LawbotHQ, 0, 1),)
        self.createHood(LawbotHQDataAI, ToontownGlobals.LawbotHQ)
        self.zoneTable[ToontownGlobals.BossbotHQ] = (
         (
          ToontownGlobals.BossbotHQ, 0, 0),)
        self.createHood(BossbotHQDataAI, ToontownGlobals.BossbotHQ)
        self.zoneTable[ToontownGlobals.GoofySpeedway] = (
         (
          ToontownGlobals.GoofySpeedway, 1, 0),)
        self.createHood(GSHoodDataAI, ToontownGlobals.GoofySpeedway)
        self.zoneTable[ToontownGlobals.OutdoorZone] = (
         (
          ToontownGlobals.OutdoorZone, 1, 0),)
        self.createHood(OZHoodDataAI, ToontownGlobals.OutdoorZone)
        self.zoneTable[ToontownGlobals.GolfZone] = (
         (
          ToontownGlobals.GolfZone, 1, 0),)
        self.createHood(GZHoodDataAI, ToontownGlobals.GolfZone)
        self.zoneTable[ToontownGlobals.SpecialHood] = (
         (
          ToontownGlobals.SpecialHood, 1, 0), (ToontownGlobals.AirborneAcres, 1, 0),
         (
          ToontownGlobals.TutorialTerrace, 1, 1), (ToontownGlobals.ScrewballStadium, 1, 0),
         (
          ToontownGlobals.RusticRaceway, 1, 0), (ToontownGlobals.CityCircuit, 1, 0),
         (
          ToontownGlobals.CorkscrewColiseum, 1, 0), (ToontownGlobals.BlizzardBoulevard, 1, 0))
        self.createHood(SpecialHoodDataAI, ToontownGlobals.SpecialHood)
        self.zoneTable[ToontownGlobals.ToontownCentralBeta] = (
         (
          ToontownGlobals.ToontownCentralBeta, 1, 0),)
        self.createHood(TTBetaHoodDataAI, ToontownGlobals.ToontownCentralBeta)
        self.notify.info('Assigning initial Cog buildings and Field Offices...')
        for suitPlanner in self.suitPlanners.values():
            suitPlanner.assignInitialSuitBuildings()

    def sendPing(self, task=None):
        if self.districtWebsiteId != '' and config.GetBool('mini-server', False):
            gameMode = TTLocalizer.MiniserverLegit if self.defaultAccessLevel == 'NO_ACCESS' else TTLocalizer.MiniserverCheats
            try:
                self.sendPingToAPI(self.districtWebsiteId, name=self.districtName, desc=self.districtDescription, population=self.districtStats.getAvatarCount(), mode=gameMode)
            except:
                self.notify.info('Could not ping the Toontown Offline website! Make sure you are connected to the Internet.')

            return Task.again
        return Task.done

    def sendPingToAPI(self, serverId, **kwargs):
        columns = self.getColumns()
        data = {'uniqueId': serverId}
        for arg in kwargs.keys():
            if arg in columns:
                data['%s' % arg] = kwargs[arg]
                continue
            self.notify.info('%s is not a valid argument!' % arg)

        resp = self.HTTPReq('http://localhost/api/miniservers/ping', data=data)
        if not resp['success']:
            self.notify.info('Could not ping the website! (Message: %s)' % resp['message'])
            return
        data = {'uniqueId': serverId}
        resp = self.HTTPReq('http://localhost/api/miniservers/id2icon', data=data)
        if not resp['success']:
            self.notify.info('Could not retrieve server icon! (Message: %s)' % resp['message'])
            return
        if resp['message']:
            self.district.b_setIconPath(resp['message'])

    def getColumns(self):
        data = self.HTTPReq('http://localhost/api/miniservers/columns')
        return data

    def HTTPReq(self, url, data=None):
        if type(data) == dict:
            data = urllib.urlencode(data)
            data = data.encode('utf-8')
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64)', 'Authorization': 'Basic dHRvZmY6SmF6enlTdHVkaW9z'}
        request = urllib2.Request(url, data, headers=headers)
        response = urllib2.urlopen(request, context=context)
        data = json.loads(response.read().decode())
        return data

    def incrementPopulation(self):
        self.districtStats.b_setAvatarCount(self.districtStats.getAvatarCount() + 1)
        self.avatarCountCheck()

    def decrementPopulation(self):
        self.districtStats.b_setAvatarCount(self.districtStats.getAvatarCount() - 1)
        self.avatarCountCheck()

    def avatarCountCheck(self):
        self.sendPing()
        if not self.districtFull and self.districtStats.getAvatarCount() >= self.districtLimit:
            self.districtFull = True
            self.notify.warning('Reached player limit! Making district unavailable...')
            self.district.b_setFull(0)
            self.notify.warning('District is now unavailable. Incoming connections will be rejected.')
        if self.districtFull and self.districtStats.getAvatarCount() < self.districtLimit:
            self.districtFull = False
            self.notify.info('Player count dropped! Making district available...')
            self.district.b_setFull(1)
            self.notify.info('District is now available. Incoming connections will be accepted.')

    def getAvatarExitEvent(self, avId):
        return 'distObjDelete-%d' % avId

    def getZoneDataStore(self):
        return self.zoneDataStore

    def genDNAFileName(self, zoneId):
        zoneId = ZoneUtil.getCanonicalZoneId(zoneId)
        hoodId = ZoneUtil.getCanonicalHoodId(zoneId)
        hood = ToontownGlobals.dnaMap[hoodId]
        if hoodId == zoneId:
            zoneId = 'sz'
            phase = ToontownGlobals.phaseMap[hoodId]
        else:
            phase = ToontownGlobals.streetPhaseMap[hoodId]
        if 'outdoor_zone' in hood or 'golf_zone' in hood:
            phase = '6'
        return 'phase_%s/dna/%s_%s.dna' % (phase, hood, zoneId)

    def findFishingPonds(self, dnaData, zoneId, area):
        fishingPonds = []
        fishingPondGroups = []
        if isinstance(dnaData, DNAGroup) and 'fishing_pond' in dnaData.getName():
            fishingPondGroups.append(dnaData)
            pond = self.fishManager.generatePond(area, zoneId)
            fishingPonds.append(pond)
        else:
            if isinstance(dnaData, DNAVisGroup):
                zoneId = ZoneUtil.getTrueZoneId(int(dnaData.getName().split(':')[0]), zoneId)
        for i in xrange(dnaData.getNumChildren()):
            foundFishingPonds, foundFishingPondGroups = self.findFishingPonds(dnaData.at(i), zoneId, area)
            fishingPonds.extend(foundFishingPonds)
            fishingPondGroups.extend(foundFishingPondGroups)

        return (
         fishingPonds, fishingPondGroups)

    def findFishingSpots(self, dnaData, fishingPond):
        fishingSpots = []
        if isinstance(dnaData, DNAGroup) and dnaData.getName()[:13] == 'fishing_spot_':
            spot = self.fishManager.generateSpots(dnaData, fishingPond)
            fishingSpots.append(spot)
        for i in xrange(dnaData.getNumChildren()):
            foundFishingSpots = self.findFishingSpots(dnaData.at(i), fishingPond)
            fishingSpots.extend(foundFishingSpots)

        return fishingSpots

    def findClassicFishingSpots(self, dnaData, fishingPond):
        fishingSpots = []
        if isinstance(dnaData, DNAGroup) and dnaData.getName()[:21] == 'classic_fishing_spot_':
            spot = self.fishManager.generateClassicSpots(dnaData, fishingPond)
            fishingSpots.append(spot)
        for i in xrange(dnaData.getNumChildren()):
            foundFishingSpots = self.findClassicFishingSpots(dnaData.at(i), fishingPond)
            fishingSpots.extend(foundFishingSpots)

        return fishingSpots

    def findPartyHats(self, dnaData, zoneId):
        return []

    def loadDNAFileAI(self, dnaStore, dnaFileName):
        return loadDNAFileAI(dnaStore, dnaFileName)

    def allocateZone(self, owner=None):
        zoneId = self.zoneAllocator.allocate()
        if owner:
            self.zoneId2owner[zoneId] = owner
        return zoneId

    def deallocateZone(self, zone):
        if self.zoneId2owner.get(zone):
            del self.zoneId2owner[zone]
        self.zoneAllocator.free(zone)

    def trueUniqueName(self, idString):
        return self.uniqueName(idString)

    def findRacingPads(self, dnaData, zoneId, area, type='racing_pad', overrideDNAZone=False):
        racingPads, racingPadGroups = [], []
        if type in dnaData.getName():
            if type == 'racing_pad':
                nameSplit = dnaData.getName().split('_')
                racePad = DistributedRacePadAI(self)
                racePad.setArea(area)
                racePad.index = int(nameSplit[2])
                racePad.genre = nameSplit[3]
                trackInfo = RaceGlobals.getNextRaceInfo(-1, racePad.genre, racePad.index)
                racePad.setTrackInfo([trackInfo[0], trackInfo[1]])
                racePad.laps = trackInfo[2]
                racePad.generateWithRequired(zoneId)
                racingPads.append(racePad)
                racingPadGroups.append(dnaData)
            elif type == 'viewing_pad':
                viewPad = DistributedViewPadAI(self)
                viewPad.setArea(area)
                viewPad.generateWithRequired(zoneId)
                racingPads.append(viewPad)
                racingPadGroups.append(dnaData)
        for i in xrange(dnaData.getNumChildren()):
            foundRacingPads, foundRacingPadGroups = self.findRacingPads(dnaData.at(i), zoneId, area, type, overrideDNAZone)
            racingPads.extend(foundRacingPads)
            racingPadGroups.extend(foundRacingPadGroups)

        return (
         racingPads, racingPadGroups)

    def findStartingBlocks(self, dnaData, pad):
        startingBlocks = []
        for i in xrange(dnaData.getNumChildren()):
            groupName = dnaData.getName()
            blockName = dnaData.at(i).getName()
            if 'starting_block' in blockName:
                cls = DistributedStartingBlockAI if 'racing_pad' in groupName else DistributedViewingBlockAI
                x, y, z = dnaData.at(i).getPos()
                h, p, r = dnaData.at(i).getHpr()
                padLocationId = int(dnaData.at(i).getName()[(-1)])
                startingBlock = cls(self, pad, x, y, z, h, p, r, padLocationId)
                startingBlock.generateWithRequired(pad.zoneId)
                startingBlocks.append(startingBlock)

        return startingBlocks

    def getAvatarDisconnectReason(self, avId):
        return self.timeManager.avId2disconnectcode.get(avId, ToontownGlobals.DisconnectUnknown)

    def findLeaderBoards(self, dnaData, zoneId):
        leaderboards = []
        if 'leaderBoard' in dnaData.getName():
            x, y, z = dnaData.getPos()
            h, p, r = dnaData.getHpr()
            leaderboard = DistributedLeaderBoardAI(self, dnaData.getName(), x, y, z, h, p, r)
            leaderboard.generateWithRequired(zoneId)
            leaderboards.append(leaderboard)
        for i in xrange(dnaData.getNumChildren()):
            foundLeaderBoards = self.findLeaderBoards(dnaData.at(i), zoneId)
            leaderboards.extend(foundLeaderBoards)

        return leaderboards

    def systemMessage(self, message):
        for doId, do in self.doId2do.items():
            if isinstance(do, DistributedPlayerAI):
                if str(doId)[0] != str(self.districtId)[0]:
                    do.d_setSystemMessage(0, message, WhisperPopup.WTSystem)

    def announceMaintenance(self, reason, type, time):
        self.systemMessage(TTLocalizer.ServerShutdownAnnouncement.format(type, time))
        taskMgr.doMethodLater(time, self.shutdownMaintenance, 'shutdownMaintenance', extraArgs=[reason])
        if time - 60.0 > 1:
            taskMgr.doMethodLater(time - 60.0, self.systemMessage, 'shutdownMaintenance', extraArgs=[TTLocalizer.ServerShutdownWarning.format(type)])

    def shutdownMaintenance(self, reason):
        for doId, do in self.doId2do.items():
            if isinstance(do, DistributedPlayerAI):
                if str(doId)[0] != str(self.districtId)[0]:
                    do.sendSetKick(reason=reason, target=do, silent=3)