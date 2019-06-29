from panda3d.core import *
from otp.otpbase import PythonUtil
import __builtin__
from toontown.toonbase.ServerSettings import ServerSettings
serverSettings = ServerSettings()
serverSettings.loadFromSettings()
for prc in serverSettings.aiConfigs:
    loadPrcFile(prc)

localConfig = ''
if serverSettings.aiBaseChannel:
    localConfig += 'air-base-channel %s\n' % serverSettings.aiBaseChannel
if serverSettings.aiMaxChannels:
    localConfig += 'air-channel-allocation %s\n' % serverSettings.aiMaxChannels
if serverSettings.aiStateServer:
    localConfig += 'air-stateserver %s\n' % serverSettings.aiStateServer
if serverSettings.aiDistrictName:
    localConfig += 'district-name %s\n' % serverSettings.aiDistrictName
if serverSettings.aiAstronIP:
    localConfig += 'air-connect %s\n' % serverSettings.aiAstronIP
if serverSettings.aiEventLoggerIP:
    localConfig += 'eventlog-host %s\n' % serverSettings.aiEventLoggerIP
if serverSettings.aiDistrictLimit:
    localConfig += 'district-limit %s\n' % serverSettings.aiDistrictLimit
if serverSettings.aiDistrictDescription:
    localConfig += 'district-description %s\n' % serverSettings.aiDistrictDescription
if serverSettings.aiDistrictId:
    localConfig += 'district-id %s\n' % serverSettings.aiDistrictId
if serverSettings.aiEventId:
    localConfig += 'event-id %s\n' % serverSettings.aiEventId
if serverSettings.uberDogDefaultAccessLevel:
    localConfig += 'default-access-level %s\n' % serverSettings.uberDogDefaultAccessLevel
loadPrcFileData('AI Args Config', localConfig)
from toontown.toonbase.ToontownSettings import ToontownSettings
gameSettings = ToontownSettings()
gameSettings.loadFromSettings()

class game:
    name = 'toontown'
    process = 'server'


__builtin__.game = game
from otp.ai.AIBaseGlobal import *
from toontown.ai.ToontownAIRepository import ToontownAIRepository
simbase.air = ToontownAIRepository(config.GetInt('air-base-channel', 401000000), config.GetInt('air-stateserver', 10000), config.GetString('district-name', 'Toon Valley'), config.GetInt('district-limit', 16), config.GetString('district-description', 'A Toontown Offline Mini-Server.'), config.GetString('district-id', ''), config.GetString('event-id', ''), config.GetString('default-access-level', 'USER'))
host = config.GetString('air-connect', '127.0.0.1')
port = 7199
if ':' in host:
    host, port = host.split(':', 1)
    port = int(port)
simbase.air.connect(host, port)
try:
    run()
except SystemExit:
    raise
except Exception:
    info = PythonUtil.describeException()
    simbase.air.writeServerEvent('ai-exception', avId=simbase.air.getAvatarIdFromSender(), accId=simbase.air.getAccountIdFromSender(), exception=info)
    raise