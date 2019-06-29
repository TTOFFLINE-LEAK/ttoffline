import json, ssl, urllib, urllib2
from direct.distributed.PyDatagram import *
from otp.ai.AIZoneData import *
from otp.ai.MagicWordManagerAI import MagicWordManagerAI
from otp.ai.TimeManagerAI import TimeManagerAI
from otp.distributed.OtpDoGlobals import *
from otp.friends.FriendManagerAI import FriendManagerAI
from toontown.ai.DistributedSillyMeterMgrAI import DistributedSillyMeterMgrAI
from toontown.ai.FishManagerAI import FishManagerAI
from toontown.ai.HolidayManagerAI import HolidayManagerAI
from toontown.ai.NewsManagerAI import NewsManagerAI
from toontown.distributed.ToontownDistrictAI import ToontownDistrictAI
from toontown.distributed.ToontownDistrictStatsAI import ToontownDistrictStatsAI
from toontown.distributed.ToontownInternalRepository import ToontownInternalRepository
from toontown.dna.DNAParser import loadDNAFileAI
from toontown.dna.DNAStorage import DNAStorage
from toontown.hood import CSHoodDataAI, CashbotHQDataAI, LawbotHQDataAI, BossbotHQDataAI
from toontown.hood import TTHoodDataAI, DDHoodDataAI, DGHoodDataAI, BRHoodDataAI, MMHoodDataAI, DLHoodDataAI, OZHoodDataAI, GSHoodDataAI, GZHoodDataAI, SBHoodDataAI, ODGHoodDataAI, TFHoodDataAI, ZoneUtil
from toontown.toon import NPCToons
if config.GetBool('want-code-redemption', True):
    from toontown.coderedemption.TTCodeRedemptionMgrAI import TTCodeRedemptionMgrAI
if config.GetBool('want-estates', True):
    from toontown.estate.EstateManagerAI import EstateManagerAI
if config.GetBool('want-parties', True):
    from toontown.uberdog.DistributedPartyManagerAI import DistributedPartyManagerAI
from toontown.toonbase import ToontownGlobals
from toontown.quest.QuestManagerAI import QuestManagerAI
from toontown.building.DistributedTrophyMgrAI import DistributedTrophyMgrAI
from toontown.shtiker.CogPageManagerAI import CogPageManagerAI
from toontown.coghq.FactoryManagerAI import FactoryManagerAI
from toontown.coghq.MintManagerAI import MintManagerAI
from toontown.coghq.LawOfficeManagerAI import LawOfficeManagerAI
from toontown.coghq.PromotionManagerAI import PromotionManagerAI
from toontown.coghq.CogSuitManagerAI import CogSuitManagerAI
from toontown.coghq.CountryClubManagerAI import CountryClubManagerAI
from toontown.suit.SuitInvasionManagerAI import SuitInvasionManagerAI
from toontown.tutorial.TutorialManagerAI import TutorialManagerAI
from toontown.catalog.CatalogManagerAI import CatalogManagerAI
if config.GetBool('want-pets', True):
    from toontown.pets.PetManagerAI import PetManagerAI
if config.GetBool('want-event-manager', False):
    from toontown.duckhunt.DistributedEventManagerAI import DistributedEventManagerAI
if config.GetBool('want-news-page', False):
    from toontown.uberdog.DistributedInGameNewsMgrAI import DistributedInGameNewsMgrAI

