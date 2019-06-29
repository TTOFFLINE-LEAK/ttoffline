from otp.otpbase import OTPGlobals
from toontown.toonbase import ToontownGlobals
from toontown.hood import ZoneUtil

def canAccess(avatarId, zoneId, function=''):
    avatar = simbase.air.doId2do.get(avatarId)
    if avatar and avatar.getGameAccess() != OTPGlobals.AccessFull and not openToAll(zoneId, avatar):
        if cmp(function, 'DistributedBoardingPartyAI.checkBoard') == 0:
            return False
        simbase.air.writeServerEvent('suspicious', avId=avatarId, issue='User with rights: %s requesting enter for paid access content without proper rights in zone %s from %s' % (avatar.getGameAccess(), zoneId, function))
        return False
    return True


def openToAll(zoneId, avatar):
    allowed = False
    canonicalZoneId = ZoneUtil.getCanonicalHoodId(zoneId)
    allowedZones = [ToontownGlobals.ToontownCentral,
     ToontownGlobals.MyEstate,
     ToontownGlobals.GoofySpeedway,
     ToontownGlobals.Tutorial]
    specialZones = [ToontownGlobals.SellbotLobby]
    if ToontownGlobals.SELLBOT_NERF_HOLIDAY in simbase.air.holidayManager.currentHolidays:
        specialZones.append(ToontownGlobals.SellbotHQ)
    ownerId = simbase.air.estateManager.getOwnerFromZone(zoneId)
    if ownerId:
        for zone in simbase.air.estateManager.getEstateZones(ownerId):
            specialZones.append(zone)

    if canonicalZoneId in allowedZones or avatar.isInEstate():
        allowed = True
    else:
        if zoneId in specialZones:
            allowed = True
        else:
            if canonicalZoneId >= ToontownGlobals.DynamicZonesBegin and not avatar.getTutorialAck():
                zoneDict = simbase.air.tutorialManager.playerDict.get(avatar.doId)
                if zoneDict:
                    allowed = True
    return allowed


def canWearSuit(avatarId, zoneId):
    canonicalZoneId = ZoneUtil.getCanonicalHoodId(zoneId)
    allowedSuitZones = [ToontownGlobals.LawbotHQ,
     ToontownGlobals.CashbotHQ,
     ToontownGlobals.SellbotHQ,
     ToontownGlobals.BossbotHQ]
    if canonicalZoneId in allowedSuitZones:
        return True
    if zoneId >= ToontownGlobals.DynamicZonesBegin:
        return True
    return False