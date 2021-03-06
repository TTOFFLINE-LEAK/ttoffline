from panda3d.core import Point3
from direct.directnotify import DirectNotifyGlobal
import HoodDataAI, ZoneUtil
from toontown.toonbase import ToontownGlobals
from toontown.coghq import DistributedCogHQDoorAI
from toontown.building import DistributedDoorAI, DoorTypes, DistributedBossElevatorAI, FADoorCodes
from toontown.coghq import LobbyManagerAI
from toontown.suit import DistributedBossbotBossAI
from toontown.building import DistributedBBElevatorAI
from toontown.building import DistributedBoardingPartyAI
from toontown.coghq import DistributedCogKartAI
from toontown.coghq import DistributedLawOfficeElevatorExtAI
from toontown.safezone import DistributedGolfKartAI
from toontown.suit import DistributedSuitPlannerAI

class BossbotHQDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('CogHoodAI')

    def __init__(self, air, zoneId=None):
        self.notify.debug('__init__: zoneId:%s' % zoneId)
        hoodId = ToontownGlobals.BossbotHQ
        if zoneId == None:
            zoneId = hoodId
        self.cogKarts = []
        HoodDataAI.HoodDataAI.__init__(self, air, zoneId, hoodId)
        return

    def startup(self):
        self.notify.info('Creating zone... Bossbot HQ')
        HoodDataAI.HoodDataAI.startup(self)

        def makeOfficeElevator(index, antiShuffle=0, minLaff=0):
            destZone = (ToontownGlobals.LawbotStageIntA,
             ToontownGlobals.LawbotStageIntB,
             ToontownGlobals.LawbotStageIntC,
             ToontownGlobals.LawbotStageIntD)[index]
            elev = DistributedLawOfficeElevatorExtAI.DistributedLawOfficeElevatorExtAI(self.air, self.air.lawMgr, destZone, index, antiShuffle=0, minLaff=minLaff)
            elev.generateWithRequired(ToontownGlobals.LawbotOfficeExt)
            self.addDistObj(elev)

        self.lobbyMgr = LobbyManagerAI.LobbyManagerAI(self.air, DistributedBossbotBossAI.DistributedBossbotBossAI)
        self.lobbyMgr.generateWithRequired(ToontownGlobals.BossbotLobby)
        self.addDistObj(self.lobbyMgr)
        self.lobbyElevator = DistributedBBElevatorAI.DistributedBBElevatorAI(self.air, self.lobbyMgr, ToontownGlobals.BossbotLobby, antiShuffle=1)
        self.lobbyElevator.generateWithRequired(ToontownGlobals.BossbotLobby)
        self.addDistObj(self.lobbyElevator)
        if simbase.config.GetBool('want-boarding-groups', 1):
            self.boardingParty = DistributedBoardingPartyAI.DistributedBoardingPartyAI(self.air, [self.lobbyElevator.doId], 8)
            self.boardingParty.generateWithRequired(ToontownGlobals.BossbotLobby)

        def makeDoor(destinationZone, intDoorIndex, extDoorIndex, zoneId, lock=0):
            intDoor = DistributedCogHQDoorAI.DistributedCogHQDoorAI(self.air, 0, DoorTypes.INT_COGHQ, zoneId, doorIndex=intDoorIndex, lockValue=lock)
            intDoor.zoneId = destinationZone
            extDoor = DistributedCogHQDoorAI.DistributedCogHQDoorAI(self.air, 0, DoorTypes.EXT_COGHQ, destinationZone, doorIndex=extDoorIndex, lockValue=lock)
            extDoor.setOtherDoor(intDoor)
            intDoor.setOtherDoor(extDoor)
            intDoor.generateWithRequired(destinationZone)
            intDoor.sendUpdate('setDoorIndex', [intDoor.getDoorIndex()])
            self.addDistObj(intDoor)
            extDoor.generateWithRequired(zoneId)
            extDoor.sendUpdate('setDoorIndex', [extDoor.getDoorIndex()])
            self.addDistObj(extDoor)
            return extDoor

        makeDoor(ToontownGlobals.BossbotLobby, 0, 0, ToontownGlobals.BossbotHQ, FADoorCodes.BB_DISGUISE_INCOMPLETE)
        kartIdList = self.createCogKarts()
        if simbase.config.GetBool('want-boarding-groups', 1):
            self.courseBoardingParty = DistributedBoardingPartyAI.DistributedBoardingPartyAI(self.air, kartIdList, 4)
            self.courseBoardingParty.generateWithRequired(self.zoneId)

    def createCogKarts(self):
        posList = ((-103.702, -43.47, 9.524), (-103.462, 31.377, 11.784), (-69.968, 96.113, 12.16))
        hprList = ((-68.17, 0, 0), (-107.653, 0, 0), (-122.766, 0, 0))
        mins = ToontownGlobals.FactoryLaffMinimums[3]
        kartIdList = []
        for cogCourse in xrange(len(posList)):
            pos = posList[cogCourse]
            hpr = hprList[cogCourse]
            cogKart = DistributedCogKartAI.DistributedCogKartAI(self.air, cogCourse, pos[0], pos[1], pos[2], hpr[0], hpr[1], hpr[2], self.air.countryClubMgr, minLaff=mins[cogCourse])
            cogKart.generateWithRequired(self.zoneId)
            self.cogKarts.append(cogKart)
            kartIdList.append(cogKart.doId)

        toonKart = DistributedGolfKartAI.DistributedGolfKartAI(self.air, 3, 98.4425, -104.494, -1.72622, 17.833, 0, 0)
        toonKart.generateWithRequired(self.zoneId)
        toonKart.start()
        return kartIdList

    def createPlanner(self, zoneId):
        zoneId = ZoneUtil.getTrueZoneId(zoneId, self.zoneId)
        sp = DistributedSuitPlannerAI.DistributedSuitPlannerAI(self.air, zoneId)
        sp.generateWithRequired(zoneId)
        sp.d_setZoneId(zoneId)
        self.air.suitPlanners[zoneId] = sp
        self.notify.debug('Created new SuitPlanner at %s' % zoneId)