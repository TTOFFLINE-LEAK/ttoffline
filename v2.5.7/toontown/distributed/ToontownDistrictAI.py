from direct.directnotify import DirectNotifyGlobal
from otp.distributed.DistributedDistrictAI import DistributedDistrictAI

class ToontownDistrictAI(DistributedDistrictAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('ToontownDistrictAI')
    ahnnLog = 0

    def __init__(self, air):
        DistributedDistrictAI.__init__(self, air)
        self.description = ''
        self.holidayValue = 0

    def allowAHNNLog(self, ahnnLog):
        self.ahnnLog = ahnnLog

    def d_allowAHNNLog(self, ahnnLog):
        self.sendUpdate('allowAHNNLog', [ahnnLog])

    def b_allowAHNNLog(self, ahnnLog):
        self.allowAHNNLog(ahnnLog)
        self.d_allowAHNNLog(ahnnLog)

    def getAllowAHNNLog(self):
        return self.ahnnLog

    def rpcSetAvailable(self, available):
        self.b_setAvailable(available)

    def setDescription(self, description):
        if not config.GetBool('want-mini-server', False):
            self.description = 'A Toontown Offline Game.'
        else:
            if description == 'N/A':
                self.description = 'A Toontown Offline Mini-Server.'
            else:
                self.description = description

    def getDescription(self):
        return self.description

    def setHolidayPasscode(self, holidayValue):
        self.holidayValue = holidayValue

    def getHolidayPasscode(self):
        return self.holidayValue