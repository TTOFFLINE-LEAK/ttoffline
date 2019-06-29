import hashlib, hmac, time
from sys import platform
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from direct.distributed.PyDatagram import *
from direct.fsm.FSM import FSM
from otp.distributed import OtpDoGlobals
from toontown.makeatoon.NameGenerator import NameGenerator
from toontown.toon.ToonDNA import ToonDNA
from toontown.toonbase import TTLocalizer
from toontown.uberdog.ClientServicesManager import FIXED_KEY
import semidbm

def judgeName(name):
    return 2


REPORT_REASONS = [
 'MODERATION_FOUL_LANGUAGE', 'MODERATION_PERSONAL_INFO',
 'MODERATION_RUDE_BEHAVIOR', 'MODERATION_BAD_NAME', 'MODERATION_HACKING']

class AccountDB:
    notify = directNotify.newCategory('AccountDB')

    def __init__(self, csm):
        self.csm = csm
        filename = simbase.config.GetString('accountdb-local-file', 'astron/databases/accounts.db')
        dbm = semidbm
        self.dbm = dbm.open(filename, 'c')

    def lookup(self, cookie, callback):
        raise NotImplementedError('lookup')

    def storeAccountID(self, databaseId, accountId, callback):
        self.dbm[databaseId] = str(accountId)
        if getattr(self.dbm, 'sync', None):
            self.dbm.sync()
            callback(True)
        else:
            self.notify.warning('Unable to associate user %s with account %d!' % (databaseId, accountId))
            callback(False)
        return


class DeveloperAccountDB(AccountDB):
    notify = directNotify.newCategory('DeveloperAccountDB')

    def lookup(self, cookie, callback):
        if cookie.startswith('.'):
            callback({'success': False, 'reason': 'Invalid cookie specified!'})
            return
        if cookie in self.dbm:

            def returnAccount(dclass, fields):
                if dclass is None or fields is None:
                    callback({'success': False, 'reason': "Account %s wasn't found in the database! You need to reset your database" % self.dbm[cookie]})
                    return
                if fields.get('TRIALER'):
                    admin = 207
                else:
                    admin = fields.get('ADMIN_ACCESS')
                callback({'success': True, 'accountId': int(self.dbm[cookie]), 
                   'databaseId': cookie, 
                   'adminAccess': admin})
                return

            self.csm.air.dbInterface.queryObject(self.csm.air.dbId, int(self.dbm[cookie]), returnAccount)
        else:
            callback({'success': True, 'accountId': 0, 
               'databaseId': cookie, 
               'adminAccess': 607})


class LocalAccountDB(AccountDB):
    notify = directNotify.newCategory('LocalAccountDB')

    def lookup(self, cookie, callback):
        if cookie.startswith('.'):
            callback({'success': False, 'reason': 'Invalid cookie specified!'})
            return
        if cookie in self.dbm:

            def returnAccount(dclass, fields):
                if dclass is None or fields is None:
                    callback({'success': False, 'reason': "Account %s wasn't found in the database! You need to reset your database" % self.dbm[cookie]})
                    return
                if fields.get('TRIALER'):
                    admin = 207
                else:
                    admin = fields.get('ADMIN_ACCESS')
                callback({'success': True, 'accountId': int(self.dbm[cookie]), 
                   'databaseId': cookie, 
                   'adminAccess': admin})
                return

            self.csm.air.dbInterface.queryObject(self.csm.air.dbId, int(self.dbm[cookie]), returnAccount)
        else:
            if not self.dbm.values():
                admin = 607
            else:
                admin = simbase.config.GetInt('default-access-level', 307)
            callback({'success': True, 'accountId': 0, 
               'databaseId': cookie, 
               'adminAccess': admin})


WISHNAME_LOCKED = 0
WISHNAME_OPEN = 1
WISHNAME_PENDING = 2
WISHNAME_APPROVED = 3
WISHNAME_REJECTED = 4

class OperationFSM(FSM):
    TARGET_CONNECTION = False

    def __init__(self, csm, target):
        self.csm = csm
        self.target = target
        FSM.__init__(self, self.__class__.__name__)

    def enterKill(self, reason=''):
        if self.TARGET_CONNECTION:
            self.csm.killConnection(self.target, reason=reason)
        else:
            self.csm.killAccount(self.target, reason=reason)
        self.demand('Off')

    def enterOff(self):
        if self.TARGET_CONNECTION:
            del self.csm.connection2fsm[self.target]
        else:
            del self.csm.account2fsm[self.target]


