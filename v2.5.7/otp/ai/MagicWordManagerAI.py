from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.distributed.MsgTypes import CLIENTAGENT_EJECT
from direct.distributed.PyDatagram import PyDatagram
from otp.ai.MagicWordGlobal import *
from otp.avatar.DistributedPlayerAI import DistributedPlayerAI

class MagicWordManagerAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('MagicWordManagerAI')

    def sendMagicWord(self, word, targetId, execute, invoker=None):
        invokerId = self.air.getAvatarIdFromSender() if invoker is None else invoker
        invoker = self.air.doId2do.get(invokerId)
        if not invoker:
            self.sendUpdateToAvatarId(invokerId, 'sendMagicWordResponse', ['missing invoker'])
            return
        if invoker.getAdminAccess() < MINIMUM_MAGICWORD_ACCESS:
            self.air.writeServerEvent('suspicious', avId=invokerId, issue='Attempted to issue magic word: %s' % word)
            dg = PyDatagram()
            dg.addServerHeader(self.GetPuppetConnectionChannel(invokerId), self.air.ourChannel, CLIENTAGENT_EJECT)
            dg.addUint16(126)
            dg.addString('Magic Words are reserved for administrators only!')
            self.air.send(dg)
            return
        target = self.air.doId2do.get(targetId)
        if not target:
            self.sendUpdateToAvatarId(invokerId, 'sendMagicWordResponse', ['missing target'])
            return
        if execute:
            response = spellbook.process(invoker, target, word)
            if response[0]:
                self.sendUpdateToAvatarId(invokerId, 'sendMagicWordResponse', [response[0]])
        else:
            response = ('Client MW executed.', )
        targetAccess = 0 if not isinstance(target, DistributedPlayerAI) else target.getAdminAccess()
        redactedCommands = [
         'lacker', 'infowarrior', 'fakenews']
        if word:
            if word.split()[0].lower() in redactedCommands:
                self.air.writeServerEvent('magic-word', invokerId=invokerId, invokerAccess=invoker.getAdminAccess(), targetId=targetId, targetAccess=targetAccess, word='redacted', response='Magic word executed successfully!')
            elif word.split()[0].lower() == 'setgm':
                if len(word.split()) == 3:
                    newWord = '%s %s' % (word.split()[0], word.split()[1])
                else:
                    newWord = word
                self.air.writeServerEvent('magic-word', invokerId=invokerId, invokerAccess=invoker.getAdminAccess(), targetId=targetId, targetAccess=targetAccess, word=newWord, response=response[0])
            elif word.split()[0].lower() == 'setce':
                if len(word.split()) == 5:
                    newWord = '%s %s %s %s' % (word.split()[0], word.split()[1], word.split()[2], word.split()[3])
                else:
                    newWord = word
                self.air.writeServerEvent('magic-word', invokerId=invokerId, invokerAccess=invoker.getAdminAccess(), targetId=targetId, targetAccess=targetAccess, word=newWord, response=response[0])
            elif word.split()[0].lower() == 'setcogindex':
                if len(word.split()) == 4:
                    newWord = '%s %s %s' % (word.split()[0], word.split()[1], word.split()[2])
                else:
                    newWord = word
                self.air.writeServerEvent('magic-word', invokerId=invokerId, invokerAccess=invoker.getAdminAccess(), targetId=targetId, targetAccess=targetAccess, word=newWord, response=response[0])
            elif word.split()[0].lower() == 'invasion':
                if len(word.split()) == 6:
                    newWord = '%s %s %s %s %s' % (
                     word.split()[0], word.split()[1], word.split()[2], word.split()[3], word.split()[4])
                else:
                    newWord = word
                self.air.writeServerEvent('magic-word', invokerId=invokerId, invokerAccess=invoker.getAdminAccess(), targetId=targetId, targetAccess=targetAccess, word=newWord, response=response[0])
            elif word.split()[0].lower() == 'spawncog':
                if len(word.split()) == 5:
                    newWord = '%s %s %s %s' % (word.split()[0], word.split()[1], word.split()[2], word.split()[3])
                else:
                    newWord = word
                self.air.writeServerEvent('magic-word', invokerId=invokerId, invokerAccess=invoker.getAdminAccess(), targetId=targetId, targetAccess=targetAccess, word=newWord, response=response[0])
            elif word.split()[0].lower() == 'sethat':
                if len(word.split()) == 4:
                    newWord = '%s %s %s' % (word.split()[0], word.split()[1], word.split()[2])
                else:
                    newWord = word
                self.air.writeServerEvent('magic-word', invokerId=invokerId, invokerAccess=invoker.getAdminAccess(), targetId=targetId, targetAccess=targetAccess, word=newWord, response=response[0])
            else:
                self.air.writeServerEvent('magic-word', invokerId=invokerId, invokerAccess=invoker.getAdminAccess(), targetId=targetId, targetAccess=targetAccess, word=word, response=response[0])
        else:
            self.air.writeServerEvent('magic-word', invokerId=invokerId, invokerAccess=invoker.getAdminAccess(), targetId=targetId, targetAccess=targetAccess, word=word, response=response[0])
        return

    def sendGlobalMagicWord(self, word, execute, targetSelf):
        invokerId = self.air.getAvatarIdFromSender()
        invoker = self.air.doId2do.get(invokerId)
        if not invoker:
            self.sendUpdateToAvatarId(invokerId, 'sendMagicWordResponse', ['missing invoker'])
            return
        if invoker.getAdminAccess() < MINIMUM_MAGICWORD_ACCESS:
            self.air.writeServerEvent('suspicious', avId=invokerId, issue='Attempted to issue magic word: %s' % word)
            dg = PyDatagram()
            dg.addServerHeader(self.GetPuppetConnectionChannel(invokerId), self.air.ourChannel, CLIENTAGENT_EJECT)
            dg.addUint16(126)
            dg.addString('Magic Words are reserved for administrators only!')
            self.air.send(dg)
            return
        doIds = simbase.air.doId2do.keys()[:]
        for doId in doIds:
            do = simbase.air.doId2do.get(doId)
            if isinstance(do, DistributedPlayerAI) and do.isPlayerControlled() and (doId != invokerId or targetSelf):
                if not do:
                    self.sendUpdateToAvatarId(invokerId, 'sendMagicWordResponse', ['missing target'])
                    continue
                self.sendMagicWord(word, doId, execute, invokerId)