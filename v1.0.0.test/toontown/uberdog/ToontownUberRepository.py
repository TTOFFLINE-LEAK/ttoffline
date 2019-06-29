from direct.directnotify import DirectNotifyGlobal
from otp.distributed.DistributedDirectoryAI import DistributedDirectoryAI
from otp.distributed.OtpDoGlobals import *
from toontown.distributed.ToontownInternalRepository import ToontownInternalRepository

class ToontownUberRepository(ToontownInternalRepository):
    notify = DirectNotifyGlobal.directNotify.newCategory('ToontownUberRepository')

    def __init__(self, baseChannel, serverId):
        ToontownInternalRepository.__init__(self, baseChannel, serverId, dcSuffix='UD')
        self.gameServicesManager = None
        self.ttoffFriendsManager = None
        self.chatManager = None
        self.deliveryManager = None
        self.banManager = None
        self.moddingManager = None
        self.centralLogger = None
        return

    def handleConnected(self):
        ToontownInternalRepository.handleConnected(self)
        rootObj = DistributedDirectoryAI(self)
        rootObj.generateWithRequiredAndId(self.getGameDoId(), 0, 0)
        self.createGlobals()
        self.notify.info('Done.')

    def createGlobals(self):
        self.gameServicesManager = self.generateGlobalObject(OTP_DO_ID_TOONTOWN_GAME_SERVICES_MANAGER, 'TTGameServicesManager')
        self.ttoffFriendsManager = self.generateGlobalObject(OTP_DO_ID_TTOFF_FRIENDS_MANAGER, 'TTOffFriendsManager')
        self.chatManager = self.generateGlobalObject(OTP_DO_ID_CHAT_MANAGER, 'TTOffChatManager')
        self.deliveryManager = self.generateGlobalObject(OTP_DO_ID_TOONTOWN_DELIVERY_MANAGER, 'DistributedDeliveryManager')
        self.banManager = self.generateGlobalObject(OTP_DO_ID_BAN_MANAGER, 'BanManager')
        self.moddingManager = self.generateGlobalObject(OTP_DO_ID_MODDING_MANAGER, 'ModdingManager')
        self.centralLogger = self.generateGlobalObject(OTP_DO_ID_CENTRAL_LOGGER, 'CentralLogger')