class LoginAccountFSM(OperationFSM):
    TARGET_CONNECTION = True
    notify = directNotify.newCategory('LoginAccountFSM')

    def enterStart(self, cookie):
        self.cookie = cookie
        self.demand('QueryAccountDB')

    def enterQueryAccountDB(self):
        self.csm.accountDB.lookup(self.cookie, self.__handleLookup)

    def __handleLookup(self, result):
        if not result.get('success'):
            self.csm.air.writeServerEvent('cookie-rejected', clientId=self.target, cookie=self.cookie)
            self.demand('Kill', result.get('reason', 'The accounts database rejected your cookie.'))
            return
        self.databaseId = result.get('databaseId', 0)
        accountId = result.get('accountId', 0)
        self.adminAccess = result.get('adminAccess', 0)
        if self.adminAccess < simbase.config.GetInt('minimum-access', 100):
            self.csm.air.writeServerEvent('insufficient-access', self.target, self.cookie)
            self.demand('Kill', result.get('reason', 'You have insufficient access to login.\nYou have access level %d and you need access level %d.' % (
             self.adminAccess, simbase.config.GetInt('minimum-access', 100))))
            return
        if accountId:
            self.accountId = accountId
            self.demand('RetrieveAccount')
        else:
            self.demand('CreateAccount')

    def enterRetrieveAccount(self):
        self.csm.air.dbInterface.queryObject(self.csm.air.dbId, self.accountId, self.__handleRetrieve)

    def __handleRetrieve(self, dclass, fields):
        if dclass != self.csm.air.dclassesByName['AccountUD']:
            self.demand('Kill', 'Your account object (%s) was not found in the database!' % dclass)
            return
        self.account = fields
        self.demand('SetAccount')

    def enterCreateAccount(self):
        self.account = {'ACCOUNT_AV_SET': [0] * 7, 'ESTATE_ID': 0, 
           'ACCOUNT_AV_SET_DEL': [], 'CREATED': time.ctime(), 
           'LAST_LOGIN': time.ctime(), 
           'ACCOUNT_ID': str(self.databaseId), 
           'ADMIN_ACCESS': self.adminAccess, 
           'TRIALER': 0}
        self.csm.air.dbInterface.createObject(self.csm.air.dbId, self.csm.air.dclassesByName['AccountUD'], self.account, self.__handleCreate)

    def __handleCreate(self, accountId):
        if self.state != 'CreateAccount':
            self.notify.warning('Received create account response outside of CreateAccount state.')
            return
        if not accountId:
            self.notify.warning('Database failed to construct an account object!')
            self.demand('Kill', 'Your account object could not be created in the game database.')
            return
        self.csm.air.writeServerEvent('accountCreated', accountId)
        self.accountId = accountId
        self.demand('StoreAccountID')

    def enterStoreAccountID(self):
        self.csm.accountDB.storeAccountID(self.databaseId, self.accountId, self.__handleStored)

    def __handleStored(self, success=True):
        if not success:
            self.demand('Kill', 'The account server could not save your account DB ID!')
            return
        self.demand('SetAccount')

    def enterSetAccount(self):
        dg = PyDatagram()
        dg.addServerHeader(self.csm.GetAccountConnectionChannel(self.accountId), self.csm.air.ourChannel, CLIENTAGENT_EJECT)
        dg.addUint16(100)
        dg.addString('This account has been logged in elsewhere.')
        self.csm.air.send(dg)
        dg = PyDatagram()
        dg.addServerHeader(self.target, self.csm.air.ourChannel, CLIENTAGENT_OPEN_CHANNEL)
        dg.addChannel(self.csm.GetAccountConnectionChannel(self.accountId))
        self.csm.air.send(dg)
        access = self.account.get('ADMIN_ACCESS', 0)
        if access >= 400:
            dg = PyDatagram()
            dg.addServerHeader(self.target, self.csm.air.ourChannel, CLIENTAGENT_OPEN_CHANNEL)
            dg.addChannel(OtpDoGlobals.OTP_MOD_CHANNEL)
            self.csm.air.send(dg)
        if access >= 500:
            dg = PyDatagram()
            dg.addServerHeader(self.target, self.csm.air.ourChannel, CLIENTAGENT_OPEN_CHANNEL)
            dg.addChannel(OtpDoGlobals.OTP_ADMIN_CHANNEL)
            self.csm.air.send(dg)
        dg = PyDatagram()
        dg.addServerHeader(self.target, self.csm.air.ourChannel, CLIENTAGENT_SET_CLIENT_ID)
        dg.addChannel(self.accountId << 32)
        self.csm.air.send(dg)
        dg = PyDatagram()
        dg.addServerHeader(self.target, self.csm.air.ourChannel, CLIENTAGENT_SET_STATE)
        dg.addUint16(2)
        self.csm.air.send(dg)
        self.csm.air.dbInterface.updateObject(self.csm.air.dbId, self.accountId, self.csm.air.dclassesByName['AccountUD'], {'LAST_LOGIN': time.ctime(), 'ACCOUNT_ID': str(self.databaseId), 
           'ADMIN_ACCESS': self.adminAccess})
        self.csm.air.writeServerEvent('account-login', clientId=self.target, accId=self.accountId, webAccId=self.databaseId, cookie=self.cookie)
        self.csm.sendUpdateToChannel(self.target, 'acceptLogin', [])
        self.demand('Off')


