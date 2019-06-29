from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObject
from otp.distributed import DistributedDistrict

class ToontownDistrict(DistributedDistrict.DistributedDistrict):
    notify = DirectNotifyGlobal.directNotify.newCategory('ToontownDistrict')

    def __init__(self, cr):
        DistributedDistrict.DistributedDistrict.__init__(self, cr)
        self.avatarCount = 0
        self.newAvatarCount = 0
        self.description = ''
        self.holidayValue = 0

    def allowAHNNLog(self, allow):
        self.allowAHNN = allow

    def getAllowAHNNLog(self):
        return self.allowAHNN

    def setDescription(self, description):
        self.description = description
        base.cr.serverDescription = self.description

    def setHolidayPasscode(self, holidayValue):
        self.holidayValue = holidayValue
        base.cr.holidayValue = self.holidayValue

    def setName(self, name):
        DistributedDistrict.DistributedDistrict.setName(self, name)
        base.cr.serverName = self.name