from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from toontown.chat.TTWhiteList import TTWhiteList

class TTOffChatManagerUD(DistributedObjectGlobalUD):
    notify = DirectNotifyGlobal.directNotify.newCategory('TTOffChatManagerUD')

    def __init__(self, air):
        DistributedObjectGlobalUD.__init__(self, air)
        self.wantWhiteList = False
        self.whiteList = None
        self.chatMgrDoIds = set()
        return

    def announceGenerate(self):
        DistributedObjectGlobalUD.announceGenerate(self)
        self.wantWhiteList = config.GetBool('want-whitelist', True)
        if self.wantWhiteList:
            self.whiteList = TTWhiteList()

    def chatMessage(self, message):
        accId = self.air.getAccountIdFromSender()
        if not accId:
            return
        avId = self.air.getAvatarIdFromSender()
        if not avId:
            self.air.writeServerEvent('suspicious', accId=accId, issue='Account sent chat without an avatar!', message=message)
            return

        def handleAvatar(dclass, fields):
            if dclass != self.air.dclassesByName['DistributedToonUD']:
                return
            senderName = fields['setName'][0]
            if self.wantWhiteList:
                filteredMessage, modifications = self.filterWhiteList(message)
            else:
                filteredMessage, modifications = message, []
            do = self.air.dclassesByName['DistributedAvatarUD']
            datagram = do.aiFormatUpdate('setTalk', avId, avId, self.air.ourChannel, [
             avId, accId, senderName, filteredMessage, modifications, 0, message])
            self.air.send(datagram)
            self.air.writeServerEvent('chat-message-said', avId=avId, message=message, filteredMessage=filteredMessage)

        self.air.dbInterface.queryObject(self.air.dbId, avId, handleAvatar)

    def whisperMessage(self, message, receiverAvId):
        accId = self.air.getAccountIdFromSender()
        if not accId:
            return
        avId = self.air.getAvatarIdFromSender()
        if not avId:
            self.air.writeServerEvent('suspicious', accId=accId, issue='Account sent chat without an avatar!', message=message)
            return

        def handleAvatar(dclass, fields):
            if dclass != self.air.dclassesByName['DistributedToonUD']:
                return
            senderName = fields['setName'][0]
            senderFriendsList = fields['setFriendsList'][0]
            if (receiverAvId, 1) in senderFriendsList:
                filteredMessage, modifications = message, []
            else:
                if self.wantWhiteList:
                    filteredMessage, modifications = self.filterWhiteList(message)
                else:
                    filteredMessage, modifications = message, []
            do = self.air.dclassesByName['DistributedAvatarUD']
            datagram = do.aiFormatUpdate('setTalkWhisper', receiverAvId, receiverAvId, self.air.ourChannel, [
             avId, accId, senderName, filteredMessage, modifications, 0, message])
            self.air.send(datagram)
            self.air.writeServerEvent('whisper-message-said', avId=avId, receiverAvId=receiverAvId, message=message, filteredMessage=filteredMessage)

        self.air.dbInterface.queryObject(self.air.dbId, avId, handleAvatar)

    def filterWhiteList(self, message):
        modifications = []
        words = message.split(' ')
        offset = 0
        i = 0
        for word in words:
            if word == '.' and len(words) == 1:
                pass
            else:
                if (word.startswith('.') or word.startswith('!')) and len(word) > 1 and i == 0:
                    modifications.append((offset + 1, offset + len(word) - 1))
                else:
                    if word and not self.whiteList.isWord(word):
                        modifications.append((offset, offset + len(word) - 1))
            offset += len(word) + 1
            i += 1

        filteredMessage = message
        for modStart, modStop in modifications:
            filteredMessage = filteredMessage[:modStart] + '*' * (modStop - modStart + 1) + filteredMessage[modStop + 1:]

        return (
         filteredMessage, modifications)

    def globalMessage(self, message):
        accId = self.air.getAccountIdFromSender()
        if not accId:
            return
        avId = self.air.getAvatarIdFromSender()
        if not avId:
            self.air.writeServerEvent('suspicious', accId=accId, issue='Account sent chat without an avatar!', message=message)
            return

        def handleAvatar(dclass, fields):
            if dclass != self.air.dclassesByName['DistributedToonUD']:
                return
            senderName = fields['setName'][0]
            if self.wantWhiteList:
                filteredMessage, modifications = self.filterWhiteList(message)
            else:
                filteredMessage, modifications = message, []
            self.sendUpdateToAllAI('receiveGlobalMessageUd2Ai', [senderName, filteredMessage])
            self.air.writeServerEvent('chat-message-said', avId=avId, message=message, filteredMessage=filteredMessage)

        self.air.dbInterface.queryObject(self.air.dbId, avId, handleAvatar)

    def addChatManager(self, doId):
        self.chatMgrDoIds.add(doId)

    def sendUpdateToAI(self, doId, field, args=[]):
        dg = self.dclass.aiFormatUpdate(field, doId, doId, self.doId, args)
        self.air.send(dg)

    def sendUpdateToAllAI(self, field, args=[]):
        for chatMgrDoId in self.chatMgrDoIds:
            self.sendUpdateToAI(chatMgrDoId, field, args)