class CreateAvatarFSM(OperationFSM):
    notify = directNotify.newCategory('CreateAvatarFSM')

    def enterStart(self, dna, index, skipTutorial):
        if index >= 7:
            self.demand('Kill', 'Invalid index (%d) specified!' % index)
            return
        if not ToonDNA().isValidNetString(dna):
            self.demand('Kill', 'Invalid DNA specified!')
            return
        self.index = index
        self.dna = dna
        self.skipTutorial = skipTutorial
        self.demand('RetrieveAccount')

    def enterRetrieveAccount(self):
        self.csm.air.dbInterface.queryObject(self.csm.air.dbId, self.target, self.__handleRetrieve)

    def __handleRetrieve(self, dclass, fields):
        if dclass != self.csm.air.dclassesByName['AccountUD']:
            self.demand('Kill', 'Your account object (%s) was not found in the database!' % dclass)
            return
        self.account = fields
        self.avList = self.account['ACCOUNT_AV_SET']
        self.avList = self.avList[:7]
        self.avList += [0] * (7 - len(self.avList))
        if self.avList[self.index]:
            self.demand('Kill', 'Avatar slot %d is already taken by another avatar (%s)!' % (
             self.index, str(self.avList[self.index])))
            return
        self.demand('CreateAvatar')

    def enterCreateAvatar(self):
        dna = ToonDNA()
        dna.makeFromNetString(self.dna)
        colorstring = TTLocalizer.NumToColor[dna.headColor]
        animaltype = TTLocalizer.AnimalToSpecies[dna.getAnimal()]
        if self.index == 6:
            name = 'Episode Toon'
        else:
            name = colorstring + ' ' + animaltype
        toonFields = {'setName': (
                     name,), 
           'WishNameState': WISHNAME_OPEN, 
           'WishName': '', 
           'setDNAString': (
                          self.dna,), 
           'setTutorialAck': (
                            int(self.skipTutorial),), 
           'setDISLid': (
                       self.target,)}
        self.csm.air.dbInterface.createObject(self.csm.air.dbId, self.csm.air.dclassesByName['DistributedToonUD'], toonFields, self.__handleCreate)

    def __handleCreate(self, avId):
        if not avId:
            self.demand('Kill', 'Database failed to create the new avatar object!')
            return
        self.avId = avId
        self.demand('StoreAvatar')

    def enterStoreAvatar(self):
        self.avList[self.index] = self.avId
        self.csm.air.dbInterface.updateObject(self.csm.air.dbId, self.target, self.csm.air.dclassesByName['AccountUD'], {'ACCOUNT_AV_SET': self.avList}, {'ACCOUNT_AV_SET': self.account['ACCOUNT_AV_SET']}, self.__handleStoreAvatar)

    def __handleStoreAvatar(self, fields):
        if fields:
            self.demand('Kill', 'Database failed to associate the new avatar to your account!')
            return
        self.csm.air.writeServerEvent('avatar-created', avId=self.avId, accId=self.target, dna=self.dna.encode('hex'), slot=self.index)
        self.csm.sendUpdateToAccountId(self.target, 'createAvatarResp', [self.avId])
        self.demand('Off')


