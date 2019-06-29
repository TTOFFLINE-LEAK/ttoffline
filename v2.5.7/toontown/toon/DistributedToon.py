from subprocess import Popen
import os, sys
from panda3d.core import *
from otp.otpbase import OTPGlobals
from otp.otpbase import OTPLocalizer
from toontown.toonbase import ToontownGlobals
from direct.directnotify import DirectNotifyGlobal
from direct.distributed.ClockDelta import *
from direct.actor import Actor
from otp.avatar import DistributedPlayer
from otp.avatar import Avatar, DistributedAvatar
from otp.speedchat import SCDecoders
from otp.chat import TalkAssistant
from otp.nametag.NametagConstants import *
from otp.margins.WhisperPopup import *
import Toon, ToonDNA
from direct.task.Task import Task
from direct.distributed import DistributedSmoothNode
from direct.distributed import DistributedObject
from direct.interval.LerpInterval import LerpFunctionInterval
from direct.fsm import ClassicFSM
from toontown.hood import ZoneUtil
from toontown.distributed import DelayDelete
from toontown.distributed.DelayDeletable import DelayDeletable
from otp.otpbase import PythonUtil
from toontown.catalog import CatalogItemList
from toontown.catalog import CatalogItem
import TTEmote
from toontown.shtiker.OptionsPage import speedChatStyles
from toontown.fishing import FishCollection
from toontown.fishing import FishTank
from toontown.suit import DistributedSuitBase
from toontown.suit import SuitDNA
from toontown.avatar import ToontownAvatarUtils
from toontown.coghq import CogDisguiseGlobals
from toontown.toonbase import TTLocalizer
import Experience, InventoryNew
from LaffMeter import LaffMeter
from toontown.speedchat import TTSCDecoders
from toontown.char import CharDNA
from toontown.chat import ToonChatGarbler
from toontown.chat import ResistanceChat
from direct.distributed.MsgTypes import *
from toontown.effects.ScavengerHuntEffects import *
from toontown.episodes import EpisodeConfig
from toontown.estate import FlowerCollection
from toontown.estate import FlowerBasket
from toontown.estate import GardenGlobals
from toontown.estate import DistributedGagTree
from toontown.estate import GardenDropGame
from toontown.parties.PartyGlobals import InviteStatus, PartyStatus
from toontown.parties.PartyInfo import PartyInfo
from toontown.parties.InviteInfo import InviteInfo
from toontown.parties.PartyReplyInfo import PartyReplyInfoBase
from toontown.parties.SimpleMailBase import SimpleMailBase
from toontown.parties import PartyGlobals
from toontown.friends import FriendHandle
from toontown.golf import GolfGlobals
from direct.interval.IntervalGlobal import Sequence, Wait, Func, Parallel, SoundInterval
from direct.controls.GravityWalker import GravityWalker
from toontown.distributed import DelayDelete
from otp.ai.MagicWordGlobal import *
from direct.gui.OnscreenImage import OnscreenImage
import time, operator, random, copy, webbrowser
if base.wantKarts:
    from toontown.racing.KartDNA import *

