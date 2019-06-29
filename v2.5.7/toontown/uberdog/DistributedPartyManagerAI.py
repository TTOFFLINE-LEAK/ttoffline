from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.task import Task
from otp.distributed.OtpDoGlobals import *
from panda3d.core import *
from toontown.parties.DistributedPartyAI import DistributedPartyAI
from datetime import datetime
from toontown.parties.PartyGlobals import *
from otp.ai.MagicWordGlobal import *

class DistributedPartyManagerAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPartyManagerAI')

    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)
        self.partyId2Zone = {}
        self.partyId2PlanningZone = {}
        self.partyId2Host = {}
        self.host2PartyId = {}
        self.avId2PartyId = {}
        self.id2Party = {}
        self.pubPartyInfo = {}
        self.idPool = range(self.air.ourChannel, self.air.ourChannel + 100000)

    def receiveId(self, ids):
        self.idPool += ids

    def _makePartyDict(self, struct):
        PARTY_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
        party = {}
        party['partyId'] = struct[0]
        party['hostId'] = struct[1]
        start = '%s-%s-%s %s:%s:00' % (struct[2], struct[3], struct[4], struct[5], struct[6])
        party['start'] = datetime.strptime(start, PARTY_TIME_FORMAT)
        end = '%s-%s-%s %s:%s:00' % (struct[7], struct[8], struct[9], struct[10], struct[11])
        party['end'] = datetime.strptime(end, PARTY_TIME_FORMAT)
        party['isPrivate'] = struct[12]
        party['inviteTheme'] = struct[13]
        party['activities'] = struct[14]
        party['decorations'] = struct[15]
        return party

    def partyManagerUdStartingUp(self):
        self.notify.info('UberDOG has said hello!')

    def partyManagerUdLost(self):
        self.notify.warning('Lost connection to the UberDOG!')

    def canBuyParties(self):
        return True

    def addPartyRequest(self, hostId, startTime, endTime, isPrivate, inviteTheme, activities, decorations, inviteeIds):
        if hostId != simbase.air.getAvatarIdFromSender():
            self.air.writeServerEvent('suspicious', avId=simbase.air.getAvatarIdFromSender(), issue='Toon tried to create a party as someone else!')
            return
        self.notify.info('Party requested: Host: %s, Start: %s, End: %s, Private: %s, Invite Theme: %s, Activities omitted, Decor omitted, Invitees: %s' % (hostId, startTime, endTime, isPrivate, inviteTheme, inviteeIds))
        simbase.air.globalPartyMgr.sendAddParty(hostId, self.host2PartyId[hostId], startTime, endTime, isPrivate, inviteTheme, activities, decorations, inviteeIds)

    def addPartyResponseUdToAi(self, partyId, errorCode, partyStruct):
        avId = partyStruct[1]
        self.notify.info('Responding to client now that UD got back to us.')
        self.sendUpdateToAvatarId(avId, 'addPartyResponse', [avId, errorCode])
        self.air.doId2do[avId].sendUpdate('setHostedParties', [[partyStruct]])

    def markInviteAsReadButNotReplied(self, todo0, todo1):
        pass

    def respondToInvite(self, todo0, todo1, todo2, todo3, todo4):
        pass

    def respondToInviteResponse(self, todo0, todo1, todo2, todo3, todo4):
        pass

    def changePrivateRequest(self, todo0, todo1):
        pass

    def changePrivateRequestAiToUd(self, todo0, todo1, todo2):
        pass

    def changePrivateResponseUdToAi(self, todo0, todo1, todo2, todo3):
        pass

    def changePrivateResponse(self, todo0, todo1, todo2):
        pass

    def changePartyStatusRequest(self, partyId, newPartyStatus):
        pass

    def changePartyStatusRequestAiToUd(self, todo0, todo1, todo2):
        pass

    def changePartyStatusResponseUdToAi(self, todo0, todo1, todo2, todo3):
        pass

    def changePartyStatusResponse(self, todo0, todo1, todo2, todo3):
        pass

    def partyInfoOfHostFailedResponseUdToAi(self, todo0):
        pass

    def givePartyRefundResponse(self, todo0, todo1, todo2, todo3, todo4):
        pass

    def getPartyZone(self, hostId, zoneId, isAvAboutToPlanParty):
        self.notify.debug('getPartyZone(hostId = %s, zoneId = %s, isAboutToPlan = %s' % (hostId, zoneId, isAvAboutToPlanParty))
        avId = self.air.getAvatarIdFromSender()
        if isAvAboutToPlanParty:
            partyId = self.idPool.pop()
            self.notify.info('Party ID: %s' % partyId)
            self.partyId2Host[partyId] = hostId
            self.partyId2PlanningZone[partyId] = zoneId
            self.host2PartyId[hostId] = partyId
            self.notify.info('Responding to a getPartyZone when planning, Av, Party, Zone: %s %s %s' % (avId, partyId, zoneId))
        else:
            if hostId not in self.host2PartyId:
                self.air.globalPartyMgr.queryPartyForHost(hostId)
                self.notify.info('Querying for details against hostId %s ' % hostId)
                return
            partyId = self.host2PartyId[hostId]
            if partyId in self.partyId2Zone:
                zoneId = self.partyId2Zone[partyId]
            else:
                self.notify.warning('getPartyZone did not match a case!')
        self.sendUpdateToAvatarId(avId, 'receivePartyZone', [hostId, partyId, zoneId])

    def partyInfoOfHostResponseUdToAi(self, partyStruct, inviteeIds):
        party = self._makePartyDict(partyStruct)
        av = self.air.doId2do.get(party['hostId'], None)
        if not av:
            return
        party['inviteeIds'] = inviteeIds
        partyId = party['partyId']
        zoneId = self.air.allocateZone(owner=self)
        self.partyId2Zone[partyId] = zoneId
        self.host2PartyId[party['hostId']] = partyId
        partyAI = DistributedPartyAI(self.air, party['hostId'], zoneId, party)
        partyAI.generateWithRequiredAndId(self.air.allocateChannel(), self.air.districtId, zoneId)
        self.id2Party[partyId] = partyAI
        self.air.globalPartyMgr.d_partyStarted(partyId, self.air.ourChannel, zoneId, av.getName())
        self.sendUpdateToAvatarId(party['hostId'], 'receivePartyZone', [party['hostId'], partyId, zoneId])
        taskMgr.doMethodLater(PARTY_DURATION, self.closeParty, 'DistributedPartyManagerAI_cleanup%s' % partyId, [partyId])
        return

    def closeParty(self, partyId):
        partyAI = self.id2Party[partyId]
        self.air.globalPartyMgr.d_partyDone(partyId)
        for av in partyAI.avIdsAtParty:
            self.sendUpdateToAvatarId(av, 'sendAvToPlayground', [av, 0])

        partyAI.b_setPartyState(PartyStatus.Finished)
        taskMgr.doMethodLater(10, self.__deleteParty, 'closeParty%d' % partyId, extraArgs=[partyId])

    def __deleteParty(self, partyId):
        partyAI = self.id2Party[partyId]
        for av in partyAI.avIdsAtParty:
            self.sendUpdateToAvatarId(av, 'sendAvToPlayground', [av, 1])

        partyAI.requestDelete()
        zoneId = self.partyId2Zone[partyId]
        del self.partyId2Zone[partyId]
        del self.id2Party[partyId]
        del self.pubPartyInfo[partyId]
        self.air.deallocateZone(zoneId)

    def freeZoneIdFromPlannedParty(self, hostId, zoneId):
        sender = self.air.getAvatarIdFromSender()
        if sender != hostId:
            self.air.writeServerEvent('suspicious', avId=sender, issue="Toon tried to free zone for someone else's party!")
            return
        partyId = self.host2PartyId[hostId]
        if partyId in self.partyId2PlanningZone:
            self.notify.info('Freeing zone...')
            self.air.deallocateZone(self.partyId2PlanningZone[partyId])
            del self.partyId2PlanningZone[partyId]
            del self.host2PartyId[hostId]
            del self.partyId2Host[partyId]

    def sendAvToPlayground(self, todo0, todo1):
        pass

    def exitParty(self, partyZone):
        avId = simbase.air.getAvatarIdFromSender()
        for partyInfo in self.pubPartyInfo.values():
            if partyInfo['zoneId'] == partyZone:
                party = self.id2Party.get(partyInfo['partyId'])
                if party:
                    party._removeAvatar(avId)

    def removeGuest(self, ownerId, avId):
        pass

    def partyManagerAIStartingUp(self, todo0, todo1):
        pass

    def partyManagerAIGoingDown(self, todo0, todo1):
        pass

    def toonHasEnteredPartyAiToUd(self, todo0):
        pass

    def toonHasExitedPartyAiToUd(self, todo0):
        pass

    def partyHasFinishedUdToAllAi(self, partyId):
        del self.pubPartyInfo[partyId]

    def updateToPublicPartyInfoUdToAllAi(self, shardId, zoneId, partyId, hostId, numGuests, maxGuests, hostName, activities, minLeft):
        started = None
        self.pubPartyInfo[partyId] = {'shardId': shardId, 
           'zoneId': zoneId, 
           'partyId': partyId, 
           'hostId': hostId, 
           'numGuests': numGuests, 
           'maxGuests': maxGuests, 
           'hostName': hostName, 
           'minLeft': minLeft, 
           'started': datetime.now(), 
           'activities': activities}
        return

    def updateToPublicPartyCountUdToAllAi(self, partyCount, partyId):
        if partyId in self.pubPartyInfo.keys():
            self.pubPartyInfo[partyId]['numGuests'] = partyCount

    def getPublicParties(self):
        p = []
        for partyId in self.pubPartyInfo:
            party = self.pubPartyInfo[partyId]
            minLeft = party['minLeft'] - int((datetime.now() - party['started']).seconds / 60)
            guests = party.get('numGuests', 0)
            if guests > 255:
                guests = 255
            else:
                if guests < 0:
                    guests = 0
            p.append([party['shardId'], party['zoneId'], guests, party.get('hostName', ''), party.get('activities', []), minLeft])

        return p

    def requestShardIdZoneIdForHostId(self, todo0):
        pass

    def sendShardIdZoneIdToAvatar(self, todo0, todo1):
        pass

    def updateAllPartyInfoToUd(self, todo0, todo1, todo2, todo3, todo4, todo5, todo6, todo7, todo8):
        pass

    def forceCheckStart(self):
        pass

    def requestMw(self, todo0, todo1, todo2, todo3):
        pass

    def mwResponseUdToAllAi(self, todo0, todo1, todo2, todo3):
        pass