class AvatarOperationFSM(OperationFSM):
    POST_ACCOUNT_STATE = 'Off'

    def enterRetrieveAccount(self):
        self.csm.air.dbInterface.queryObject(self.csm.air.dbId, self.target, self.__handleRetrieve)

    def __handleRetrieve(self, dclass, fields):
        if dclass != self.csm.air.dclassesByName['AccountUD']:
            self.demand('Kill', 'Your account object (%s) was not found in the database!' % dclass)
            return
        self.account = fields
        self.avList = self.account['ACCOUNT_AV_SET']
        self.trialer = self.account['TRIALER']
        self.avList = self.avList[:7]
        self.avList += [0] * (7 - len(self.avList))
        self.demand(self.POST_ACCOUNT_STATE)


class GetAvatarsFSM(AvatarOperationFSM):
    notify = directNotify.newCategory('GetAvatarsFSM')
    POST_ACCOUNT_STATE = 'QueryAvatars'

    def enterStart(self):
        self.demand('RetrieveAccount')

    def enterQueryAvatars(self):
        self.pendingAvatars = set()
        self.avatarFields = {}
        for avId in self.avList:
            if avId:
                self.pendingAvatars.add(avId)

                def response(dclass, fields, avId=avId):
                    if self.state != 'QueryAvatars':
                        return
                    if dclass != self.csm.air.dclassesByName['DistributedToonUD']:
                        self.demand('Kill', "One of the account's avatars is invalid! Its DClass is %s, but it should be DistributedToonUD!" % dclass)
                        return
                    if not fields.has_key('setDISLid'):
                        self.csm.air.dbInterface.updateObject(self.csm.air.dbId, avId, self.csm.air.dclassesByName['DistributedToonUD'], {'setDISLid': [self.target]})
                    self.avatarFields[avId] = fields
                    self.pendingAvatars.remove(avId)
                    if not self.pendingAvatars:
                        self.demand('SendAvatars')

                self.csm.air.dbInterface.queryObject(self.csm.air.dbId, avId, response)

        if not self.pendingAvatars:
            self.demand('SendAvatars')

    def enterSendAvatars(self):
        potentialAvs = []
        for avId, fields in self.avatarFields.items():
            index = self.avList.index(avId)
            wns = fields.get('WishNameState', WISHNAME_LOCKED)
            name = fields['setName'][0]
            if wns == WISHNAME_OPEN:
                nameState = 1
            else:
                if wns == WISHNAME_PENDING:
                    nameState = 2
                else:
                    if wns == WISHNAME_APPROVED:
                        nameState = 3
                        name = fields['WishName']
                    else:
                        if wns == WISHNAME_REJECTED:
                            nameState = 4
                        else:
                            if wns == WISHNAME_LOCKED:
                                nameState = 0
                            else:
                                self.csm.notify.warning('Avatar %d is in unknown name state %s.' % (avId, wns))
                                nameState = 0
            potentialAvs.append([avId, name, fields['setDNAString'][0],
             index, nameState])

        self.csm.sendUpdateToAccountId(self.target, 'setTrialer', [
         self.trialer])
        self.csm.sendUpdateToAccountId(self.target, 'setAvatars', [potentialAvs])
        self.demand('Off')


class DeleteAvatarFSM(GetAvatarsFSM):
    notify = directNotify.newCategory('DeleteAvatarFSM')
    POST_ACCOUNT_STATE = 'ProcessDelete'

    def enterStart(self, avId):
        self.avId = avId
        GetAvatarsFSM.enterStart(self)

    def enterProcessDelete(self):
        if self.avId not in self.avList:
            self.demand('Kill', 'Tried to delete an avatar (%d) not in the account!' % self.avId)
            return
        index = self.avList.index(self.avId)
        self.avList[index] = 0
        avsDeleted = list(self.account.get('ACCOUNT_AV_SET_DEL', []))
        avsDeleted.append([self.avId, int(time.time())])
        estateId = self.account.get('ESTATE_ID', 0)
        if estateId != 0:
            self.csm.air.dbInterface.updateObject(self.csm.air.dbId, estateId, self.csm.air.dclassesByName['DistributedEstateAI'], {'setSlot%dToonId' % index: [0], 'setSlot%dGarden' % index: [[]]})
        self.csm.air.dbInterface.updateObject(self.csm.air.dbId, self.target, self.csm.air.dclassesByName['AccountUD'], {'ACCOUNT_AV_SET': self.avList, 'ACCOUNT_AV_SET_DEL': avsDeleted}, {'ACCOUNT_AV_SET': self.account['ACCOUNT_AV_SET'], 'ACCOUNT_AV_SET_DEL': self.account['ACCOUNT_AV_SET_DEL']}, self.__handleDelete)

    def __handleDelete(self, fields):
        if fields:
            self.demand('Kill', 'Database failed to mark the avatar (%d) deleted!' % self.avId)
            return
        self.csm.air.friendsManager.clearList(self.avId)
        self.csm.air.writeServerEvent('avatar-deleted', avId=self.avId, accId=self.target)
        self.demand('QueryAvatars')