class ToontownAIRepository(ToontownInternalRepository):

    def __init__(self, baseChannel, serverId, districtName, holidayPasscode, serverDescription, miniserverId):
        ToontownInternalRepository.__init__(self, baseChannel, serverId, dcSuffix='AI')
        self.districtName = districtName
        self.holidayPasscode = holidayPasscode
        self.holidayValue = 0
        self.serverDescription = serverDescription
        self.zoneAllocator = UniqueIdAllocator(ToontownGlobals.DynamicZonesBegin, ToontownGlobals.DynamicZonesEnd)
        self.zoneId2owner = {}
        NPCToons.generateZone2NpcDict()
        self.zoneTable = {}
        self.hoodArray = []
        self.hoods = []
        self._dnaStoreMap = {}
        self.zoneDataStore = AIZoneDataStore()
        self.useAllMinigames = self.config.GetBool('want-all-minigames', False)
        self.doLiveUpdates = self.config.GetBool('want-live-updates', True)
        self.reachedPlayerLimit = False
        self.fishManager = FishManagerAI()
        self.questManager = QuestManagerAI(self)
        self.cogPageManager = CogPageManagerAI()
        self.factoryMgr = FactoryManagerAI(self)
        self.mintMgr = MintManagerAI(self)
        self.lawOfficeMgr = LawOfficeManagerAI(self)
        self.countryClubMgr = CountryClubManagerAI(self)
        self.promotionMgr = PromotionManagerAI(self)
        self.cogSuitMgr = CogSuitManagerAI(self)
        self.wantCogdominiums = self.config.GetBool('want-cogdominums', False)
        self.buildingManagers = {}
        self.suitPlanners = {}
        self.inEpisode = False
        self.cutsceneActivated = False
        self.currentEpisode = None
        self.wantMiniServer = config.GetBool('want-mini-server', False)
        if not self.wantMiniServer:
            self.wantPrologue = config.GetBool('want-prologue', False)
        else:
            self.wantPrologue = False
        return

    def getTrackClsends(self):
        return False

    def handleConnected(self):
        ToontownInternalRepository.handleConnected(self)
        if self.holidayPasscode != '':
            self.initServerHoliday()
        self.districtId = self.allocateChannel()
        self.notify.info('Creating district (%d)...' % self.districtId)
        self.distributedDistrict = ToontownDistrictAI(self)
        self.distributedDistrict.setName(self.districtName)
        self.distributedDistrict.setDescription(self.serverDescription)
        self.distributedDistrict.setHolidayPasscode(self.holidayValue)
        self.distributedDistrict.generateWithRequiredAndId(self.districtId, self.getGameDoId(), OTP_ZONE_ID_MANAGEMENT)
        self.notify.info('Claiming ownership of district (%d)...' % self.districtId)
        dg = PyDatagram()
        dg.addServerHeader(self.districtId, self.ourChannel, STATESERVER_OBJECT_SET_AI)
        dg.addChannel(self.ourChannel)
        self.send(dg)
        self.notify.info('Creating global objects...')
        self.createGlobals()
        self.notify.info('Creating zones (Playgrounds and Cog HQs)...')
        self.createZones()

    def districtReady(self):
        for sp in self.suitPlanners.values():
            sp.assignInitialSuitBuildings()

        self.notify.info('Making district available...')
        self.distributedDistrict.b_setAvailable(1)
        self.notify.info('District is now ready. Have fun in Toontown!')
        self.sendPing()
        taskMgr.doMethodLater(30, self.sendPing, 'pingWebsite')

    def HTTPReq(self, url, data=None):
        if type(data) == dict:
            data = urllib.urlencode(data)
            data = data.encode('utf-8')
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64)'}
        request = urllib2.Request(url, data, headers=headers)
        response = urllib2.urlopen(request, context=context)
        data = json.loads(response.read().decode())
        return data

    def sendPing(self, task=None):
        if self.wantMiniServer:
            serverId = config.GetString('server-id', '')
            if serverId != '':
                gameMode = 'Elections' if config.GetBool('want-doomsday', False) else 'Normal'
                try:
                    self.sendPingToAPI(serverId, name=self.districtName, desc=self.serverDescription, population=self.districtStats.getAvatarCount(), mode=gameMode)
                except:
                    self.notify.info('Could not ping the website! ')

                return Task.again
        return Task.done

    def getColumns(self):
        data = self.HTTPReq('https://ttoffline.com/api/miniservers/columns')
        return data

    def sendPingToAPI(self, serverId, **kwargs):
        columns = self.getColumns()
        data = {'uniqueId': serverId}
        for arg in kwargs.keys():
            if arg in columns:
                data['%s' % arg] = kwargs[arg]
                continue
            self.notify.info('%s is not a valid argument!' % arg)

        resp = self.HTTPReq('https://ttoffline.com/api/miniservers/ping', data=data)
        if not resp['success']:
            self.notify.info('Could not ping the website! (Message: %s)' % resp['message'])

    def incrementPopulation(self):
        self.districtStats.b_setAvatarCount(self.districtStats.getAvatarCount() + 1)
        self.avatarCountCheck()
        self.sendPing()

    def decrementPopulation(self):
        self.districtStats.b_setAvatarCount(self.districtStats.getAvatarCount() - 1)
        self.avatarCountCheck()
        self.sendPing()

    def avatarCountCheck(self):
        if not self.reachedPlayerLimit and self.districtStats.getAvatarCount() >= config.GetInt('miniserver-player-limit', ToontownGlobals.DefaultMiniserverLimit):
            self.reachedPlayerLimit = True
            self.notify.warning('Reached player limit! Making district unavailable...')
            self.distributedDistrict.b_setAvailable(0)
            self.notify.warning('District is now unavailable. Incoming connections will be rejected.')
        if self.reachedPlayerLimit and self.districtStats.getAvatarCount() < config.GetInt('miniserver-player-limit', ToontownGlobals.DefaultMiniserverLimit):
            self.reachedPlayerLimit = False
            self.notify.info('Player count dropped! Making district available...')
            self.distributedDistrict.b_setAvailable(1)
            self.notify.info('District is now available. Incoming connections will be accepted.')

    def allocateZone(self, owner=None):
        zoneId = self.zoneAllocator.allocate()
        if owner:
            self.zoneId2owner[zoneId] = owner
        return zoneId

    def deallocateZone(self, zone):
        if self.zoneId2owner.get(zone):
            del self.zoneId2owner[zone]
        self.zoneAllocator.free(zone)

    def getZoneDataStore(self):
        return self.zoneDataStore

    def getAvatarExitEvent(self, avId):
        return 'distObjDelete-%d' % avId

    def getAvatarZoneChangeEvent(self, avId):
        return 'DOChangeZone-%d' % avId

    def avIsInEpisode(self):
        return self.currentEpisode is not None

    def createGlobals(self):
        self.districtStats = ToontownDistrictStatsAI(self)
        self.districtStats.settoontownDistrictId(self.districtId)
        self.districtStats.generateWithRequiredAndId(self.allocateChannel(), self.getGameDoId(), OTP_ZONE_ID_DISTRICTS)
        self.notify.info('Created district stats AI (%d).' % self.districtStats.doId)
        self.timeManager = TimeManagerAI(self)
        self.timeManager.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)
        self.newsManager = NewsManagerAI(self)
        self.newsManager.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)
        self.suitInvasionManager = SuitInvasionManagerAI(self)
        self.holidayManager = HolidayManagerAI(self)
        self.magicWordManager = MagicWordManagerAI(self)
        self.magicWordManager.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)
        self.friendManager = FriendManagerAI(self)
        self.friendManager.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)
        self.sillyMeterMgr = DistributedSillyMeterMgrAI(self)
        self.sillyMeterMgr.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)
        if config.GetBool('want-code-redemption', True):
            self.codeRedemptionMgr = TTCodeRedemptionMgrAI(self)
            self.codeRedemptionMgr.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)
        if config.GetBool('want-parties', True):
            self.partyManager = DistributedPartyManagerAI(self)
            self.partyManager.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)
            self.globalPartyMgr = self.generateGlobalObject(OTP_DO_ID_GLOBAL_PARTY_MANAGER, 'GlobalPartyManager')
        if config.GetBool('want-estates', True):
            self.estateManager = EstateManagerAI(self)
            self.estateManager.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)
        self.trophyMgr = DistributedTrophyMgrAI(self)
        self.trophyMgr.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)
        if simbase.wantPets:
            self.petMgr = PetManagerAI(self)
        self.tutorialManager = TutorialManagerAI(self)
        self.tutorialManager.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)
        self.catalogManager = CatalogManagerAI(self)
        self.catalogManager.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)
        if config.GetBool('want-event-manager', False):
            self.eventManager = DistributedEventManagerAI(self)
            self.eventManager.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)
        if config.GetBool('want-news-page', False):
            self.inGameNewsMgr = DistributedInGameNewsMgrAI(self)
            self.inGameNewsMgr.setLatestIssueStr('2013-08-22 23:49:46')
            self.inGameNewsMgr.generateWithRequired(OTP_ZONE_ID_MANAGEMENT)
        self.banManager = self.generateGlobalObject(OTP_DO_ID_BAN_MANAGER, 'BanManager')

    def createZones(self):
        if config.GetBool('want-playgrounds', True):
            if config.GetBool('want-toontown-central', True):
                self.hoodArray.append(TTHoodDataAI.TTHoodDataAI)
                self.zoneTable[2000] = ((2000, 1, 0), (2100, 1, 1), (2200, 1, 1), (2300, 1, 1))
            if config.GetBool('want-donalds-dock', True):
                self.hoodArray.append(DDHoodDataAI.DDHoodDataAI)
                self.zoneTable[1000] = ((1000, 1, 0), (1100, 1, 1), (1200, 1, 1), (1300, 1, 1))
            if config.GetBool('want-daisy-gardens', True):
                self.hoodArray.append(DGHoodDataAI.DGHoodDataAI)
                self.zoneTable[5000] = ((5000, 1, 0), (5100, 1, 1), (5200, 1, 1), (5300, 1, 1))
            if config.GetBool('want-minnies-melodyland', True):
                self.hoodArray.append(MMHoodDataAI.MMHoodDataAI)
                self.zoneTable[4000] = ((4000, 1, 0), (4100, 1, 1), (4200, 1, 1), (4300, 1, 1))
            if config.GetBool('want-the-brrrgh', True):
                self.hoodArray.append(BRHoodDataAI.BRHoodDataAI)
                self.zoneTable[3000] = ((3000, 1, 0), (3100, 1, 1), (3200, 1, 1), (3300, 1, 1))
            if config.GetBool('want-donalds-dreamland', True):
                self.hoodArray.append(DLHoodDataAI.DLHoodDataAI)
                self.zoneTable[9000] = ((9000, 1, 0), (9100, 1, 1), (9200, 1, 1))
            if config.GetBool('want-goofy-speedway', True):
                self.hoodArray.append(GSHoodDataAI.GSHoodDataAI)
                self.zoneTable[8000] = ((8000, 1, 0), )
            if config.GetBool('want-acorn-acres', True):
                self.hoodArray.append(OZHoodDataAI.OZHoodDataAI)
                self.zoneTable[6000] = ((6000, 1, 0), )
            if config.GetBool('want-toonfest', True):
                self.hoodArray.append(TFHoodDataAI.TFHoodDataAI)
                self.zoneTable[ToontownGlobals.ToonFest] = ((ToontownGlobals.ToonFest, 1, 0),)
            if config.GetBool('want-minigolf', True):
                self.hoodArray.append(GZHoodDataAI.GZHoodDataAI)
                self.zoneTable[17000] = ((17000, 1, 0), )
            if not self.wantMiniServer:
                if config.GetBool('want-scrooge-bank', True):
                    self.hoodArray.append(SBHoodDataAI.SBHoodDataAI)
                    self.zoneTable[1002000] = ()
                if config.GetBool('want-old-daisy-gardens', True):
                    self.hoodArray.append(ODGHoodDataAI.ODGHoodDataAI)
                    self.zoneTable[21000] = ((21000, 1, 0), (21300, 1, 1))
        if config.GetBool('want-cog-headquarters', True):
            if config.GetBool('want-sellbot-hq', True):
                self.hoodArray.append(CSHoodDataAI.CSHoodDataAI)
                self.zoneTable[11000] = ((11000, 1, 0), (11200, 1, 0))
            if config.GetBool('want-cashbot-hq', True):
                self.hoodArray.append(CashbotHQDataAI.CashbotHQDataAI)
                self.zoneTable[12000] = ((12000, 1, 0), )
            if config.GetBool('want-lawbot-hq', True):
                self.hoodArray.append(LawbotHQDataAI.LawbotHQDataAI)
                self.zoneTable[13000] = ((13000, 1, 0), )
            if config.GetBool('want-bossbot-hq', True):
                self.hoodArray.append(BossbotHQDataAI.BossbotHQDataAI)
                self.zoneTable[10000] = ((10000, 0, 0), (10900, 1, 0))
        self.__nextHood(0)

    def __nextHood(self, hoodIndex):
        if hoodIndex >= len(self.hoodArray):
            self.districtReady()
            return Task.done
        self.hoods.append(self.hoodArray[hoodIndex](self))
        taskMgr.doMethodLater(0, ToontownAIRepository.__nextHood, 'nextHood', [self, hoodIndex + 1])
        return Task.done

    def dnaStoreMap(self, zone):
        dnaStore = self._dnaStoreMap.get(zone)
        if not dnaStore:
            dnaStore = DNAStorage()
            self.loadDNAFileAI(dnaStore, self.genDNAFileName(zone))
            self._dnaStoreMap[zone] = dnaStore
        return dnaStore

    def genDNAFileName(self, zoneId):
        zoneId = ZoneUtil.getCanonicalZoneId(zoneId)
        hoodId = ZoneUtil.getCanonicalHoodId(zoneId)
        hood = ToontownGlobals.dnaMap[hoodId]
        if hoodId == zoneId:
            zoneId = 'sz'
            phase = ToontownGlobals.phaseMap[hoodId]
        else:
            phase = ToontownGlobals.streetPhaseMap[hoodId]
        return 'phase_%s/dna/%s_%s.jazz' % (phase, hood, zoneId)

    def loadDNAFileAI(self, dnaStore, filename):
        return loadDNAFileAI(dnaStore, filename)

    def initServerHoliday(self):
        self.notify.info('Holiday Passcode detected. Initalizing Holiday...')
        holidayPasscodes = ['holidayHW2017811154', 'holidayHW2017421808', 'holidayHW2017475201', 'holidayHW2017669818',
         'holidayHW2017001496', 'holidayHW2017139447']
        for passcode in holidayPasscodes:
            if passcode == self.holidayPasscode:
                self.holidayValue = holidayPasscodes.index(passcode) + 1

        if self.holidayPasscode in holidayPasscodes:
            self.notify.info("Holdiay Passcode '%s' is active on this District!" % self.holidayPasscode)
        else:
            self.notify.info("Holdiay Passcode '%s' is not a valid Passcode!" % self.holidayPasscode)