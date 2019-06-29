from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData
from toontown.server.DedicatedServer import DedicatedServer
loadPrcFileData('dedicated server config', '\n    window-type none\n    default-directnotify-level info\n')
from toontown.toonbase.ServerSettings import ServerSettings
serverSettings = ServerSettings()
serverSettings.loadFromSettings()
from toontown.toonbase.GameSettings import GameSettings
gameSettings = GameSettings()
gameSettings.loadFromSettings()
ShowBase()
dedicatedServer = DedicatedServer(isLocal=False)
dedicatedServer.start()
base.run()