class SetNameTypedFSM(AvatarOperationFSM):
    notify = directNotify.newCategory('SetNameTypedFSM')
    POST_ACCOUNT_STATE = 'RetrieveAvatar'

    def enterStart(self, avId, name):
        self.avId = avId
        self.name = name
        if self.avId:
            self.demand('RetrieveAccount')
            return
        self.demand('JudgeName')

    def enterRetrieveAvatar(self):
        if self.avId and self.avId not in self.avList:
            self.demand('Kill', 'Tried to name an avatar (%d) not in the account!' % self.avId)
            return
        self.csm.air.dbInterface.queryObject(self.csm.air.dbId, self.avId, self.__handleAvatar)

    def __handleAvatar(self, dclass, fields):
        if dclass != self.csm.air.dclassesByName['DistributedToonUD']:
            self.demand('Kill', "One of the account's avatars is invalid! Its DClass is %s, but it should be DistributedToonUD!" % dclass)
            return
        if fields['WishNameState'] != WISHNAME_OPEN:
            self.demand('Kill', 'Avatar %d is not supposed to be able to be named right now! Its name status is %d.' % (
             self.avId, fields['WishNameState']))
            return
        self.demand('JudgeName')

    def enterJudgeName(self):
        status = judgeName(self.name)
        if self.avId and status:
            if status == 2:
                self.csm.air.dbInterface.updateObject(self.csm.air.dbId, self.avId, self.csm.air.dclassesByName['DistributedToonUD'], {'WishNameState': WISHNAME_LOCKED, 'WishName': '', 
                   'setName': (
                             self.name,)})
            else:
                self.csm.air.dbInterface.updateObject(self.csm.air.dbId, self.avId, self.csm.air.dclassesByName['DistributedToonUD'], {'WishNameState': WISHNAME_PENDING, 'WishName': self.name, 
                   'WishNameTimestamp': int(time.time())})
        if self.avId:
            self.csm.air.writeServerEvent('avatar-wishname', self.avId, self.name)
        self.csm.sendUpdateToAccountId(self.target, 'setNameTypedResp', [self.avId, status])
        self.demand('Off')


class SetNamePatternFSM(AvatarOperationFSM):
    notify = directNotify.newCategory('SetNamePatternFSM')
    POST_ACCOUNT_STATE = 'RetrieveAvatar'

    def enterStart(self, avId, pattern):
        self.avId = avId
        self.pattern = pattern
        self.demand('RetrieveAccount')

    def enterRetrieveAvatar(self):
        if self.avId and self.avId not in self.avList:
            self.demand('Kill', 'Tried to name an avatar (%d) not in the account!' % self.avId)
            return
        self.csm.air.dbInterface.queryObject(self.csm.air.dbId, self.avId, self.__handleAvatar)

    def __handleAvatar(self, dclass, fields):
        if dclass != self.csm.air.dclassesByName['DistributedToonUD']:
            self.demand('Kill', "One of the account's avatars is invalid! Its DClass is %s, but it should be DistributedToonUD!" % dclass)
            return
        if fields['WishNameState'] != WISHNAME_OPEN:
            self.demand('Kill', 'Avatar %d is not supposed to be able to be named right now! Its name status is %d.' % (
             self.avId, fields['WishNameState']))
            return
        self.demand('SetName')

    def enterSetName(self):
        parts = []
        for p, f in self.pattern:
            if p == 213:
                p = 212
            part = self.csm.nameGenerator.nameDictionary.get(p, ('', ''))[1]
            if f:
                part = part[:1].upper() + part[1:]
            else:
                part = part.lower()
            parts.append(part)

        parts[2] += parts.pop(3)
        while '' in parts:
            parts.remove('')

        name = (' ').join(parts)
        self.csm.air.dbInterface.updateObject(self.csm.air.dbId, self.avId, self.csm.air.dclassesByName['DistributedToonUD'], {'WishNameState': WISHNAME_LOCKED, 'WishName': '', 
           'setName': (
                     name,)})
        self.csm.air.writeServerEvent('avatar-named', avId=self.avId, name=name)
        self.csm.sendUpdateToAccountId(self.target, 'setNamePatternResp', [self.avId, 1])
        self.demand('Off')


