from direct.directnotify import DirectNotifyGlobal
from DNALoader import DNALoader
notify = DirectNotifyGlobal.directNotify.newCategory('dna')

class DNABulkLoader:

    def __init__(self, dnaStorage, dnaFiles):
        self.dnaStorage = dnaStorage
        self.dnaFiles = dnaFiles

    def loadDNAFiles(self):
        for dnaFile in self.dnaFiles:
            notify.info('Reading %s' % dnaFile)
            loadDNABulk(self.dnaStorage, dnaFile)

        del self.dnaStorage
        del self.dnaFiles


def loadDNABulk(dnaStorage, dnaFile):
    dnaLoader = DNALoader()
    dnaFile = '/' + dnaFile
    dnaLoader.loadDNAFile(dnaStorage, dnaFile)
    dnaLoader.destroy()


def loadDNAFile(dnaStorage, dnaFile):
    notify.info('Reading %s' % dnaFile)
    dnaLoader = DNALoader()
    dnaFile = '/' + dnaFile
    node = dnaLoader.loadDNAFile(dnaStorage, dnaFile)
    dnaLoader.destroy()
    if node.node().getNumChildren() > 0:
        return node.node()
    return


def loadDNAFileAI(dnaStorage, dnaFile):
    notify.debug('Reading %s' % dnaFile)
    dnaLoader = DNALoader()
    dnaFile = '/' + dnaFile
    data = dnaLoader.loadDNAFileAI(dnaStorage, dnaFile)
    dnaLoader.destroy()
    return data