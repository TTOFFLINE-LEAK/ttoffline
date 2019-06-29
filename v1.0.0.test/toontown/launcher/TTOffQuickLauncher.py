import os
from direct.showbase.EventManagerGlobal import *
from toontown.launcher.TTOffLauncherBase import TTOffLauncherBase
from toontown.toonbase import TTLocalizer

class TTOffQuickLauncher(TTOffLauncherBase):
    GameName = 'Toontown Offline'
    ForegroundSleepTime = 0.001
    Localizer = TTLocalizer

    def __init__(self):
        print 'Running: TTOffQuickLauncher'
        TTOffLauncherBase.__init__(self)
        self.useTTOffSpecificLogin = config.GetBool('ttoff-specific-login', 0)
        self.ttoffPlayTokenKey = 'TTOFF_PLAY_TOKEN'
        print 'useTTOffSpecificLogin=%s' % self.useTTOffSpecificLogin
        self.parseWebAcctParams()
        self.showPhase = -1
        self.maybeStartGame()
        self.mainLoop()

    def getValue(self, key, default=None):
        return os.environ.get(key, default)

    def setValue(self, key, value):
        os.environ[key] = str(value)

    def getTestServerFlag(self):
        return self.getValue('IS_TEST_SERVER', 0)

    def getGameServer(self):
        return self.getValue('TTOFF_GAME_SERVER', '127.0.0.1')

    def getLogFileName(self):
        return 'ttoff'

    def parseWebAcctParams(self):
        self.secretNeedsParentPasswordKey = 0
        self.chatEligibleKey = 1

    def getBlue(self):
        return

    def getPlayToken(self):
        playToken = self.getValue(self.ttoffPlayTokenKey)
        self.setValue(self.ttoffPlayTokenKey, '')
        if playToken == 'NO PLAYTOKEN':
            playToken = None
        return playToken

    def setRegistry(self, name, value):
        pass

    def getRegistry(self, name, missingValue=None):
        self.notify.info('getRegistry %s' % ((name, missingValue),))
        self.notify.info('checking env' % os.environ)
        if missingValue == None:
            missingValue = ''
        value = os.environ.get(name, missingValue)
        try:
            value = int(value)
        except:
            pass

        return value

    def getAccountServer(self):
        return ''

    def getGame2Done(self):
        return True

    def getNeedPwForSecretKey(self):
        if self.useTTOffSpecificLogin:
            self.notify.info('getNeedPwForSecretKey using ttoff-specific-login')
            return False
        return self.secretNeedsParentPasswordKey

    def getParentPasswordSet(self):
        if self.useTTOffSpecificLogin:
            self.notify.info('getParentPasswordSet using ttoff-specific-login')
            return True
        return self.chatEligibleKey

    def startGame(self):
        self.newTaskManager()
        eventMgr.restart()
        from toontown.toonbase import ToontownStart