class AcknowledgeNameFSM(AvatarOperationFSM):
    notify = directNotify.newCategory('AcknowledgeNameFSM')
    POST_ACCOUNT_STATE = 'GetTargetAvatar'

    def enterStart(self, avId):
        self.avId = avId
        self.demand('RetrieveAccount')

    def enterGetTargetAvatar(self):
        if self.avId not in self.avList:
            self.demand('Kill', 'Tried to acknowledge name on an avatar (%d) not in the account!' % self.avId)
            return
        self.csm.air.dbInterface.queryObject(self.csm.air.dbId, self.avId, self.__handleAvatar)

    def __handleAvatar(self, dclass, fields):
        if dclass != self.csm.air.dclassesByName['DistributedToonUD']:
            self.demand('Kill', "One of the account's avatars is invalid! Its DClass is %s, but it should be DistributedToonUD!" % dclass)
            return
        wns = fields['WishNameState']
        wn = fields['WishName']
        name = fields['setName'][0]
        if wns == WISHNAME_APPROVED:
            wns = WISHNAME_LOCKED
            name = wn
            wn = ''
        else:
            if wns == WISHNAME_REJECTED:
                wns = WISHNAME_OPEN
                wn = ''
            else:
                self.demand('Kill', 'Tried to acknowledge name on an avatar (%d) in %s state!' % (self.avId, wns))
                return
        self.csm.air.dbInterface.updateObject(self.csm.air.dbId, self.avId, self.csm.air.dclassesByName['DistributedToonUD'], {'WishNameState': wns, 'WishName': wn, 
           'setName': (
                     name,)}, {'WishNameState': fields['WishNameState'], 'WishName': fields['WishName'], 
           'setName': fields['setName']})
        self.csm.sendUpdateToAccountId(self.target, 'acknowledgeAvatarNameResp', [])
        self.demand('Off')


class LoadAvatarFSM(AvatarOperationFSM):
    notify = directNotify.newCategory('LoadAvatarFSM')
    POST_ACCOUNT_STATE = 'GetTargetAvatar'

    def enterStart(self, avId):
        self.avId = avId
        self.demand('RetrieveAccount')

    def enterGetTargetAvatar(self):
        if self.avId not in self.avList:
            self.demand('Kill', 'Tried to play an avatar (%d) not in the account!' % self.avId)
            return
        self.csm.air.dbInterface.queryObject(self.csm.air.dbId, self.avId, self.__handleAvatar)

    def __handleAvatar(self, dclass, fields):
        if dclass != self.csm.air.dclassesByName['DistributedToonUD']:
            self.demand('Kill', "One of the account's avatars is invalid! Its DClass is %s, but it should be DistributedToonUD!" % dclass)
            return
        self.avatar = fields
        self.demand('SetAvatar')

    def enterSetAvatar(self):
        channel = self.csm.GetAccountConnectionChannel(self.target)
        dgcleanup = PyDatagram()
        dgcleanup.addServerHeader(self.avId, channel, STATESERVER_OBJECT_DELETE_RAM)
        dgcleanup.addUint32(self.avId)
        dg = PyDatagram()
        dg.addServerHeader(channel, self.csm.air.ourChannel, CLIENTAGENT_ADD_POST_REMOVE)
        dg.addString(dgcleanup.getMessage())
        self.csm.air.send(dg)
        adminAccess = self.account.get('ADMIN_ACCESS', 0)
        adminAccess = adminAccess - adminAccess % 100
        self.csm.air.sendActivate(self.avId, 0, 0, self.csm.air.dclassesByName['DistributedToonUD'], {'setAdminAccess': [self.account.get('ADMIN_ACCESS', 0)]})
        dg = PyDatagram()
        dg.addServerHeader(channel, self.csm.air.ourChannel, CLIENTAGENT_OPEN_CHANNEL)
        dg.addChannel(self.csm.GetPuppetConnectionChannel(self.avId))
        self.csm.air.send(dg)
        dg = PyDatagram()
        dg.addServerHeader(channel, self.csm.air.ourChannel, CLIENTAGENT_ADD_SESSION_OBJECT)
        dg.addUint32(self.avId)
        self.csm.air.send(dg)
        dg = PyDatagram()
        dg.addServerHeader(channel, self.csm.air.ourChannel, CLIENTAGENT_SET_CLIENT_ID)
        dg.addChannel(self.target << 32 | self.avId)
        self.csm.air.send(dg)
        dg = PyDatagram()
        dg.addServerHeader(self.avId, self.csm.air.ourChannel, STATESERVER_OBJECT_SET_OWNER)
        dg.addChannel(self.csm.GetAccountConnectionChannel(self.target))
        self.csm.air.send(dg)
        fields = self.avatar
        fields.update({'setAdminAccess': [self.account.get('ADMIN_ACCESS', 0)]})
        self.csm.air.friendsManager.toonOnline(self.avId, fields)
        self.csm.air.globalPartyMgr.avatarJoined(self.avId)
        self.csm.air.writeServerEvent('avatar-chosen', avId=self.avId, accId=self.target)
        self.demand('Off')


