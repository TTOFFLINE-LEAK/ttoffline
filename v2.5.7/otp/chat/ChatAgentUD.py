from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from toontown.chat.TTWhiteList import TTWhiteList
from toontown.chat.TTBlackList import TTBlackList
from toontown.chat.TTSequenceList import TTSequenceList
from otp.distributed import OtpDoGlobals

class ChatAgentUD(DistributedObjectGlobalUD):
    notify = DirectNotifyGlobal.directNotify.newCategory('ChatAgentUD')

    def announceGenerate(self):
        DistributedObjectGlobalUD.announceGenerate(self)
        self.wantBlacklist = config.GetBool('want-blacklist', True)
        self.wantBlacklistSequence = config.GetBool('want-blacklist-sequence', True)
        self.wantWhitelist = config.GetBool('want-whitelist', True)
        if self.wantWhitelist:
            self.whiteList = TTWhiteList()
        if self.wantBlacklist:
            self.blackList = TTBlackList()
        if self.wantBlacklistSequence:
            self.sequenceList = TTSequenceList()
        self.chatMode2channel = {1: OtpDoGlobals.OTP_MOD_CHANNEL, 2: OtpDoGlobals.OTP_ADMIN_CHANNEL}
        self.chatMode2prefix = {1: '[MOD] ', 
           2: '[ADMIN] '}

    def chatMessage(self, message, chatMode):
        sender = self.air.getAvatarIdFromSender()
        if sender == 0:
            self.air.writeServerEvent('suspicious', accId=self.air.getAccountIdFromSender(), issue='Account sent chat without an avatar', message=message)
            return
        cleanMessage, modifications = self.cleanMessage(message)
        self.air.writeServerEvent('chat-said', avId=sender, chatMode=chatMode, msg=message, cleanMsg=cleanMessage)
        helloNeighbor = ''
        if chatMode != 0:
            helloNeighbor = str(chatMode) + 'trueGamerAAA' + str(chatMode)
            modifications = []
        DistributedAvatar = self.air.dclassesByName['DistributedAvatarUD']
        dg = DistributedAvatar.aiFormatUpdate('setTalk', sender, self.chatMode2channel.get(chatMode, sender), self.air.ourChannel, [
         0, 0, helloNeighbor, cleanMessage, modifications, 0])
        self.air.send(dg)

    def whisperMessage(self, receiverAvId, message):
        sender = self.air.getAvatarIdFromSender()
        if sender == 0:
            self.air.writeServerEvent('suspicious', accId=self.air.getAccountIdFromSender(), issue='Account sent chat without an avatar', message=message)
            return
        cleanMessage, modifications = self.cleanMessage(message)
        self.air.writeServerEvent('whisper-said', avId=sender, reciever=receiverAvId, msg=message, cleanMsg=cleanMessage)
        DistributedAvatar = self.air.dclassesByName['DistributedAvatarUD']
        dg = DistributedAvatar.aiFormatUpdate('setTalkWhisper', receiverAvId, receiverAvId, self.air.ourChannel, [
         sender, sender, '', cleanMessage, modifications, 0])
        self.air.send(dg)

    def sfWhisperMessage(self, receiverAvId, message):
        sender = self.air.getAvatarIdFromSender()
        if sender == 0:
            self.air.writeServerEvent('suspicious', accId=self.air.getAccountIdFromSender(), issue='Account sent chat without an avatar', message=message)
            return
        if config.GetBool('allow-secret-chat', True):
            cleanMessage, modifications = message, []
        else:
            cleanMessage, modifications = self.cleanMessage(message)
        self.air.writeServerEvent('sf-whisper-said', avId=sender, reciever=receiverAvId, msg=message, cleanMsg=cleanMessage)
        DistributedAvatar = self.air.dclassesByName['DistributedAvatarUD']
        dg = DistributedAvatar.aiFormatUpdate('setTalkWhisper', receiverAvId, receiverAvId, self.air.ourChannel, [
         sender, sender, '', cleanMessage, modifications, 0])
        self.air.send(dg)

    def cleanMessage(self, message):
        modifications = []
        if self.wantWhitelist:
            modifications += self.cleanWhitelist(message)
        cleanMessage = message
        if self.wantBlacklist:
            modifications += self.cleanBlacklist(cleanMessage)
        if self.wantBlacklistSequence:
            modifications += self.cleanSequences(cleanMessage)
        for modStart, modStop in modifications:
            cleanMessage = cleanMessage[:modStart] + '*' * (modStop - modStart + 1) + cleanMessage[modStop + 1:]

        return (
         cleanMessage, modifications)

    def cleanWhitelist(self, message):
        modifications = []
        words = message.split(' ')
        offset = 0
        for word in words:
            if word and not self.whiteList.isWord(word):
                modifications.append((offset, offset + len(word) - 1))
            offset += len(word) + 1

        return modifications

    def cleanBlacklist(self, message):
        modifications = []
        words = message.split(' ')
        offset = 0
        for word in words:
            if word and self.blackList.isWord(word):
                modifications.append((offset, offset + len(word) - 1))
            offset += len(word) + 1

        return modifications

    def cleanSequences(self, message):
        modifications = []
        offset = 0
        words = message.split()
        for wordit in xrange(len(words)):
            word = words[wordit].lower()
            seqlist = self.sequenceList.getList(word)
            if len(seqlist) > 0:
                for seqit in xrange(len(seqlist)):
                    sequence = seqlist[seqit]
                    splitseq = sequence.split()
                    if len(words) - (wordit + 1) >= len(splitseq):
                        cmplist = words[wordit + 1:]
                        del cmplist[len(splitseq):]
                        cmplist = [ word.lower() for word in cmplist ]
                        if cmp(cmplist, splitseq) == 0:
                            modifications.append((offset, offset + len(word) + len(sequence) - 1))

            offset += len(word) + 1

        return modifications