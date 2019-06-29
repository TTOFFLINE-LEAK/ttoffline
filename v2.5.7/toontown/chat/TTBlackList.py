import os, datetime
from panda3d.core import *
from direct.directnotify import DirectNotifyGlobal
from direct.showbase import AppRunnerGlobal
from otp.chat.BlackList import BlackList
from toontown.toonbase import TTLocalizer

class TTBlackList(BlackList):
    RedownloadTaskName = 'RedownloadBlacklistTask'
    BlacklistBaseDir = config.GetString('blacklist-base-dir', '')
    BlacklistStageDir = config.GetString('blacklist-stage-dir', 'blacklist')
    BlacklistOverHttp = config.GetBool('blacklist-over-http', False)
    BlacklistFileName = config.GetString('blacklist-filename', 'tblacklist.dat')

    def __init__(self):
        self.redownloadingBlacklist = False
        self.startRedownload = datetime.datetime.now()
        self.endRedownload = datetime.datetime.now()
        self.percentDownloaded = 0.0
        self.notify = DirectNotifyGlobal.directNotify.newCategory('TTBlackList')
        if not os.path.exists('config/'):
            os.mkdir('config/')
        if not os.path.isfile('config/%s' % self.BlacklistFileName):
            from toontown.chat.BlackListData import BlackListData
            with open('config/%s' % self.BlacklistFileName, 'w') as (data):
                data.write(BlackListData)
                data.close()
        blacklistFile = open('config/%s' % self.BlacklistFileName)
        data = blacklistFile.read()
        blacklistFile.close()
        lines = data.split('\n')
        BlackList.__init__(self, lines)
        if self.BlacklistOverHttp:
            self.redownloadBlacklist()
        self.defaultWord = TTLocalizer.ChatGarblerDefault[0]

    def unload(self):
        self.removeDownloadingTextTask()

    def redownloadBlacklist(self):
        self.percentDownload = 0.0
        self.notify.info('starting redownloadBlacklist')
        self.startRedownload = datetime.datetime.now()
        self.redownloadingBlacklist = True
        self.addDownloadingTextTask()
        self.blacklistUrl = self.getBlacklistUrl()
        self.blacklistDir = Filename(self.findBlacklistDir())
        Filename(self.blacklistDir + '/.').makeDir()
        http = HTTPClient.getGlobalPtr()
        self.url = self.blacklistUrl + self.BlacklistFileName
        self.ch = http.makeChannel(True)
        localFilename = Filename(self.blacklistDir, 'tblacklist.dat')
        self.ch.getHeader(DocumentSpec(self.url))
        size = self.ch.getFileSize()
        doc = self.ch.getDocumentSpec()
        localSize = localFilename.getFileSize()
        outOfDate = True
        if size == localSize:
            if doc.hasDate():
                date = doc.getDate()
                localDate = HTTPDate(localFilename.getTimestamp())
                if localDate.compareTo(date) > 0:
                    outOfDate = False
                    self.notify.info('Blacklist is up to date')
        taskMgr.remove(self.RedownloadTaskName)
        if outOfDate and self.ch.isValid():
            self.ch.beginGetDocument(doc)
            self.ch.downloadToFile(localFilename)
            taskMgr.add(self.downloadBlacklistTask, self.RedownloadTaskName)
        else:
            self.updateBlacklist()

    def getBlacklistUrl(self):
        result = config.GetString('fallback-blacklist-url', 'http://cdn.toontown.disney.go.com/toontown/en/')
        override = config.GetString('blacklist-url', '')
        if override:
            self.notify.info('got an override url,  using %s for the blacklist' % override)
            result = override
        else:
            try:
                launcherUrl = base.launcher.getValue('GAME_BLACKLIST_URL', '')
                if launcherUrl:
                    result = launcherUrl
                    self.notify.info('got GAME_BLACKLIST_URL from launcher using %s' % result)
                else:
                    self.notify.info('blank GAME_BLACKLIST_URL from launcher, using %s' % result)
            except:
                self.notify.warning('got exception getting GAME_BLACKLIST_URL from launcher, using %s' % result)

        return result

    def addDownloadingTextTask(self):
        self.removeDownloadingTextTask()
        task = taskMgr.doMethodLater(1, self.loadingTextTask, 'BlacklistDownloadingTextTask')
        task.startTime = globalClock.getFrameTime()
        self.loadingTextTask(task)

    def removeDownloadingTextTask(self):
        taskMgr.remove('BlacklistDownloadingTextTask')

    def loadingTextTask(self, task):
        timeIndex = int(globalClock.getFrameTime() - task.startTime) % 3
        timeStrs = (TTLocalizer.NewsPageDownloadingNews0, TTLocalizer.NewsPageDownloadingNews1, TTLocalizer.NewsPageDownloadingNews2)
        textToDisplay = timeStrs[timeIndex] % int(self.percentDownloaded * 100)
        return task.again

    def findBlacklistDir(self):
        if self.BlacklistOverHttp:
            return self.BlacklistStageDir
        searchPath = DSearchPath()
        if AppRunnerGlobal.appRunner:
            searchPath.appendDirectory(Filename.expandFrom('$TT_3_5_ROOT/phase_3.5/models/news'))
        else:
            basePath = os.path.expandvars('$TTMODELS') or './ttmodels'
            searchPath.appendDirectory(Filename.fromOsSpecific(basePath + '/built/' + self.NewsBaseDir))
            searchPath.appendDirectory(Filename(self.NewsBaseDir))
        pfile = Filename(self.BlacklistFileName)
        found = vfs.resolveFilename(pfile, searchPath)
        if not found:
            self.notify.warning('findBlacklistDir - no path: %s' % self.BlacklistFileName)
            self.setErrorMessage(TTLocalizer.NewsPageErrorDownloadingFile % self.BlacklistFileName)
            return None
        self.notify.debug('found blacklist file %s' % pfile)
        realDir = pfile.getDirname()
        return realDir

    def downloadBlacklistTask(self, task):
        if self.ch.run():
            return task.cont
        doc = self.ch.getDocumentSpec()
        date = ''
        if doc.hasDate():
            date = doc.getDate().getString()
        if not self.ch.isValid():
            self.notify.warning('Unable to download %s' % self.url)
            self.redownloadingBlacklist = False
            return task.done
        self.notify.info('Done downloading blacklist file')
        self.updateBlacklist()
        return task.done

    def updateBlacklist(self):
        localFilename = Filename(self.blacklistDir, 'tblacklist.dat')
        if not localFilename.exists():
            return
        data = vfs.readFile(localFilename, 1)
        lines = data.split('\n')
        self.words = []
        for line in lines:
            self.words.append(line.strip('\n\r').lower())

        self.words.sort()
        self.numWords = len(self.words)
        self.defaultWord = TTLocalizer.ChatGarblerDefault[0]

    def handleNewBlacklist(self):
        self.redownloadBlacklist()