class UnloadAvatarFSM(OperationFSM):
    notify = directNotify.newCategory('UnloadAvatarFSM')

    def enterStart(self, avId):
        self.avId = avId
        self.demand('UnloadAvatar')

    def enterUnloadAvatar(self):
        channel = self.csm.GetAccountConnectionChannel(self.target)
        self.csm.air.friendsManager.toonOffline(self.avId)
        dg = PyDatagram()
        dg.addServerHeader(channel, self.csm.air.ourChannel, CLIENTAGENT_CLEAR_POST_REMOVES)
        self.csm.air.send(dg)
        dg = PyDatagram()
        dg.addServerHeader(channel, self.csm.air.ourChannel, CLIENTAGENT_CLOSE_CHANNEL)
        dg.addChannel(self.csm.GetPuppetConnectionChannel(self.avId))
        self.csm.air.send(dg)
        dg = PyDatagram()
        dg.addServerHeader(channel, self.csm.air.ourChannel, CLIENTAGENT_SET_CLIENT_ID)
        dg.addChannel(self.target << 32)
        self.csm.air.send(dg)
        dg = PyDatagram()
        dg.addServerHeader(channel, self.csm.air.ourChannel, CLIENTAGENT_REMOVE_SESSION_OBJECT)
        dg.addUint32(self.avId)
        self.csm.air.send(dg)
        dg = PyDatagram()
        dg.addServerHeader(self.avId, channel, STATESERVER_OBJECT_DELETE_RAM)
        dg.addUint32(self.avId)
        self.csm.air.send(dg)
        self.csm.air.writeServerEvent('avatar-unload', avId=self.avId)
        self.demand('Off')


