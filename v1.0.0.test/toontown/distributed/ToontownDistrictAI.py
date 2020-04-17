from direct.directnotify import DirectNotifyGlobal
from otp.distributed.DistributedDistrictAI import DistributedDistrictAI
from toontown.toonbase import TTLocalizer

class ToontownDistrictAI(DistributedDistrictAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('ToontownDistrictAI')

    def __init__(self, air):
        DistributedDistrictAI.__init__(self, air)
        self.ahnnLog = False
        self.description = ''
        self.iconPath = ''

    def allowAHNNLog(self, ahnnLog):
        self.ahnnLog = ahnnLog

    def d_allowAHNNLog(self, ahnnLog):
        self.sendUpdate('allowAHNNLog', [ahnnLog])

    def b_allowAHNNLog(self, ahnnLog):
        self.allowAHNNLog(ahnnLog)
        self.d_allowAHNNLog(ahnnLog)

    def getAllowAHNNLog(self):
        return self.ahnnLog

    def setDescription(self, description):
        if not config.GetBool('mini-server', False):
            self.description = TTLocalizer.DiscordOffline
        elif description == TTLocalizer.WordPageNA:
            self.description = TTLocalizer.DistrictMiniserverDefault
        else:
            self.description = description

    def getDescription(self):
        return self.description

    def setIconPath(self, path):
        self.iconPath = path

    def d_setIconPath(self, path):
        self.sendUpdate('setIconPath', [path])

    def b_setIconPath(self, path):
        self.setIconPath(path)
        self.d_setIconPath(path)

    def getIconPath(self):
        return self.iconPath