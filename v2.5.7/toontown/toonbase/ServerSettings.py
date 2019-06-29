from direct.directnotify import DirectNotifyGlobal
from otp.otpbase.Settings import Settings

class ServerSettings:
    notify = DirectNotifyGlobal.directNotify.newCategory('ServerSettings')
    notify.setInfo(True)

    def __init__(self):
        self.settings = Settings('config/server.json')

    def loadFromSettings(self):
        self.notify.info('Loading settings...')
        uberDogMaxChannels = self.settings.getInt('uberdog', 'max-channels', 999999)
        self.settings.updateSetting('uberdog', 'max-channels', uberDogMaxChannels)
        self.uberDogMaxChannels = uberDogMaxChannels
        uberDogStateServer = self.settings.getInt('uberdog', 'stateserver', 4002)
        self.settings.updateSetting('uberdog', 'stateserver', uberDogStateServer)
        self.uberDogStateServer = uberDogStateServer
        uberDogAstronIP = self.settings.getString('uberdog', 'astron-ip', '127.0.0.1:7199')
        self.settings.updateSetting('uberdog', 'astron-ip', uberDogAstronIP)
        self.uberDogAstronIP = uberDogAstronIP
        uberDogEventLoggerIP = self.settings.getString('uberdog', 'eventlogger-ip', '127.0.0.1:7197')
        self.settings.updateSetting('uberdog', 'eventlogger-ip', uberDogEventLoggerIP)
        self.uberDogEventLoggerIP = uberDogEventLoggerIP
        uberDogServerPassword = self.settings.getString('uberdog', 'server-password', '')
        self.settings.updateSetting('uberdog', 'server-password', uberDogServerPassword)
        self.uberDogServerPassword = uberDogServerPassword
        uberDogDefaultAccessLevel = self.settings.getInt('uberdog', 'default-access-level', 307)
        self.settings.updateSetting('uberdog', 'default-access-level', uberDogDefaultAccessLevel)
        self.uberDogDefaultAccessLevel = uberDogDefaultAccessLevel
        aiMaxChannels = self.settings.getInt('ai', 'max-channels', 999999)
        self.settings.updateSetting('ai', 'max-channels', aiMaxChannels)
        self.aiMaxChannels = aiMaxChannels
        aiStateServer = self.settings.getInt('ai', 'stateserver', 4002)
        self.settings.updateSetting('ai', 'stateserver', aiStateServer)
        self.aiStateServer = aiStateServer
        aiDistrictName = self.settings.getString('ai', 'district-name', 'Toontown')
        self.settings.updateSetting('ai', 'district-name', aiDistrictName)
        self.aiDistrictName = aiDistrictName
        aiAstronIP = self.settings.getString('ai', 'astron-ip', '127.0.0.1:7199')
        self.settings.updateSetting('ai', 'astron-ip', aiAstronIP)
        self.aiAstronIP = aiAstronIP
        aiEventLoggerIP = self.settings.getString('ai', 'eventlogger-ip', '127.0.0.1:7197')
        self.settings.updateSetting('ai', 'eventlogger-ip', aiEventLoggerIP)
        self.aiEventLoggerIP = aiEventLoggerIP
        aiHolidayPasscode = self.settings.getString('ai', 'holiday-passcode', '')
        self.settings.updateSetting('ai', 'holiday-passcode', aiHolidayPasscode)
        self.aiHolidayPasscode = aiHolidayPasscode
        aiServerDescription = self.settings.getString('ai', 'server-description', 'A Toontown Offline Mini-Server.')
        self.settings.updateSetting('ai', 'server-description', aiServerDescription)
        self.aiServerDescription = aiServerDescription
        aiServerId = self.settings.getString('ai', 'server-id', '')
        self.settings.updateSetting('ai', 'server-id', aiServerId)
        self.aiServerId = aiServerId
        self.notify.info('Loaded.')