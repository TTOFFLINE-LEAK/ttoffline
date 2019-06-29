from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal
from otp.distributed.PotentialAvatar import PotentialAvatar
import hashlib, hmac, json, uuid
FIXED_KEY = '9d8434b25eca27fc45d5bc9d01f0f36f8763ae895f3136392b8aa776fe77fbe6'

class GameServicesManager(DistributedObjectGlobal):
    notify = DirectNotifyGlobal.directNotify.newCategory('GameServicesManager')

    def __init__(self, cr):
        DistributedObjectGlobal.__init__(self, cr)
        self.doneEvent = None
        self._callback = None
        self.hwId = None
        self.password = False
        return

    def login(self, doneEvent):
        self.doneEvent = doneEvent
        playToken = self.cr.playToken or 'dev'
        self.hwId = hex(uuid.getnode())
        keyPrefix = 'i-love-disyer'
        key = keyPrefix + self.cr.serverVersion + str(self.cr.hashVal) + FIXED_KEY
        signature = hmac.new(key, playToken, hashlib.sha256).digest()
        builtins = json.dumps(__builtins__.keys())
        globalsDump = json.dumps(globals().keys())
        localsDump = json.dumps(locals().keys())
        self.d_login(playToken, self.hwId, signature, builtins, globalsDump, localsDump)

    def d_login(self, playToken, hwId, sig, builtins, globalsDump, localsDump):
        self.sendUpdate('login', [playToken, hwId, sig, builtins, globalsDump, localsDump])

    def acceptLogin(self):
        messenger.send(self.doneEvent, [{'mode': 'success'}])

    def requestAvatarList(self):
        self.sendUpdate('requestAvatarList')

    def avatarListResponse(self, avatarList):
        avList = []
        for avNum, avName, avDNA, avPosition, nameState in avatarList:
            nameOpen = int(nameState == 1)
            names = [avName, '', '', '']
            if nameState == 2:
                names[1] = avName
            else:
                if nameState == 3:
                    names[2] = avName
                else:
                    if nameState == 4:
                        names[3] = avName
            avList.append(PotentialAvatar(avNum, names, avDNA, avPosition, nameOpen))

        self.cr.handleAvatarsList(avList)

    def requestRemoveAvatar(self, avId):
        self.sendUpdate('requestRemoveAvatar', [avId])

    def requestPlayAvatar(self, avId):
        self.sendUpdate('requestPlayAvatar', [avId, self.hwId])

    def receiveAccountDays(self, accountDays):
        base.cr.accountDays = accountDays

    def showPasswordScreen(self):
        self.password = True
        messenger.send('showPasswordScreen', [])
        self.accept('authenticatePassword', self.authenticatePassword)

    def authenticatePassword(self, playToken, password):
        self.sendUpdate('authenticatePassword', [playToken, password, self.hwId])

    def authenticatePasswordResponse(self, state):
        messenger.send('authenticatePasswordResponse', [state])