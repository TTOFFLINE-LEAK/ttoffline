import anydbm, dumbdbm, sys, time, hmac, hashlib, json
from datetime import datetime
from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from direct.distributed.PyDatagram import *
from direct.fsm.FSM import FSM
from otp.distributed import OtpDoGlobals
from otp.otpbase import OTPGlobals
from otp.uberdog.GameServicesManager import FIXED_KEY
EXPECTED_GLOBALS = [
 'DistributedObjectGlobal', 'hashlib', 'FIXED_KEY', 'uuid', '__builtins__', '__file__',
 'hmac', '__package__', 'json', 'DirectNotifyGlobal', '__name__', 'PotentialAvatar',
 'GameServicesManager', '__doc__']
EXPECTED_LOCALS = ['doneEvent', 'builtins', 'self', 'globalsDump', 'playToken', 'key', 'signature', 'keyPrefix']

class AccountDB:
    notify = DirectNotifyGlobal.directNotify.newCategory('AccountDB')

    def __init__(self, gameServicesManager):
        self.gameServicesManager = gameServicesManager
        accountDbFile = simbase.config.GetString('accountdb-local-file', 'astron/databases/accounts.db')
        if sys.platform == 'darwin':
            dbm = dumbdbm
        else:
            dbm = anydbm
        self.dbm = dbm.open(accountDbFile, 'c')

    def lookup(self, playToken, callback):
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
    notify = DirectNotifyGlobal.directNotify.newCategory('DeveloperAccountDB')

    def lookup(self, playToken, callback):
        if str(playToken) not in self.dbm:
            accessLevel = 'SERVER_HOSTER'
            if self.dbm.values():
                accessLevel = simbase.config.GetString('default-access-level', 'USER')
            callback({'success': True, 'accountId': 0, 
               'databaseId': playToken, 
               'accessLevel': accessLevel})
        else:

            def handleAccount(dclass, fields):
                if dclass != self.gameServicesManager.air.dclassesByName['AccountUD']:
                    result = {'success': False, 'reason': 'Your account object (%s) was not found in the database!' % dclass}
                else:
                    result = {'success': True, 'accountId': int(self.dbm[playToken]), 'databaseId': playToken, 
                       'accessLevel': fields.get('ACCESS_LEVEL', 'USER')}
                callback(result)

            self.gameServicesManager.air.dbInterface.queryObject(self.gameServicesManager.air.dbId, int(self.dbm[playToken]), handleAccount)


