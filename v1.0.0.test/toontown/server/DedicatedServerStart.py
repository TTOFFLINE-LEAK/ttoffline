from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData
from toontown.server.DedicatedServer import DedicatedServer
import sys
loadPrcFileData('dedicated server config', '\n    window-type none\n    default-directnotify-level info\n')
if '--test' in sys.argv:
    loadPrcFileData('test server config', 'astron-config-path astron/config/astrond_test.yml')
from toontown.toonbase.ServerSettings import ServerSettings
serverSettings = ServerSettings()
serverSettings.loadFromSettings()
from toontown.toonbase.ToontownSettings import ToontownSettings
gameSettings = ToontownSettings()
gameSettings.loadFromSettings()
ShowBase()
dedicatedServer = DedicatedServer(isLocal=False)
dedicatedServer.start()
base.run()