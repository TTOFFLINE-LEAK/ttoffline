from panda3d.core import *
from direct.directnotify.DirectNotifyGlobal import *
from direct.showbase import Loader
from toontown.toontowngui import TTOffLoadingScreen
from toontown.dna.DNAParser import *

class ToontownLoader(Loader.Loader):
    TickPeriod = 0.2

    def __init__(self, base):
        Loader.Loader.__init__(self, base)
        self.inBulkBlock = None
        self.blockName = None
        self.loadingScreen = TTOffLoadingScreen.TTOffLoadingScreen()
        return

    def destroy(self):
        self.loadingScreen.destroy()
        del self.loadingScreen
        Loader.Loader.destroy(self)

    def beginBulkLoad(self, name, label, range, gui, tipCategory):
        self._loadStartT = globalClock.getRealTime()
        Loader.Loader.notify.info("starting bulk load of block '%s'" % name)
        if self.inBulkBlock:
            Loader.Loader.notify.warning("Tried to start a block ('%s'), but am already in a block ('%s')" % (name, self.blockName))
            return
        self.inBulkBlock = 1
        self._lastTickT = globalClock.getRealTime()
        self.blockName = name
        if hasattr(base, 'cr') and base.cr.currentEpisode == 'short_work':
            self.loadingScreen.highRiseReset()
        else:
            if not self.loadingScreen.firstInit:
                self.loadingScreen.generalReset()
        self.loadingScreen.begin(range, label, gui, tipCategory)
        return

    def endBulkLoad(self, name):
        if not self.inBulkBlock:
            Loader.Loader.notify.warning("Tried to end a block ('%s'), but not in one" % name)
            return
        if name != self.blockName:
            Loader.Loader.notify.warning("Tried to end a block ('%s'), other then the current one ('%s')" % (name, self.blockName))
            return
        self.inBulkBlock = None
        if base.cr.loadingStuff == 69:
            self.loadingScreen.end(name)
            expectedCount = 0
            loadedCount = 0
        else:
            if base.cr.currentEpisode == 'short_work' or base.cr.currentEpisode == 'gyro_tale':
                self.loadingScreen.end(name)
                expectedCount = 0
                loadedCount = 0
            else:
                expectedCount, loadedCount = self.loadingScreen.end(name)
        now = globalClock.getRealTime()
        Loader.Loader.notify.info("At end of block '%s', expected %s, loaded %s, duration=%s" % (self.blockName,
         expectedCount,
         loadedCount,
         now - self._loadStartT))
        return

    def abortBulkLoad(self):
        if self.inBulkBlock:
            Loader.Loader.notify.info("Aborting block ('%s')" % self.blockName)
            self.inBulkBlock = None
            self.loadingScreen.abort()
        return

    def tick(self):
        if self.inBulkBlock:
            now = globalClock.getRealTime()
            if now - self._lastTickT > self.TickPeriod:
                self._lastTickT += self.TickPeriod
                self.loadingScreen.tick()
                try:
                    base.cr.considerHeartbeat()
                except:
                    pass

    def loadModel(self, *args, **kw):
        ret = Loader.Loader.loadModel(self, *args, **kw)
        self.tick()
        return ret

    def loadFont(self, *args, **kw):
        ret = Loader.Loader.loadFont(self, *args, **kw)
        self.tick()
        return ret

    def loadTexture(self, texturePath, alphaPath=None, okMissing=False):
        ret = Loader.Loader.loadTexture(self, texturePath, alphaPath, okMissing=okMissing)
        self.tick()
        if alphaPath:
            self.tick()
        return ret

    def jazzModel(self, *args, **kw):
        ret = Loader.Loader.loadModel(self, *args, **kw)
        if ret:
            gsg = base.win.getGsg()
            if gsg:
                ret.prepareScene(gsg)
        return ret

    def jazzFont(self, *args, **kw):
        return Loader.Loader.loadFont(self, *args, **kw)

    def jazzTexture(self, texturePath, alphaPath=None, okMissing=False):
        return Loader.Loader.loadTexture(self, texturePath, alphaPath, okMissing=okMissing)

    def loadSfx(self, soundPath):
        ret = Loader.Loader.loadSfx(self, soundPath)
        self.tick()
        return ret

    def loadMusic(self, soundPath):
        ret = Loader.Loader.loadMusic(self, soundPath)
        self.tick()
        return ret

    def loadDNAFileAI(self, dnaStore, dnaFile):
        ret = loadDNAFileAI(dnaStore, dnaFile)
        self.tick()
        return ret

    def loadDNAFile(self, dnaStore, dnaFile):
        ret = loadDNAFile(dnaStore, dnaFile)
        self.tick()
        return ret