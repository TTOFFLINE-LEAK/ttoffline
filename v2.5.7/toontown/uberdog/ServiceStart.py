import gc
gc.disable()
from panda3d.core import *
import __builtin__
from toontown.toonbase.ServerSettings import ServerSettings
serverSettings = ServerSettings()
serverSettings.loadFromSettings()
from toontown.toonbase.GameSettings import GameSettings
gameSettings = GameSettings()
gameSettings.loadFromSettings()
localconfig = ''
if serverSettings.uberDogMaxChannels:
    localconfig += 'air-channel-allocation %s\n' % serverSettings.uberDogMaxChannels
if serverSettings.uberDogStateServer:
    localconfig += 'air-stateserver %s\n' % serverSettings.uberDogStateServer
if serverSettings.uberDogAstronIP:
    localconfig += 'air-connect %s\n' % serverSettings.uberDogAstronIP
if serverSettings.uberDogEventLoggerIP:
    localconfig += 'eventlog-host %s\n' % serverSettings.uberDogEventLoggerIP
if serverSettings.uberDogServerPassword:
    localconfig += 'server-password %s\n' % serverSettings.uberDogServerPassword
if serverSettings.uberDogDefaultAccessLevel:
    localconfig += 'default-access-level %s\n' % serverSettings.uberDogDefaultAccessLevel
loadPrcFileData('Command-line', localconfig)

class game:
    name = 'uberDog'
    process = 'server'


__builtin__.game = game
from otp.ai.AIBaseGlobal import *
from toontown.uberdog.ToontownUberRepository import ToontownUberRepository
simbase.air = ToontownUberRepository(config.GetInt('air-base-channel', 400000000), config.GetInt('air-stateserver', 10000))
host = config.GetString('air-connect', '127.0.0.1')
port = 7199
if ':' in host:
    host, port = host.split(':', 1)
    port = int(port)
simbase.air.connect(host, port)
gc.enable()
gc.collect()
try:
    run()
except SystemExit:
    raise
except Exception:
    info = PythonUtil.describeException()
    simbase.air.writeServerEvent('uberdog-exception', avId=simbase.air.getAvatarIdFromSender(), accId=simbase.air.getAccountIdFromSender(), info=info)
    raise