class DistributedToon(DistributedPlayer.DistributedPlayer, Toon.Toon, DistributedSmoothNode.DistributedSmoothNode, DelayDeletable):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedToon')
    partyNotify = DirectNotifyGlobal.directNotify.newCategory('DistributedToon_Party')
    chatGarbler = ToonChatGarbler.ToonChatGarbler()
    gmNameTag = None

    def __init__(self, cr, bFake=False):
        try:
            self.DistributedToon_initialized
            return
        except:
            self.DistributedToon_initialized = 1

        DistributedPlayer.DistributedPlayer.__init__(self, cr)
        Toon.Toon.__init__(self)
        DistributedSmoothNode.DistributedSmoothNode.__init__(self, cr)
        self.overheadMeter = None
        self.__meterMode = 0
        self.bFake = bFake
        self.kart = None
        self._isGM = False
        self._gmType = None
        self.trophyScore = 0
        self.trophyStar = None
        self.trophyStarSpeed = 0
        self.safeZonesVisited = []
        self.NPCFriendsDict = {}
        self.earnedExperience = None
        self.track = None
        self.effect = None
        self.maxCarry = 0
        self.disguisePageFlag = 0
        self.sosPageFlag = 0
        self.disguisePage = None
        self.sosPage = None
        self.gardenPage = None
        self.cogTypes = [0,
         0,
         0,
         0,
         0]
        self.cogLevels = [0,
         0,
         0,
         0,
         0]
        self.cogParts = [0,
         0,
         0,
         0,
         0]
        self.cogMerits = [0,
         0,
         0,
         0,
         0]
        self.savedCheesyEffect = ToontownGlobals.CENormal
        self.savedCheesyHoodId = 0
        self.savedCheesyExpireTime = 0
        if hasattr(base, 'wantPets') and base.wantPets:
            self.petTrickPhrases = []
            self.petDNA = None
            self.petName = ''
        self.customMessages = []
        self.resistanceMessages = []
        self.cogSummonsEarned = []
        self.catalogNotify = ToontownGlobals.NoItems
        self.mailboxNotify = ToontownGlobals.NoItems
        self.simpleMailNotify = ToontownGlobals.NoItems
        self.inviteMailNotify = ToontownGlobals.NoItems
        self.catalogScheduleCurrentWeek = 0
        self.catalogScheduleNextTime = 0
        self.monthlyCatalog = CatalogItemList.CatalogItemList()
        self.weeklyCatalog = CatalogItemList.CatalogItemList()
        self.backCatalog = CatalogItemList.CatalogItemList()
        self.onOrder = CatalogItemList.CatalogItemList(store=CatalogItem.Customization | CatalogItem.DeliveryDate)
        self.onGiftOrder = CatalogItemList.CatalogItemList(store=CatalogItem.Customization | CatalogItem.DeliveryDate)
        self.mailboxContents = CatalogItemList.CatalogItemList(store=CatalogItem.Customization)
        self.deliveryboxContentsContents = CatalogItemList.CatalogItemList(store=CatalogItem.Customization | CatalogItem.GiftTag)
        self.awardMailboxContents = CatalogItemList.CatalogItemList(store=CatalogItem.Customization)
        self.onAwardOrder = CatalogItemList.CatalogItemList(store=CatalogItem.Customization | CatalogItem.DeliveryDate)
        self.splash = None
        self.tossTrack = None
        self.pieTracks = {}
        self.splatTracks = {}
        self.lastTossedPie = 0
        self.clothesTopsList = []
        self.clothesBottomsList = []
        self.hatList = []
        self.glassesList = []
        self.backpackList = []
        self.shoesList = []
        self.tunnelTrack = None
        self.tunnelPivotPos = [-14, -6, 0]
        self.tunnelCenterOffset = 9.0
        self.tunnelCenterInfluence = 0.6
        self.pivotAngle = 135
        self.posIndex = 0
        self.houseId = 0
        self.money = 0
        self.bankMoney = 0
        self.maxMoney = 0
        self.maxBankMoney = 0
        self.emblems = [0, 0]
        self.maxNPCFriends = 16
        self.petId = 0
        self.bPetTutorialDone = False
        self.bFishBingoTutorialDone = False
        self.bFishBingoMarkTutorialDone = False
        self.accessories = []
        if base.wantKarts:
            self.kartDNA = [
             -1] * getNumFields()
        self.flowerCollection = None
        self.shovel = 0
        self.shovelSkill = 0
        self.shovelModel = None
        self.wateringCan = 0
        self.wateringCanSkill = 0
        self.wateringCanModel = None
        self.gardenSpecials = []
        self.unlimitedSwing = 0
        self.soundSequenceList = []
        self.boardingParty = None
        self.__currentDialogue = None
        self.mail = None
        self.invites = []
        self.hostedParties = []
        self.partiesInvitedTo = []
        self.partyReplyInfoBases = []
        self.gmState = 0
        self.gmNameTagEnabled = 0
        self.gmNameTagColor = 'whiteGM'
        self.gmNameTagString = ''
        self._lastZombieContext = None
        self.rainbowSeq = None
        self.tokens = 0
        self.skidValue = False
        self.toonHallPanel = False
        self.greenSequence = None
        self.trolley = None
        self.trolleyDropSequence = None
        self.trolleyLocalSequence = None
        self.dropSfx = None
        self.landSfx = None
        self.trolleySfx = None
        self.fadeSfx = None
        return

    def disable(self):
        for soundSequence in self.soundSequenceList:
            soundSequence.finish()

        self.finishGreenSequence()
        self.finishTrolleyDropSequence()
        self.soundSequenceList = []
        if self.boardingParty:
            self.boardingParty.demandDrop()
            self.boardingParty = None
        self.ignore('clientCleanup')
        self.stopAnimations()
        self.clearCheesyEffect()
        self.stopBlink()
        self.stopSmooth()
        self.stopLookAroundNow()
        self.setGhostMode(0)
        if self.track != None:
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        if self.effect != None:
            self.effect.destroy()
            self.effect = None
        if self.splash != None:
            self.splash.destroy()
            self.splash = None
        if self.emote != None:
            self.emote.finish()
            self.emote = None
        if self.trolley != None:
            self.trolley.removeNode()
            self.trolley = None
        self.cleanupPies()
        if self.isDisguised:
            self.takeOffSuit()
        if self.tunnelTrack:
            self.tunnelTrack.finish()
            self.tunnelTrack = None
        self.setTrophyScore(0)
        self.removeGMIcon()
        if self.cr.toons.has_key(self.doId):
            del self.cr.toons[self.doId]
        DistributedPlayer.DistributedPlayer.disable(self)
        return

    def delete(self):
        try:
            self.DistributedToon_deleted
        except:
            if self == base.localAvatar:
                messenger.send('droppedWood')
            self.DistributedToon_deleted = 1
            del self.safeZonesVisited
            DistributedPlayer.DistributedPlayer.delete(self)
            Toon.Toon.delete(self)
            DistributedSmoothNode.DistributedSmoothNode.delete(self)

    def generate(self):
        DistributedPlayer.DistributedPlayer.generate(self)
        DistributedSmoothNode.DistributedSmoothNode.generate(self)
        self.cr.toons[self.doId] = self
        if base.cr.trophyManager != None:
            base.cr.trophyManager.d_requestTrophyScore()
        self.startBlink()
        self.startSmooth()
        self.accept('clientCleanup', self._handleClientCleanup)
        return

    def announceGenerate(self):
        DistributedPlayer.DistributedPlayer.announceGenerate(self)
        if self.animFSM.getCurrentState().getName() == 'off':
            self.setAnimState('neutral')
        if base.cr.newsManager:
            if base.cr.newsManager.isHolidayRunning(ToontownGlobals.APRIL_FOOLS_COSTUMES):
                self.startAprilToonsControls()

    def _handleClientCleanup(self):
        if self.track != None:
            DelayDelete.cleanupDelayDeletes(self.track)
        return

    def setDNAString(self, dnaString):
        Toon.Toon.setDNAString(self, dnaString)

    def duckHunted(self, hp):
        self.sendUpdate('duckHunted', [hp])

    def doDoodHG(self, h1, h2, g1, g2):
        self.sendUpdate('doDoodHG', [h1, h2, g1, g2])

    def doDoodBS(self, b1, b2, s1, s2):
        self.sendUpdate('doDoodHG', [b1, b2, s1, s2])

    def setDNA(self, dna):
        if base.cr.newsManager:
            if base.cr.newsManager.isHolidayRunning(ToontownGlobals.SPOOKY_BLACK_CAT):
                black = 26
                heads = ['cls',
                 'css',
                 'csl',
                 'cll']
                dna.setTemporary(random.choice(heads), black, black, black)
            else:
                dna.restoreTemporary(self.style)
        oldHat = self.getHat()
        oldGlasses = self.getGlasses()
        oldBackpack = self.getBackpack()
        oldShoes = self.getShoes()
        self.setHat(0, 0, 0)
        self.setGlasses(0, 0, 0)
        self.setBackpack(0, 0, 0)
        self.setShoes(0, 0, 0)
        Toon.Toon.setDNA(self, dna)
        self.setHat(*oldHat)
        self.setGlasses(*oldGlasses)
        self.setBackpack(*oldBackpack)
        self.setShoes(*oldShoes)

    def setHat(self, idx, textureIdx, colorIdx):
        Toon.Toon.setHat(self, idx, textureIdx, colorIdx)

    def setGlasses(self, idx, textureIdx, colorIdx):
        Toon.Toon.setGlasses(self, idx, textureIdx, colorIdx)

    def setBackpack(self, idx, textureIdx, colorIdx):
        Toon.Toon.setBackpack(self, idx, textureIdx, colorIdx)

    def setShoes(self, idx, textureIdx, colorIdx):
        Toon.Toon.setShoes(self, idx, textureIdx, colorIdx)

    def setGM(self, type):
        wasGM = self._isGM
        self._isGM = type != 0
        self._gmType = None
        if self._isGM:
            self._gmType = type - 1
        if self._isGM != wasGM:
            self._handleGMName()
        return

    def requestVerifyGM(self):
        self.d_verifyGM()

    def d_verifyGM(self):
        if os.path.exists('gm_token.dat'):
            fileStream = open('gm_token.dat')
            fileData = fileStream.read()
            fileStream.close()
            del fileStream
            self.sendUpdate('verifyGM', [fileData])
        else:
            self.sendUpdate('verifyGM', [''])

    def setExperience(self, experience):
        self.experience = Experience.Experience(experience, self)
        if self.inventory:
            self.inventory.updateGUI()

    def setInventory(self, inventoryNetString):
        if not self.inventory:
            self.inventory = InventoryNew.InventoryNew(self, inventoryNetString)
        self.inventory.updateInvString(inventoryNetString)

    def setLastHood(self, lastHood):
        self.lastHood = lastHood

    def setBattleId(self, battleId):
        self.battleId = battleId
        messenger.send('ToonBattleIdUpdate', [self.doId])

    def b_setSCToontask(self, taskId, toNpcId, toonProgress, msgIndex):
        self.setSCToontask(taskId, toNpcId, toonProgress, msgIndex)
        self.d_setSCToontask(taskId, toNpcId, toonProgress, msgIndex)
        return

    def d_setSCToontask(self, taskId, toNpcId, toonProgress, msgIndex):
        messenger.send('wakeup')
        self.sendUpdate('setSCToontask', [taskId,
         toNpcId,
         toonProgress,
         msgIndex])

    def setSCToontask(self, taskId, toNpcId, toonProgress, msgIndex):
        if self.doId in base.localAvatar.ignoreList:
            return
        chatString = TTSCDecoders.decodeTTSCToontaskMsg(taskId, toNpcId, toonProgress, msgIndex)
        if chatString:
            self.setChatAbsolute(chatString, CFSpeech | CFQuicktalker | CFTimeout)

    def b_setSCSinging(self, msgIndex):
        self.setSCSinging(msgIndex)
        self.d_setSCSinging(msgIndex)
        return

    def d_setSCSinging(self, msgIndex):
        messenger.send('wakeup')
        self.sendUpdate('setSCSinging', [msgIndex])

    def sendLogSuspiciousEvent(self, msg):
        localAvatar.sendUpdate('logSuspiciousEvent', ['%s for %s' % (msg, self.doId)])

    def setSCSinging(self, msgIndex):
        self.sendUpdate('logSuspiciousEvent', ['invalid msgIndex in setSCSinging: %s from %s' % (msgIndex, self.doId)])

    def d_reqSCResistance(self, msgIndex):
        messenger.send('wakeup')
        nearbyPlayers = self.getNearbyPlayers(ResistanceChat.EFFECT_RADIUS)
        self.sendUpdate('reqSCResistance', [msgIndex, nearbyPlayers])

    def getNearbyPlayers(self, radius, includeSelf=True):
        nearbyToons = []
        toonIds = self.cr.getObjectsOfExactClass(DistributedToon)
        for toonId, toon in toonIds.items():
            if toon is not self:
                dist = toon.getDistance(self)
                if dist < radius:
                    nearbyToons.append(toonId)

        if includeSelf:
            nearbyToons.append(self.doId)
        return nearbyToons

    def setSCResistance(self, msgIndex, nearbyToons=[]):
        chatString = TTSCDecoders.decodeTTSCResistanceMsg(msgIndex)
        if chatString:
            self.setChatAbsolute(chatString, CFSpeech | CFTimeout)
        ResistanceChat.doEffect(msgIndex, self, nearbyToons)

    def d_battleSOS(self, requesterId, sendToId=None):
        self.sendUpdate('battleSOS', [requesterId], sendToId)

    def battleSOS(self, requesterId):
        avatar = base.cr.identifyAvatar(requesterId)
        if isinstance(avatar, DistributedToon) or isinstance(avatar, FriendHandle.FriendHandle):
            self.setSystemMessage(requesterId, TTLocalizer.MovieSOSWhisperHelp % avatar.getName(), whisperType=WhisperPopup.WTBattleSOS)
        else:
            if avatar is not None:
                self.notify.warning('got battleSOS from non-toon %s' % requesterId)
        return

    def getDialogueArray(self, *args):
        if base.cr.newsManager:
            if base.cr.newsManager.isHolidayRunning(ToontownGlobals.APRIL_FOOLS_COSTUMES) and not base.cr.newsManager.isHolidayRunning(ToontownGlobals.ORANGES):
                self.animalSound = random.randrange(0, 10)
            else:
                if self.isCog == 2 or self.isCog == 6 or self.isCog == 69 or self.isCog == 31:
                    return Toon.SkeletonDialogueArray
                if self.isCog != 5 and self.isCog:
                    return Toon.SuitDialogueArray
                if self.getCheesyEffect()[0] == ToontownGlobals.CESurleeCutout:
                    return Toon.MonkeyDialogueArray
                if self.getCheesyEffect()[0] == ToontownGlobals.CEPreposteraCutout:
                    return Toon.HorseDialogueArray
                if self.getCheesyEffect()[0] == ToontownGlobals.CEDimmCutout:
                    return Toon.DuckDialogueArray
        if hasattr(self, 'animalSound'):
            types = [Toon.DogDialogueArray,
             Toon.CatDialogueArray,
             Toon.HorseDialogueArray,
             Toon.MouseDialogueArray,
             Toon.RabbitDialogueArray,
             Toon.DuckDialogueArray,
             Toon.MonkeyDialogueArray,
             Toon.BearDialogueArray,
             Toon.PigDialogueArray,
             Toon.SuitDialogueArray,
             Toon.SkeletonDialogueArray]
            try:
                return types[self.animalSound]
            except:
                return Toon.Toon.getDialogueArray(self, *args)

        return Toon.Toon.getDialogueArray(self, *args)

    def setDefaultShard(self, shard):
        self.defaultShard = shard

    def setDefaultZone(self, zoneId):
        if zoneId >= 20000 and zoneId < 22000:
            zoneId = zoneId + 2000
        if base.cr.avIsInEpisode():
            zoneId = EpisodeConfig.episodes[base.cr.currentEpisode].get('defaultZoneId', ToontownGlobals.ToontownCentral)
        try:
            hoodPhase = base.cr.hoodMgr.getPhaseFromHood(zoneId)
        except:
            if base.cr.avIsInEpisode():
                self.defaultZone = EpisodeConfig.episodes[base.cr.currentEpisode].get('defaultZoneId', ToontownGlobals.ToontownCentral)
            else:
                self.defaultZone = ToontownGlobals.ToontownCentral
            return

        if not base.cr.isPaid() or launcher and not launcher.getPhaseComplete(hoodPhase):
            if base.cr.avIsInEpisode():
                self.defaultZone = EpisodeConfig.episodes[base.cr.currentEpisode].get('defaultZoneId', ToontownGlobals.ToontownCentral)
            else:
                self.defaultZone = ToontownGlobals.ToontownCentral
        else:
            if base.cr.avIsInEpisode():
                self.defaultZone = EpisodeConfig.episodes[base.cr.currentEpisode].get('defaultZoneId', ToontownGlobals.ToontownCentral)
            else:
                self.defaultZone = zoneId

    def setShtickerBook(self, string):
        pass

    def setAsGM(self, state):
        self.notify.debug('Setting GM State: %s' % state)
        DistributedPlayer.DistributedPlayer.setAsGM(self, state)

    def d_updateGMNameTag(self):
        self.refreshName()

    def updateGMNameTag(self, tagString, color, state):
        try:
            unicode(tagString, 'utf-8')
        except UnicodeDecodeError:
            self.sendUpdate('logSuspiciousEvent', ['invalid GM name tag: %s from %s' % (tagString, self.doId)])
            return

    def refreshName(self):
        return
        self.notify.debug('Refreshing GM Nametag String: %s Color: %s State: %s' % (self.gmNameTagString, self.gmNameTagColor, self.gmNameTagEnabled))
        if hasattr(self, 'nametag') and self.gmNameTagEnabled:
            self.setDisplayName(self.gmNameTagString)
            self.setName(self.gmNameTagString)
            self.trophyStar1 = loader.loadModel('models/misc/smiley')
            self.trophyStar1.reparentTo(self.nametag.getNameIcon())
            self.trophyStar1.setScale(1)
            self.trophyStar1.setZ(2.25)
            self.trophyStar1.setColor(Vec4(0.75, 0.75, 0.75, 0.75))
            self.trophyStar1.setTransparency(1)
            self.trophyStarSpeed = 15
        else:
            taskMgr.add(self.__refreshNameCallBack, self.uniqueName('refreshNameCallBack'))

    def __starSpin1(self, task):
        now = globalClock.getFrameTime()
        r = now * 90 % 360.0
        self.trophyStar1.setH(r)
        return Task.cont

    def __refreshNameCallBack(self, task):
        if hasattr(self, 'nametag') and self.nametag.getName() != '':
            self.refreshName()
            return Task.done
        return Task.cont

    def setTalk(self, fromAV, fromAC, avatarName, chat, mods, flags):
        if base.cr.avatarFriendsManager.checkIgnored(fromAV):
            self.d_setWhisperIgnored(fromAV)
            return
        if fromAV in self.ignoreList:
            self.d_setWhisperIgnored(fromAV)
            return
        if config.GetBool('want-sleep-reply-on-regular-chat', 0):
            if base.localAvatar.sleepFlag == 1:
                self.sendUpdate('setSleepAutoReply', [base.localAvatar.doId], fromAV)
        newText, scrubbed = self.scrubTalk(chat, mods)
        coolColor = False
        if avatarName != '':
            coolColor = True
            chatTypeIndicator = int(avatarName[0])
            if chatTypeIndicator == 2:
                mods = [
                 2]
        self.displayTalk(newText, mods, coolColor)
        base.talkAssistant.receiveOpenTalk(fromAV, avatarName, fromAC, None, newText)
        return

    def isAvFriend(self, avId):
        return base.cr.isFriend(avId) or base.cr.playerFriendsManager.isAvatarOwnerPlayerFriend(avId)

    def setTalkWhisper(self, fromAV, fromAC, avatarName, chat, mods, flags):
        handle = base.cr.identifyAvatar(fromAV)
        if not handle:
            return
        avatarName = handle.getName()
        if not localAvatar.acceptingNonFriendWhispers:
            if not self.isAvFriend(fromAV):
                return
        if base.cr.avatarFriendsManager.checkIgnored(fromAV):
            self.d_setWhisperIgnored(fromAV)
            return
        if fromAV in self.ignoreList:
            self.d_setWhisperIgnored(fromAV)
            return
        if config.GetBool('ignore-whispers', 0):
            return
        if base.localAvatar.sleepFlag == 1:
            if not base.cr.identifyAvatar(fromAV) == base.localAvatar:
                self.sendUpdate('setSleepAutoReply', [base.localAvatar.doId], fromAV)
        newText, scrubbed = self.scrubTalk(chat, mods)
        self.displayTalkWhisper(fromAV, avatarName, chat, mods)
        base.talkAssistant.receiveWhisperTalk(fromAV, avatarName, fromAC, None, self.doId, self.getName(), newText)
        return

    def setSleepAutoReply(self, fromId):
        pass

    def _isValidWhisperSource(self, source):
        return isinstance(source, FriendHandle.FriendHandle) or isinstance(source, DistributedToon)

    def setWhisperSCEmoteFrom(self, fromId, emoteId):
        handle = base.cr.identifyFriend(fromId)
        if handle == None:
            return
        if not self._isValidWhisperSource(handle):
            self.notify.warning('setWhisperSCEmoteFrom non-toon %s' % fromId)
            return
        if not localAvatar.acceptingNonFriendWhispers:
            if not self.isAvFriend(fromId):
                return
        if base.cr.avatarFriendsManager.checkIgnored(fromId):
            self.d_setWhisperIgnored(fromId)
            return
        if base.localAvatar.sleepFlag == 1:
            if not base.cr.identifyAvatar(fromId) == base.localAvatar:
                self.sendUpdate('setSleepAutoReply', [base.localAvatar.doId], fromId)
        chatString = SCDecoders.decodeSCEmoteWhisperMsg(emoteId, handle.getName())
        if chatString:
            self.displayWhisper(fromId, chatString, WhisperPopup.WTEmote)
            base.talkAssistant.receiveAvatarWhisperSpeedChat(TalkAssistant.SPEEDCHAT_EMOTE, emoteId, fromId)
        return

    def setWhisperSCFrom(self, fromId, msgIndex):
        handle = base.cr.identifyFriend(fromId)
        if handle == None:
            return
        if not self._isValidWhisperSource(handle):
            self.notify.warning('setWhisperSCFrom non-toon %s' % fromId)
            return
        if not localAvatar.acceptingNonFriendWhispers:
            if not self.isAvFriend(fromId):
                return
        if base.cr.avatarFriendsManager.checkIgnored(fromId):
            self.d_setWhisperIgnored(fromId)
            return
        if fromId in self.ignoreList:
            self.d_setWhisperIgnored(fromId)
            return
        if base.localAvatar.sleepFlag == 1:
            if not base.cr.identifyAvatar(fromId) == base.localAvatar:
                self.sendUpdate('setSleepAutoReply', [base.localAvatar.doId], fromId)
        chatString = SCDecoders.decodeSCStaticTextMsg(msgIndex)
        if chatString:
            self.displayWhisper(fromId, chatString, WhisperPopup.WTQuickTalker)
            base.talkAssistant.receiveAvatarWhisperSpeedChat(TalkAssistant.SPEEDCHAT_NORMAL, msgIndex, fromId)
        return

    def setWhisperSCCustomFrom(self, fromId, msgIndex):
        handle = base.cr.identifyFriend(fromId)
        if handle == None:
            return
        if not localAvatar.acceptingNonFriendWhispers:
            if not self.isAvFriend(fromId):
                return
        return DistributedPlayer.DistributedPlayer.setWhisperSCCustomFrom(self, fromId, msgIndex)

    def whisperSCToontaskTo(self, taskId, toNpcId, toonProgress, msgIndex, sendToId):
        messenger.send('wakeup')
        self.sendUpdate('setWhisperSCToontaskFrom', [self.doId,
         taskId,
         toNpcId,
         toonProgress,
         msgIndex], sendToId)

    def setWhisperSCToontaskFrom(self, fromId, taskId, toNpcId, toonProgress, msgIndex):
        sender = base.cr.identifyFriend(fromId)
        if sender == None:
            return
        if not localAvatar.acceptingNonFriendWhispers:
            if not self.isAvFriend(fromId):
                return
        if fromId in self.ignoreList:
            self.d_setWhisperIgnored(fromId)
        chatString = TTSCDecoders.decodeTTSCToontaskMsg(taskId, toNpcId, toonProgress, msgIndex)
        if chatString:
            self.displayWhisper(fromId, chatString, WhisperPopup.WTQuickTalker)
        return

    def setMaxNPCFriends(self, max):
        max &= 32767
        if max != self.maxNPCFriends:
            self.maxNPCFriends = max
            messenger.send(self.uniqueName('maxNPCFriendsChange'))
        else:
            self.maxNPCFriends = max

    def getMaxNPCFriends(self):
        return self.maxNPCFriends

    def getNPCFriendsDict(self):
        return self.NPCFriendsDict

    def setNPCFriendsDict(self, NPCFriendsList):
        NPCFriendsDict = {}
        for friendPair in NPCFriendsList:
            NPCFriendsDict[friendPair[0]] = friendPair[1]

        self.NPCFriendsDict = NPCFriendsDict

    def setMaxAccessories(self, max):
        self.maxAccessories = max

    def getMaxAccessories(self):
        return self.maxAccessories

    def setHatList(self, clothesList):
        self.hatList = clothesList

    def getHatList(self):
        return self.hatList

    def setGlassesList(self, clothesList):
        self.glassesList = clothesList

    def getGlassesList(self):
        return self.glassesList

    def setBackpackList(self, clothesList):
        self.backpackList = clothesList

    def getBackpackList(self):
        return self.backpackList

    def setShoesList(self, clothesList):
        self.shoesList = clothesList

    def getShoesList(self):
        return self.shoesList

    def isTrunkFull(self, extraAccessories=0):
        numAccessories = (len(self.hatList) + len(self.glassesList) + len(self.backpackList) + len(self.shoesList)) / 3
        return numAccessories + extraAccessories >= self.maxAccessories

    def setMaxClothes(self, max):
        self.maxClothes = max

    def getMaxClothes(self):
        return self.maxClothes

    def getClothesTopsList(self):
        return self.clothesTopsList

    def setClothesTopsList(self, clothesList):
        self.clothesTopsList = clothesList

    def getClothesBottomsList(self):
        return self.clothesBottomsList

    def setClothesBottomsList(self, clothesList):
        self.clothesBottomsList = clothesList

    def catalogGenClothes(self, avId):
        if avId == self.doId:
            self.generateToonClothes()
            self.loop('neutral')

    def catalogGenAccessories(self, avId):
        if avId == self.doId:
            self.generateToonAccessories()
            self.loop('neutral')

    def isClosetFull(self, extraClothes=0):
        numClothes = len(self.clothesTopsList) / 4 + len(self.clothesBottomsList) / 2
        return numClothes + extraClothes >= self.maxClothes

    def setMaxHp(self, hitPoints):
        DistributedPlayer.DistributedPlayer.setMaxHp(self, hitPoints)
        if self.inventory:
            self.inventory.updateGUI()

    def setHp(self, hp):
        DistributedPlayer.DistributedPlayer.setHp(self, hp)
        self.__considerUpdateMeter()
        if self.isDisguised:
            self.suit.currHP = self.hp
            self.suit.maxHP = self.maxHp
            if self.maxHp == self.hp:
                self.suit.corpMedallion.show()
                self.suit.healthBar.hide()
            else:
                self.suit.corpMedallion.hide()
                self.suit.healthBar.show()
                self.suit.updateHealthBar(self.hp, True, True)

    def setHealthDisplay(self, mode):
        self.__meterMode = mode
        self.__considerUpdateMeter()

    def __considerUpdateMeter(self):
        wantMeter = self.__shouldDisplayMeter()
        if wantMeter and not self.overheadMeter:
            self.overheadMeter = LaffMeter(self.style, self.hp, self.maxHp)
            self.overheadMeter.setAvatar(self)
            self.overheadMeter.setZ(5)
            self.overheadMeter.setScale(1.5)
            self.overheadMeter.reparentTo(NodePath(self.nametag.getNameIcon()))
            self.overheadMeter.hide(BitMask32.bit(1))
            self.overheadMeter.start()
        else:
            if not wantMeter and self.overheadMeter:
                self.overheadMeter.stop()
                self.overheadMeter.destroy()
                self.overheadMeter = None
        return

    def __shouldDisplayMeter(self):
        if self.__meterMode == 0:
            return False
        if self.__meterMode == 1:
            return True
        if self.__meterMode == 2:
            return self.hp < self.maxHp

    def died(self):
        messenger.send(self.uniqueName('died'))
        if self.isLocal():
            target_sz = ZoneUtil.getSafeZoneId(self.defaultZone)
            place = self.cr.playGame.getPlace()
            if place and place.fsm:
                place.fsm.request('died', [
                 {'loader': ZoneUtil.getLoaderName(target_sz), 'where': ZoneUtil.getWhereName(target_sz, 1), 
                    'how': 'teleportIn', 
                    'hoodId': target_sz, 
                    'zoneId': target_sz, 
                    'shardId': None, 
                    'avId': -1, 
                    'battle': 1}])
        return

    def exitIndex(self):
        self.sendUpdate('exitIndex')

    def setInterface(self, string):
        pass

    def setZonesVisited(self, hoods):
        self.safeZonesVisited = hoods

    def setHoodsVisited(self, hoods):
        self.hoodsVisited = hoods
        if ToontownGlobals.SellbotHQ in hoods or ToontownGlobals.CashbotHQ in hoods or ToontownGlobals.LawbotHQ in hoods:
            self.setDisguisePageFlag(1)

    def wrtReparentTo(self, parent):
        DistributedSmoothNode.DistributedSmoothNode.wrtReparentTo(self, parent)

    def setTutorialAck(self, tutorialAck):
        self.tutorialAck = 1
        if config.GetBool('want-toontorial', 1):
            self.tutorialAck = tutorialAck

    def setEarnedExperience(self, earnedExp):
        self.earnedExperience = earnedExp

    def b_setTunnelIn(self, endX, tunnelOrigin):
        timestamp = globalClockDelta.getFrameNetworkTime()
        pos = tunnelOrigin.getPos(render)
        h = tunnelOrigin.getH(render)
        self.setTunnelIn(timestamp, endX, pos[0], pos[1], pos[2], h)
        self.d_setTunnelIn(timestamp, endX, pos[0], pos[1], pos[2], h)

    def d_setTunnelIn(self, timestamp, endX, x, y, z, h):
        self.sendUpdate('setTunnelIn', [timestamp,
         endX,
         x,
         y,
         z,
         h])

    def setTunnelIn(self, timestamp, endX, x, y, z, h):
        t = globalClockDelta.networkToLocalTime(timestamp)
        self.handleTunnelIn(t, endX, x, y, z, h)

    def getTunnelInToonTrack(self, endX, tunnelOrigin):
        pivotNode = tunnelOrigin.attachNewNode(self.uniqueName('pivotNode'))
        pivotNode.setPos(*self.tunnelPivotPos)
        pivotNode.setHpr(0, 0, 0)
        pivotY = pivotNode.getY(tunnelOrigin)
        endY = 5.0
        straightLerpDur = abs(endY - pivotY) / ToontownGlobals.ToonForwardSpeed
        pivotDur = 2.0
        pivotLerpDur = pivotDur * (90.0 / self.pivotAngle)
        self.reparentTo(pivotNode)
        self.setPos(0, 0, 0)
        self.setX(tunnelOrigin, endX)
        targetX = self.getX()
        self.setX(self.tunnelCenterOffset + (targetX - self.tunnelCenterOffset) * (1.0 - self.tunnelCenterInfluence))
        self.setHpr(tunnelOrigin, 0, 0, 0)
        pivotNode.setH(-self.pivotAngle)
        return Sequence(Wait(1.6), Parallel(LerpHprInterval(pivotNode, pivotDur, hpr=Point3(0, 0, 0), name=self.uniqueName('tunnelInPivot')), Sequence(Wait(pivotDur - pivotLerpDur), LerpPosInterval(self, pivotLerpDur, pos=Point3(targetX, 0, 0), name=self.uniqueName('tunnelInPivotLerpPos')))), Func(self.wrtReparentTo, render), Func(pivotNode.removeNode), LerpPosInterval(self, straightLerpDur, pos=Point3(endX, endY, 0.1), other=tunnelOrigin, name=self.uniqueName('tunnelInStraightLerp')))

    def handleTunnelIn(self, startTime, endX, x, y, z, h):
        self.stopSmooth()
        tunnelOrigin = render.attachNewNode('tunnelOrigin')
        tunnelOrigin.setPosHpr(x, y, z, h, 0, 0)
        if self.tunnelTrack:
            self.tunnelTrack.finish()
        self.tunnelTrack = Sequence(self.getTunnelInToonTrack(endX, tunnelOrigin), Func(tunnelOrigin.removeNode), Func(self.startSmooth))
        tOffset = globalClock.getFrameTime() - (startTime + self.smoother.getDelay())
        if tOffset < 0.0:
            self.tunnelTrack = Sequence(Wait(-tOffset), self.tunnelTrack)
            self.tunnelTrack.start()
        else:
            self.tunnelTrack.start(tOffset)

    def b_setTunnelOut(self, startX, startY, tunnelOrigin):
        timestamp = globalClockDelta.getFrameNetworkTime()
        pos = tunnelOrigin.getPos(render)
        h = tunnelOrigin.getH(render)
        self.setTunnelOut(timestamp, startX, startY, pos[0], pos[1], pos[2], h)
        self.d_setTunnelOut(timestamp, startX, startY, pos[0], pos[1], pos[2], h)

    def d_setTunnelOut(self, timestamp, startX, startY, x, y, z, h):
        self.sendUpdate('setTunnelOut', [timestamp,
         startX,
         startY,
         x,
         y,
         z,
         h])

    def setTunnelOut(self, timestamp, startX, startY, x, y, z, h):
        t = globalClockDelta.networkToLocalTime(timestamp)
        self.handleTunnelOut(t, startX, startY, x, y, z, h)

    def getTunnelOutToonTrack(self, startX, startY, tunnelOrigin):
        startPos = self.getPos(tunnelOrigin)
        startHpr = self.getHpr(tunnelOrigin)
        reducedAvH = PythonUtil.fitDestAngle2Src(startHpr[0], 180)
        pivotNode = tunnelOrigin.attachNewNode(self.uniqueName('pivotNode'))
        pivotNode.setPos(*self.tunnelPivotPos)
        pivotNode.setHpr(0, 0, 0)
        pivotY = pivotNode.getY(tunnelOrigin)
        straightLerpDur = abs(startY - pivotY) / ToontownGlobals.ToonForwardSpeed
        pivotDur = 2.0
        pivotLerpDur = pivotDur * (90.0 / self.pivotAngle)

        def getTargetPos(self=self):
            pos = self.getPos()
            return Point3(self.tunnelCenterOffset + (pos[0] - self.tunnelCenterOffset) * (1.0 - self.tunnelCenterInfluence), pos[1], pos[2])

        return Sequence(Parallel(LerpPosInterval(self, straightLerpDur, pos=Point3(startX, pivotY, 0.1), startPos=startPos, other=tunnelOrigin, name=self.uniqueName('tunnelOutStraightLerp')), LerpHprInterval(self, straightLerpDur * 0.8, hpr=Point3(reducedAvH, 0, 0), startHpr=startHpr, other=tunnelOrigin, name=self.uniqueName('tunnelOutStraightLerpHpr'))), Func(self.wrtReparentTo, pivotNode), Parallel(LerpHprInterval(pivotNode, pivotDur, hpr=Point3(-self.pivotAngle, 0, 0), name=self.uniqueName('tunnelOutPivot')), LerpPosInterval(self, pivotLerpDur, pos=getTargetPos, name=self.uniqueName('tunnelOutPivotLerpPos'))), Func(self.wrtReparentTo, render), Func(pivotNode.removeNode))

    def handleTunnelOut(self, startTime, startX, startY, x, y, z, h):
        tunnelOrigin = render.attachNewNode('tunnelOrigin')
        tunnelOrigin.setPosHpr(x, y, z, h, 0, 0)
        if self.tunnelTrack:
            self.tunnelTrack.finish()
        self.tunnelTrack = Sequence(Func(self.stopSmooth), self.getTunnelOutToonTrack(startX, startY, tunnelOrigin), Func(self.detachNode), Func(tunnelOrigin.removeNode))
        tOffset = globalClock.getFrameTime() - (startTime + self.smoother.getDelay())
        if tOffset < 0.0:
            self.tunnelTrack = Sequence(Wait(-tOffset), self.tunnelTrack)
            self.tunnelTrack.start()
        else:
            self.tunnelTrack.start(tOffset)

    def enterTeleportOut(self, *args, **kw):
        Toon.Toon.enterTeleportOut(self, *args, **kw)
        if self.track:
            self.track.delayDelete = DelayDelete.DelayDelete(self, 'enterTeleportOut')

    def exitTeleportOut(self):
        if self.track != None:
            DelayDelete.cleanupDelayDeletes(self.track)
        Toon.Toon.exitTeleportOut(self)
        return

    def b_setAnimState(self, animName, animMultiplier=1.0, callback=None, extraArgs=[]):
        self.d_setAnimState(animName, animMultiplier, None, extraArgs)
        self.setAnimState(animName, animMultiplier, None, None, callback, extraArgs)
        return

    def d_setAnimState(self, animName, animMultiplier=1.0, timestamp=None, extraArgs=[]):
        timestamp = globalClockDelta.getFrameNetworkTime()
        self.sendUpdate('setAnimState', [animName, animMultiplier, timestamp])

    def setAnimState(self, animName, animMultiplier=1.0, timestamp=None, animType=None, callback=None, extraArgs=[]):
        if not animName or animName == 'None':
            return
        if timestamp == None:
            ts = 0.0
        else:
            ts = globalClockDelta.localElapsedTime(timestamp)
        if config.GetBool('check-invalid-anims', True):
            if animMultiplier > 1.0 and animName in ('neutral', ):
                animMultiplier = 1.0
        if self.animFSM.getStateNamed(animName):
            self.animFSM.request(animName, [animMultiplier,
             ts,
             callback,
             extraArgs])
        self.cleanupPieInHand()
        return

    def b_setEmoteState(self, animIndex, animMultiplier):
        self.setEmoteState(animIndex, animMultiplier)
        self.d_setEmoteState(animIndex, animMultiplier)

    def d_setEmoteState(self, animIndex, animMultiplier):
        timestamp = globalClockDelta.getFrameNetworkTime()
        self.sendUpdate('setEmoteState', [animIndex, animMultiplier, timestamp])

    def setEmoteState(self, animIndex, animMultiplier, timestamp=None):
        if animIndex == TTEmote.EmoteClear:
            return
        if timestamp == None:
            ts = 0.0
        else:
            ts = globalClockDelta.localElapsedTime(timestamp)
        callback = None
        extraArgs = []
        extraArgs.insert(0, animIndex)
        self.doEmote(animIndex, animMultiplier, ts, callback, extraArgs)
        return

    def setCogStatus(self, cogStatusList):
        self.cogs = cogStatusList

    def setCogCount(self, cogCountList):
        self.cogCounts = cogCountList

    def setCogRadar(self, radar):
        self.cogRadar = radar

    def setBuildingRadar(self, radar):
        self.buildingRadar = radar

    def setRankNinesUnlocked(self, unlocked):
        self.rankNinesUnlocked = unlocked

    def setCogTypes(self, types):
        for x in xrange(len(types)):
            if types[x] > 7:
                types[x] = 7

        self.cogTypes = types
        if self.disguisePage:
            self.disguisePage.updatePage()

    def setCogLevels(self, levels):
        self.cogLevels = levels
        if self.disguisePage:
            self.disguisePage.updatePage()

    def getCogLevels(self):
        return self.cogLevels

    def setCogParts(self, parts):
        self.cogParts = parts
        if self.disguisePage:
            self.disguisePage.updatePage()

    def getCogParts(self):
        return self.cogParts

    def setCogMerits(self, merits):
        self.cogMerits = merits
        if self.disguisePage:
            self.disguisePage.updatePage()

    def readyForPromotion(self, dept):
        merits = base.localAvatar.cogMerits[dept]
        totalMerits = CogDisguiseGlobals.getTotalMerits(self, dept)
        if merits >= totalMerits:
            return 1
        return 0

    def jumpScare(self):
        happySong = base.loader.loadMusic('phase_14.5/audio/bgm/eggs/cherryjm.ogg')
        base.playMusic(happySong, looping=1, volume=0.8)
        if base.shaderMgr.shader is None:
            base.shaderMgr.enableRetroShader()
        return

    def setCogIndex(self, index, becomeCog=0):
        self.cogIndex = index
        if self.cogIndex == -1:
            if self.isDisguised:
                self.takeOffSuit()
        else:
            if base.cr.newsManager.isHolidayRunning(ToontownGlobals.ORANGES):
                cogIndex = self.style.armColor % 8 + SuitDNA.suitsPerDept * (self.style.sleeveTex % 5)
                becomeCog = self.style.botTexColor % 3 + 1
                cog = SuitDNA.suitHeadTypes[cogIndex]
                self.putOnSuit(cog, becomeCog=becomeCog)
            else:
                parts = self.getCogParts()
                if becomeCog == 49:
                    self.putOnSuit('ph', becomeCog=becomeCog)
                else:
                    if becomeCog == 50:
                        self.putOnSuit('fts', becomeCog=becomeCog)
                    else:
                        if becomeCog == 51:
                            self.putOnSuit('ctn', becomeCog=becomeCog)
                        else:
                            if CogDisguiseGlobals.isPaidSuitComplete(self, parts, index):
                                cogIndex = self.cogTypes[index] + SuitDNA.suitsPerDept * index
                                cog = SuitDNA.suitHeadTypes[cogIndex]
                                self.putOnSuit(cog, becomeCog=becomeCog)
                            else:
                                self.putOnSuit(index, rental=True, becomeCog=becomeCog)

    def charTrans(self, index):
        if index == -1:
            if self.isTransformed:
                self.becomeToon()
        else:
            self.becomeChar(index)

    def petTrans(self, index, petName, petDNA):
        if index == -1:
            if self.isBecomePet:
                self.noMorePet()
        else:
            self.petName = petName
            self.petDNA = petDNA
            self.becomePet(self.petName, self.petDNA)

    def goonTrans(self, index):
        if index == -1:
            if self.isGoon:
                self.noMoreGoon()
        else:
            self.becomeGoon(index)

    def bossTrans(self, index):
        if index == -1:
            if self.isBossCog:
                self.noMoreBoss()
        else:
            self.becomeBoss(index)

    def setTPose(self):
        self.updateToonDNA(self.style, 1, True)
        self.generateToonAccessories()
        if self.isDisguised:
            suitType = self.suit.style.name
            becomeCog = self.isCog
            if self.suit.isRental:
                rental = True
            else:
                rental = False
            self.putOnSuit(suitType, True, rental, becomeCog, True)
        else:
            if self.isTransformed:
                charType = CharDNA.charTypes.index(self.char.style.name)
                self.becomeChar(charType, True)
            else:
                if self.isBecomePet:
                    self.becomePet(self.petName, self.petDNA, True)
                else:
                    if self.isGoon:
                        goonType = SuitDNA.goonTypes.index(self.goon.style.name)
                        self.becomeGoon(goonType, True)
                    else:
                        if self.isBossCog:
                            bossType = SuitDNA.suitDepts.index(self.boss.style.dept)
                            self.becomeBoss(bossType, True)

    def isCog(self):
        if self.cogIndex == -1:
            return 0
        return 1

    def setMuzzle(self, muzzle):
        self.hideNormalMuzzle()
        self.hideSurpriseMuzzle()
        self.hideSadMuzzle()
        self.hideSmileMuzzle()
        self.hideAngryMuzzle()
        self.hideLaughMuzzle()
        if muzzle == 0:
            self.showNormalMuzzle()
        else:
            if muzzle == 1:
                self.showSurpriseMuzzle()
            else:
                if muzzle == 2:
                    self.showSadMuzzle()
                else:
                    if muzzle == 3:
                        self.showSmileMuzzle()
                    else:
                        if muzzle == 4:
                            self.showAngryMuzzle()
                        else:
                            if muzzle == 5:
                                self.showLaughMuzzle()

    def setEyes(self, eyes):
        Toon.Toon.setEyes(self, eyes)

    def setDisguisePageFlag(self, flag):
        if flag and hasattr(self, 'book'):
            self.loadDisguisePages()
        self.disguisePageFlag = flag

    def setSosPageFlag(self, flag):
        if flag and hasattr(self, 'book'):
            self.loadSosPages()
        self.sosPageFlag = flag

    def setFishCollection(self, genusList, speciesList, weightList):
        self.fishCollection = FishCollection.FishCollection()
        self.fishCollection.makeFromNetLists(genusList, speciesList, weightList)

    def getFishCollection(self):
        return self.fishCollection

    def setMaxFishTank(self, maxTank):
        self.maxFishTank = maxTank

    def getMaxFishTank(self):
        return self.maxFishTank

    def setFishTank(self, genusList, speciesList, weightList):
        self.fishTank = FishTank.FishTank()
        self.fishTank.makeFromNetLists(genusList, speciesList, weightList)
        messenger.send(self.uniqueName('fishTankChange'))

    def getFishTank(self):
        return self.fishTank

    def isFishTankFull(self):
        return len(self.fishTank) >= self.maxFishTank

    def setFishingRod(self, rodId):
        self.fishingRod = rodId

    def getFishingRod(self):
        return self.fishingRod

    def setFishingTrophies(self, trophyList):
        self.fishingTrophies = trophyList

    def getFishingTrophies(self):
        return self.fishingTrophies

    def setQuests(self, flattenedQuests):
        questList = []
        questLen = 5
        for i in range(0, len(flattenedQuests), questLen):
            questList.append(flattenedQuests[i:i + questLen])

        self.quests = questList
        if self == base.localAvatar:
            messenger.send('questsChanged')

    def setQuestCarryLimit(self, limit):
        self.questCarryLimit = limit
        if self == base.localAvatar:
            messenger.send('questsChanged')

    def getQuestCarryLimit(self):
        return self.questCarryLimit

    def d_requestDeleteQuest(self, questDesc):
        self.sendUpdate('requestDeleteQuest', [list(questDesc)])

    def setMaxCarry(self, maxCarry):
        self.maxCarry = maxCarry
        if self.inventory:
            self.inventory.updateGUI()

    def getMaxCarry(self):
        return self.maxCarry

    def startAprilToonsControls(self):
        if isinstance(base.localAvatar.controlManager.currentControls, GravityWalker):
            base.localAvatar.controlManager.currentControls.setGravity(ToontownGlobals.GravityValue * 0.75)

    def stopAprilToonsControls(self):
        if isinstance(base.localAvatar.controlManager.currentControls, GravityWalker):
            base.localAvatar.controlManager.currentControls.setGravity(ToontownGlobals.GravityValue * 2.0)

    def setCheesyEffect(self, effect, hoodId, expireTime):
        self.savedCheesyEffect = effect
        self.savedCheesyHoodId = hoodId
        self.savedCheesyExpireTime = expireTime
        if self == base.localAvatar:
            self.notify.debug('setCheesyEffect(%s, %s, %s)' % (effect, hoodId, expireTime))
            if effect != ToontownGlobals.CENormal:
                serverTime = time.time() + self.cr.getServerDelta()
                duration = expireTime * 60 - serverTime
                if duration < 0:
                    self.notify.debug('effect should have expired %s ago.' % PythonUtil.formatElapsedSeconds(-duration))
                else:
                    self.notify.debug('effect will expire in %s.' % PythonUtil.formatElapsedSeconds(duration))
        if self.activeState == DistributedObject.ESGenerated:
            self.reconsiderCheesyEffect(lerpTime=0.5)
        else:
            self.reconsiderCheesyEffect()

    def getCheesyEffect(self):
        return (
         self.savedCheesyEffect, self.savedCheesyHoodId, self.savedCheesyExpireTime)

    def reconsiderCheesyEffect(self, lerpTime=0):
        effect = self.savedCheesyEffect
        hoodId = self.savedCheesyHoodId
        if not self.cr.areCheesyEffectsAllowed():
            effect = ToontownGlobals.CENormal
        if hoodId != 0:
            try:
                currentHoodId = base.cr.playGame.hood.id
            except:
                currentHoodId = None

            if hoodId == 1:
                if currentHoodId == ToontownGlobals.ToontownCentral:
                    effect = ToontownGlobals.CENormal
            elif currentHoodId != None and currentHoodId != hoodId:
                effect = ToontownGlobals.CENormal
        if self.ghostMode:
            effect = ToontownGlobals.CEGhost
        self.applyCheesyEffect(effect, lerpTime=lerpTime)
        return

    def setGhostMode(self, flag):
        if self.ghostMode != flag:
            self.ghostMode = flag
            if not hasattr(self, 'cr'):
                return
            if self.activeState <= DistributedObject.ESDisabled:
                self.notify.debug('not applying cheesy effect to disabled Toon')
            else:
                if self.activeState == DistributedObject.ESGenerating:
                    self.reconsiderCheesyEffect()
                else:
                    if self.activeState == DistributedObject.ESGenerated:
                        self.reconsiderCheesyEffect(lerpTime=0.5)
                    else:
                        self.notify.warning('unknown activeState: %s' % self.activeState)
            self.showNametag2d()
            self.showNametag3d()
            if hasattr(self, 'collNode'):
                if self.ghostMode:
                    self.collNode.setCollideMask(ToontownGlobals.GhostBitmask)
                else:
                    self.collNode.setCollideMask(ToontownGlobals.WallBitmask | ToontownGlobals.PieBitmask)
            if self.isLocal():
                if self.ghostMode:
                    self.useGhostControls()
                else:
                    self.useWalkControls()

    if hasattr(base, 'wantPets') and base.wantPets:

        def setPetTrickPhrases(self, petTricks):
            self.petTrickPhrases = petTricks
            if self.isLocal():
                messenger.send('petTrickPhrasesChanged')

    def setCustomMessages(self, customMessages):
        self.customMessages = customMessages
        if self.isLocal():
            messenger.send('customMessagesChanged')

    def setResistanceMessages(self, resistanceMessages):
        self.resistanceMessages = resistanceMessages
        if self.isLocal():
            messenger.send('resistanceMessagesChanged')

    def getResistanceMessageCharges(self, textId):
        msgs = self.resistanceMessages
        for i in range(len(msgs)):
            if msgs[i][0] == textId:
                return msgs[i][1]

        return 0

    def setCatalogSchedule(self, currentWeek, nextTime):
        self.catalogScheduleCurrentWeek = currentWeek
        self.catalogScheduleNextTime = nextTime
        if self.isLocal():
            self.notify.debug('setCatalogSchedule(%s, %s)' % (currentWeek, nextTime))
            if nextTime:
                serverTime = time.time() + self.cr.getServerDelta()
                duration = nextTime * 60 - serverTime
                self.notify.debug('next catalog in %s.' % PythonUtil.formatElapsedSeconds(duration))

    def setCatalog(self, monthlyCatalog, weeklyCatalog, backCatalog):
        self.monthlyCatalog = CatalogItemList.CatalogItemList(monthlyCatalog)
        self.weeklyCatalog = CatalogItemList.CatalogItemList(weeklyCatalog)
        self.backCatalog = CatalogItemList.CatalogItemList(backCatalog)
        if self.catalogNotify == ToontownGlobals.NewItems:
            self.catalogNotify = ToontownGlobals.OldItems

    def setCatalogNotify(self, catalogNotify, mailboxNotify):
        if len(self.weeklyCatalog) + len(self.monthlyCatalog) == 0:
            catalogNotify = ToontownGlobals.NoItems
        if len(self.mailboxContents) == 0:
            mailboxNotify = ToontownGlobals.NoItems
        self.catalogNotify = catalogNotify
        self.mailboxNotify = mailboxNotify
        if self.isLocal():
            self.gotCatalogNotify = 1
            self.refreshOnscreenButtons()
            print 'local'

    def setDeliverySchedule(self, onOrder):
        self.onOrder = CatalogItemList.CatalogItemList(onOrder, store=CatalogItem.Customization | CatalogItem.DeliveryDate)
        if self == base.localAvatar:
            nextTime = self.onOrder.getNextDeliveryDate()
            if nextTime != None:
                serverTime = time.time() + self.cr.getServerDelta()
                duration = nextTime * 60 - serverTime
                self.notify.debug('next delivery in %s.' % PythonUtil.formatElapsedSeconds(duration))
            messenger.send('setDeliverySchedule-%s' % self.doId)
        return

    def setMailboxContents(self, mailboxContents):
        self.mailboxContents = CatalogItemList.CatalogItemList(mailboxContents, store=CatalogItem.Customization)
        messenger.send('setMailboxContents-%s' % self.doId)

    def setAwardSchedule(self, onOrder):
        self.onAwardOrder = CatalogItemList.CatalogItemList(onOrder, store=CatalogItem.Customization | CatalogItem.DeliveryDate)
        if self == base.localAvatar:
            nextTime = self.onAwardOrder.getNextDeliveryDate()
            if nextTime != None:
                serverTime = time.time() + self.cr.getServerDelta()
                duration = nextTime * 60 - serverTime
                self.notify.debug('next delivery in %s.' % PythonUtil.formatElapsedSeconds(duration))
            messenger.send('setAwardSchedule-%s' % self.doId)
        return

    def setAwardMailboxContents(self, awardMailboxContents):
        self.notify.debug('Setting awardMailboxContents to %s.' % awardMailboxContents)
        self.awardMailboxContents = CatalogItemList.CatalogItemList(awardMailboxContents, store=CatalogItem.Customization)
        self.notify.debug('awardMailboxContents is %s.' % self.awardMailboxContents)
        messenger.send('setAwardMailboxContents-%s' % self.doId)

    def setAwardNotify(self, awardNotify):
        self.notify.debug('setAwardNotify( %s )' % awardNotify)
        self.awardNotify = awardNotify
        if self.isLocal():
            self.gotCatalogNotify = 1
            self.refreshOnscreenButtons()

    def setGiftSchedule(self, onGiftOrder):
        self.onGiftOrder = CatalogItemList.CatalogItemList(onGiftOrder, store=CatalogItem.Customization | CatalogItem.DeliveryDate)
        if self == base.localAvatar:
            nextTime = self.onGiftOrder.getNextDeliveryDate()
            if nextTime != None:
                serverTime = time.time() + self.cr.getServerDelta()
                duration = nextTime * 60 - serverTime
                self.notify.debug('next delivery in %s.' % PythonUtil.formatElapsedSeconds(duration))
        return

    def playSplashEffect(self, x, y, z):
        if localAvatar.zoneId not in [ToontownGlobals.DonaldsDock, ToontownGlobals.OutdoorZone, ToontownGlobals.ToonFest] and (not hasattr(localAvatar, 'inEstate') or localAvatar.inEstate != 1):
            if random.random() < 0.1:
                self.sendLogSuspiciousEvent('AvatarHackWarning! playing hacked splash effect')
            return
        from toontown.effects import Splash
        if self.splash == None:
            self.splash = Splash.Splash(render)
        self.splash.setPos(x, y, z)
        self.splash.setScale(2)
        self.splash.play()
        place = base.cr.playGame.getPlace()
        if place:
            if hasattr(place.loader, 'submergeSound'):
                base.playSfx(place.loader.submergeSound, node=self)
        return

    def d_playSplashEffect(self, x, y, z):
        self.sendUpdate('playSplashEffect', [x, y, z])

    def setTrackAccess(self, trackArray):
        self.trackArray = trackArray
        if self.inventory:
            self.inventory.updateGUI()

    def getTrackAccess(self):
        return self.trackArray

    def hasTrackAccess(self, track):
        return self.trackArray[track]

    def setTrackProgress(self, trackId, progress):
        self.trackProgressId = trackId
        self.trackProgress = progress
        if hasattr(self, 'trackPage'):
            self.trackPage.updatePage()

    def getTrackProgress(self):
        return [
         self.trackProgressId, self.trackProgress]

    def getTrackProgressAsArray(self, maxLength=15):
        shifts = map(operator.rshift, maxLength * [self.trackProgress], range(maxLength - 1, -1, -1))
        digits = map(operator.mod, shifts, maxLength * [2])
        digits.reverse()
        return digits

    def setTeleportAccess(self, teleportZoneArray):
        self.teleportZoneArray = teleportZoneArray

    def getTeleportAccess(self):
        return self.teleportZoneArray

    def hasTeleportAccess(self, zoneId):
        return zoneId in self.teleportZoneArray

    def setQuestHistory(self, questList):
        self.questHistory = questList

    def getQuestHistory(self):
        return self.questHistory

    def setRewardHistory(self, rewardTier, rewardList):
        self.rewardTier = rewardTier
        self.rewardHistory = rewardList

    def getRewardHistory(self):
        return (
         self.rewardTier, self.rewardHistory)

    def doSmoothTask(self, task):
        self.smoother.computeAndApplySmoothPosHpr(self, self)
        self.setSpeed(self.smoother.getSmoothForwardVelocity(), self.smoother.getSmoothRotationalVelocity())
        return Task.cont

    def d_setParent(self, parentToken):
        DistributedSmoothNode.DistributedSmoothNode.d_setParent(self, parentToken)

    def setEmoteAccess(self, bits):
        self.emoteAccess = bits
        if self == base.localAvatar:
            messenger.send('emotesChanged')

    def b_setHouseId(self, id):
        self.setHouseId(id)
        self.d_setHouseId(id)

    def d_setHouseId(self, id):
        self.sendUpdate('setHouseId', [id])

    def setHouseId(self, id):
        self.houseId = id

    def getHouseId(self):
        return self.houseId

    def setPosIndex(self, index):
        self.posIndex = index

    def getPosIndex(self):
        return self.posIndex

    def b_setSpeedChatStyleIndex(self, index):
        realIndexToSend = 0
        if type(index) == type(0) and 0 <= index and index < len(speedChatStyles):
            realIndexToSend = index
        else:
            base.cr.centralLogger.writeClientEvent('Hacker alert b_setSpeedChatStyleIndex invalid')
        self.setSpeedChatStyleIndex(realIndexToSend)
        self.d_setSpeedChatStyleIndex(realIndexToSend)
        return

    def d_setSpeedChatStyleIndex(self, index):
        realIndexToSend = 0
        if type(index) == type(0) and 0 <= index and index < len(speedChatStyles):
            realIndexToSend = index
        else:
            base.cr.centralLogger.writeClientEvent('Hacker alert d_setSpeedChatStyleIndex invalid')
        self.sendUpdate('setSpeedChatStyleIndex', [realIndexToSend])

    def setSpeedChatStyleIndex(self, index):
        realIndexToUse = 0
        if type(index) == type(0) and 0 <= index and index < len(speedChatStyles):
            realIndexToUse = index
        else:
            base.cr.centralLogger.writeClientEvent('Hacker victim setSpeedChatStyleIndex invalid attacking toon = %d' % self.doId)
        self.speedChatStyleIndex = realIndexToUse
        nameKey, arrowColor, rolloverColor, frameColor = speedChatStyles[realIndexToUse]
        self.nametag.setQtColor(VBase4(frameColor[0], frameColor[1], frameColor[2], 1))
        if self.isLocal():
            messenger.send('SpeedChatStyleChange', [])

    def getSpeedChatStyleIndex(self):
        return self.speedChatStyleIndex

    def setMaxMoney(self, maxMoney):
        self.maxMoney = maxMoney

    def getMaxMoney(self):
        return self.maxMoney

    def setMoney(self, money):
        if money != self.money:
            self.money = money
            messenger.send(self.uniqueName('moneyChange'), [self.money])

    def getMoney(self):
        return self.money

    def setTokens(self, tokens):
        if tokens != self.tokens:
            self.tokens = tokens
            messenger.send(self.uniqueName('tokensChange'), [self.tokens])

    def getTokens(self):
        return self.tokens

    def setMaxBankMoney(self, maxMoney):
        self.maxBankMoney = maxMoney

    def getMaxBankMoney(self):
        return self.maxBankMoney

    def setBankMoney(self, money):
        self.bankMoney = money
        messenger.send(self.uniqueName('bankMoneyChange'), [self.bankMoney])

    def getBankMoney(self):
        return self.bankMoney

    def getTotalMoney(self):
        return self.getBankMoney() + self.getMoney()

    def setEmblems(self, emblems):
        if self.emblems != emblems:
            self.emblems = emblems
            messenger.send(self.uniqueName('emblemsChange'), [self.emblems])

    def getEmblems(self):
        return self.emblems

    def isEnoughEmblemsToBuy(self, itemEmblemPrices):
        for emblemIndex, emblemPrice in enumerate(itemEmblemPrices):
            if emblemIndex >= len(self.emblems):
                return False
            if self.emblems[emblemIndex] < emblemPrice:
                return False

        return True

    def isEnoughMoneyAndEmblemsToBuy(self, moneyPrice, itemEmblemPrices):
        if self.getTotalMoney() < moneyPrice:
            return False
        for emblemIndex, emblemPrice in enumerate(itemEmblemPrices):
            if emblemIndex >= len(self.emblems):
                return False
            if self.emblems[emblemIndex] < emblemPrice:
                return False

        return True

    def presentPie(self, x, y, z, h, timestamp32):
        if self.numPies <= 0:
            return
        if not launcher.getPhaseComplete(5):
            return
        lastTossTrack = Sequence()
        if self.tossTrack:
            lastTossTrack = self.tossTrack
            tossTrack = None
        ts = globalClockDelta.localElapsedTime(timestamp32, bits=32)
        ts -= self.smoother.getDelay()
        ival = self.getPresentPieInterval(x, y, z, h)
        if ts > 0:
            startTime = ts
            lastTossTrack.finish()
        else:
            ival = Sequence(Wait(-ts), ival)
            lastTossTrack.finish()
            startTime = 0
        ival = Sequence(ival)
        ival.start(startTime)
        self.tossTrack = ival
        return

    def tossPie(self, x, y, z, h, sequence, power, throwType, timestamp32):
        if self.numPies <= 0:
            return
        if self.numPies != ToontownGlobals.FullPies:
            self.setNumPies(self.numPies - 1)
        self.lastTossedPie = globalClock.getFrameTime()
        if not launcher.getPhaseComplete(5):
            return
        lastTossTrack = Sequence()
        if self.tossTrack:
            lastTossTrack = self.tossTrack
            tossTrack = None
        lastPieTrack = Sequence()
        if self.pieTracks.has_key(sequence):
            lastPieTrack = self.pieTracks[sequence]
            del self.pieTracks[sequence]
        ts = globalClockDelta.localElapsedTime(timestamp32, bits=32)
        ts -= self.smoother.getDelay()
        toss, pie, flyPie = self.getTossPieInterval(x, y, z, h, power, throwType)
        if ts > 0:
            startTime = ts
            lastTossTrack.finish()
            lastPieTrack.finish()
        else:
            toss = Sequence(Wait(-ts), toss)
            pie = Sequence(Wait(-ts), pie)
            lastTossTrack.finish()
            lastPieTrack.finish()
            startTime = 0
        self.tossTrack = toss
        toss.start(startTime)
        pie = Sequence(pie, Func(self.pieFinishedFlying, sequence))
        self.pieTracks[sequence] = pie
        pie.start(startTime)
        return

    def pieFinishedFlying(self, sequence):
        if self.pieTracks.has_key(sequence):
            del self.pieTracks[sequence]

    def pieFinishedSplatting(self, sequence):
        if self.splatTracks.has_key(sequence):
            del self.splatTracks[sequence]

    def pieSplat(self, x, y, z, sequence, pieCode, timestamp32):
        if self.isLocal():
            return
        elapsed = globalClock.getFrameTime() - self.lastTossedPie
        if elapsed > 30:
            return
        if not launcher.getPhaseComplete(5):
            return
        lastPieTrack = Sequence()
        if self.pieTracks.has_key(sequence):
            lastPieTrack = self.pieTracks[sequence]
            del self.pieTracks[sequence]
        if self.splatTracks.has_key(sequence):
            lastSplatTrack = self.splatTracks[sequence]
            del self.splatTracks[sequence]
            lastSplatTrack.finish()
        ts = globalClockDelta.localElapsedTime(timestamp32, bits=32)
        ts -= self.smoother.getDelay()
        splat = self.getPieSplatInterval(x, y, z, pieCode)
        splat = Sequence(Func(messenger.send, 'pieSplat', [self, pieCode]), splat)
        if ts > 0:
            startTime = ts
            lastPieTrack.finish()
        else:
            splat = Sequence(Wait(-ts), splat)
            startTime = 0
        splat = Sequence(splat, Func(self.pieFinishedSplatting, sequence))
        self.splatTracks[sequence] = splat
        splat.start(startTime)

    def cleanupPies(self):
        for track in self.pieTracks.values():
            track.finish()

        self.pieTracks = {}
        for track in self.splatTracks.values():
            track.finish()

        self.splatTracks = {}
        self.cleanupPieInHand()

    def cleanupPieInHand(self):
        if self.tossTrack:
            self.tossTrack.finish()
            self.tossTrack = None
        self.cleanupPieModel()
        return

    def setNumPies(self, numPies):
        self.numPies = numPies
        if self.isLocal():
            self.updatePieButton()
            if numPies == 0:
                self.interruptPie()

    def setPieType(self, pieType):
        self.pieType = pieType
        if self.isLocal():
            self.updatePieButton()

    def setPieThrowType(self, throwType):
        self.pieThrowType = throwType

    def setTrophyScore(self, score):
        self.trophyScore = score
        if self.trophyStar != None:
            self.trophyStar.removeNode()
            self.trophyStar = None
        if self.trophyStarSpeed != 0:
            taskMgr.remove(self.uniqueName('starSpin'))
            self.trophyStarSpeed = 0
        if hasattr(self, 'gmIcon') and self.gmIcon:
            return
        if self.trophyScore >= ToontownGlobals.TrophyStarLevels[4]:
            self.trophyStar = loader.loadModel('phase_3.5/models/gui/name_star')
            np = NodePath(self.nametag.getNameIcon())
            self.trophyStar.reparentTo(np)
            self.trophyStar.setScale(2)
            self.trophyStar.setZ(2)
            self.trophyStar.setColor(ToontownGlobals.TrophyStarColors[4])
            self.trophyStarSpeed = 15
            if self.trophyScore >= ToontownGlobals.TrophyStarLevels[5]:
                taskMgr.add(self.__starSpin, self.uniqueName('starSpin'))
        else:
            if self.trophyScore >= ToontownGlobals.TrophyStarLevels[2]:
                self.trophyStar = loader.loadModel('phase_3.5/models/gui/name_star')
                np = NodePath(self.nametag.getNameIcon())
                self.trophyStar.reparentTo(np)
                self.trophyStar.setScale(1.5)
                self.trophyStar.setZ(1.6)
                self.trophyStar.setColor(ToontownGlobals.TrophyStarColors[2])
                self.trophyStarSpeed = 10
                if self.trophyScore >= ToontownGlobals.TrophyStarLevels[3]:
                    taskMgr.add(self.__starSpin, self.uniqueName('starSpin'))
            else:
                if self.trophyScore >= ToontownGlobals.TrophyStarLevels[0]:
                    self.trophyStar = loader.loadModel('phase_3.5/models/gui/name_star')
                    np = NodePath(self.nametag.getNameIcon())
                    self.trophyStar.reparentTo(np)
                    self.trophyStar.setScale(1.5)
                    self.trophyStar.setZ(1.6)
                    self.trophyStar.setColor(ToontownGlobals.TrophyStarColors[0])
                    self.trophyStarSpeed = 8
                    if self.trophyScore >= ToontownGlobals.TrophyStarLevels[1]:
                        taskMgr.add(self.__starSpin, self.uniqueName('starSpin'))
        return

    def __starSpin(self, task):
        now = globalClock.getFrameTime()
        r = now * self.trophyStarSpeed % 360.0
        self.trophyStar.setR(r)
        return Task.cont

    def setCogLoop(self, loop, start, end):
        if self.isDisguised:
            if start == -1:
                start = None
            if end == -1:
                end = None
            self.suit.loop(loop, fromFrame=start, toFrame=end)
        return

    def setCogPose(self, anim, frame):
        if self.isDisguised:
            self.suit.pose(anim, frame)

    def setCogPingPong(self, anim, start, end):
        if self.isDisguised:
            if start == -1:
                start = None
            if end == -1:
                end = None
            self.suit.pingpong(anim, fromFrame=start, toFrame=end)
        return

    def getZoneId(self):
        place = base.cr.playGame.getPlace()
        if place:
            return place.getZoneId()
        return
        return

    def getRequestID(self):
        return CLIENT_GET_AVATAR_DETAILS

    def announceBingo(self):
        self.setChatAbsolute(TTLocalizer.FishBingoBingo, CFSpeech | CFTimeout)

    def b_setFishBingoTutorialDone(self, bDone):
        self.d_setFishBingoTutorialDone(bDone)
        self.setFishBingoTutorialDone(bDone)

    def d_setFishBingoTutorialDone(self, bDone):
        self.sendUpdate('setFishBingoTutorialDone', [bDone])

    def setFishBingoTutorialDone(self, bDone):
        self.bFishBingoTutorialDone = bDone

    def b_setFishBingoMarkTutorialDone(self, bDone):
        self.d_setFishBingoMarkTutorialDone(bDone)
        self.setFishBingoMarkTutorialDone(bDone)

    def d_setFishBingoMarkTutorialDone(self, bDone):
        self.sendUpdate('setFishBingoMarkTutorialDone', [bDone])

    def setFishBingoMarkTutorialDone(self, bDone):
        self.bFishBingoMarkTutorialDone = bDone

    def squish(self, damage):
        if self == base.localAvatar:
            base.cr.playGame.getPlace().fsm.request('squished')
            self.stunToon()
            self.setZ(self.getZ(render) + 0.025)

    def d_squish(self, damage):
        self.sendUpdate('squish', [damage])

    def b_squish(self, damage):
        if not self.isStunned:
            self.squish(damage)
            self.d_squish(damage)
            self.playDialogueForString('!')

    def getShadowJoint(self):
        return Toon.Toon.getShadowJoint(self)

    if base.wantKarts:

        def hasKart(self):
            return self.kartDNA[KartDNA.bodyType] != -1

        def getKartDNA(self):
            return self.kartDNA

        def setTickets(self, numTickets):
            self.tickets = numTickets

        def getTickets(self):
            return self.tickets

        def getAccessoryByType(self, accType):
            return self.kartDNA[accType]

        def setCurrentKart(self, avId):
            self.kartId = avId

        def releaseKart(self):
            self.kartId = None
            return

        def setKartBodyType(self, bodyType):
            self.kartDNA[KartDNA.bodyType] = bodyType

        def getKartBodyType(self):
            return self.kartDNA[KartDNA.bodyType]

        def setKartBodyColor(self, bodyColor):
            self.kartDNA[KartDNA.bodyColor] = bodyColor

        def getKartBodyColor(self):
            return self.kartDNA[KartDNA.bodyColor]

        def setKartAccessoryColor(self, accColor):
            self.kartDNA[KartDNA.accColor] = accColor

        def getKartAccessoryColor(self):
            return self.kartDNA[KartDNA.accColor]

        def setKartEngineBlockType(self, ebType):
            self.kartDNA[KartDNA.ebType] = ebType

        def getKartEngineBlockType(self):
            return self.kartDNA[KartDNA.ebType]

        def setKartSpoilerType(self, spType):
            self.kartDNA[KartDNA.spType] = spType

        def getKartSpoilerType(self):
            return self.kartDNA[KartDNA.spType]

        def setKartFrontWheelWellType(self, fwwType):
            self.kartDNA[KartDNA.fwwType] = fwwType

        def getKartFrontWheelWellType(self):
            return self.kartDNA[KartDNA.fwwType]

        def setKartBackWheelWellType(self, bwwType):
            self.kartDNA[KartDNA.bwwType] = bwwType

        def getKartBackWheelWellType(self):
            return self.kartDNA[KartDNA.bwwType]

        def setKartRimType(self, rimsType):
            self.kartDNA[KartDNA.rimsType] = rimsType

        def setKartDecalType(self, decalType):
            self.kartDNA[KartDNA.decalType] = decalType

        def getKartDecalType(self):
            return self.kartDNA[KartDNA.decalType]

        def getKartRimType(self):
            return self.kartDNA[KartDNA.rimsType]

        def setKartAccessoriesOwned(self, accessories):
            while len(accessories) < 16:
                accessories.append(-1)

            self.accessories = accessories

        def getKartAccessoriesOwned(self):
            owned = copy.deepcopy(self.accessories)
            while InvalidEntry in owned:
                owned.remove(InvalidEntry)

            return owned

        def requestKartDNAFieldUpdate(self, dnaField, fieldValue):
            self.notify.debug('requestKartDNAFieldUpdate - dnaField %s, fieldValue %s' % (dnaField, fieldValue))
            self.sendUpdate('updateKartDNAField', [dnaField, fieldValue])

        def requestAddOwnedAccessory(self, accessoryId):
            self.notify.debug('requestAddOwnedAccessor - purchased accessory %s' % accessoryId)
            self.sendUpdate('addOwnedAccessory', [accessoryId])

        def requestRemoveOwnedAccessory(self, accessoryId):
            self.notify.debug('requestRemoveOwnedAccessor - removed accessory %s' % accessoryId)
            self.sendUpdate('removeOwnedAccessory', [accessoryId])

        def setKartingTrophies(self, trophyList):
            self.kartingTrophies = trophyList

        def getKartingTrophies(self):
            return self.kartingTrophies

        def setKartingHistory(self, history):
            self.kartingHistory = history

        def getKartingHistory(self):
            return self.kartingHistory

        def setKartingPersonalBest(self, bestTimes):
            self.kartingPersonalBest = bestTimes

        def getKartingPersonalBest(self):
            return self.kartingPersonalBest

        def setKartingPersonalBest2(self, bestTimes2):
            self.kartingPersonalBest2 = bestTimes2

        def getKartingPersonalBest2(self):
            return self.kartingPersonalBest2

        def getKartingPersonalBestAll(self):
            return self.kartingPersonalBest + self.kartingPersonalBest2

    if hasattr(base, 'wantPets') and base.wantPets:

        def setPetId(self, petId):
            self.petId = petId
            if petId == 0:
                self.petDNA = None
                self.petName = None
            else:
                if self.isLocal():
                    base.cr.addPetToFriendsMap()
            return

        def getPetId(self):
            return self.petId

        def hasPet(self):
            return self.petId != 0

        def b_setPetTutorialDone(self, bDone):
            self.d_setPetTutorialDone(bDone)
            self.setPetTutorialDone(bDone)

        def d_setPetTutorialDone(self, bDone):
            self.sendUpdate('setPetTutorialDone', [bDone])

        def setPetTutorialDone(self, bDone):
            self.bPetTutorialDone = bDone

        def b_setPetMovie(self, petId, flag):
            self.d_setPetMovie(petId, flag)
            self.setPetMovie(petId, flag)

        def d_setPetMovie(self, petId, flag):
            self.sendUpdate('setPetMovie', [petId, flag])

        def setPetMovie(self, petId, flag):
            pass

        def lookupPetDNA(self):
            if self.petId and not self.petDNA:
                from toontown.pets import PetDetail
                PetDetail.PetDetail(self.petId, self.__petDetailsLoaded)

        def __petDetailsLoaded(self, pet):
            self.petDNA = pet.style

    def trickOrTreatTargetMet(self, beanAmount):
        if self.effect:
            self.effect.stop()
        self.effect = TrickOrTreatTargetEffect(beanAmount)
        self.effect.play()

    def trickOrTreatMilestoneMet(self):
        if self.effect:
            self.effect.stop()
        self.effect = TrickOrTreatMilestoneEffect()
        self.effect.play()

    def winterCarolingTargetMet(self, beanAmount):
        if self.effect:
            self.effect.stop()
        self.effect = WinterCarolingEffect(beanAmount)
        self.effect.play()

    def d_reqCogSummons(self, type, suitIndex):
        if type == 'single':
            pass
        else:
            if type == 'building':
                pass
            else:
                if type == 'invasion':
                    pass
        self.sendUpdate('reqCogSummons', [type, suitIndex])

    def cogSummonsResponse(self, returnCode, suitIndex, doId):
        messenger.send('cog-summons-response', [returnCode, suitIndex, doId])

    def setCogSummonsEarned(self, cogSummonsEarned):
        self.cogSummonsEarned = cogSummonsEarned

    def getCogSummonsEarned(self):
        return self.cogSummonsEarned

    def hasCogSummons(self, suitIndex, type=None):
        summons = self.getCogSummonsEarned()
        curSetting = summons[suitIndex]
        if type == 'single':
            return curSetting & 1
        if type == 'building':
            return curSetting & 2
        if type == 'invasion':
            return curSetting & 4
        return curSetting

    def setFlowerCollection(self, speciesList, varietyList):
        self.flowerCollection = FlowerCollection.FlowerCollection()
        self.flowerCollection.makeFromNetLists(speciesList, varietyList)

    def getFlowerCollection(self):
        return self.flowerCollection

    def setMaxFlowerBasket(self, maxFlowerBasket):
        self.maxFlowerBasket = maxFlowerBasket

    def getMaxFlowerBasket(self):
        return self.maxFlowerBasket

    def isFlowerBasketFull(self):
        return len(self.flowerBasket) >= self.maxFlowerBasket

    def setFlowerBasket(self, speciesList, varietyList):
        self.flowerBasket = FlowerBasket.FlowerBasket()
        self.flowerBasket.makeFromNetLists(speciesList, varietyList)
        messenger.send('flowerBasketUpdated')

    def getFlowerBasket(self):
        return self.flowerBasket

    def setShovel(self, shovelId):
        self.shovel = shovelId

    def attachShovel(self):
        self.shovelModel = self.getShovelModel()
        self.shovelModel.reparentTo(self.rightHand)
        return self.shovelModel

    def detachShovel(self):
        if self.shovelModel:
            self.shovelModel.removeNode()

    def getShovelModel(self):
        shovels = loader.loadModel('phase_5.5/models/estate/shovels')
        shovelId = ['A',
         'B',
         'C',
         'D'][self.shovel]
        shovel = shovels.find('**/shovel' + shovelId)
        shovel.setH(-90)
        shovel.setP(216)
        shovel.setX(0.2)
        shovel.detachNode()
        shovels.removeNode()
        return shovel

    def setShovelSkill(self, skillLevel):
        self.shovelSkill = skillLevel

    def getBoxCapability(self):
        return GardenGlobals.getShovelPower(self.shovel, self.shovelSkill)

    def setWateringCan(self, wateringCanId):
        self.wateringCan = wateringCanId

    def attachWateringCan(self):
        self.wateringCanModel = self.getWateringCanModel()
        self.wateringCanModel.reparentTo(self.rightHand)
        return self.wateringCanModel

    def detachWateringCan(self):
        if self.wateringCanModel:
            self.wateringCanModel.removeNode()

    def getWateringCanModel(self):
        scalePosHprsTable = ((0.25, 0.1, 0, 0.2, -90, -125, -45),
         (0.2, 0.0, 0.25, 0.2, -90, -125, -45),
         (0.2, 0.2, 0.1, 0.2, -90, -125, -45),
         (0.2, 0.0, 0.25, 0.2, -90, -125, -45))
        cans = loader.loadModel('phase_5.5/models/estate/watering_cans')
        canId = ['A',
         'B',
         'C',
         'D'][self.wateringCan]
        can = cans.find('**/water_can' + canId)
        can.setScale(scalePosHprsTable[self.wateringCan][0])
        can.setPos(scalePosHprsTable[self.wateringCan][1], scalePosHprsTable[self.wateringCan][2], scalePosHprsTable[self.wateringCan][3])
        can.setHpr(scalePosHprsTable[self.wateringCan][4], scalePosHprsTable[self.wateringCan][5], scalePosHprsTable[self.wateringCan][6])
        can.detachNode()
        cans.removeNode()
        if hasattr(base, 'rwc'):
            if base.rwc:
                if hasattr(self, 'wateringCan2'):
                    self.wateringCan2.removeNode()
                self.wateringCan2 = can.copyTo(self.rightHand)
            else:
                self.wateringCan2.removeNode()
        return can

    def setWateringCanSkill(self, skillLevel):
        self.wateringCanSkill = skillLevel

    def setGardenSpecials(self, specials):
        self.gardenSpecials = specials
        if hasattr(self, 'gardenPage') and self.gardenPage:
            self.gardenPage.updatePage()

    def getGardenSpecials(self):
        return self.gardenSpecials

    def getMyTrees(self):
        treeDict = self.cr.getObjectsOfClass(DistributedGagTree.DistributedGagTree)
        trees = []
        for tree in treeDict.values():
            if tree.getOwnerId() == self.doId:
                trees.append(tree)

        if not trees:
            pass
        return trees

    def isTreePlanted(self, track, level):
        trees = self.getMyTrees()
        for tree in trees:
            if tree.gagTrack == track and tree.gagLevel == level:
                return True

        return False

    def doIHaveRequiredTrees(self, track, level):
        trees = self.getMyTrees()
        trackAndLevelList = []
        for tree in trees:
            trackAndLevelList.append((tree.gagTrack, tree.gagLevel))

        haveRequired = True
        for curLevel in range(level):
            testTuple = (
             track, curLevel)
            if testTuple not in trackAndLevelList:
                haveRequired = False
                break

        return haveRequired

    def setTrackBonusLevel(self, trackArray):
        self.trackBonusLevel = trackArray
        if self.inventory:
            self.inventory.updateGUI()

    def getTrackBonusLevel(self, track=None):
        if track == None:
            return self.trackBonusLevel
        return self.trackBonusLevel[track]
        return

    def checkGagBonus(self, track, level):
        trackBonus = self.getTrackBonusLevel(track)
        return trackBonus >= level

    def setGardenTrophies(self, trophyList):
        self.gardenTrophies = trophyList

    def getGardenTrophies(self):
        return self.gardenTrophies

    def useSpecialResponse(self, returnCode):
        messenger.send('use-special-response', [returnCode])

    def setGardenStarted(self, bStarted):
        self.gardenStarted = bStarted

    def getGardenStarted(self):
        return self.gardenStarted

    def sendToGolfCourse(self, zoneId):
        print 'sending to golfCourse'
        hoodId = self.cr.playGame.hood.hoodId
        golfRequest = {'loader': 'safeZoneLoader', 'where': 'golfcourse', 
           'how': 'teleportIn', 
           'hoodId': hoodId, 
           'zoneId': zoneId, 
           'shardId': None, 
           'avId': -1}
        base.cr.playGame.getPlace().requestLeave(golfRequest)
        return

    def getGolfTrophies(self):
        return self.golfTrophies

    def getGolfCups(self):
        return self.golfCups

    def setGolfHistory(self, history):
        self.golfHistory = history
        self.golfTrophies = GolfGlobals.calcTrophyListFromHistory(self.golfHistory)
        self.golfCups = GolfGlobals.calcCupListFromHistory(self.golfHistory)
        if hasattr(self, 'book'):
            self.addGolfPage()

    def getGolfHistory(self):
        return self.golfHistory

    def hasPlayedGolf(self):
        retval = False
        for historyValue in self.golfHistory:
            if historyValue:
                retval = True
                break

        return retval

    def setPackedGolfHoleBest(self, packedHoleBest):
        unpacked = GolfGlobals.unpackGolfHoleBest(packedHoleBest)
        self.setGolfHoleBest(unpacked)

    def setGolfHoleBest(self, holeBest):
        self.golfHoleBest = holeBest

    def getGolfHoleBest(self):
        return self.golfHoleBest

    def setGolfCourseBest(self, courseBest):
        self.golfCourseBest = courseBest

    def getGolfCourseBest(self):
        return self.golfCourseBest

    def setUnlimitedSwing(self, unlimitedSwing):
        self.unlimitedSwing = unlimitedSwing

    def getUnlimitedSwing(self):
        return self.unlimitedSwing

    def getPinkSlips(self):
        if hasattr(self, 'pinkSlips'):
            return self.pinkSlips
        return 0

    def setPinkSlips(self, pinkSlips):
        self.pinkSlips = pinkSlips

    def setAccess(self, access):
        self.setGameAccess(access)
        self.setDisplayName(self.getName())

    def setGameAccess(self, access):
        self.gameAccess = access

    def getGameAccess(self):
        if hasattr(self, 'gameAccess'):
            return self.gameAccess
        return 0

    def setDisplayName(self, str):
        if self.getGameAccess() == OTPGlobals.AccessFull and not self.isDisguised:
            self.setFancyNametag(name=str)
        else:
            self.removeFancyNametag()
            Avatar.Avatar.setDisplayName(self, str)

    def setFancyNametag(self, name=None):
        if name == None:
            name = self.getName()
        if self.getNametagStyle() == 100:
            self.setFont(ToontownGlobals.getToonFont())
        else:
            self.setFont(ToontownGlobals.getNametagFont(self.getNametagStyle()))
        Avatar.Avatar.setDisplayName(self, name)
        return

    def removeFancyNametag(self):
        self.nametag.clearShadow()

    def getNametagStyle(self):
        if hasattr(self, 'nametagStyle'):
            return self.nametagStyle
        return 0

    def setNametagStyle(self, nametagStyle):
        if hasattr(self, 'gmToonLockStyle') and self.gmToonLockStyle:
            return
        if config.GetBool('want-nametag-avids', 0):
            nametagStyle = 0
        self.nametagStyle = nametagStyle
        self.setDisplayName(self.getName())

    def setNametagType(self, type):
        self.setPlayerType(type, True)
        if not self.isLocal():
            if type == 2 and base.localAvatar.getAdminAccess() >= 400:
                self.setPickable(1)
            else:
                self.setPickable(0)

    def setAnimPlayRate(self, rate):
        for anim in self.getAnimNames():
            self.setPlayRate(rate, anim)

        if rate == 1:
            self.forceRate = False
        else:
            self.forceRate = True
        self.rate = rate

    def getAvIdName(self):
        paidStr = PythonUtil.choice(self.getGameAccess() == OTPGlobals.AccessFull, 'P', 'F')
        return '%s\n%s (%s)' % (self.getName(), self.doId, paidStr)

    def getTTSVolume(self):
        avatarPos = self.getPos(base.localAvatar)
        result = int(round((avatarPos[0] + avatarPos[1]) / 2))
        if result > 100:
            result = 100
        else:
            if result < 0:
                result = 0
        volumeList = range(100, -1, -1)
        return volumeList[result]

    def playCurrentDialogue(self, dialogue, chatFlags, interrupt=1):
        reality = False
        if chatFlags & CFExclaim == 512:
            reality = True
        if interrupt and self.__currentDialogue is not None:
            self.__currentDialogue.stop()
        self.__currentDialogue = dialogue
        if dialogue:
            base.playSfx(dialogue, node=self)
        else:
            if chatFlags & CFSpeech != 0 or chatFlags & CFExclaim == 512:
                if self.nametag.getNumChatPages() > 0:
                    self.playDialogueForString(self.nametag.getChat(), exclaim=reality)
                    if self.soundChatBubble != None:
                        base.playSfx(self.soundChatBubble, node=self)
                elif self.nametag.getChatStomp() > 0:
                    self.playDialogueForString(self.nametag.getStompText(), self.nametag.getStompDelay(), exclaim=reality)
        return

    def playDialogueForString(self, chatString, delay=0.0, exclaim=False):
        if len(chatString) == 0:
            return
        searchString = chatString.lower()
        if searchString.find(OTPLocalizer.DialogSpecial) >= 0:
            type = 'special'
        else:
            if searchString.find(OTPLocalizer.DialogExclamation) >= 0 or exclaim:
                type = 'exclamation'
            else:
                if searchString.find(OTPLocalizer.DialogQuestion) >= 0:
                    type = 'question'
                else:
                    if random.randint(0, 1):
                        type = 'statementA'
                    else:
                        type = 'statementB'
        stringLength = len(chatString)
        if stringLength <= OTPLocalizer.DialogLength1:
            length = 1
        else:
            if stringLength <= OTPLocalizer.DialogLength2:
                length = 2
            else:
                if stringLength <= OTPLocalizer.DialogLength3:
                    length = 3
                else:
                    length = 4
        self.playDialogue(type, length, delay, chatString)

    def playDialogue(self, type, length, delay=0.0, chatString=''):
        if base.textToSpeech:
            animalType = self.style.getType()
            if sys.platform == 'darwin':
                if self.getTTSVolume() == 0:
                    return
                if config.GetString('language', 'english') == 'french':
                    voice = 'Thomas'
                else:
                    if animalType == 'dog':
                        voice = 'Alex'
                    else:
                        if animalType == 'cat':
                            voice = 'Samantha'
                        else:
                            if animalType == 'horse':
                                voice = 'Daniel'
                            else:
                                if animalType == 'mouse':
                                    voice = 'Junior'
                                else:
                                    if animalType == 'rabbit':
                                        voice = 'Princess'
                                    else:
                                        if animalType == 'duck':
                                            voice = 'Fred'
                                        else:
                                            if animalType == 'monkey':
                                                voice = 'Deranged'
                                            else:
                                                if animalType == 'bear':
                                                    voice = 'Bruce'
                                                else:
                                                    if animalType == 'pig':
                                                        voice = 'Albert'
                                                    else:
                                                        if animalType == 'riggy':
                                                            voice = 'Hysterical'
                                                        else:
                                                            voice = 'Alex'
                Popen(['say', voice, chatString])
            else:
                if animalType == 'dog':
                    pitch = '-p50'
                else:
                    if animalType == 'cat':
                        pitch = '-p80'
                    else:
                        if animalType == 'horse':
                            pitch = '-p30'
                        else:
                            if animalType == 'mouse':
                                pitch = '-p99'
                            else:
                                if animalType == 'rabbit':
                                    pitch = '-p95'
                                else:
                                    if animalType == 'duck':
                                        pitch = '-p35'
                                    else:
                                        if animalType == 'monkey':
                                            pitch = '-p85'
                                        else:
                                            if animalType == 'bear':
                                                pitch = '-p20'
                                            else:
                                                if animalType == 'pig':
                                                    pitch = '-p25'
                                                else:
                                                    if animalType == 'riggy':
                                                        pitch = '-p75'
                                                    else:
                                                        pitch = '-p50'
                volume = '-a' + str(self.getTTSVolume())
                if volume == '-a0':
                    return
                lang = '-v' + config.GetString('language', 'english')[:2]
                Popen([os.environ['PROGRAMFILES'] + '\\eSpeak\\command_line\\espeak', pitch, volume, lang, chatString])
        else:
            dialogueArray = self.getDialogueArray()
            if dialogueArray == None:
                return
        sfxIndex = None
        if type == 'statementA' or type == 'statementB':
            if length == 1:
                sfxIndex = 0
            elif length == 2:
                sfxIndex = 1
            elif length >= 3:
                sfxIndex = 2
        else:
            if type == 'question':
                sfxIndex = 3
            else:
                if type == 'exclamation':
                    sfxIndex = 4
                else:
                    if type == 'special':
                        sfxIndex = 5
                    else:
                        self.notify.error('unrecognized dialogue type: ', type)
        if sfxIndex != None and sfxIndex < len(dialogueArray) and dialogueArray[sfxIndex] != None:
            soundSequence = Sequence(Wait(delay), SoundInterval(dialogueArray[sfxIndex], node=None, listenerNode=base.localAvatar, loop=0, volume=1.0))
            self.soundSequenceList.append(soundSequence)
            soundSequence.start()
            self.cleanUpSoundList()
        return

    def cleanUpSoundList(self):
        removeList = []
        for soundSequence in self.soundSequenceList:
            if soundSequence.isStopped():
                removeList.append(soundSequence)

        for soundSequence in removeList:
            self.soundSequenceList.remove(soundSequence)

    def sendLogMessage(self, message):
        self.sendUpdate('logMessage', [message])

    def setChatAbsolute(self, chatString, chatFlags, dialogue=None, interrupt=1, quiet=0, hmm=False):
        if not hmm and hasattr(self, 'ogqt'):
            self.nametag.setQtColor(self.ogqt)
            del self.ogqt
        DistributedAvatar.DistributedAvatar.setChatAbsolute(self, chatString, chatFlags, dialogue, interrupt)

    def setChatMuted(self, chatString, chatFlags, dialogue=None, interrupt=1, quiet=0):
        self.nametag.setChat(chatString, chatFlags)
        self.playCurrentDialogue(dialogue, chatFlags - CFSpeech, interrupt)

    def displayTalk(self, chatString, mods=None, coolColor=False):
        flags = CFSpeech | CFTimeout
        if base.talkAssistant.isThought(chatString):
            flags = CFThought
            chatString = base.talkAssistant.removeThoughtPrefix(chatString)
        else:
            if base.talkAssistant.isExclaim(chatString):
                flags = CFExclaim | CFTimeout
                chatString = base.talkAssistant.removeExclaimPrefix(chatString)
        if coolColor:
            flags = CFQuicktalker | flags
            hmm = False
            if len(mods) == 1:
                if mods[(len(mods) - 1)] == 2:
                    hmm = True
                    if not hasattr(self, 'ogqt'):
                        self.ogqt = self.nametag.qtColor
                    self.nametag.setQtColor(VBase4(0.5, 0.5, 0.5, 1))
            self.setChatAbsolute(chatString, flags, hmm=hmm)
        else:
            self.nametag.setChat(chatString, flags)
            if base.toonChatSounds:
                self.playCurrentDialogue(None, flags, interrupt=1)
        return

    def setMail(self, mail):
        DistributedToon.partyNotify.debug('setMail called with %d mail items' % len(mail))
        self.mail = []
        for i in xrange(len(mail)):
            oneMailItem = mail[i]
            newMail = SimpleMailBase(*oneMailItem)
            self.mail.append(newMail)

    def setSimpleMailNotify(self, simpleMailNotify):
        DistributedToon.partyNotify.debug('setSimpleMailNotify( %s )' % simpleMailNotify)
        self.simpleMailNotify = simpleMailNotify
        if self.isLocal():
            self.gotCatalogNotify = 1
            self.refreshOnscreenButtons()

    def setInviteMailNotify(self, inviteMailNotify):
        DistributedToon.partyNotify.debug('setInviteMailNotify( %s )' % inviteMailNotify)
        self.inviteMailNotify = inviteMailNotify
        if self.isLocal():
            self.gotCatalogNotify = 1
            self.refreshOnscreenButtons()

    def setInvites(self, invites):
        DistributedToon.partyNotify.debug('setInvites called passing in %d invites.' % len(invites))
        self.invites = []
        for i in xrange(len(invites)):
            oneInvite = invites[i]
            newInvite = InviteInfo(*oneInvite)
            self.invites.append(newInvite)

    def updateInviteMailNotify(self):
        invitesInMailbox = self.getInvitesToShowInMailbox()
        newInvites = 0
        readButNotRepliedInvites = 0
        for invite in invitesInMailbox:
            if invite.status == PartyGlobals.InviteStatus.NotRead:
                newInvites += 1
            else:
                if invite.status == PartyGlobals.InviteStatus.ReadButNotReplied:
                    readButNotRepliedInvites += 1
            if __dev__:
                partyInfo = self.getOnePartyInvitedTo(invite.partyId)
                if not partyInfo:
                    self.notify.error('party info not found in partiesInvtedTo, partyId = %s' % str(invite.partyId))

        if newInvites:
            self.setInviteMailNotify(ToontownGlobals.NewItems)
        else:
            if readButNotRepliedInvites:
                self.setInviteMailNotify(ToontownGlobals.OldItems)
            else:
                self.setInviteMailNotify(ToontownGlobals.NoItems)

    def getInvitesToShowInMailbox(self):
        result = []
        for invite in self.invites:
            appendInvite = True
            if invite.status == InviteStatus.Accepted or invite.status == InviteStatus.Rejected:
                appendInvite = False
            if appendInvite:
                partyInfo = self.getOnePartyInvitedTo(invite.partyId)
                if not partyInfo:
                    appendInvite = False
                if appendInvite:
                    if partyInfo.status == PartyGlobals.PartyStatus.Cancelled:
                        appendInvite = False
                if appendInvite:
                    endDate = partyInfo.endTime.date()
                    curDate = base.cr.toontownTimeManager.getCurServerDateTime().date()
                    if endDate < curDate:
                        appendInvite = False
            if appendInvite:
                result.append(invite)

        return result

    def getNumInvitesToShowInMailbox(self):
        result = len(self.getInvitesToShowInMailbox())
        return result

    def setHostedParties(self, hostedParties):
        DistributedToon.partyNotify.debug('setHostedParties called passing in %d parties.' % len(hostedParties))
        self.hostedParties = []
        for i in xrange(len(hostedParties)):
            hostedInfo = hostedParties[i]
            newParty = PartyInfo(*hostedInfo)
            self.hostedParties.append(newParty)

    def setPartiesInvitedTo(self, partiesInvitedTo):
        DistributedToon.partyNotify.debug('setPartiesInvitedTo called passing in %d parties.' % len(partiesInvitedTo))
        self.partiesInvitedTo = []
        for i in xrange(len(partiesInvitedTo)):
            partyInfo = partiesInvitedTo[i]
            newParty = PartyInfo(*partyInfo)
            self.partiesInvitedTo.append(newParty)

        self.updateInviteMailNotify()

    def getOnePartyInvitedTo(self, partyId):
        result = None
        for i in xrange(len(self.partiesInvitedTo)):
            partyInfo = self.partiesInvitedTo[i]
            if partyInfo.partyId == partyId:
                result = partyInfo
                break

        return result

    def getInviteForPartyId(self, partyId):
        result = None
        for invite in self.invites:
            if invite.partyId == partyId:
                result = invite
                break

        return result

    def setPartyReplies(self, replies):
        DistributedToon.partyNotify.debug('setPartyReplies called passing in %d parties.' % len(replies))
        self.partyReplyInfoBases = []
        for i in xrange(len(replies)):
            partyReply = replies[i]
            repliesForOneParty = PartyReplyInfoBase(*partyReply)
            self.partyReplyInfoBases.append(repliesForOneParty)

    def setPartyCanStart(self, partyId):
        DistributedToon.partyNotify.debug('setPartyCanStart called passing in partyId=%s' % partyId)
        for partyInfo in self.hostedParties:
            if partyInfo.partyId == partyId:
                partyInfo.status = PartyGlobals.PartyStatus.CanStart
                from toontown.shtiker import EventsPage
                if hasattr(self, 'eventsPage') and base.localAvatar.book.entered and base.localAvatar.book.isOnPage(self.eventsPage) and self.eventsPage.getMode() == EventsPage.EventsPage_Host:
                    base.localAvatar.eventsPage.loadHostedPartyInfo()
                if hasattr(self, 'displaySystemClickableWhisper'):
                    self.displaySystemClickableWhisper(0, TTLocalizer.PartyCanStart, whisperType=WhisperPopup.WTSystem)
                else:
                    self.setSystemMessage(0, TTLocalizer.PartyCanStart)

    def setPartyStatus(self, partyId, newStatus):
        DistributedToon.partyNotify.debug('setPartyCanStatus called passing in partyId=%s status=%s' % (partyId, newStatus))
        found = False
        for partyInfo in self.hostedParties:
            if partyInfo.partyId == partyId:
                partyInfo.status = newStatus
                found = True
                break

        for partyInfo in self.partiesInvitedTo:
            if partyInfo.partyId == partyId:
                partyInfo.status = newStatus
                found = True
                from toontown.shtiker import EventsPage
                if hasattr(self, 'eventsPage') and base.localAvatar.book.entered and base.localAvatar.book.isOnPage(self.eventsPage) and self.eventsPage.getMode() == EventsPage.EventsPage_Invited:
                    base.localAvatar.eventsPage.loadInvitations()
                if newStatus == PartyStatus.Started and hasattr(self, 'displaySystemClickableWhisper'):
                    invite = self.getInviteForPartyId(partyId)
                    if invite:
                        name = ' '
                        host = base.cr.identifyAvatar(partyInfo.hostId)
                        if host:
                            name = host.getName()
                        if invite.status == InviteStatus.Accepted:
                            displayStr = TTLocalizer.PartyHasStartedAcceptedInvite % TTLocalizer.GetPossesive(name, 'party')
                            self.displaySystemClickableWhisper(-1, displayStr, whisperType=WhisperPopup.WTSystem)
                        else:
                            displayStr = TTLocalizer.PartyHasStartedNotAcceptedInvite % TTLocalizer.GetPossesive(name, 'party')
                            self.setSystemMessage(partyInfo.hostId, displayStr, whisperType=WhisperPopup.WTSystem)
                break

        if not found:
            self.notify.warning("setPartyCanStart can't find partyId=% status=%d" % (partyId, newStatus))

    def announcePartyStarted(self, partyId):
        DistributedToon.partyNotify.debug('announcePartyStarted')
        return
        for partyReplyInfo in self.partyReplyInfoBases:
            if partyReplyInfo.partyId == partyId:
                for singleReply in partyReplyInfo.replies:
                    toonId = singleReply.inviteeId
                    if base.cr.isFriend(toonId):
                        if base.cr.isFriendOnline(toonId):
                            if singleReply.status == InviteStatus.Accepted:
                                self.whisperSCTo(5302, toonId, 0)
                            else:
                                self.whisperSCTo(5302, toonId, 0)

    def updateInvite(self, inviteKey, newStatus):
        DistributedToon.partyNotify.debug('updateInvite( inviteKey=%d, newStatus=%s )' % (inviteKey, InviteStatus.getString(newStatus)))
        for invite in self.invites:
            if invite.inviteKey == inviteKey:
                invite.status = newStatus
                self.updateInviteMailNotify()
                break

    def updateReply(self, partyId, inviteeId, newStatus):
        DistributedToon.partyNotify.debug('updateReply( partyId=%d, inviteeId=%d, newStatus=%s )' % (partyId, inviteeId, InviteStatus.getString(newStatus)))
        for partyReplyInfoBase in self.partyReplyInfoBases:
            if partyReplyInfoBase.partyId == partyId:
                for reply in partyReplyInfoBase.replies:
                    if reply.inviteeId == inviteeId:
                        reply.status = newStatus
                        break

    def scrubTalk(self, message, mods):
        scrubbed = 0
        text = copy.copy(message)
        for mod in mods:
            index = mod[0]
            length = mod[1] - mod[0] + 1
            newText = text[0:index] + length * '\x07' + text[index + length:]
            text = newText

        words = text.split(' ')
        newwords = []
        for word in words:
            if word == '':
                newwords.append(word)
            elif word[0] == '\x07' or len(word) > 1 and word[0] == '.' and word[1] == '\x07':
                newwords.append('\x01WLDisplay\x01' + self.chatGarbler.garbleSingle(self, word) + '\x02')
                scrubbed = 1
            elif not self.whiteListEnabled or base.whiteList.isWord(word):
                newwords.append(word)
            else:
                flag = 0
                for friendId, flags in self.friendsList:
                    if not flags & ToontownGlobals.FriendChat:
                        flag = 1

                if flag:
                    scrubbed = 1
                    newwords.append('\x01WLDisplay\x01' + word + '\x02')
                else:
                    newwords.append(word)

        newText = (' ').join(newwords)
        return (
         newText, scrubbed)

    def replaceBadWords(self, text):
        words = text.split(' ')
        newwords = []
        for word in words:
            if word == '':
                newwords.append(word)
            elif word[0] == '\x07':
                newwords.append('\x01WLRed\x01' + self.chatGarbler.garbleSingle(self, word) + '\x02')
            elif not self.whiteListEnabled or base.whiteList.isWord(word):
                newwords.append(word)
            else:
                newwords.append('\x01WLRed\x01' + word + '\x02')

        newText = (' ').join(newwords)
        return newText

    def toonUp(self, hpGained, hasInteractivePropBonus=False):
        if self.hp == None or hpGained < 0:
            return
        oldHp = self.hp
        if self.hp + hpGained <= 0:
            self.hp += hpGained
        else:
            self.hp = min(max(self.hp, 0) + hpGained, self.maxHp)
        hpGained = self.hp - max(oldHp, 0)
        if hpGained > 0:
            self.showHpText(hpGained, hasInteractivePropBonus=hasInteractivePropBonus)
            self.hpChange(quietly=0)
        return

    def showHpText(self, number, bonus=0, scale=1, hasInteractivePropBonus=False):
        if self.HpTextEnabled and not self.ghostMode:
            if number != 0:
                if self.hpText:
                    self.hideHpText()
                self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
                if number < 0:
                    self.HpTextGenerator.setText(str(number))
                else:
                    hpGainedStr = '+' + str(number)
                    if hasInteractivePropBonus:
                        hpGainedStr += '\n' + TTLocalizer.InteractivePropTrackBonusTerms[0]
                    self.HpTextGenerator.setText(hpGainedStr)
                self.HpTextGenerator.clearShadow()
                self.HpTextGenerator.setAlign(TextNode.ACenter)
                if bonus == 1:
                    r = 1.0
                    g = 1.0
                    b = 0
                    a = 1
                else:
                    if bonus == 2:
                        r = 1.0
                        g = 0.5
                        b = 0
                        a = 1
                    else:
                        if number < 0:
                            r = 0.9
                            g = 0
                            b = 0
                            a = 1
                        else:
                            r = 0
                            g = 0.9
                            b = 0
                            a = 1
                self.HpTextGenerator.setTextColor(r, g, b, a)
                self.hpTextNode = self.HpTextGenerator.generate()
                self.hpText = self.attachNewNode(self.hpTextNode)
                self.hpText.setScale(scale)
                self.hpText.setBillboardPointEye()
                self.hpText.setBin('fixed', 100)
                self.hpText.setPos(0, 0, self.height / 2)
                seq = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(0.85), self.hpText.colorInterval(0.1, Vec4(r, g, b, 0)), Func(self.hideHpText))
                seq.start()

    def setName(self, name='unknownDistributedAvatar'):
        DistributedPlayer.DistributedPlayer.setName(self, name)
        self._handleGMName()

    def _handleGMName(self):
        name = self.name
        self.setDisplayName(name)
        if self._isGM:
            self.setNametagStyle(5)
            self.setGMIcon(self._gmType)
            self.gmToonLockStyle = False
        else:
            self.gmToonLockStyle = False
            self.removeGMIcon()
            self.setNametagStyle(100)

    def setGMIcon(self, gmType=None):
        if hasattr(self, 'gmIcon') and self.gmIcon:
            return
        if not gmType:
            gmType = self._gmType
        iconInfo = (
         ('phase_3.5/models/gui/tt_m_gui_gm_toontroop_whistle', '**/*whistleIcon*', 'phase_3.5/maps/gamegui_palette_3clla_1.jpg',
 4),
         ('phase_3.5/models/gui/tt_m_gui_gm_toontroop_whistle', '**/*whistleIcon*', 'phase_3.5/maps/gamegui_palette_3clla_1.jpg',
 4),
         ('phase_3.5/models/gui/tt_m_gui_gm_toonResistance_fist', '**/*fistIcon*', 'phase_3.5/maps/gamegui_palette_3clla_1.jpg',
 4),
         ('phase_3.5/models/gui/tt_m_gui_gm_toontroop_getConnected', '**/*whistleIcon*', 'phase_3.5/maps/gamegui_palette_3clla_1.jpg',
 4),
         ('phase_3.5/models/gui/tt_m_gui_gm_toontroop_whistle', '**/*whistleIcon*', 'phase_3.5/maps/gamegui_palette_3clla_2.jpg',
 4),
         ('phase_3.5/models/gui/tt_m_gui_gm_toonResistance_fist', '**/*fistIcon*', 'phase_3.5/maps/gamegui_palette_3clla_2.jpg',
 4),
         ('phase_3.5/models/gui/tt_m_gui_gm_toontroop_getConnected', '**/*whistleIcon*', 'phase_3.5/maps/gamegui_palette_3clla_2.jpg',
 4),
         ('phase_3.5/models/gui/tt_m_gui_gm_toonResistance_fist', '**/*fistIcon*', 'phase_3.5/maps/gamegui_palette_3clla_3.jpg',
 4),
         ('phase_3.5/models/gui/tt_m_gui_gm_toontroop_getConnected', '**/*whistleIcon*', 'phase_3.5/maps/gamegui_palette_3clla_3.jpg',
 4))
        if gmType > len(iconInfo) - 1:
            return
        modelName, searchString, texture, scale = iconInfo[gmType]
        icons = loader.loadModel(modelName)
        self.gmIcon = icons.find(searchString)
        ts = self.gmIcon.findTextureStage('*')
        tex = loader.loadTexture(texture)
        self.gmIcon.setTexture(ts, tex, 1)
        self.gmIcon.setScale(scale)
        np = NodePath(self.nametag.getNameIcon())
        self.gmIcon.reparentTo(np)
        self.setTrophyScore(self.trophyScore)
        self.gmIcon.setZ(-2.5)
        self.gmIcon.setY(0.0)
        self.gmIcon.setColor(Vec4(1.0, 1.0, 1.0, 1.0))
        self.gmIcon.setTransparency(1)
        self.gmIconInterval = LerpHprInterval(self.gmIcon, 3.0, Point3(0, 0, 0), Point3(-360, 0, 0))
        self.gmIconInterval.loop()

    def setGMPartyIcon(self):
        gmType = self._gmType
        iconInfo = ('phase_3.5/models/gui/tt_m_gui_gm_toonResistance_fist', 'phase_3.5/models/gui/tt_m_gui_gm_toontroop_whistle',
                    'phase_3.5/models/gui/tt_m_gui_gm_toonResistance_fist', 'phase_3.5/models/gui/tt_m_gui_gm_toontroop_getConnected')
        if gmType > len(iconInfo) - 1:
            return
        self.gmIcon = loader.loadModel(iconInfo[gmType])
        self.gmIcon.reparentTo(NodePath(self.nametag.getNameIcon()))
        self.gmIcon.setScale(3.25)
        self.setTrophyScore(self.trophyScore)
        self.gmIcon.setZ(1.0)
        self.gmIcon.setY(0.0)
        self.gmIcon.setColor(Vec4(1.0, 1.0, 1.0, 1.0))
        self.gmIcon.setTransparency(1)
        self.gmIconInterval = LerpHprInterval(self.gmIcon, 3.0, Point3(0, 0, 0), Point3(-360, 0, 0))
        self.gmIconInterval.loop()

    def removeGMIcon(self):
        if hasattr(self, 'gmIconInterval') and self.gmIconInterval:
            self.gmIconInterval.finish()
            del self.gmIconInterval
        if hasattr(self, 'gmIcon') and self.gmIcon:
            self.gmIcon.detachNode()
            del self.gmIcon

    def setAnimalSound(self, index):
        self.animalSound = index

    def magicFanfare(self):
        from toontown.battle import Fanfare
        fanfare = Sequence(Fanfare.makeFanfare(0, self)[0])
        fanfare.start()

    def magicGreenByeBye(self, cog, isToon=0):
        if cog:
            if isToon == 1:
                if cog.isDisguised:
                    self.cogFlyOut = cog.getSuitTeleport(moveIn=0)
                    seq = Sequence(Func(self.cogFlyOut.start), Wait(6), Func(cog.reparentTo, hidden), Func(cog.removeActive))
                else:
                    seq = Sequence(Func(cog.animFSM.request, 'TeleportOut'), Wait(cog.getDuration('teleport')), Func(cog.reparentTo, hidden), Func(cog.stopBlink), Func(cog.removeActive))
            else:
                if isToon == 2:
                    seq = Sequence(Func(cog.reparentTo, hidden), Func(self.nodiiii.removeNode))
                else:
                    self.cogFlyOut = cog.beginSupaFlyMove(VBase3(cog.getX(), cog.getY(), cog.getZ()), 0, 'flyOut')
                    seq = Sequence(Func(self.cogFlyOut.start), Wait(6), Func(cog.reparentTo, hidden), Func(cog.removeActive))
            seq.start()

    def magicGreen(self, cogType='f', toonId=0):
        dept = None
        level = None
        x = 0
        self.cogs = None
        self.flyIns = None
        if cogType == 'ols' or cogType == 'ty':
            dept = False
        if cogType == 'ty':
            level = 'TY'
        else:
            if cogType == 'fts':
                level = '11' + TTLocalizer.SkeleRevivePostFix
        self.finishGreenSequence()
        if cogType in ('sellbots', 'cashbots', 'lawbots', 'bossbots', 'hackerbots'):
            if cogType == 'sellbots':
                cogList = [
                 'cc', 'tm', 'nd', 'gh', 'ms', 'tf', 'm', 'mh']
            else:
                if cogType == 'cashbots':
                    cogList = [
                     'sc', 'pp', 'tw', 'bc', 'nc', 'mb', 'ls', 'rb']
                else:
                    if cogType == 'lawbots':
                        cogList = [
                         'bf', 'b', 'dt', 'ac', 'bs', 'sd', 'le', 'bw']
                    else:
                        if cogType == 'bossbots':
                            cogList = [
                             'f', 'p', 'ym', 'mm', 'ds', 'hh', 'cr', 'tbc']
                        else:
                            if cogType == 'hackerbots':
                                cogList = [
                                 'm1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8']
            self.cog = ToontownAvatarUtils.createDistributedCog(cogList[0], self.getX() - 3, self.getY(), self.getZ(), self.getH() - self.getH() * 3, 0, 0, parent=hidden, level=level, dept=dept)
            self.cog2 = ToontownAvatarUtils.createDistributedCog(cogList[1], self.getX() - 3, self.getY() - 3, self.getZ(), self.getH() - self.getH() * 3, 0, 0, parent=hidden, level=level, dept=dept)
            self.cog3 = ToontownAvatarUtils.createDistributedCog(cogList[2], self.getX() - 3, self.getY() + 3, self.getZ(), self.getH() - self.getH() * 3, 0, 0, parent=hidden, level=level, dept=dept)
            self.cog4 = ToontownAvatarUtils.createDistributedCog(cogList[3], self.getX(), self.getY() - 3, self.getZ(), self.getH() - self.getH() * 3, 0, 0, parent=hidden, level=level, dept=dept)
            self.cog5 = ToontownAvatarUtils.createDistributedCog(cogList[4], self.getX(), self.getY() + 3, self.getZ(), self.getH() - self.getH() * 3, 0, 0, parent=hidden, level=level, dept=dept)
            self.cog6 = ToontownAvatarUtils.createDistributedCog(cogList[5], self.getX() + 3, self.getY() + 3, self.getZ(), self.getH() - self.getH() * 3, 0, 0, parent=hidden, level=level, dept=dept)
            self.cog7 = ToontownAvatarUtils.createDistributedCog(cogList[6], self.getX() + 3, self.getY() - 3, self.getZ(), self.getH() - self.getH() * 3, 0, 0, parent=hidden, level=level, dept=dept)
            self.cog8 = ToontownAvatarUtils.createDistributedCog(cogList[7], self.getX() + 3, self.getY(), self.getZ(), self.getH() - self.getH() * 3, 0, 0, parent=hidden, level=level, dept=dept)
            self.cogFlyIn = self.cog.beginSupaFlyMove(VBase3(self.getX() - 3, self.getY(), self.getZ()), 1, 'flyIn', walkAfterLanding=False)
            self.cogFlyIn2 = self.cog2.beginSupaFlyMove(VBase3(self.getX() - 3, self.getY() - 3, self.getZ()), 1, 'flyIn', walkAfterLanding=False)
            self.cogFlyIn3 = self.cog3.beginSupaFlyMove(VBase3(self.getX() - 3, self.getY() + 3, self.getZ()), 1, 'flyIn', walkAfterLanding=False)
            self.cogFlyIn4 = self.cog4.beginSupaFlyMove(VBase3(self.getX(), self.getY() - 3, self.getZ()), 1, 'flyIn', walkAfterLanding=False)
            self.cogFlyIn5 = self.cog5.beginSupaFlyMove(VBase3(self.getX(), self.getY() + 3, self.getZ()), 1, 'flyIn', walkAfterLanding=False)
            self.cogFlyIn6 = self.cog6.beginSupaFlyMove(VBase3(self.getX() + 3, self.getY() + 3, self.getZ()), 1, 'flyIn', walkAfterLanding=False)
            self.cogFlyIn7 = self.cog7.beginSupaFlyMove(VBase3(self.getX() + 3, self.getY() - 3, self.getZ()), 1, 'flyIn', walkAfterLanding=False)
            self.cogFlyIn8 = self.cog8.beginSupaFlyMove(VBase3(self.getX() + 3, self.getY(), self.getZ()), 1, 'flyIn', walkAfterLanding=False)
            self.cogs = [
             self.cog, self.cog2, self.cog3, self.cog4, self.cog5, self.cog6, self.cog7, self.cog8]
            self.flyIns = [self.cogFlyIn, self.cogFlyIn2, self.cogFlyIn3, self.cogFlyIn4, self.cogFlyIn5, self.cogFlyIn6, self.cogFlyIn7, self.cogFlyIn8]
            for cog in self.cogs:
                cog.setTransparency(1)

        else:
            if toonId == 2:
                if self.isDisguised:
                    if self.isCog != 0 and self.isCog != 5:
                        level = self.cogLevels[SuitDNA.suitDepts.index(SuitDNA.getSuitDept(self.suit.style.name))] + 1
                        self.cog = ToontownAvatarUtils.createDistributedCog(self.suit.style.name, 0, 0, 0.025, self.getH() - self.getH() * 3, 0, 0, parent=hidden, level=level, dept=dept, isSkelecog=self.suit.isSkeleton, isWaiter=self.suit.isWaiter, isVirtual=self.suit.isVirtuallyVirtual, colorType=self.nametag.colorCode)
                        toonId = 0
                    else:
                        self.toon = ToontownAvatarUtils.createUniqueToon(self.getName(), self.style.asTuple(), self.hat, self.glasses, self.backpack, self.shoes, 0, 0, 0.025, self.getH() - self.getH() * 3, 0, 0, parent=hidden, isDisguised=True, suitType=self.suit.style.name, isWaiter=self.suit.isWaiter, isRental=self.suit.isRental, colorType=self.nametag.colorCode, cogLevels=self.getCogLevels(), cheesyEffect=self.cheesyEffect)
                else:
                    self.toon = ToontownAvatarUtils.createUniqueToon(self.getName(), self.style.asTuple(), self.hat, self.glasses, self.backpack, self.shoes, self.getX(), self.getY(), self.getZ(), self.getH(), 0, 0, parent=hidden, colorType=self.nametag.colorCode, cheesyEffect=self.cheesyEffect, nametagStyle=self.nametagStyle)
            else:
                if toonId != 0:
                    self.toon = ToontownAvatarUtils.createToon(toonId, self.getX(), self.getY(), self.getZ(), self.getH(), 0, 0, parent=hidden)
                else:
                    if cogType == 'panda':
                        self.panda = Actor.Actor('phase_3/models/char/panda', {'walk': 'phase_3/models/char/panda-walk'})
                        self.panda.setPosHpr(self.getX(), self.getY(), self.getZ(), self.getH() - 180, 0, 0)
                        self.panda.setScale(0.5)
                        self.panda.setBlend(frameBlend=config.GetBool('interpolate-animations', True))
                        self.nodiiii = NodePath('boober')
                        self.nodiiii.setPosHpr(self.getX(), self.getY(), self.getZ(), self.getH() - 180, 0, 0)
                    else:
                        if cogType != 'ty':
                            self.cog = ToontownAvatarUtils.createDistributedCog(cogType, 0, 0, 0.025, self.getH() - self.getH() * 3, 0, 0, parent=hidden, level=level, dept=dept)
                        else:
                            self.cog = ToontownAvatarUtils.createCog(cogType, 0, 0, 0.025, self.getH() - self.getH() * 3, 0, 0, parent=hidden, level=level, dept=dept)
            if cogType == 'panda':
                self.panda.setTransparency(1)
            else:
                if toonId == 0:
                    self.cog.setTransparency(1)
                else:
                    self.toon.setTransparency(1)
            if toonId != 0:
                if self.toon.isDisguised:
                    self.cogFlyIn = self.toon.getSuitTeleport(moveIn=1, greenPos=(self.getX(), self.getY(), self.getZ()))
                else:
                    self.toonTeleportIn = Sequence(Func(self.toon.animFSM.request, 'TeleportIn'), Wait(1.517), Func(self.toon.animFSM.request, 'neutral'))
            else:
                if cogType == 'panda':
                    pass
                else:
                    if cogType != 'ty':
                        self.cogFlyIn = self.cog.beginSupaFlyMove(VBase3(self.getX() + 1.69, self.getY() + 1.69, self.getZ()), 1, 'flyIn', walkAfterLanding=False)
        if cogType == 'cag':
            button = loader.loadModel('phase_3.5/models/props/button.bam')
            pressingButton = loader.loadSfx('phase_5/audio/sfx/SA_pressing_button.ogg')
            pressingButton.setVolume(1.0)
            suitTrack = Sequence(Parallel(Sequence(Func(button.reparentTo, self.cog.find('**/joint_Lhold')), Func(button.setPosHpr, 0, 0.2, 0, 0, 0, 180), Func(button.setScale, 0), button.scaleInterval(0.5, Point3(1, 1, 1)), Wait(3.5), button.scaleInterval(0.5, Point3(0, 0, 0)), Func(button.reparentTo, hidden)), Sequence(Wait(1.25), Func(base.playSfx, pressingButton, node=self.cog)), Sequence(ActorInterval(self.cog, 'phone', endFrame=24), ActorInterval(self.cog, 'phone', startFrame=50))))
            green = Sequence(Parallel(Func(self.cog.reparentTo, render), Func(self.cog.addActive)), Func(self.cogFlyIn.start), Wait(5), Func(self.cog.setChatAbsolute, 'What does this button do?', CFSpeech | CFTimeout), Func(suitTrack.start), Wait(suitTrack.getDuration()), Func(self.cog.loop, 'neurtal'), Wait(1), Func(self.cog.setChatAbsolute, 'Well, that just escalated quickly...', CFSpeech | CFTimeout), Func(self.magicGreenByeBye, self.cog))
        else:
            if cogType == 'bfs':
                green = Sequence(Parallel(Func(self.cog.reparentTo, render), Func(self.cog.addActive)), Func(self.cogFlyIn.start), Wait(5), Func(self.cog.setChatAbsolute, 'FLEX.', CFSpeech | CFTimeout), ActorInterval(self.cog, 'glower'), Func(self.cog.setChatAbsolute, 'FLEX.', CFSpeech | CFTimeout), ActorInterval(self.cog, 'effort', startFrame=80), Func(self.cog.setChatAbsolute, 'FLEX.', CFSpeech | CFTimeout), ActorInterval(self.cog, 'victory', playRate=2), Func(self.cog.loop, 'neutral'), Wait(1), Func(self.cog.setChatAbsolute, 'Do you even lift?', CFSpeech | CFTimeout), Func(self.magicGreenByeBye, self.cog))
            else:
                if cogType == 'ty':
                    fadingOn = loader.loadSfx('phase_14.5/audio/sfx/appearing_from_nowhere.ogg')
                    fadingOff = loader.loadSfx('phase_14.5/audio/sfx/disappearing_from_now_on.ogg')
                    green = Sequence(Parallel(Func(self.cog.reparentTo, render), Func(self.cog.addActive)), Func(self.cog.setPos, self.getX() + 1.69, self.getY() + 1.69, self.getZ()), Func(self.cog.setTransparency, True), Func(self.cog.setColorScale, 1, 1, 1, 0), Func(self.cog.loop, 'neutral'), Func(base.playSfx, fadingOn, node=self.cog), self.cog.colorScaleInterval(5, VBase4(1, 1, 1, 1)), Func(self.cog.setChatAbsolute, 'You will not be spared.', CFSpeech | CFTimeout), ActorInterval(self.cog, 'finger-wag'), Func(self.cog.loop, 'neutral'), Wait(1), Func(base.playSfx, fadingOff, node=self.cog), self.cog.colorScaleInterval(5, VBase4(1, 1, 1, 0)), Func(self.cog.setTransparency, False), Parallel(Func(self.cog.reparentTo, hidden), Func(self.cog.removeActive)))
                else:
                    if cogType in ('sellbots', 'cashbots', 'lawbots', 'bossbots', 'hackerbots'):
                        for cog in self.cogs:
                            cogFlyIn = self.flyIns[x]
                            green = Sequence(Parallel(Func(cog.reparentTo, render), Func(cog.addActive)), Func(cogFlyIn.start), Wait(5), Func(cog.setChatAbsolute, 'Time to make a new Toon.', CFSpeech | CFTimeout), ActorInterval(cog, 'victory'), Func(cog.loop, 'neutral'), Wait(1), Func(self.magicGreenByeBye, cog))
                            green.start()
                            x += 1

                    else:
                        if toonId != 0:
                            if self.toon.style.getAnimal() == 'bear':
                                angryToonSFX = loader.loadSfx('phase_3.5/audio/dial/AV_bear_exclaim.ogg')
                            else:
                                angryToonSFX = loader.loadSfx('phase_3.5/audio/sfx/avatar_emotion_angry.ogg')
                            if self.toon.isDisguised:
                                green = Sequence(Parallel(Func(self.toon.reparentTo, render), Func(self.toon.addActive)), Func(self.cogFlyIn.start), Wait(5), Func(self.toon.setChatAbsolute, 'Time to make a new Toon.', CFSpeech | CFTimeout), ActorInterval(self.toon.suit, 'victory'), Func(self.toon.suit.loop, 'neutral'), Wait(1), Func(self.magicGreenByeBye, self.toon, 1))
                            else:
                                green = Sequence(Parallel(Func(self.toon.reparentTo, render), Func(self.toon.addActive)), Func(self.toonTeleportIn.start), Wait(1.517), Func(self.toon.setChatAbsolute, 'You stink!', CFSpeech | CFTimeout), Parallel(Func(self.toon.headsUp, self), SoundInterval(angryToonSFX, loop=1, node=self.toon), Sequence(Func(self.toon.angryEyes), Func(self.toon.blinkEyes), ActorInterval(self.toon, 'angry'), Func(self.toon.normalEyes), Func(self.toon.blinkEyes), Func(self.toon.loop, 'neutral')), Wait(3)), Func(self.toon.setChatAbsolute, 'Time to make a new Toon!', CFSpeech | CFTimeout), ActorInterval(self.toon, 'hypnotize'), Func(self.magicGreenByeBye, self.toon, 1))
                        else:
                            if cogType == 'panda':
                                green = Sequence(Func(self.panda.reparentTo, render), Func(self.panda.loop, 'walk'), Parallel(LerpColorScaleInterval(self.panda, 1.0, colorScale=VBase4(1, 1, 1, 1), startColorScale=VBase4(1, 1, 1, 0)), LerpPosInterval(self.panda, 5.0, (0,
                                                                                                                                                                                                                                                                            -25,
                                                                                                                                                                                                                                                                            0), other=self.nodiiii), Sequence(Wait(4), LerpScaleInterval(self.panda, 1.0, 0))), Func(self.magicGreenByeBye, self.panda, 2))
                            else:
                                green = Sequence(Parallel(Func(self.cog.reparentTo, render), Func(self.cog.addActive)), Func(self.cogFlyIn.start), Wait(5), Func(self.cog.setChatAbsolute, 'Time to make a new Toon.', CFSpeech | CFTimeout), ActorInterval(self.cog, 'victory'), Func(self.cog.loop, 'neutral'), Wait(1), Func(self.magicGreenByeBye, self.cog))
        green.start()
        self.greenSequence = green
        return

    def finishGreenSequence(self):
        if self.greenSequence and self.greenSequence.isPlaying():
            self.greenSequence.finish()
        self.greenSequence = None
        return

    def magicTeleportRequest(self, requesterId):
        self.sendUpdate('magicTeleportResponse', [requesterId, base.cr.playGame.getPlaceId()])

    def magicTeleportInitiate(self, hoodId, zoneId):
        loaderId = ZoneUtil.getBranchLoaderName(zoneId)
        whereId = ZoneUtil.getToonWhereName(zoneId)
        if ZoneUtil.isDynamicZone(zoneId) and hoodId in [ToontownGlobals.BossbotHQ, ToontownGlobals.LawbotHQ, ToontownGlobals.CashbotHQ, ToontownGlobals.SellbotHQ]:
            whereId = 'cogHQBossBattle'
        if zoneId in [ToontownGlobals.BossbotLobby, ToontownGlobals.LawbotLobby, ToontownGlobals.CashbotLobby, ToontownGlobals.SellbotLobby, ToontownGlobals.LawbotOfficeExt]:
            how = 'walk'
        else:
            how = 'teleportIn'
        requestStatus = [
         {'loader': loaderId, 'where': whereId, 
            'how': how, 
            'hoodId': hoodId, 
            'zoneId': zoneId, 
            'shardId': None, 
            'avId': -1}]
        base.cr.playGame.getPlace().fsm.forceTransition('teleportOut', requestStatus)
        return

    def setImmortalMode(self, immortalMode):
        self.sendUpdate('setImmortalMode', [immortalMode])

    def stun(self, damage):
        if self == base.localAvatar:
            self.stunToon()

    def d_stun(self, damage):
        self.sendUpdate('squish', [damage])

    def b_stun(self, damage):
        if not self.isStunned and self.hp > 0:
            self.stun(damage)
            self.d_stun(damage)
            self.playDialogueForString('!')

    def rainbow(self):
        blue = (0.0, 0.0, 1.0, 1.0)
        green = (0.0, 1.0, 0.0, 1.0)
        red = (1.0, 0.0, 0.0, 1.0)
        yellow = (0.945, 0.957, 0.259, 1.0)
        orange = (0.898, 0.42, 0.024, 1.0)
        pink = (0.898, 0.027, 0.667, 1.0)
        self.rainbowSeq = Sequence(LerpColorScaleInterval(render, 0.5, green, blue), LerpColorScaleInterval(render, 0.5, red, green), LerpColorScaleInterval(render, 0.5, yellow, red), LerpColorScaleInterval(render, 0.5, orange, yellow), LerpColorScaleInterval(render, 0.5, pink, orange), LerpColorScaleInterval(render, 0.5, blue, pink))
        self.rainbowSeq.loop()

    def rainbowEnd(self):
        self.rainbowSeq.finish()
        render.clearColorScale()
        self.rainbowSeq = None
        return

    def setToonScale(self, scale):
        bigRipper = self.magicScale
        self.magicScale = scale
        self.resetHeight()
        self.getGeomNode().getChild(0).setScale(self.magicScale)
        if self.isDisguised:
            self.suitGeom.setScale(self.suitGeom.getScale() / bigRipper * self.magicScale)
        if self.isTransformed:
            self.charGeom.setScale(self.charGeom.getScale() / bigRipper * self.magicScale)
        if self.isBecomePet:
            self.petGeom.setScale(self.petGeom.getScale() / bigRipper * self.magicScale)
        if self.isGoon:
            self.goonGeom.setScale(self.goonGeom.getScale() / bigRipper * self.magicScale)
        if self.isBossCog:
            self.bossGeom.setScale(self.bossGeom.getScale() / bigRipper * self.magicScale)
        if self.animeChair:
            self.animeChair.setScale(self.animeChair.getScale() / bigRipper * self.magicScale)

    def setToonHallPanel(self, state):
        self.toonHallPanel = state

    def doTeleport(self, hood):
        place = base.cr.playGame.getPlace()
        if place:
            place.doTeleport(hood)

    def infoWarrior(self):
        webbrowser.open('https://www.infowars.com/')

    def fakeNews(self):
        webbrowser.open('https://www.msnbc.com/')
        webbrowser.open('https://www.cnn.com/')

    def playSound(self, sound, loop=0):
        soundWithExt = sound + '.ogg'
        bgmSearchPath = DSearchPath()
        bgmSearchPath.appendDirectory('/phase_3/audio/bgm')
        bgmSearchPath.appendDirectory('/phase_3.5/audio/bgm')
        bgmSearchPath.appendDirectory('/phase_4/audio/bgm')
        bgmSearchPath.appendDirectory('/phase_5.5/audio/bgm')
        bgmSearchPath.appendDirectory('/phase_6/audio/bgm')
        bgmSearchPath.appendDirectory('/phase_7/audio/bgm')
        bgmSearchPath.appendDirectory('/phase_8/audio/bgm')
        bgmSearchPath.appendDirectory('/phase_9/audio/bgm')
        bgmSearchPath.appendDirectory('/phase_10/audio/bgm')
        bgmSearchPath.appendDirectory('/phase_11/audio/bgm')
        bgmSearchPath.appendDirectory('/phase_12/audio/bgm')
        bgmSearchPath.appendDirectory('/phase_13/audio/bgm')
        bgmSearchPath.appendDirectory('/phase_14.5/audio/bgm')
        bgmSearchPath.appendDirectory('/phase_14.5/audio/bgm/eggs')
        dialSearchPath = DSearchPath()
        dialSearchPath.appendDirectory('/phase_3/audio/dial')
        dialSearchPath.appendDirectory('/phase_3.5/audio/dial')
        dialSearchPath.appendDirectory('/phase_4/audio/dial')
        dialSearchPath.appendDirectory('/phase_5.5/audio/dial')
        dialSearchPath.appendDirectory('/phase_6/audio/dial')
        dialSearchPath.appendDirectory('/phase_8/audio/dial')
        sfxSearchPath = DSearchPath()
        sfxSearchPath.appendDirectory('/phase_3/audio/sfx')
        sfxSearchPath.appendDirectory('/phase_3.5/audio/sfx')
        sfxSearchPath.appendDirectory('/phase_4/audio/sfx')
        sfxSearchPath.appendDirectory('/phase_5/audio/sfx')
        sfxSearchPath.appendDirectory('/phase_5.5/audio/sfx')
        sfxSearchPath.appendDirectory('/phase_6/audio/sfx')
        sfxSearchPath.appendDirectory('/phase_8/audio/sfx')
        sfxSearchPath.appendDirectory('/phase_9/audio/sfx')
        sfxSearchPath.appendDirectory('/phase_10/audio/sfx')
        sfxSearchPath.appendDirectory('/phase_11/audio/sfx')
        sfxSearchPath.appendDirectory('/phase_12/audio/sfx')
        sfxSearchPath.appendDirectory('/phase_13/audio/sfx')
        sfxSearchPath.appendDirectory('/phase_14.5/audio/sfx')
        filename = Filename(soundWithExt)
        found = vfs.resolveFilename(filename, bgmSearchPath)
        if found:
            music = base.loader.loadMusic(filename.getFullpath())
            base.playMusic(music, looping=loop, volume=0.8)
            if not music.getLoop():
                taskMgr.doMethodLater(music.length() + 1, self.playZoneMusic, self.taskName('play-zone-music'))
        else:
            found = vfs.resolveFilename(filename, dialSearchPath)
            if not found:
                found = vfs.resolveFilename(filename, sfxSearchPath)
            if not found:
                self.notify.warning('%s not found on:' % soundWithExt)
                print bgmSearchPath
                print dialSearchPath
                print sfxSearchPath
            else:
                sfx = base.loader.loadSfx(filename.getFullpath())
                base.playSfx(sfx, looping=loop, volume=0.8)

    def playZoneMusic(self, task):
        place = base.cr.playGame.getPlace()
        if place:
            base.playMusic(place.loader.music, looping=1, volume=0.8)
        return task.done

    def dingDing(self, timestamp):
        if self.trolleyDropSequence and self.trolleyDropSequence.isPlaying():
            return
        if not self.trolley:
            station = loader.loadModel('phase_4/models/modules/trolley_station_TT.bam')
            self.trolley = station.find('**/trolley_car')
            self.trolley.reparentTo(self)
            station.removeNode()
            self.trolley.setBillboardPointEye()
        self.dropSfx = loader.loadSfx('phase_5/audio/sfx/cogbldg_drop.ogg')
        self.landSfx = loader.loadSfx('phase_5/audio/sfx/AA_drop_boat_cog.ogg')
        self.trolleySfx = loader.loadSfx('phase_4/audio/sfx/MG_sfx_travel_game_bell_for_trolley.ogg')
        self.fadeSfx = loader.loadSfx('phase_4/audio/sfx/SZ_trolley_bell.ogg')
        self.trolley.setZ(250)
        self.trolleyDropSequence = Sequence(Func(base.playSfx, self.dropSfx), Parallel(self.trolley.scaleInterval(1, (1,
                                                                                                                      1,
                                                                                                                      1)), self.trolley.posInterval(7, (0,
                                                                                                                                                        0,
                                                                                                                                                        0))), Func(base.playSfx, self.landSfx), Func(base.playSfx, self.trolleySfx, 0, 1, 1.5), self.trolley.posInterval(0.1, (0,
                                                                                                                                                                                                                                                                               0,
                                                                                                                                                                                                                                                                               0.5)), self.trolley.posInterval(0.1, (0,
                                                                                                                                                                                                                                                                                                                     0,
                                                                                                                                                                                                                                                                                                                     0)), Wait(0.4), Func(base.playSfx, self.fadeSfx, 0, 1, 1.5), self.trolley.scaleInterval(1, (0,
                                                                                                                                                                                                                                                                                                                                                                                                                 0,
                                                                                                                                                                                                                                                                                                                                                                                                                 0)))
        ts = globalClockDelta.localElapsedTime(timestamp)
        self.trolleyDropSequence.start(ts)
        if self.isLocal():
            self.trolleyLocalSequence = Sequence(Wait(7), Func(self.b_setAnimState, 'Squish')).start(ts)

    def finishTrolleyDropSequence(self):
        if self.trolleyDropSequence and self.trolleyDropSequence.isPlaying():
            self.trolleyDropSequence.finish()
        if self.trolleyLocalSequence and self.trolleyLocalSequence.isPlaying():
            self.trolleyLocalSequence.finish()
        self.trolleyDropSequence = None
        self.trolleyLocalSequence = None
        if self.dropSfx:
            self.dropSfx = None
        if self.landSfx:
            self.landSfx = None
        if self.trolleySfx:
            self.trolleySfx = None
        if self.fadeSfx:
            self.fadeSfx = None
        return


