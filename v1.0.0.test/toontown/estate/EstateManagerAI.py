import functools
from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.fsm.FSM import FSM
from toontown.estate import HouseGlobals
from toontown.estate.DistributedHouseAI import DistributedHouseAI
from toontown.toon import ToonDNA

class LoadHouseOperation(FSM):

    def __init__(self, mgr, estate, index, avatar, callback):
        FSM.__init__(self, 'LoadHouseOperation')
        self.mgr = mgr
        self.estate = estate
        self.index = index
        self.avatar = avatar
        self.callback = callback
        self.done = False
        self.houseId = None
        self.house = None
        self.gender = None
        return

    def start(self):
        if self.avatar is None:
            taskMgr.doMethodLater(0.0, self.demand, 'makeBlankHouse-%s' % id(self), extraArgs=['MakeBlankHouse'])
            return
        style = ToonDNA.ToonDNA()
        style.makeFromNetString(self.avatar.get('setDNAString')[0])
        self.houseId = self.avatar.get('setHouseId', [0])[0]
        self.gender = style.gender
        if self.houseId == 0:
            self.demand('CreateHouse')
        else:
            self.demand('LoadHouse')
        return

    def enterMakeBlankHouse(self):
        self.house = DistributedHouseAI(self.mgr.air)
        self.house.setHousePos(self.index)
        self.house.setColor(self.index)
        self.house.generateWithRequired(self.estate.zoneId)
        self.estate.houses[self.index] = self.house
        self.demand('Off')

    def enterCreateHouse(self):
        self.mgr.air.dbInterface.createObject(self.mgr.air.dbId, self.mgr.air.dclassesByName['DistributedHouseAI'], {'setName': [self.avatar['setName'][0]], 'setAvatarId': [
                         self.avatar['avId']]}, self.__handleHouseCreated)

    def __handleHouseCreated(self, houseId):
        if self.state != 'CreateHouse':
            return
        av = self.mgr.air.doId2do.get(self.avatar['avId'])
        if av:
            av.b_setHouseId(houseId)
        else:
            self.mgr.air.dbInterface.updateObject(self.mgr.air.dbId, self.avatar['avId'], self.mgr.air.dclassesByName['DistributedToonAI'], {'setHouseId': [houseId]})
        self.houseId = houseId
        self.demand('LoadHouse')

    def enterLoadHouse(self):
        self.mgr.air.sendActivate(self.houseId, self.mgr.air.districtId, self.estate.zoneId, self.mgr.air.dclassesByName['DistributedHouseAI'], {'setHousePos': [self.index], 'setColor': [
                      self.index], 
           'setName': [
                     self.avatar['setName'][0]], 
           'setAvatarId': [
                         self.avatar['avId']]})
        self.acceptOnce('generate-%d' % self.houseId, self.__handleHouseGenerated)

    def __handleHouseGenerated(self, house):
        house.estate = self.estate
        house.interior.gender = self.gender
        house.interior.start()
        self.house = house
        self.estate.houses[self.index] = self.house
        if config.GetBool('want-gardening', False):
            self.house.createGardenManager()
        self.demand('Off')

    def exitLoadHouse(self):
        self.ignore('generate-%d' % self.houseId)

    def enterOff(self):
        self.done = True
        self.callback(self.house)


