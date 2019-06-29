import hashlib, hmac, uuid
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal
from panda3d.core import *
from otp.distributed.PotentialAvatar import PotentialAvatar
from otp.margins.WhisperPopup import *
from otp.otpbase import OTPLocalizer, OTPGlobals
FIXED_KEY = '5d98815f20cfc727496066016f0a8819adaae803ffd4bfeb5a793f26e7c6b7c1'

class ClientServicesManager(DistributedObjectGlobal):
    notify = directNotify.newCategory('ClientServicesManager')
    systemMessageSfx = None
    avIdsReportedThisSession = []
    passwordProtected = False

    def performLogin(self, doneEvent):
        self.doneEvent = doneEvent
        cookie = self.cr.playToken or 'dev'
        serverURL = self.cr.serverList[0].getServer()
        self.hwId = hex(uuid.getnode())
        key = config.GetString('csmud-secret', 'broken-code-store') + self.cr.serverVersion + str(self.cr.hashVal) + FIXED_KEY
        sig = hmac.new(key, cookie, hashlib.sha256).digest()
        self.notify.debug('Sending login cookie: ' + cookie)
        self.sendUpdate('login', [cookie, self.hwId, sig, serverURL])

    def acceptLogin(self):
        messenger.send(self.doneEvent, [{'mode': 'success'}])

    def loginResponse(self, passwordProtected):
        self.passwordProtected = passwordProtected
        messenger.send('csmLoginResponse', [passwordProtected])

    def authenticateLogin(self, cookie, password):
        self.sendUpdate('authenticateLogin', [cookie, password, self.hwId])

    def authenticationResponse(self, success):
        messenger.send('csmAuthenticationResponse', [success])

    def requestAvatars(self):
        self.sendUpdate('requestAvatars')

    def setAvatars(self, avatars):
        avList = []
        for avNum, avName, avDNA, avPosition, nameState in avatars:
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

    def setTrialer(self, isTrialer):
        self.cr.setIsPaid(not isTrialer)

    def sendCreateAvatar(self, avDNA, _, index, skipTutorial=True):
        self.sendUpdate('createAvatar', [avDNA.makeNetString(), index, skipTutorial])

    def createAvatarResp(self, avId):
        messenger.send('nameShopCreateAvatarDone', [avId])

    def sendDeleteAvatar(self, avId):
        self.sendUpdate('deleteAvatar', [avId])

    def sendSetNameTyped(self, avId, name, callback):
        self._callback = callback
        self.sendUpdate('setNameTyped', [avId, name])

    def setNameTypedResp(self, avId, status):
        self._callback(avId, status)

    def sendSetNamePattern(self, avId, p1, f1, p2, f2, p3, f3, p4, f4, callback):
        self._callback = callback
        self.sendUpdate('setNamePattern', [avId, p1, f1, p2, f2, p3, f3, p4, f4])

    def setNamePatternResp(self, avId, status):
        self._callback(avId, status)

    def sendAcknowledgeAvatarName(self, avId, callback):
        self._callback = callback
        self.sendUpdate('acknowledgeAvatarName', [avId])

    def acknowledgeAvatarNameResp(self):
        self._callback()

    def sendChooseAvatar(self, avId):
        self.sendUpdate('chooseAvatar', [avId])
        if base.cr.banManager:
            base.cr.banManager.d_sendHardwareId(self.hwId)

    def systemMessage(self, code, params):
        msg = OTPLocalizer.CRSystemMessages.get(code)
        if not msg:
            self.notify.warning('Got invalid system-message code: %d' % code)
            return
        try:
            message = msg % tuple(params)
        except TypeError:
            self.notify.warning('Got invalid parameters for system-message %d: %r' % (code, params))
            return

        whisper = WhisperPopup(message, OTPGlobals.getInterfaceFont(), WhisperPopup.WTSystem)
        whisper.manage(base.marginManager)
        if not self.systemMessageSfx:
            self.systemMessageSfx = base.loader.loadSfx('phase_4/audio/sfx/clock03.ogg')
        if self.systemMessageSfx:
            base.playSfx(self.systemMessageSfx)

    def hasReportedPlayer(self, avId):
        return avId in self.avIdsReportedThisSession

    def d_reportPlayer(self, avId, category):
        if self.hasReportedPlayer(avId):
            return
        self.avIdsReportedThisSession.append(avId)
        self.sendUpdate('reportPlayer', [avId, category])