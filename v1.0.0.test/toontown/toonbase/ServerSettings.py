from direct.directnotify import DirectNotifyGlobal
from otp.settings.Settings import Settings

class ServerSettings:
    notify = DirectNotifyGlobal.directNotify.newCategory('ServerSettings')
    notify.setInfo(True)

    def __init__(self):
        self.settings = Settings('config/server.json')

    def loadFromSettings(self):
        self.notify.info('Loading settings...')
        self.uberDogBaseChannel = 1000000
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
        self.uberDogExpectedBuiltin = ''
        self.uberDogExpectedLocals = []
        uberDogConfigs = self.settings.getList('uberdog', 'configs', ['config/general.prc', 'config/prod.prc'])
        self.settings.updateSetting('uberdog', 'configs', uberDogConfigs)
        self.uberDogConfigs = uberDogConfigs
        uberDogServerPassword = self.settings.getString('uberdog', 'server-password', '')
        self.settings.updateSetting('uberdog', 'server-password', uberDogServerPassword)
        self.uberDogServerPassword = uberDogServerPassword
        uberDogWhitelistedUsernames = self.settings.getList('uberdog', 'whitelisted-usernames', [], -1)
        self.settings.updateSetting('uberdog', 'whitelisted-usernames', uberDogWhitelistedUsernames)
        self.uberDogWhitelistedUsernames = uberDogWhitelistedUsernames
        uberDogDefaultAccessLevel = self.settings.getString('uberdog', 'default-access-level', 'USER')
        self.settings.updateSetting('uberdog', 'default-access-level', uberDogDefaultAccessLevel)
        self.uberDogDefaultAccessLevel = uberDogDefaultAccessLevel
        self.aiBaseChannel = 401000000
        aiMaxChannels = self.settings.getInt('ai', 'max-channels', 999999)
        self.settings.updateSetting('ai', 'max-channels', aiMaxChannels)
        self.aiMaxChannels = aiMaxChannels
        aiStateServer = self.settings.getInt('ai', 'stateserver', 4002)
        self.settings.updateSetting('ai', 'stateserver', aiStateServer)
        self.aiStateServer = aiStateServer
        aiDistrictName = self.settings.getString('ai', 'district-name', 'Toon Valley')
        self.settings.updateSetting('ai', 'district-name', aiDistrictName)
        self.aiDistrictName = aiDistrictName
        aiAstronIP = self.settings.getString('ai', 'astron-ip', '127.0.0.1:7199')
        self.settings.updateSetting('ai', 'astron-ip', aiAstronIP)
        self.aiAstronIP = aiAstronIP
        aiEventLoggerIP = self.settings.getString('ai', 'eventlogger-ip', '127.0.0.1:7197')
        self.settings.updateSetting('ai', 'eventlogger-ip', aiEventLoggerIP)
        self.aiEventLoggerIP = aiEventLoggerIP
        aiConfigs = self.settings.getList('ai', 'configs', ['config/general.prc', 'config/prod.prc'])
        self.settings.updateSetting('ai', 'configs', aiConfigs)
        self.aiConfigs = aiConfigs
        expMultiplier = self.settings.getFloat('ai', 'exp-multiplier', 1.0)
        self.settings.updateSetting('ai', 'exp-multiplier', expMultiplier)
        self.expMultiplier = expMultiplier
        meritMultiplier = self.settings.getFloat('ai', 'merit-multiplier', 1.0)
        self.settings.updateSetting('ai', 'merit-multiplier', meritMultiplier)
        self.meritMultiplier = meritMultiplier
        doodleMultiplier = self.settings.getFloat('ai', 'doodle-multiplier', 1.0)
        self.settings.updateSetting('ai', 'doodle-multiplier', doodleMultiplier)
        self.doodleMultiplier = doodleMultiplier
        defaultMaxToon = self.settings.getBool('ai', 'default-max-toon', False)
        self.settings.updateSetting('ai', 'default-max-toon', defaultMaxToon)
        self.defaultMaxToon = defaultMaxToon
        defaultZone = self.settings.getString('ai', 'default-zone', 'TTC')
        self.settings.updateSetting('ai', 'default-zone', defaultZone)
        self.defaultZone = defaultZone
        aiDistrictLimit = self.settings.getInt('ai', 'district-limit', 16)
        self.settings.updateSetting('ai', 'district-limit', aiDistrictLimit)
        self.aiDistrictLimit = aiDistrictLimit
        aiDistrictDescription = self.settings.getString('ai', 'district-description', 'A Toontown Offline Mini-Server.')
        self.settings.updateSetting('ai', 'district-description', aiDistrictDescription)
        self.aiDistrictDescription = aiDistrictDescription
        aiDistrictId = self.settings.getString('ai', 'district-id', '')
        self.settings.updateSetting('ai', 'district-id', aiDistrictId)
        self.aiDistrictId = aiDistrictId
        aiEventId = self.settings.getString('ai', 'event-id', '')
        self.settings.updateSetting('ai', 'event-id', aiEventId)
        self.aiEventId = aiEventId
        self.notify.info('Loaded.')