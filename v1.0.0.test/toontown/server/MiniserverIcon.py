import os, shutil, datetime
from panda3d.core import *
from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObject
from direct.showbase import AppRunnerGlobal
from toontown.toonbase import TTLocalizer

class MiniserverIcon(DistributedObject.DistributedObject):
    RedownloadTaskName = 'RedownloadMiniserverIcon'
    IconsBaseDir = 'icons'
    notify = DirectNotifyGlobal.directNotify.newCategory('MiniserverIcon')

    def __init__(self, fileName, url):
        self.iconFileName = fileName + '.jpg'
        self.iconUrl = url
        self.downloadingIcon = False
        self.percentDownloaded = 0.0
        self.startDownload = datetime.datetime.now()
        self.endDownload = datetime.datetime.now()
        self.notify.info('Miniserver Icon url is %s' % self.iconUrl)
        self.redownloadIcon()

    def replaceTexture(self):
        searchPath = DSearchPath()
        searchPath.appendDirectory(self.directory)

    def redownloadIcon(self):
        self.precentDownload = 0.0
        self.startRedownload = datetime.datetime.now()
        self.downloadingIcon = True
        Filename(self.IconsBaseDir + '/.').makeDir()
        http = HTTPClient.getGlobalPtr()
        self.url = self.iconUrl
        self.ch = http.makeChannel(True)
        localFilename = Filename(self.IconsBaseDir, self.iconFileName)
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
                    self.notify.info('Miniserver Icon is up to date')
        if outOfDate and self.ch.isValid():
            self.ch.beginGetDocument(doc)
            self.ch.downloadToFile(localFilename)
            taskMgr.add(self.downloadIconTask, self.RedownloadTaskName)

    def downloadIconTask(self, task):
        if self.ch.run():
            return task.cont
        doc = self.ch.getDocumentSpec()
        date = ''
        if doc.hasDate():
            date = doc.getDate().getString()
        if not self.ch.isValid():
            self.redownloadingIcon = False
            return task.done
        self.notify.info('Done downloading miniserver icons')
        return task.done