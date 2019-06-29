from otp.uberdog.GameServicesManagerUD import *
from toontown.makeatoon.NameGenerator import NameGenerator
from toontown.toon.ToonDNA import ToonDNA
from toontown.toonbase import TTLocalizer

def judgeName(name):
    return True


class SetNamePatternOperation(AvatarOperation):
    notify = DirectNotifyGlobal.directNotify.newCategory('SetNamePatternOperation')
    postAccountState = 'RetrieveAvatar'

    def __init__(self, gameServicesManager, target):
        AvatarOperation.__init__(self, gameServicesManager, target)
        self.avId = None
        self.pattern = None
        return

    def enterStart(self, avId, pattern):
        self.avId = avId
        self.pattern = pattern
        self.demand('RetrieveAccount')

    def enterRetrieveAvatar(self):
        if self.avId and self.avId not in self.avList:
            self.demand('Kill', 'Tried to name an avatar not in the account!')
            return
        self.gameServicesManager.air.dbInterface.queryObject(self.gameServicesManager.air.dbId, self.avId, self.__handleAvatar)

    def __handleAvatar(self, dclass, fields):
        if dclass != self.gameServicesManager.air.dclassesByName['DistributedToonUD']:
            self.demand('Kill', "One of the account's avatars is invalid!")
            return
        if fields['WishNameState'][0] != 'OPEN':
            self.demand('Kill', 'Avatar is not in a nameable state!')
        self.demand('SetName')

    def enterSetName(self):
        parts = []
        for p, f in self.pattern:
            part = self.gameServicesManager.nameGenerator.nameDictionary.get(p, ('',
                                                                                 ''))[1]
            if f:
                part = part[:1].upper() + part[1:]
            else:
                part = part.lower()
            parts.append(part)

        parts[2] += parts.pop(3)
        while '' in parts:
            parts.remove('')

        name = (' ').join(parts)
        self.gameServicesManager.air.dbInterface.updateObject(self.gameServicesManager.air.dbId, self.avId, self.gameServicesManager.air.dclassesByName['DistributedToonUD'], {'WishNameState': ('LOCKED', ), 'WishName': ('', ), 
           'setName': (
                     name,)})
        self.gameServicesManager.air.writeServerEvent('avatar-named', self.avId, name)
        self.gameServicesManager.sendUpdateToAccountId(self.target, 'namePatternResponse', [self.avId, 1])
        self.demand('Off')


class SetNameTypedOperation(AvatarOperation):
    notify = DirectNotifyGlobal.directNotify.newCategory('SetNameTypedOperation')
    postAccountState = 'RetrieveAvatar'

    def __init__(self, gameServicesManager, target):
        AvatarOperation.__init__(self, gameServicesManager, target)
        self.avId = None
        self.name = None
        return

    def enterStart(self, avId, name):
        self.avId = avId
        self.name = name
        if self.avId:
            self.demand('RetrieveAccount')
            return
        self.demand('JudgeName')

    def enterRetrieveAvatar(self):
        if self.avId and self.avId not in self.avList:
            self.demand('Kill', 'Tried to name an avatar not in the account!')
            return
        self.gameServicesManager.air.dbInterface.queryObject(self.gameServicesManager.air.dbId, self.avId, self.__handleAvatar)

    def __handleAvatar(self, dclass, fields):
        if dclass != self.gameServicesManager.air.dclassesByName['DistributedToonUD']:
            self.demand('Kill', "One of the account's avatars is invalid!")
            return
        if fields['WishNameState'][0] != 'OPEN':
            self.demand('Kill', 'Avatar is not in a nameable state!')
        self.demand('JudgeName')

    def enterJudgeName(self):
        status = judgeName(self.name)
        tempAutoAcceptBool = True
        if self.avId and status:
            if tempAutoAcceptBool:
                self.gameServicesManager.air.dbInterface.updateObject(self.gameServicesManager.air.dbId, self.avId, self.gameServicesManager.air.dclassesByName['DistributedToonUD'], {'WishNameState': ('LOCKED', ), 'WishName': ('', ), 
                   'setName': (
                             self.name,)})
            else:
                self.gameServicesManager.air.dbInterface.updateObject(self.gameServicesManager.air.dbId, self.avId, self.gameServicesManager.air.dclassesByName['DistributedToonUD'], {'WishNameState': ('PENDING', ), 'WishName': (
                              self.name,)})
        if self.avId:
            if tempAutoAcceptBool:
                self.gameServicesManager.air.writeServerEvent('avatar-name-accepted', self.avId, self.name)
            else:
                self.gameServicesManager.air.writeServerEvent('avatar-wish-name', self.avId, self.name)
        if status and tempAutoAcceptBool:
            status = 2
        self.gameServicesManager.sendUpdateToAccountId(self.target, 'nameTypedResponse', [self.avId, status])
        self.demand('Off')


