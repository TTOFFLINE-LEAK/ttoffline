from otp.distributed.DistributedDirectoryAI import DistributedDirectoryAI
from otp.distributed.OtpDoGlobals import *
from toontown.distributed.ToontownInternalRepository import ToontownInternalRepository

class ToontownUberRepository(ToontownInternalRepository):

    def __init__(self, baseChannel, serverId):
        ToontownInternalRepository.__init__(self, baseChannel, serverId, dcSuffix='UD')
        self.wantUD = config.GetBool('want-ud', True)

    def handleConnected(self):
        ToontownInternalRepository.handleConnected(self)
        if config.GetBool('want-ClientServicesManagerUD', self.wantUD):
            rootObj = DistributedDirectoryAI(self)
            rootObj.generateWithRequiredAndId(self.getGameDoId(), 0, 0)
        self.createGlobals()
        self.notify.info('UberDOG has successfully initialized.')

    def createGlobals(self):
        self.csm = self.generateGlobalIfWanted(OTP_DO_ID_CLIENT_SERVICES_MANAGER, 'ClientServicesManager')
        self.chatAgent = self.generateGlobalIfWanted(OTP_DO_ID_CHAT_MANAGER, 'ChatAgent')
        self.friendsManager = self.generateGlobalIfWanted(OTP_DO_ID_TT_FRIENDS_MANAGER, 'TTFriendsManager')
        if config.GetBool('want-parties', True):
            self.globalPartyMgr = self.generateGlobalIfWanted(OTP_DO_ID_GLOBAL_PARTY_MANAGER, 'GlobalPartyManager')
        else:
            self.globalPartyMgr = None
        self.banManager = self.generateGlobalIfWanted(OTP_DO_ID_BAN_MANAGER, 'BanManager')
        return

    def generateGlobalIfWanted(self, doId, name):
        if config.GetBool('want-%sUD' % name, self.wantUD):
            return self.generateGlobalObject(doId, name)
        return
        return