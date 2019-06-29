import gc
gc.disable()
from panda3d.core import *
import __builtin__, os
from toontown.toonbase.ServerSettings import ServerSettings
serverSettings = ServerSettings()
serverSettings.loadFromSettings()
from toontown.toonbase.GameSettings import GameSettings
gameSettings = GameSettings()
gameSettings.loadFromSettings()
localconfig = ''
if serverSettings.aiMaxChannels:
    localconfig += 'air-channel-allocation %s\n' % serverSettings.aiMaxChannels
if serverSettings.aiStateServer:
    localconfig += 'air-stateserver %s\n' % serverSettings.aiStateServer
if serverSettings.aiDistrictName:
    localconfig += 'district-name %s\n' % serverSettings.aiDistrictName
if serverSettings.aiAstronIP:
    localconfig += 'air-connect %s\n' % serverSettings.aiAstronIP
if serverSettings.aiEventLoggerIP:
    localconfig += 'eventlog-host %s\n' % serverSettings.aiEventLoggerIP
if serverSettings.aiHolidayPasscode:
    localconfig += 'holiday-passcode %s\n' % serverSettings.aiHolidayPasscode
if serverSettings.aiServerDescription:
    localconfig += 'server-description %s\n' % serverSettings.aiServerDescription
if serverSettings.aiServerId:
    localconfig += 'server-id %s\n' % serverSettings.aiServerId
loadPrcFileData('Command-line', localconfig)

class game:
    name = 'toontown'
    process = 'server'


__builtin__.game = game
from otp.ai.AIBaseGlobal import *
from toontown.ai.ToontownAIRepository import ToontownAIRepository
simbase.air = ToontownAIRepository(config.GetInt('air-base-channel', 401000000), config.GetInt('air-stateserver', 10000), config.GetString('district-name', 'Devhaven'), config.GetString('holiday-passcode', ''), config.GetString('server-description', 'A Toontown Offline Mini-Server.'), config.GetString('server-id', ''))
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
    if not os.path.exists('logs/'):
        os.mkdir('logs/')
    info = PythonUtil.describeException()
    simbase.air.writeServerEvent('ai-exception', avId=simbase.air.getAvatarIdFromSender(), accId=simbase.air.getAccountIdFromSender(), exception=info)
    with open(config.GetString('ai-crash-log-name', 'logs/ai-crash.log'), 'w+') as (f):
        f.write(info + '\n')
    raise