class CreateAvatarOperation(GameOperation):
    notify = DirectNotifyGlobal.directNotify.newCategory('CreateAvatarOperation')

    def __init__(self, gameServicesManager, target):
        GameOperation.__init__(self, gameServicesManager, target)
        self.index = None
        self.dna = None
        self.name = None
        return

    def enterStart(self, dna, name, index):
        if index >= 6:
            self.demand('Kill', 'Invalid index specified!')
            return
        if not ToonDNA().isValidNetString(dna):
            self.demand('Kill', 'Invalid DNA specified!')
            return
        self.index = index
        self.dna = dna
        self.name = name
        self.demand('RetrieveAccount')

    def enterRetrieveAccount(self):
        self.gameServicesManager.air.dbInterface.queryObject(self.gameServicesManager.air.dbId, self.target, self.__handleRetrieve)

    def __handleRetrieve(self, dclass, fields):
        if dclass != self.gameServicesManager.air.dclassesByName['AccountUD']:
            self.demand('Kill', 'Your account object (%s) was not found in the database!' % dclass)
            return
        self.account = fields
        self.avList = self.account['ACCOUNT_AV_SET']
        self.avList = self.avList[:6]
        self.avList += [0] * (6 - len(self.avList))
        if self.avList[self.index]:
            self.demand('Kill', 'This avatar slot is already taken by another avatar!')
            return
        self.demand('CreateAvatar')

    def enterCreateAvatar(self):
        dna = ToonDNA()
        dna.makeFromNetString(self.dna)
        colorString = TTLocalizer.NumToColor[dna.headColor]
        animalType = TTLocalizer.AnimalToSpecies[dna.getAnimal()]
        name = (' ').join((colorString, animalType))
        if self.name != '':
            toonFields = {'setName': (self.name,), 'WishNameState': ('LOCKED', ), 'WishName': ('', ), 
               'setDNAString': (
                              self.dna,), 
               'setDISLid': (
                           self.target,), 
               'setNametagStyle': (100, )}
        else:
            toonFields = {'setName': (name,), 'WishNameState': ('OPEN', ), 
               'WishName': ('', ), 
               'setDNAString': (
                              self.dna,), 
               'setDISLid': (
                           self.target,), 
               'setNametagStyle': (100, )}
        self.gameServicesManager.air.dbInterface.createObject(self.gameServicesManager.air.dbId, self.gameServicesManager.air.dclassesByName['DistributedToonUD'], toonFields, self.__handleCreate)

    def __handleCreate(self, avId):
        if not avId:
            self.demand('Kill', 'Database failed to create the new avatar object!')
            return
        self.avId = avId
        self.demand('StoreAvatar')

    def enterStoreAvatar(self):
        self.avList[self.index] = self.avId
        self.gameServicesManager.air.dbInterface.updateObject(self.gameServicesManager.air.dbId, self.target, self.gameServicesManager.air.dclassesByName['AccountUD'], {'ACCOUNT_AV_SET': self.avList}, {'ACCOUNT_AV_SET': self.account['ACCOUNT_AV_SET']}, self.__handleStoreAvatar)

    def __handleStoreAvatar(self, fields):
        if fields:
            self.demand('Kill', 'Database failed to associate the new avatar to your account!')
            return
        self.gameServicesManager.air.writeServerEvent('avatar-created', self.avId, self.target, self.dna.encode('hex'), self.index)
        self.gameServicesManager.sendUpdateToAccountId(self.target, 'createAvatarResponse', [self.avId])
        self.demand('Off')


class AcknowledgeNameOperation(AvatarOperation):
    notify = DirectNotifyGlobal.directNotify.newCategory('AcknowledgeNameFSM')
    postAccountState = 'GetTargetAvatar'

    def __init__(self, gameServicesManager, target):
        AvatarOperation.__init__(self, gameServicesManager, target)
        self.avId = None
        return

    def enterStart(self, avId):
        self.avId = avId
        self.demand('RetrieveAccount')

    def enterGetTargetAvatar(self):
        if self.avId not in self.avList:
            self.demand('Kill', 'Tried to acknowledge name on an avatar not in the account!')
            return
        self.gameServicesManager.air.dbInterface.queryObject(self.gameServicesManager.air.dbId, self.avId, self.__handleAvatar)

    def __handleAvatar(self, dclass, fields):
        if dclass != self.gameServicesManager.air.dclassesByName['DistributedToonUD']:
            self.demand('Kill', "One of the account's avatars is invalid!")
            return
        wishNameState = fields['WishNameState'][0]
        wishName = fields['WishName'][0]
        name = fields['setName'][0]
        if wishNameState == 'APPROVED':
            wishNameState = 'LOCKED'
            name = wishName
            wishName = ''
        else:
            if wishNameState == 'REJECTED':
                wishNameState = 'OPEN'
                wishName = ''
            else:
                self.demand('Kill', 'Tried to acknowledge name on an avatar in invalid state (%s) !' % wishNameState)
                return
        self.gameServicesManager.air.dbInterface.updateObject(self.gameServicesManager.air.dbId, self.avId, self.gameServicesManager.air.dclassesByName['DistributedToonUD'], {'WishNameState': (wishNameState,), 'WishName': (
                      wishName,), 
           'setName': (
                     name,)}, {'WishNameState': fields['WishNameState'], 'WishName': fields['WishName'], 
           'setName': fields['setName']})
        self.gameServicesManager.sendUpdateToAccountId(self.target, 'acknowledgeAvatarNameResponse', [])
        self.demand('Off')


class TTGameServicesManagerUD(GameServicesManagerUD):
    notify = DirectNotifyGlobal.directNotify.newCategory('TTGameServicesManagerUD')
    avatarDclass = 'DistributedToonUD'

    def __init__(self, air):
        GameServicesManagerUD.__init__(self, air)
        self.nameGenerator = None
        return

    def announceGenerate(self):
        GameServicesManagerUD.announceGenerate(self)
        self.nameGenerator = NameGenerator()

    def setNamePattern(self, avId, p1, f1, p2, f2, p3, f3, p4, f4):
        self.runOperation(SetNamePatternOperation, avId, [(p1, f1), (p2, f2),
         (
          p3, f3), (p4, f4)])

    def setNameTyped(self, avId, name):
        self.runOperation(SetNameTypedOperation, avId, name)

    def createAvatar(self, dna, name, index):
        self.runOperation(CreateAvatarOperation, dna, name, index)

    def acknowledgeAvatarName(self, avId):
        self.runOperation(AcknowledgeNameOperation, avId)