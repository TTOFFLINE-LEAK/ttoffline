from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObjectGlobal
from direct.task.Task import Task
from toontown.hood import ZoneUtil
from toontown.toonbase import ToontownGlobals, TTLocalizer
from direct import discord_rpc
import time
discordToken = '461761173814116352'

class DiscordManager(DistributedObjectGlobal.DistributedObjectGlobal):
    notify = DirectNotifyGlobal.directNotify.newCategory('DiscordManager')
    neverDisable = 1

    def __init__(self, cr):
        DistributedObjectGlobal.DistributedObjectGlobal.__init__(self, cr)
        cr.discordManager = self
        self.discordRpc = discord_rpc
        self.state = TTLocalizer.DiscordOffline
        self.details = TTLocalizer.DiscordPickAToon
        self.largeImage = ToontownGlobals.DefaultIcon
        self.largeImageText = TTLocalizer.DiscordPickAToon
        self.smallImage = 'dog'
        self.smallImageText = 'Toon'
        self.partyId = '69'
        self.districtAvatarCount = None
        self.districtLimit = None
        self.joinSecret = None
        self.start = time.time()
        self.launchPresence()
        return

    def readyCallback(self, current_user):
        print ('Our user: {}').format(current_user)

    def disconnectedCallback(self, codeno, codemsg):
        print ('Disconnected from Discord rich presence RPC. Code {}: {}').format(codeno, codemsg)

    def joinCallback(self, joinSecret):
        print 'go hypsinigrad yourself' + joinSecret

    def errorCallback(self, errno, errmsg):
        print ('An error occurred! Error {}: {}').format(errno, errmsg)

    def launchPresence(self):
        callbacks = {'ready': self.readyCallback, 
           'disconnected': self.disconnectedCallback, 
           'joinGame': self.joinCallback, 
           'spectateGame': None, 
           'joinRequest': self.joinCallback, 
           'error': self.errorCallback}
        self.discordRpc.initialize(discordToken, callbacks=callbacks, log=True)
        self.updatePresence()
        updateTask = Task.loop(Task(self.updateConnection), Task.pause(1.0), Task(self.runCallbacks))
        taskMgr.add(updateTask, 'update-presence-task')
        return

    def updateConnection(self, task):
        self.discordRpc.update_connection()
        return Task.done

    def runCallbacks(self, task):
        self.discordRpc.run_callbacks()
        return Task.done

    def updatePresence(self):
        presenceInfo = {'state': self.state, 
           'details': self.details, 
           'start_timestamp': self.start, 
           'large_image_key': self.largeImage, 
           'large_image_text': self.largeImageText, 
           'small_image_key': self.smallImage, 
           'small_image_text': self.smallImageText, 
           'party_id': self.partyId, 
           'party_size': self.districtAvatarCount, 
           'party_max': self.districtLimit, 
           'join_secret': self.joinSecret}
        self.discordRpc.update_presence(**presenceInfo)

    def shutdownPresence(self):
        taskMgr.remove('update-presence-task')
        self.discordRpc.shutdown()

    def setInfo(self, state=None, details=None, largeImage=None, largeImageText=None, smallImage=None, smallImageText=None, zoneId=None, joinSecret=None):
        if not details and zoneId:
            details = self.getDetailsByZoneId(zoneId)
        if not largeImageText and zoneId:
            largeImageText = self.getLargeImageTextByZoneId(zoneId)
        if not smallImage and hasattr(base, 'localAvatar'):
            smallImage = self.getSmallImage()
        if not smallImageText and hasattr(base, 'localAvatar'):
            smallImageText = self.getSmallImageText()
        if not joinSecret and hasattr(base, 'localAvatar'):
            joinSecret = self.getAvId()
        self.state = state
        self.details = details
        self.largeImage = largeImage
        self.largeImageText = largeImageText
        self.smallImage = smallImage
        self.smallImageText = smallImageText
        self.joinSecret = joinSecret
        self.updatePresence()

    def setState(self, state):
        self.state = state
        self.updatePresence()

    def getState(self):
        if config.GetBool('mini-server', False):
            self.state = base.cr.serverName
            districtAvatarCount = self.getDistrictAvatarCount()
            if not hasattr(base, 'localAvatar'):
                districtAvatarCount += 1
            self.setDistrictAvatarCount(districtAvatarCount)
        else:
            self.state = TTLocalizer.DiscordOffline
            self.setDistrictAvatarCount(None)
        return self.state

    def setDetails(self, details):
        self.details = details
        self.updatePresence()

    def getDetailsByZoneId(self, zoneId):
        if zoneId in TTLocalizer.GlobalStreetNames.keys():
            return TTLocalizer.GlobalStreetNames[zoneId][2]
        if zoneId in TTLocalizer.zone2TitleDict.keys():
            return TTLocalizer.zone2TitleDict[zoneId][0]

    def setLargeImage(self, largeImage):
        self.largeImage = largeImage
        self.updatePresence()

    def setLargeImageText(self, largeImageText):
        self.largeImageText = largeImageText
        self.updatePresence()

    def getLargeImageTextByZoneId(self, zoneId):
        zoneId = ZoneUtil.getHoodId(zoneId)
        if zoneId in ToontownGlobals.hoodNameMap.keys():
            return ToontownGlobals.hoodNameMap[zoneId][2]
        if zoneId in TTLocalizer.zone2TitleDict.keys():
            return TTLocalizer.zone2TitleDict[zoneId][0]
        if not ZoneUtil.isDynamicZone(zoneId):
            return TTLocalizer.GlobalStreetNames[zoneId][2]
        return

    def setSmallImage(self, smallImage):
        self.smallImage = smallImage
        self.updatePresence()

    def getSmallImage(self):
        return base.localAvatar.style.getAnimal()

    def setSmallImageText(self, smallImageText):
        self.smallImageText = smallImageText
        self.updatePresence()

    def getSmallImageText(self):
        return base.localAvatar.getName()

    def getAvId(self):
        return str(base.localAvatar.getDoId())

    def setDistrictLimit(self, districtLimit):
        self.districtLimit = districtLimit
        self.updatePresence()

    def getDistrictLimit(self):
        return self.districtLimit

    def setDistrictId(self, districtId):
        self.districtId = districtId
        self.updatePresence()

    def setDistrictAvatarCount(self, districtAvatarCount):
        self.districtAvatarCount = districtAvatarCount
        self.updatePresence()

    def getDistrictAvatarCount(self):
        return base.cr.activeDistrictMap[self.districtId].avatarCount