@magicWord(category=CATEGORY_MODERATION)
def globaltp():
    toon = spellbook.getInvoker()
    zoneId = toon.zoneId
    spellbook.getInvoker().sendUpdate('setTeleportOverride', [1])
    base.localAvatar.setTeleportAccess([1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 11000, 12000, 13000])
    return 'Global teleport activated for the current session.'


@magicWord(category=CATEGORY_OVERRIDE)
def help():
    return "Refer to your Shticker Book for a list of all commands! Some may require server moderation privileges. Selecting a Toon, then using 2 '~' characters will target a command on them."


@magicWord(category=CATEGORY_MODERATION)
def sleep():
    if not base.localAvatar.neverSleep:
        base.localAvatar.disableSleeping()
        return 'Sleeping has been deactivated for the current session.'
    base.localAvatar.enableSleeping()
    return 'Sleeping has been activated for the current session.'


@magicWord(category=CATEGORY_GUI)
def gardenGame():
    base.localAvatar.game = GardenDropGame.GardenDropGame()


@magicWord(category=CATEGORY_MOBILITY)
def toonfest():
    toon = spellbook.getInvoker()
    zoneId = toon.zoneId
    spellbook.getInvoker().magicTeleportInitiate(7000, 7000)
    return 'On the way!'


@magicWord(category=CATEGORY_CHARACTERSTATS)
def rainbow():
    if base.localAvatar.rainbowSeq:
        base.localAvatar.rainbowEnd()
        return "Good bye rainbows, I'll never forget you."
    base.localAvatar.rainbow()
    return "Toontastic! There's rainbows everywhere!"