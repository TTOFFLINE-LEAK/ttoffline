from panda3d.core import *
from otp.otpbase import PythonUtil
import __builtin__
from toontown.toonbase.ServerSettings import ServerSettings
serverSettings = ServerSettings()
serverSettings.loadFromSettings()
for prc in serverSettings.uberDogConfigs:
    loadPrcFile(prc)

localConfig = ''
if serverSettings.uberDogBaseChannel:
    localConfig += 'air-base-channel %s\n' % serverSettings.uberDogBaseChannel
if serverSettings.uberDogMaxChannels:
    localConfig += 'air-channel-allocation %s\n' % serverSettings.uberDogMaxChannels
if serverSettings.uberDogStateServer:
    localConfig += 'air-stateserver %s\n' % serverSettings.uberDogStateServer
if serverSettings.uberDogAstronIP:
    localConfig += 'air-connect %s\n' % serverSettings.uberDogAstronIP
if serverSettings.uberDogEventLoggerIP:
    localConfig += 'eventlog-host %s\n' % serverSettings.uberDogEventLoggerIP
if serverSettings.uberDogExpectedBuiltin:
    localConfig += 'expected-builtin %s\n' % serverSettings.uberDogExpectedBuiltin
if serverSettings.uberDogExpectedLocals:
    localConfig += 'expected-locals %s\n' % serverSettings.uberDogExpectedLocals
if serverSettings.uberDogServerPassword:
    localConfig += 'server-password %s\n' % serverSettings.uberDogServerPassword
if serverSettings.uberDogWhitelistedUsernames:
    localConfig += 'whitelisted-usernames %s\n' % serverSettings.uberDogWhitelistedUsernames
if serverSettings.uberDogDefaultAccessLevel:
    localConfig += 'default-access-level %s\n' % serverSettings.uberDogDefaultAccessLevel
loadPrcFileData('UberDOG Args Config', localConfig)
from toontown.toonbase.ToontownSettings import ToontownSettings
gameSettings = ToontownSettings()
gameSettings.loadFromSettings()

class game:
    name = 'uberDog'
    process = 'server'


__builtin__.game = game
__builtin__.settings = serverSettings
from otp.ai.AIBaseGlobal import *
from toontown.uberdog.ToontownUberRepository import ToontownUberRepository
simbase.air = ToontownUberRepository(config.GetInt('air-base-channel', 400000000), config.GetInt('air-stateserver', 10000))
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
    simbase.air.writeServerEvent('uberdog-exception', avId=simbase.air.getAvatarIdFromSender(), accId=simbase.air.getAccountIdFromSender(), info=info)
    raise