class ClientServicesManagerUD(DistributedObjectGlobalUD):
    notify = directNotify.newCategory('ClientServicesManagerUD')

    def announceGenerate(self):
        DistributedObjectGlobalUD.announceGenerate(self)
        self.connection2fsm = {}
        self.account2fsm = {}
        self.nameGenerator = NameGenerator()
        self.wantMiniServer = config.GetBool('want-mini-server', False)
        dbtype = config.GetString('accountdb-type', 'developer')
        if dbtype == 'developer':
            self.accountDB = DeveloperAccountDB(self)
        else:
            if dbtype == 'local':
                self.accountDB = LocalAccountDB(self)
            else:
                self.notify.error('Invalid account DB type configured: %s' % dbtype)
        self.loginsEnabled = True

    def killConnection(self, connId, code=122, reason=''):
        self.notify.info('Booting client: %d out for reason(%d): %s' % (
         int(connId), int(code), str(reason)))
        dg = PyDatagram()
        dg.addServerHeader(connId, self.air.ourChannel, CLIENTAGENT_EJECT)
        dg.addUint16(int(code))
        dg.addString(str(reason))
        self.air.send(dg)

    def killConnectionFSM(self, connId):
        fsm = self.connection2fsm.get(connId)
        if not fsm:
            self.notify.warning('Tried to kill connection %d for duplicate FSM, but none exists!' % connId)
            return
        self.killConnection(connId, reason='An operation is already underway: ' + fsm.name)

    def killAccount(self, accountId, reason):
        self.killConnection(self.GetAccountConnectionChannel(accountId), reason=reason)

    def killAccountFSM(self, accountId):
        fsm = self.account2fsm.get(accountId)
        if not fsm:
            self.notify.warning('Tried to kill account %d for duplicate FSM, but none exists!' % accountId)
            return
        self.killAccount(accountId, 'An operation is already underway: ' + fsm.name)

    def runAccountFSM(self, fsmtype, *args):
        sender = self.air.getAccountIdFromSender()
        if not sender:
            self.killAccount(sender, 'Client is not logged in.')
        if sender in self.account2fsm:
            self.killAccountFSM(sender)
            return
        self.account2fsm[sender] = fsmtype(self, sender)
        self.account2fsm[sender].request('Start', *args)

    def setLoginEnabled(self, enable):
        if not enable:
            self.notify.warning('The CSMUD has been told to reject logins! All future logins will now be rejected.')
        self.loginsEnabled = enable

    def login(self, cookie, hwId, sig, serverURL):
        self.notify.debug('Received login cookie %r from %d' % (cookie, self.air.getMsgSender()))
        sender = self.air.getMsgSender()
        self.air.writeServerEvent('login', hwId=hwId, serverURL=serverURL, cookie=cookie)
        if not self.wantMiniServer and serverURL != '127.0.0.1':
            self.killConnection(sender, 201, 'This server is not currently running in mini-server mode. Please try again later.')
            return
        if not self.loginsEnabled:
            self.killConnection(sender, 200, 'Logins are currently disabled. Please try again later.')
            return
        if sender >> 32:
            self.killConnection(sender, reason='Client is already logged in.')
            return
        key = config.GetString('csmud-secret', 'broken-code-store') + config.GetString('server-version', 'no_version_set') + str(self.air.hashVal) + FIXED_KEY
        computedSig = hmac.new(key, cookie, hashlib.sha256).digest()
        if sig != computedSig:
            self.killConnection(sender, reason='The accounts database rejected your cookie')
            return
        if config.GetString('server-password', ''):
            self.sendUpdateToChannel(sender, 'loginResponse', [True])
            return
        self.sendUpdateToChannel(sender, 'loginResponse', [False])
        self.performLogin(hwId, cookie)

    def authenticateLogin(self, cookie, password, hwId):
        sender = self.air.getMsgSender()
        if password == config.GetString('server-password', ''):
            self.sendUpdateToChannel(sender, 'authenticationResponse', [True])
            self.performLogin(hwId, cookie)
        else:
            self.sendUpdateToChannel(sender, 'authenticationResponse', [False])

    def performLogin(self, hwId, cookie):
        immuneHardwareIds = ['0x5800e36aeac8L']
        sender = self.air.getMsgSender()
        data = simbase.air.banManager.getActiveBans()[0]
        if hwId in data and hwId not in immuneHardwareIds:
            data = data[hwId]
            reason = data['reason']
            simbase.air.writeServerEvent('security', issue='Client has attempted to login but their account has been terminated!', accId=data['accId'], hwId=hwId, cookie=cookie, reason=reason)
            self.killConnection(connId=sender, code=152, reason=data['reason'])
        if sender in self.connection2fsm:
            self.killConnectionFSM(sender)
            return
        self.connection2fsm[sender] = LoginAccountFSM(self, sender)
        self.connection2fsm[sender].request('Start', cookie)

    def requestAvatars(self):
        self.notify.debug('Received avatar list request from %d' % self.air.getMsgSender())
        self.runAccountFSM(GetAvatarsFSM)

    def createAvatar(self, dna, index, skipTutorial):
        self.runAccountFSM(CreateAvatarFSM, dna, index, skipTutorial)

    def deleteAvatar(self, avId):
        self.runAccountFSM(DeleteAvatarFSM, avId)

    def setNameTyped(self, avId, name):
        self.runAccountFSM(SetNameTypedFSM, avId, name)

    def setNamePattern(self, avId, p1, f1, p2, f2, p3, f3, p4, f4):
        self.runAccountFSM(SetNamePatternFSM, avId, [(p1, f1), (p2, f2),
         (
          p3, f3), (p4, f4)])

    def acknowledgeAvatarName(self, avId):
        self.runAccountFSM(AcknowledgeNameFSM, avId)

    def chooseAvatar(self, avId):
        currentAvId = self.air.getAvatarIdFromSender()
        accountId = self.air.getAccountIdFromSender()
        if currentAvId and avId:
            self.killAccount(accountId, 'A Toon is already chosen!')
            return
        if not currentAvId and not avId:
            return
        if avId:
            self.runAccountFSM(LoadAvatarFSM, avId)
        else:
            self.runAccountFSM(UnloadAvatarFSM, currentAvId)

    def reportPlayer(self, avId, category):
        reporterId = self.air.getAvatarIdFromSender()
        if len(REPORT_REASONS) <= category:
            self.air.writeServerEvent('suspicious', avId=reporterId, issue='Invalid report reason index (%d) sent by avatar.' % category)
            return
        self.air.writeServerEvent('player-reported', reporterId=reporterId, avId=avId, category=REPORT_REASONS[category])