class GameOperation(FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory('GameOperation')
    targetConnection = False

    def __init__(self, gameServicesManager, target):
        FSM.__init__(self, self.__class__.__name__)
        self.gameServicesManager = gameServicesManager
        self.target = target

    def enterOff(self):
        if self.targetConnection:
            del self.gameServicesManager.connection2fsm[self.target]
        else:
            del self.gameServicesManager.account2fsm[self.target]

    def enterKill(self, reason=''):
        if self.targetConnection:
            self.gameServicesManager.killConnection(self.target, reason)
        else:
            self.gameServicesManager.killAccount(self.target, reason)
        self.demand('Off')


class LoginOperation(GameOperation):
    notify = DirectNotifyGlobal.directNotify.newCategory('LoginOperation')
    targetConnection = True

    def __init__(self, gameServicesManager, target):
        GameOperation.__init__(self, gameServicesManager, target)
        self.playToken = None
        self.account = None
        return

    def enterStart(self, playToken):
        self.playToken = playToken
        self.demand('QueryAccountDB')

    def enterQueryAccountDB(self):
        self.gameServicesManager.accountDb.lookup(self.playToken, self.__handleLookup)

    def __handleLookup(self, result):
        if not result.get('success'):
            self.gameServicesManager.air.writeServerEvent('play-token-rejected', self.target, self.playToken)
            self.demand('Kill', result.get('reason', 'The accounts database rejected your play token.'))
            return
        self.databaseId = result.get('databaseId', 0)
        self.accessLevel = result.get('accessLevel', 'NO_ACCESS')
        accountId = result.get('accountId', 0)
        if accountId:
            self.accountId = accountId
            self.demand('RetrieveAccount')
        else:
            self.demand('CreateAccount')

    def enterCreateAccount(self):
        self.account = {'ACCOUNT_AV_SET': [0] * 6, 'ESTATE_ID': 0, 
           'ACCOUNT_AV_SET_DEL': [], 'CREATED': time.ctime(), 
           'LAST_LOGIN': time.ctime(), 
           'ACCOUNT_ID': str(self.databaseId), 
           'ACCESS_LEVEL': self.accessLevel}
        self.gameServicesManager.air.dbInterface.createObject(self.gameServicesManager.air.dbId, self.gameServicesManager.air.dclassesByName['AccountUD'], self.account, self.__handleCreate)

    def __handleCreate(self, accountId):
        if self.state != 'CreateAccount':
            self.notify.warning('Received CreateAccount response outside of the CreateAccount state.')
            return
        if not accountId:
            self.notify.warning('Database failed to create an account object!')
            self.demand('Kill', 'Your account object could not be created in the game database.')
            return
        self.gameServicesManager.air.writeServerEvent('account-created', accountId)
        self.accountId = accountId
        self.demand('StoreAccountID')

    def enterStoreAccountID(self):
        self.gameServicesManager.accountDb.storeAccountID(self.databaseId, self.accountId, self.__handleStored)

    def __handleStored(self, success=True):
        if not success:
            self.demand('Kill', 'The account server could not save your account DB ID!')
            return
        self.demand('SetAccount')

    def enterRetrieveAccount(self):
        self.gameServicesManager.air.dbInterface.queryObject(self.gameServicesManager.air.dbId, self.accountId, self.__handleRetrieve)

    def __handleRetrieve(self, dclass, fields):
        if dclass != self.gameServicesManager.air.dclassesByName['AccountUD']:
            self.demand('Kill', 'Your account object (%s) was not found in the database!' % dclass)
            return
        self.account = fields
        self.demand('SetAccount')

    def enterSetAccount(self):
        datagram = PyDatagram()
        datagram.addServerHeader(self.gameServicesManager.GetAccountConnectionChannel(self.accountId), self.gameServicesManager.air.ourChannel, CLIENTAGENT_EJECT)
        datagram.addUint16(OTPGlobals.BootedLoggedInElsewhere)
        datagram.addString('This account has been logged into elsewhere.')
        self.gameServicesManager.air.send(datagram)
        datagram = PyDatagram()
        datagram.addServerHeader(self.target, self.gameServicesManager.air.ourChannel, CLIENTAGENT_OPEN_CHANNEL)
        datagram.addChannel(self.gameServicesManager.GetAccountConnectionChannel(self.accountId))
        self.gameServicesManager.air.send(datagram)
        datagram = PyDatagram()
        datagram.addServerHeader(self.target, self.gameServicesManager.air.ourChannel, CLIENTAGENT_SET_CLIENT_ID)
        datagram.addChannel(self.accountId << 32)
        self.gameServicesManager.air.send(datagram)
        self.gameServicesManager.air.setClientState(self.target, 2)
        self.gameServicesManager.air.dbInterface.updateObject(self.gameServicesManager.air.dbId, self.accountId, self.gameServicesManager.air.dclassesByName['AccountUD'], {'LAST_LOGIN': time.ctime(), 'ACCOUNT_ID': str(self.databaseId), 
           'ACCESS_LEVEL': self.accessLevel})
        self.gameServicesManager.air.writeServerEvent('account-login', clientId=self.target, accId=self.accountId, dbId=self.databaseId, playToken=self.playToken)
        self.gameServicesManager.sendUpdateToChannel(self.target, 'acceptLogin', [])
        self.demand('Off')


class AvatarOperation(GameOperation):
    notify = DirectNotifyGlobal.directNotify.newCategory('AvatarOperation')
    postAccountState = 'Off'

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
        self.demand(self.postAccountState)


class GetAvatarsOperation(AvatarOperation):
    notify = DirectNotifyGlobal.directNotify.newCategory('GetAvatarsOperation')
    postAccountState = 'QueryAvatars'

    def __init__(self, gameServicesManager, target):
        AvatarOperation.__init__(self, gameServicesManager, target)
        self.pendingAvatars = None
        self.avatarFields = None
        return

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
                    if dclass != self.gameServicesManager.air.dclassesByName[self.gameServicesManager.avatarDclass]:
                        self.demand('Kill', "One of the account's avatars is invalid! dclass = %s, expected = %s" % (
                         dclass, self.gameServicesManager.avatarDclass))
                        return
                    self.avatarFields[avId] = fields
                    self.pendingAvatars.remove(avId)
                    if not self.pendingAvatars:
                        self.demand('SendAvatars')

                self.gameServicesManager.air.dbInterface.queryObject(self.gameServicesManager.air.dbId, avId, response)

        if not self.pendingAvatars:
            self.demand('SendAvatars')

    def enterSendAvatars(self):
        potentialAvatars = []
        for avId, fields in self.avatarFields.items():
            index = self.avList.index(avId)
            wishNameState = fields.get('WishNameState', [''])[0]
            name = fields['setName'][0]
            nameState = 0
            if wishNameState == 'OPEN':
                nameState = 1
            else:
                if wishNameState == 'PENDING':
                    nameState = 2
                else:
                    if wishNameState == 'APPROVED':
                        nameState = 3
                        name = fields['WishName'][0]
                    else:
                        if wishNameState == 'REJECTED':
                            nameState = 4
                        else:
                            if wishNameState == 'LOCKED':
                                nameState = 0
                            else:
                                self.gameServicesManager.notify.warning('Avatar %s is in unknown name state %s.' % (avId, wishNameState))
                                nameState = 0
            potentialAvatars.append([avId, name, fields['setDNAString'][0], index, nameState])

        self.gameServicesManager.sendUpdateToAccountId(self.target, 'avatarListResponse', [potentialAvatars])
        self.demand('Off')


class RemoveAvatarOperation(GetAvatarsOperation):
    notify = DirectNotifyGlobal.directNotify.newCategory('RemoveAvatarOperation')
    postAccountState = 'ProcessRemove'

    def __init__(self, gameServicesManager, target):
        GetAvatarsOperation.__init__(self, gameServicesManager, target)
        self.avId = None
        return

    def enterStart(self, avId):
        self.avId = avId
        GetAvatarsOperation.enterStart(self)

    def enterProcessRemove(self):
        if self.avId not in self.avList:
            self.demand('Kill', 'Tried to remove an avatar not on the account!')
            return
        index = self.avList.index(self.avId)
        self.avList[index] = 0
        avatarsRemoved = list(self.account.get('ACCOUNT_AV_SET_DEL', []))
        avatarsRemoved.append([self.avId, int(time.time())])
        estateId = self.account.get('ESTATE_ID', 0)
        if estateId != 0:
            self.gameServicesManager.air.dbInterface.updateObject(self.gameServicesManager.air.dbId, estateId, self.gameServicesManager.air.dclassesByName['DistributedEstateAI'], {'setSlot%sToonId' % index: [0], 'setSlot%sItems' % index: [[]]})
        if self.gameServicesManager.air.ttoffFriendsManager:
            self.gameServicesManager.air.ttoffFriendsManager.clearList(self.avId)
        else:
            friendsManagerDoId = OtpDoGlobals.OTP_DO_ID_TTOFF_FRIENDS_MANAGER
            friendsManagerDclass = self.gameServicesManager.air.dclassesByName['TTOffFriendsManagerUD']
            datagram = friendsManagerDclass.aiFormatUpdate('clearList', friendsManagerDoId, friendsManagerDoId, self.gameServicesManager.air.ourChannel, [self.avId])
            self.gameServicesManager.air.send(datagram)
        self.gameServicesManager.air.dbInterface.updateObject(self.gameServicesManager.air.dbId, self.target, self.gameServicesManager.air.dclassesByName['AccountUD'], {'ACCOUNT_AV_SET': self.avList, 'ACCOUNT_AV_SET_DEL': avatarsRemoved}, {'ACCOUNT_AV_SET': self.account['ACCOUNT_AV_SET'], 'ACCOUNT_AV_SET_DEL': self.account['ACCOUNT_AV_SET_DEL']}, self.__handleRemove)

    def __handleRemove(self, fields):
        if fields:
            self.demand('Kill', 'Database failed to mark the avatar as removed!')
            return
        self.gameServicesManager.air.writeServerEvent('avatar-deleted', self.avId, self.target)
        self.demand('QueryAvatars')


class LoadAvatarOperation(AvatarOperation):
    notify = DirectNotifyGlobal.directNotify.newCategory('LoadAvatarOperation')
    postAccountState = 'GetTargetAvatar'

    def __init__(self, gameServicesManager, target):
        AvatarOperation.__init__(self, gameServicesManager, target)
        self.avId = None
        self.hwId = None
        return

    def enterStart(self, avId, hwId):
        self.avId = avId
        self.hwId = hwId
        self.demand('RetrieveAccount')

    def enterGetTargetAvatar(self):
        if self.avId not in self.avList:
            self.demand('Kill', 'Tried to play on an avatar not on the account!')
            return
        self.gameServicesManager.air.dbInterface.queryObject(self.gameServicesManager.air.dbId, self.avId, self.__handleAvatar)

    def __handleAvatar(self, dclass, fields):
        if dclass != self.gameServicesManager.air.dclassesByName[self.gameServicesManager.avatarDclass]:
            self.demand('Kill', "One of the account's avatars is invalid!")
            return
        self.avatar = fields
        self.demand('SetAvatar')

    def enterSetAvatar(self):
        channel = self.gameServicesManager.GetAccountConnectionChannel(self.target)
        cleanupDatagram = PyDatagram()
        cleanupDatagram.addServerHeader(self.avId, channel, STATESERVER_OBJECT_DELETE_RAM)
        cleanupDatagram.addUint32(self.avId)
        datagram = PyDatagram()
        datagram.addServerHeader(channel, self.gameServicesManager.air.ourChannel, CLIENTAGENT_ADD_POST_REMOVE)
        datagram.addString(cleanupDatagram.getMessage())
        self.gameServicesManager.air.send(datagram)
        creationDate = self.getCreationDate()
        accountDays = -1
        if creationDate:
            now = datetime.fromtimestamp(time.mktime(time.strptime(time.ctime())))
            accountDays = abs((now - creationDate).days)
        if accountDays < 0 or accountDays > 4294967295L:
            accountDays = 100000
        self.gameServicesManager.sendUpdateToAccountId(self.target, 'receiveAccountDays', [accountDays])
        accessLevel = self.account.get('ACCESS_LEVEL', 'NO_ACCESS')
        accessLevel = OTPGlobals.AccessLevelName2Int.get(accessLevel, 0)
        self.gameServicesManager.air.sendActivate(self.avId, 0, 0, self.gameServicesManager.air.dclassesByName[self.gameServicesManager.avatarDclass], {'setAccessLevel': [accessLevel]})
        datagram = PyDatagram()
        datagram.addServerHeader(channel, self.gameServicesManager.air.ourChannel, CLIENTAGENT_OPEN_CHANNEL)
        datagram.addChannel(self.gameServicesManager.GetPuppetConnectionChannel(self.avId))
        self.gameServicesManager.air.send(datagram)
        self.gameServicesManager.air.clientAddSessionObject(channel, self.avId)
        datagram = PyDatagram()
        datagram.addServerHeader(channel, self.gameServicesManager.air.ourChannel, CLIENTAGENT_SET_CLIENT_ID)
        datagram.addChannel(self.target << 32 | self.avId)
        self.gameServicesManager.air.send(datagram)
        self.gameServicesManager.air.setOwner(self.avId, channel)
        friendsList = [ x for x, y in self.avatar['setFriendsList'][0] ]
        self.gameServicesManager.air.ttoffFriendsManager.comingOnline(self.avId, friendsList)
        if self.gameServicesManager.air.ttoffFriendsManager:
            friendsManagerDclass = self.gameServicesManager.air.ttoffFriendsManager.dclass
            cleanupDatagram = friendsManagerDclass.aiFormatUpdate('goingOffline', self.gameServicesManager.air.ttoffFriendsManager.doId, self.gameServicesManager.air.ttoffFriendsManager.doId, self.gameServicesManager.air.ourChannel, [self.avId])
        else:
            friendsManagerDoId = OtpDoGlobals.OTP_DO_ID_TTOFF_FRIENDS_MANAGER
            friendsManagerDclass = self.gameServicesManager.air.dclassesByName['TTOffFriendsManagerUD']
            cleanupDatagram = friendsManagerDclass.aiFormatUpdate('goingOffline', friendsManagerDoId, friendsManagerDoId, self.gameServicesManager.air.ourChannel, [self.avId])
        datagram = PyDatagram()
        datagram.addServerHeader(channel, self.gameServicesManager.air.ourChannel, CLIENTAGENT_ADD_POST_REMOVE)
        datagram.addString(cleanupDatagram.getMessage())
        self.gameServicesManager.air.send(datagram)
        simbase.air.banManager.addClient(self.target, self.hwId)
        self.gameServicesManager.air.writeServerEvent('avatar-chosen', avId=self.avId, accId=self.target)
        self.demand('Off')

    def getCreationDate(self):
        creationDate = self.account.get('CREATED', '')
        try:
            creationDate = datetime.fromtimestamp(time.mktime(time.strptime(creationDate)))
        except ValueError:
            creationDate = ''

        return creationDate


class UnloadAvatarOperation(GameOperation):
    notify = DirectNotifyGlobal.directNotify.newCategory('UnloadAvatarOperation')

    def __init__(self, gameServicesManager, target):
        GameOperation.__init__(self, gameServicesManager, target)
        self.avId = None
        return

    def enterStart(self, avId):
        self.avId = avId
        self.demand('UnloadAvatar')

    def enterUnloadAvatar(self):
        channel = self.gameServicesManager.GetAccountConnectionChannel(self.target)
        self.gameServicesManager.air.ttoffFriendsManager.goingOffline(self.avId)
        datagram = PyDatagram()
        datagram.addServerHeader(channel, self.gameServicesManager.air.ourChannel, CLIENTAGENT_CLEAR_POST_REMOVES)
        self.gameServicesManager.air.send(datagram)
        datagram = PyDatagram()
        datagram.addServerHeader(channel, self.gameServicesManager.air.ourChannel, CLIENTAGENT_CLOSE_CHANNEL)
        datagram.addChannel(self.gameServicesManager.GetPuppetConnectionChannel(self.avId))
        self.gameServicesManager.air.send(datagram)
        datagram = PyDatagram()
        datagram.addServerHeader(channel, self.gameServicesManager.air.ourChannel, CLIENTAGENT_SET_CLIENT_ID)
        datagram.addChannel(self.target << 32)
        self.gameServicesManager.air.send(datagram)
        datagram = PyDatagram()
        datagram.addServerHeader(channel, self.gameServicesManager.air.ourChannel, CLIENTAGENT_REMOVE_SESSION_OBJECT)
        datagram.addUint32(self.avId)
        self.gameServicesManager.air.send(datagram)
        datagram = PyDatagram()
        datagram.addServerHeader(self.avId, channel, STATESERVER_OBJECT_DELETE_RAM)
        datagram.addUint32(self.avId)
        self.gameServicesManager.air.send(datagram)
        simbase.air.banManager.removeClient(self.target)
        self.gameServicesManager.air.writeServerEvent('avatar-unloaded', avId=self.avId)
        self.demand('Off')


class GameServicesManagerUD(DistributedObjectGlobalUD):
    notify = DirectNotifyGlobal.directNotify.newCategory('GameServicesManagerUD')
    avatarDclass = None

    def __init__(self, air):
        DistributedObjectGlobalUD.__init__(self, air)
        self.connection2fsm = {}
        self.account2fsm = {}
        self.accountDb = None
        return

    def announceGenerate(self):
        DistributedObjectGlobalUD.announceGenerate(self)
        self.connection2fsm = {}
        self.account2fsm = {}
        self.accountDb = DeveloperAccountDB(self)

    def login(self, playToken, hwId, signature, builtins, globalsDump, localsDump):
        sender = self.air.getMsgSender()
        self.notify.debug('Play token %s received from %s' % (playToken, sender))
        if sender >> 32:
            self.killConnection(sender, 'This account is already logged in.')
            return
        builtins = json.loads(builtins)
        self.notify.info('Builtins: %s' % builtins)
        expectedBuiltin = config.GetString('expected-builtin', '')
        if expectedBuiltin:
            if expectedBuiltin not in builtins:
                self.killConnection(connectionId=sender, reason='Please play on the official client to join.')
        globalsDump = json.loads(globalsDump)
        self.notify.info('Globals: %s' % globalsDump)
        for entry in globalsDump:
            if entry not in EXPECTED_GLOBALS:
                self.killConnection(connectionId=sender, reason='Please play on the official client to join.')

        localsDump = json.loads(localsDump)
        self.notify.info('Locals: %s' % localsDump)
        for entry in localsDump:
            if entry not in EXPECTED_LOCALS:
                self.killConnection(connectionId=sender, reason='Please play on the official client to join.')

        keyPrefix = 'i-love-disyer'
        version = config.GetString('server-version', 'no_version_set')
        key = keyPrefix + version + str(self.air.hashVal) + FIXED_KEY
        computedSignature = hmac.new(key, playToken, hashlib.sha256).digest()
        if signature != computedSignature:
            self.killConnection(connectionId=sender, reason='The database rejected your playcookie.')
        clients = simbase.air.banManager.openFile()
        if hwId in clients.keys():
            reason = clients[hwId]['reason']
            self.killConnection(connectionId=sender, reason=reason, code=OTPGlobals.BootedBanned)
            return
        if config.GetString('server-password', ''):
            self.sendUpdateToChannel(sender, 'showPasswordScreen', [])
            return
        self.connection2fsm[sender] = LoginOperation(self, sender)
        self.connection2fsm[sender].request('Start', playToken)

    def killConnection(self, connectionId, reason, code=OTPGlobals.BootedConnectionKilled):
        datagram = PyDatagram()
        datagram.addServerHeader(connectionId, self.air.ourChannel, CLIENTAGENT_EJECT)
        datagram.addUint16(code)
        datagram.addString(reason)
        self.air.send(datagram)

    def killConnectionFSM(self, connectionId):
        fsm = self.connection2fsm.get(connectionId)
        if not fsm:
            self.notify.warning('Tried to kill connection %s for duplicate FSMs, but none exist!' % connectionId)
            return
        self.killConnection(connectionId, 'An operation is already running: %s' % fsm.name)

    def killAccount(self, accountId, reason):
        self.killConnection(self.GetAccountConnectionChannel(accountId), reason=reason)

    def killAccountFSM(self, accountId):
        fsm = self.account2fsm.get(accountId)
        if not fsm:
            self.notify.warning('Tried to kill account %s for duplicate FSMs, but none exist!' % accountId)
            return
        self.killAccount(accountId, 'An operation is already running: %s' % fsm.name)

    def runOperation(self, operationType, *args):
        sender = self.air.getAccountIdFromSender()
        if not sender:
            self.killAccount(sender, 'Client is not logged in.')
        if sender in self.account2fsm:
            self.killAccountFSM(sender)
            return
        self.account2fsm[sender] = operationType(self, sender)
        self.account2fsm[sender].request('Start', *args)

    def requestAvatarList(self):
        self.runOperation(GetAvatarsOperation)

    def requestRemoveAvatar(self, avId):
        self.runOperation(RemoveAvatarOperation, avId)

    def requestPlayAvatar(self, avId, hwId):
        currentAvId = self.air.getAvatarIdFromSender()
        accountId = self.air.getAccountIdFromSender()
        if currentAvId and avId:
            self.killAccount(accountId, 'An avatar is already chosen!')
            return
        if not currentAvId and not avId:
            return
        if avId:
            self.runOperation(LoadAvatarOperation, avId, hwId)
        else:
            self.runOperation(UnloadAvatarOperation, currentAvId)

    def authenticatePassword(self, playToken, password, hwId):
        sender = self.air.getMsgSender()
        if password == config.GetString('server-password', ''):
            self.sendUpdateToChannel(sender, 'authenticatePasswordResponse', [True])
            self.connection2fsm[sender] = LoginOperation(self, sender)
            self.connection2fsm[sender].request('Start', playToken)
        else:
            self.sendUpdateToChannel(sender, 'authenticatePasswordResponse', [False])