class LoadEstateOperation(FSM):

    def __init__(self, mgr, callback):
        FSM.__init__(self, 'LoadEstateOperation')
        self.mgr = mgr
        self.callback = callback
        self.estate = None
        self.accId = None
        self.zoneId = None
        self.avIds = None
        self.avatars = None
        self.houseOperations = None
        self.petOperations = None
        return

    def start(self, accId, zoneId):
        self.accId = accId
        self.zoneId = zoneId
        self.demand('QueryAccount')

    def enterQueryAccount(self):
        self.mgr.air.dbInterface.queryObject(self.mgr.air.dbId, self.accId, self.__handleQueryAccount)

    def __handleQueryAccount(self, dclass, fields):
        if self.state != 'QueryAccount':
            return
        if dclass != self.mgr.air.dclassesByName['AccountAI']:
            self.mgr.notify.warning('Account %d has non-account dclass %d!' % (self.accId, dclass))
            self.demand('Failure')
            return
        self.accFields = fields
        self.estateId = fields.get('ESTATE_ID', 0)
        self.demand('QueryAvatars')

    def enterQueryAvatars(self):
        self.avIds = self.accFields.get('ACCOUNT_AV_SET', [0] * 6)
        self.avatars = {}
        for index, avId in enumerate(self.avIds):
            if avId == 0:
                self.avatars[index] = None
                continue
            self.mgr.air.dbInterface.queryObject(self.mgr.air.dbId, avId, functools.partial(self.__handleQueryAvatar, index=index))

        return

    def __handleQueryAvatar(self, dclass, fields, index):
        if self.state != 'QueryAvatars':
            return
        if dclass != self.mgr.air.dclassesByName['DistributedToonAI']:
            self.mgr.notify.warning('Account %d has avatar %d with non-Toon dclass %d!' % (self.accId, self.avIds[index], dclass))
            self.demand('Failure')
            return
        fields['avId'] = self.avIds[index]
        self.avatars[index] = fields
        if len(self.avatars) == 6:
            self.__gotAllAvatars()

    def __gotAllAvatars(self):
        if self.estateId:
            self.demand('LoadEstate')
        else:
            self.demand('CreateEstate')

    def enterCreateEstate(self):
        self.mgr.air.dbInterface.createObject(self.mgr.air.dbId, self.mgr.air.dclassesByName['DistributedEstateAI'], {}, self.__handleEstateCreated)

    def __handleEstateCreated(self, estateId):
        if self.state != 'CreateEstate':
            return
        self.estateId = estateId
        self.mgr.air.dbInterface.updateObject(self.mgr.air.dbId, self.accId, self.mgr.air.dclassesByName['AccountAI'], {'ESTATE_ID': estateId})
        self.demand('LoadEstate')

    def enterLoadEstate(self):
        fields = {'setSlot%dToonId' % i:(avId,) for i, avId in enumerate(self.avIds)}
        self.mgr.air.sendActivate(self.estateId, self.mgr.air.districtId, self.zoneId, self.mgr.air.dclassesByName['DistributedEstateAI'], fields)
        self.acceptOnce('generate-%d' % self.estateId, self.__handleEstateGenerated)

    def __handleEstateGenerated(self, estate):
        self.estate = estate
        self.estate.pets = []
        ownerId = self.mgr.getOwnerFromZone(self.estate.zoneId)
        owner = self.mgr.air.doId2do.get(ownerId)
        if owner:
            self.mgr.toon2estate[owner] = self.estate
        self.estate.b_setIdList(self.avIds)
        self.demand('LoadHouses')

    def exitLoadEstate(self):
        self.ignore('generate-%d' % self.estateId)

    def enterLoadHouses(self):
        self.houseOperations = []
        for houseIndex in xrange(6):
            houseOperation = LoadHouseOperation(self.mgr, self.estate, houseIndex, self.avatars[houseIndex], self.__handleHouseLoaded)
            self.houseOperations.append(houseOperation)
            houseOperation.start()

    def __handleHouseLoaded(self, house):
        if self.state != 'LoadHouses':
            house.requestDelete()
            return
        if all(houseOperation.done for houseOperation in self.houseOperations):
            self.demand('LoadPets')

    def enterLoadPets(self):
        self.petOperations = []
        for houseIndex in xrange(6):
            av = self.avatars[houseIndex]
            if av and av['setPetId'][0] != 0:
                petOperation = LoadPetOperation(self.mgr, self.estate, av, self.__handlePetLoaded)
                self.petOperations.append(petOperation)
                petOperation.start()

        if not self.petOperations:
            taskMgr.doMethodLater(0, lambda : self.demand('Finished'), 'no-pets', extraArgs=[])

    def __handlePetLoaded(self, pet):
        if self.state != 'LoadPets':
            pet.requestDelete()
            return
        if all(petOperation.done for petOperation in self.petOperations):
            self.demand('Finished')

    def enterFinished(self):
        self.petOperations = []
        self.callback(True)

    def enterFailure(self):
        self.cancel()
        self.callback(False)

    def cancel(self):
        if self.estate:
            self.estate.destroy()
            self.estate = None
        self.demand('Off')
        return


class LoadPetOperation(FSM):

    def __init__(self, mgr, estate, toon, callback):
        FSM.__init__(self, 'LoadPetFSM')
        self.mgr = mgr
        self.estate = estate
        self.toon = toon
        self.callback = callback
        self.done = False
        self.petId = 0

    def start(self):
        if type(self.toon) == dict:
            self.petId = self.toon['setPetId'][0]
        else:
            self.petId = self.toon.getPetId()
        if self.petId not in self.mgr.air.doId2do:
            self.mgr.air.sendActivate(self.petId, self.mgr.air.districtId, self.estate.zoneId)
            self.acceptOnce('generate-%d' % self.petId, self.__generated)
        else:
            self.__generated(self.mgr.air.doId2do[self.petId])

    def __generated(self, pet):
        self.pet = pet
        self.estate.pets.append(pet)
        self.demand('Off')

    def enterOff(self):
        self.ignore('generate-%d' % self.petId)
        self.done = True
        self.callback(self.pet)


class EstateManagerAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('EstateManagerAI')

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.toon2estate = {}
        self.estate = {}
        self.estate2toons = {}
        self.estate2timeout = {}
        self.zone2toons = {}
        self.zone2owner = {}
        self.petOperations = []

    def getEstateZone(self, avId, name):
        senderId = self.air.getAvatarIdFromSender()
        accId = self.air.getAccountIdFromSender()
        senderAv = self.air.doId2do.get(senderId)
        if not senderAv:
            self.air.writeServerEvent('suspicious', senderId, 'Sent getEstateZone() but not on district!')
            return
        if avId and avId != senderId:
            av = self.air.doId2do.get(avId)
            if av and av.dclass == self.air.dclassesByName['DistributedToonAI']:
                estate = self.toon2estate.get(av)
                if estate:
                    avId = estate.owner.doId
                    zoneId = estate.zoneId
                    self._mapToEstate(senderAv, estate)
                    self._unloadEstate(senderAv)
                    if senderAv and senderAv.getPetId() != 0:
                        pet = self.air.doId2do.get(senderAv.getPetId())
                        if pet:
                            self.acceptOnce(self.air.getAvatarExitEvent(senderAv.getPetId()), self.__handleLoadPet, extraArgs=[
                             estate, senderAv])
                            pet.requestDelete()
                        else:
                            self.__handleLoadPet(estate, senderAv)
                    if hasattr(senderAv, 'enterEstate'):
                        senderAv.enterEstate(avId, zoneId)
                    self.sendUpdateToAvatarId(senderId, 'setEstateZone', [avId, zoneId])
            self.sendUpdateToAvatarId(senderId, 'setEstateZone', [0, 0])
            return
        estate = getattr(senderAv, 'estate', None)
        if estate:
            self._mapToEstate(senderAv, senderAv.estate)
            if senderAv and senderAv.getPetId() != 0:
                pet = self.air.doId2do.get(senderAv.getPetId())
                if pet:
                    self.acceptOnce(self.air.getAvatarExitEvent(senderAv.getPetId()), self.__handleLoadPet, extraArgs=[
                     estate, senderAv])
                    pet.requestDelete()
                else:
                    self.__handleLoadPet(estate, senderAv)
            if hasattr(senderAv, 'enterEstate'):
                senderAv.enterEstate(senderId, estate.zoneId)
            self.sendUpdateToAvatarId(senderId, 'setEstateZone', [senderId, estate.zoneId])
            if estate in self.estate2timeout:
                self.estate2timeout[estate].remove()
                del self.estate2timeout[estate]
            return
        if getattr(senderAv, 'loadEstateOperation', None):
            return
        zoneId = self.air.allocateZone()
        self.zone2owner[zoneId] = avId

        def estateLoaded(success):
            if success:
                senderAv.estate = senderAv.loadEstateOperation.estate
                senderAv.estate.owner = senderAv
                self._mapToEstate(senderAv, senderAv.estate)
                if hasattr(senderAv, 'enterEstate'):
                    senderAv.enterEstate(senderId, zoneId)
                self.sendUpdateToAvatarId(senderId, 'setEstateZone', [senderId, zoneId])
            else:
                self.sendUpdateToAvatarId(senderId, 'setEstateZone', [0, 0])
                self.air.deallocateZone(zoneId)
                del self.zone2owner[zoneId]
            senderAv.loadEstateOperation = None
            return

        self.acceptOnce(self.air.getAvatarExitEvent(senderAv.doId), self.__handleUnexpectedExit, extraArgs=[senderAv])
        if senderAv and senderAv.getPetId() != 0:
            pet = self.air.doId2do.get(senderAv.getPetId())
            if pet:
                self.acceptOnce(self.air.getAvatarExitEvent(senderAv.getPetId()), self.__handleLoadEstate, extraArgs=[
                 senderAv, estateLoaded, accId, zoneId])
                pet.requestDelete()
                return
        self.__handleLoadEstate(senderAv, estateLoaded, accId, zoneId)
        return

    def __handleUnexpectedExit(self, senderAv):
        self._unmapFromEstate(senderAv)
        self._unloadEstate(senderAv)

    def exitEstate(self):
        senderId = self.air.getAvatarIdFromSender()
        senderAv = self.air.doId2do.get(senderId)
        if not senderAv:
            self.air.writeServerEvent('suspicious', senderId, 'Sent exitEstate() but not on district!')
            return
        self._unmapFromEstate(senderAv)
        self._unloadEstate(senderAv)

    def removeFriend(self, ownerId, avId):
        if not (ownerId or avId):
            return
        owner = self.air.doId2do.get(ownerId)
        if not owner:
            return
        friend = self.air.doId2do.get(avId)
        if not friend:
            return
        estate = self.estate.get(ownerId)
        if not estate:
            return
        if ownerId not in estate.getIdList():
            return
        toons = self.estate2toons.get(estate, [])
        if owner not in toons and friend not in toons:
            return
        friendInList = False
        for friendPair in owner.getFriendsList():
            if type(friendPair) == tuple:
                friendId = friendPair[0]
            else:
                friendId = friendPair
            if friendId == avId:
                friendInList = True
                break

        if not friendInList:
            self.sendUpdateToAvatarId(friend.doId, 'sendAvToPlayground', [friend.doId, 1])

    def _unloadEstate(self, av):
        if getattr(av, 'estate', None):
            estate = av.estate
            if estate not in self.estate2timeout:
                self.estate2timeout[estate] = taskMgr.doMethodLater(HouseGlobals.BOOT_GRACE_PERIOD, self._cleanupEstate, estate.uniqueName('unload-estate'), extraArgs=[
                 estate])
            self._sendToonsToPlayground(av.estate, 0)
        if getattr(av, 'loadEstateOperation', None):
            self.air.deallocateZone(av.loadEstateOperation.zoneId)
            av.loadEstateOperation.cancel()
            av.loadEstateOperation = None
        if av and hasattr(av, 'exitEstate') and hasattr(av, 'isInEstate') and av.isInEstate():
            av.exitEstate()
        if av and av.getPetId() != 0:
            self.ignore(self.air.getAvatarExitEvent(av.getPetId()))
            pet = self.air.doId2do.get(av.getPetId())
            if pet:
                pet.requestDelete()
        self.ignore(self.air.getAvatarExitEvent(av.doId))
        return

    def _mapToEstate(self, av, estate):
        self._unmapFromEstate(av)
        self.estate[av.doId] = estate
        self.estate2toons.setdefault(estate, []).append(av)
        if av not in self.toon2estate:
            self.toon2estate[av] = estate
        self.zone2toons.setdefault(estate.zoneId, []).append(av.doId)

    def _unmapFromEstate(self, av):
        estate = self.toon2estate.get(av)
        if not estate:
            return
        try:
            del self.estate[av.doId]
        except KeyError:
            pass
        else:
            del self.toon2estate[av]
            try:
                self.estate2toons[estate].remove(av)
            except (KeyError, ValueError):
                pass

            try:
                self.zone2toons[estate.zoneId].remove(av.doId)
            except (KeyError, ValueError):
                pass

    def _cleanupEstate(self, estate):
        self._sendToonsToPlayground(estate, 1)
        for av in self.estate2toons.get(estate, []):
            try:
                del self.estate[av.doId]
                del self.toon2estate[av]
            except KeyError:
                pass

        try:
            del self.estate2toons[estate]
        except KeyError:
            pass
        else:
            try:
                del self.zone2toons[estate.zoneId]
            except KeyError:
                pass

        if estate in self.estate2timeout:
            del self.estate2timeout[estate]
        estate.destroy()
        estate.owner.estate = None
        for pet in estate.pets:
            pet.requestDelete()

        estate.pets = []
        self.air.deallocateZone(estate.zoneId)
        del self.zone2owner[estate.zoneId]
        return

    def _sendToonsToPlayground(self, estate, reason):
        for toon in self.estate2toons.get(estate, []):
            self.sendUpdateToAvatarId(toon.doId, 'sendAvToPlayground', [toon.doId, reason])

    def _lookupEstate(self, toon):
        return self.toon2estate.get(toon)

    def getEstateZones(self, ownerId):
        toon = self.air.doId2do.get(ownerId)
        if not toon:
            return []
        estate = self.toon2estate.get(toon)
        if not estate:
            return []
        return [
         estate.zoneId]

    def getEstateHouseZones(self, ownerId):
        houseZones = []
        toon = self.air.doId2do.get(ownerId)
        if not toon:
            return houseZones
        estate = self.toon2estate.get(toon)
        if not estate:
            return houseZones
        houses = estate.houses
        for house in houses:
            houseZones.append(house.interiorZone)

        return houseZones

    def getOwnerFromZone(self, zoneId):
        return self.zone2owner.get(zoneId, 0)

    def __handleLoadPet(self, estate, av):
        petOperation = LoadPetOperation(self, estate, av, self.__handlePetLoaded)
        self.petOperations.append(petOperation)
        petOperation.start()

    def __handlePetLoaded(self, _):
        if all(petOperation.done for petOperation in self.petOperations):
            self.petOperations = []

    def __handleLoadEstate(self, av, callback, accId, zoneId):
        self._unmapFromEstate(av)
        av.loadEstateOperation = LoadEstateOperation(self, callback)
        av.loadEstateOperation.start(accId, zoneId)