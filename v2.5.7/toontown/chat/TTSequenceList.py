from panda3d.core import *
from otp.chat.SequenceList import SequenceList
from direct.directnotify import DirectNotifyGlobal
import os

class TTSequenceList(SequenceList):

    def __init__(self):
        self.notify = DirectNotifyGlobal.directNotify.newCategory('TTSequenceList')
        sequenceListURL = config.GetString('blacklist-sequence-url', '')
        if sequenceListURL == '':
            self.notify.warning('No Sequence BL URL specified! Continuing with local sequence.')
            SequenceList.__init__(self, self.loadSquencesLocally())
        else:
            SequenceList.__init__(self, self.downloadSequences(sequenceListURL))

    def downloadSequences(self, url):
        fs = Ramfile()
        http = HTTPClient.getGlobalPtr()
        self.ch = http.makeChannel(True)
        self.ch.getHeader(DocumentSpec(url))
        doc = self.ch.getDocumentSpec()
        self.ch.getDocument(doc)
        self.ch.downloadToRam(fs)
        return fs.getData().split('\r\n')

    def loadSquencesLocally(self):
        if not os.path.exists('config/'):
            os.mkdir('config/')
        if not os.path.isfile('config/tsequence.dat'):
            from toontown.chat.SequenceListData import SequenceListData
            with open('config/tsequence.dat', 'w') as (data):
                data.write(SequenceListData)
                data.close()
        sequenceListFile = open('config/tsequence.dat')
        data = sequenceListFile.read()
        sequenceListFile.close()
        return data.split('\n')