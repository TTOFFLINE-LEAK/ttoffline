import atexit, os, subprocess, sys, time
from direct.directnotify import DirectNotifyGlobal
from otp.otpbase import OTPLocalizer
ASTRON_DONE_MSG = 'Event Logger: Opened new log.'
UBERDOG_DONE_MSG = 'ToontownUberRepository: Done.'
AI_DONE_MSG = 'District is now ready. Have fun in Toontown Offline!'
AI_ZONE_MSG = 'Creating zone... '
PYTHON_TRACEBACK_MSG = 'Traceback (most recent call last):'
INTERNAL_EXCEPTION_MSG = ':AstronInternalRepository(warning): INTERNAL-EXCEPTION: '

class DedicatedServer:
    notify = DirectNotifyGlobal.directNotify.newCategory('DedicatedServer')

    def __init__(self, isLocal=False):
        self.isLocal = isLocal
        self.astronProcess = None
        self.astronLog = None
        self.uberDogProcess = None
        self.uberDogLog = None
        self.uberDogInternalExceptions = []
        self.aiProcess = None
        self.aiLog = None
        self.aiInternalExceptions = []
        return

    def start(self):
        atexit.register(self.killProcesses)
        if self.isLocal:
            self.notify.info('Starting local server...')
        else:
            self.notify.info('Starting dedicated server...')
        if config.GetBool('auto-start-local-server', True) and not self.isLocal and not config.GetBool('mini-server', False):
            self.notify.warning('You are trying to start the server manually, but auto-start-local-server is enabled!\nYou do not need to run this file in singleplayer, the server will start for you.\nRunning this file and the game in singleplayer with auto-start-local-server on will break the server.\nIf you wish to use this file anyway, either connect to your server as a miniserver, or disable auto-start-local-server in settings.json.\nIf you intend to run the server only, no harm will come from continuing.\nDisable auto-start-local-server in settings.json to remove this warning.\nKeep in mind that if you disable this setting you will have to run this file to play singleplayer.\n')
            shouldQuit = raw_input('Press enter to continue, or type "q" and press enter to quit.\n').lower()
            if shouldQuit == 'q':
                sys.exit()
        self.notify.info('Starting Astron...')
        astronLogFile = self.generateLog('astron')
        self.astronLog = open(astronLogFile, 'a')
        self.notify.info('Opened new Astron log: %s' % astronLogFile)
        if config.GetBool('auto-start-local-server', True):
            gameServicesDialog['text'] = OTPLocalizer.CRLoadingGameServices + '\n\n' + OTPLocalizer.CRLoadingGameServicesAstron
        astronConfig = config.GetString('astron-config-path', 'astron/config/astrond.yml')
        if sys.platform == 'win32':
            self.astronProcess = subprocess.Popen(('astron\\astrond.exe --loglevel info {0}').format(astronConfig.replace('/', '\\')), stdin=self.astronLog, stdout=self.astronLog, stderr=self.astronLog)
        else:
            if sys.platform == 'linux2':
                env = os.environ.copy()
                env['LD_LIBRARY_PATH'] = os.path.abspath('./astron/libraries')
                self.astronProcess = subprocess.Popen([
                 './astron/astrond-linux', '--loglevel', 'info', astronConfig], stdin=self.astronLog, stdout=self.astronLog, stderr=self.astronLog, env=env)
            else:
                self.astronProcess = subprocess.Popen([
                 './astron/astrond', '--loglevel', 'info', astronConfig], stdin=self.astronLog, stdout=self.astronLog, stderr=self.astronLog)
        taskMgr.add(self.startUberDog, 'start-uberdog-task')

    def startUberDog(self, task):
        astronLogFile = self.astronLog.name
        astronLog = open(astronLogFile)
        astronLogData = astronLog.read()
        astronLog.close()
        if ASTRON_DONE_MSG not in astronLogData:
            return task.again
        self.notify.info('Astron started successfully!')
        self.notify.info('Starting UberDOG server...')
        uberDogLogFile = self.generateLog('uberdog')
        self.uberDogLog = open(uberDogLogFile, 'a')
        self.notify.info('Opened new UberDOG log: %s' % uberDogLogFile)
        if sys.platform == 'win32':
            uberDogArguments = 'TTOffEngine.exe --uberdog'
        else:
            uberDogArguments = [
             './TTOffEngine', '--uberdog']
        if config.GetBool('auto-start-local-server', True):
            gameServicesDialog['text'] = OTPLocalizer.CRLoadingGameServices + '\n\n' + OTPLocalizer.CRLoadingGameServicesUberdog
        self.uberDogProcess = subprocess.Popen(uberDogArguments, stdin=self.uberDogLog, stdout=self.uberDogLog, stderr=self.uberDogLog)
        taskMgr.add(self.startAI, 'start-ai-task')
        return task.done

    def startAI(self, task):
        uberDogLogFile = self.uberDogLog.name
        uberDogLog = open(uberDogLogFile)
        uberDogLogData = uberDogLog.read()
        uberDogLog.close()
        if UBERDOG_DONE_MSG not in uberDogLogData:
            return task.again
        self.notify.info('UberDOG started successfully!')
        self.notify.info('Starting AI server...')
        aiLogFile = self.generateLog('ai')
        self.aiLog = open(aiLogFile, 'a')
        self.notify.info('Opened new AI log: %s' % aiLogFile)
        if sys.platform == 'win32':
            aiArguments = 'TTOffEngine.exe --ai'
        else:
            aiArguments = [
             './TTOffEngine', '--ai']
        if config.GetBool('auto-start-local-server', True):
            gameServicesDialog['text'] = OTPLocalizer.CRLoadingGameServices + '\n\n' + OTPLocalizer.CRLoadingGameServicesAI
        self.aiProcess = subprocess.Popen(aiArguments, stdin=self.aiLog, stdout=self.aiLog, stderr=self.aiLog)
        taskMgr.add(self.serverStarted, 'server-started-task')
        return task.done

    def serverStarted(self, task):
        aiLogFile = self.aiLog.name
        aiLog = open(aiLogFile)
        aiLogData = aiLog.read()
        aiLog.close()
        if AI_DONE_MSG not in aiLogData:
            return task.again
        self.notify.info('AI started successfully!')
        self.notify.info('Server is now ready. Have fun in Toontown Offline!')
        if self.isLocal:
            messenger.send('localServerReady')
        taskMgr.add(self.checkForCrashes, 'check-for-crashes-task')
        return task.done

    def checkForCrashes(self, task):
        uberDogLogFile = self.uberDogLog.name
        uberDogLog = open(uberDogLogFile)
        uberDogLogData = uberDogLog.read().split('\n')
        uberDogLog.close()
        for i in xrange(len(uberDogLogData)):
            lineNum = len(uberDogLogData) - 1 - i
            line = uberDogLogData[lineNum]
            if PYTHON_TRACEBACK_MSG in line:
                previousLineNum = len(uberDogLogData) - 1 - (i + 1)
                previousLine = uberDogLogData[previousLineNum]
                if INTERNAL_EXCEPTION_MSG in previousLine:
                    if previousLineNum not in self.uberDogInternalExceptions:
                        self.uberDogInternalExceptions.append(previousLineNum)
                        self.notify.warning('An internal exception has occurred in the UberDOG server: %s' % line[len(INTERNAL_EXCEPTION_MSG):])
                else:
                    self.killProcesses()
                    self.notify.error('Oh no, this mini-server has crashed!\n\nThe UberDOG server has crashed, and you will need to restart your mini-server.\n\nIf this problem persists, please contact a developer and provide them with your most recent log from the "logs/uberdog" folder.')
            elif INTERNAL_EXCEPTION_MSG in line:
                if lineNum not in self.uberDogInternalExceptions:
                    self.uberDogInternalExceptions.append(lineNum)
                    self.notify.warning('An internal exception has occurred in the UberDOG server: %s' % line[len(INTERNAL_EXCEPTION_MSG):])

        aiLogFile = self.aiLog.name
        aiLog = open(aiLogFile)
        aiLogData = aiLog.read().split('\n')
        aiLog.close()
        for i in xrange(len(aiLogData)):
            lineNum = len(aiLogData) - 1 - i
            line = aiLogData[lineNum]
            if PYTHON_TRACEBACK_MSG in line:
                previousLineNum = len(aiLogData) - 1 - (i + 1)
                previousLine = aiLogData[previousLineNum]
                if INTERNAL_EXCEPTION_MSG in previousLine:
                    if previousLineNum not in self.aiInternalExceptions:
                        self.aiInternalExceptions.append(previousLineNum)
                        self.notify.warning('An internal exception has occurred in the AI server: %s' % line[len(INTERNAL_EXCEPTION_MSG):])
                else:
                    self.killProcesses()
                    self.notify.error('Oh no, this mini-server has crashed!\n\nThe AI server has crashed, and you will need to restart your mini-server.\n\nIf this problem persists, please contact a developer and provide them with your most recent log from the "logs/ai" folder.')
            elif INTERNAL_EXCEPTION_MSG in line:
                if lineNum not in self.aiInternalExceptions:
                    self.aiInternalExceptions.append(lineNum)
                    self.notify.warning('An internal exception has occurred in the AI server: %s' % line[len(INTERNAL_EXCEPTION_MSG):])

        return task.again

    def killProcesses(self):
        if self.aiProcess:
            self.aiProcess.terminate()
        if self.uberDogProcess:
            self.uberDogProcess.terminate()
        if self.astronProcess:
            self.astronProcess.terminate()

    @staticmethod
    def generateLog(logPrefix):
        ltime = 1 and time.localtime()
        logSuffix = '%02d%02d%02d_%02d%02d%02d' % (ltime[0] - 2000, ltime[1], ltime[2],
         ltime[3], ltime[4], ltime[5])
        if not os.path.exists('logs/'):
            os.mkdir('logs/')
        if not os.path.exists('logs/%s/' % logPrefix):
            os.mkdir('logs/%s/' % logPrefix)
        logFile = 'logs/%s/%s-%s.log' % (logPrefix, logPrefix, logSuffix)
        return logFile