from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectGlobalAI import DistributedObjectGlobalAI
from direct.distributed.MsgTypes import CLIENTAGENT_EJECT
from direct.distributed.PyDatagram import PyDatagram
from otp.ai.MagicWordGlobal import *
from toontown.toon.DistributedToonAI import DistributedToonAI

class BanManagerAI(DistributedObjectGlobalAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('BanManagerAI')

    def __init__(self, air):
        DistributedObjectGlobalAI.__init__(self, air)
        self.air = air

    def b_banPlayer(self, avId, accountId, reason):
        self.d_sendAddNewBan(avId, accountId, reason)

    def d_sendAddNewBan(self, avId, accountId, reason):
        self.sendUpdate('addNewBan', [avId, accountId, reason])

    def b_kickPlayer(self, avId, reason):
        datagram = PyDatagram()
        datagram.addServerHeader(self.GetPuppetConnectionChannel(avId), self.air.ourChannel, CLIENTAGENT_EJECT)
        datagram.addUint16(155)
        datagram.addString(str(reason))
        self.air.send(datagram)


@magicWord(category=CATEGORY_MODERATION, types=[str])
def ban(reason='Not specified.'):
    target = spellbook.getTarget()
    invoker = spellbook.getInvoker()
    if target.getDoId() not in simbase.air.doId2do.keys() or invoker.getDoId() not in simbase.air.doId2do.keys():
        simbase.air.writeServerEvent('suspicious', issue='Invalid invoker: %s and target: %s when trying to ban them.' % (
         invoker.getDoId(), target.getDoId()))
        return 'Failed to ban avatar!'
    if not isinstance(target, DistributedToonAI) and not isinstance(invoker, DistributedToonAI):
        return 'You can only ban an avatar.'
    if target.getDoId() == invoker.getDoId():
        return "You can't ban yourself, %s" % target.getName()
    target.sendSetBan(reason=reason, target=target, invoker=invoker)
    return 'Banned %s!' % target.getName()


@magicWord(category=CATEGORY_MODERATION, types=[str])
def kick(reason='Not specified.'):
    target = spellbook.getTarget()
    invoker = spellbook.getInvoker()
    if target.getDoId() not in simbase.air.doId2do.keys() or invoker.getDoId() not in simbase.air.doId2do.keys():
        simbase.air.writeServerEvent('suspicious', issue='Invalid invoker: %s and target: %s when trying to kick them.' % (
         invoker.getDoId(), target.getDoId()))
        return 'Failed to kick avatar!'
    if not isinstance(target, DistributedToonAI) and not isinstance(invoker, DistributedToonAI):
        return 'You can only kick an avatar.'
    if target.getDoId() == invoker.getDoId():
        return "You can't kick yourself, %s" % target.getName()
    target.sendSetKick(reason=reason, target=target, invoker=invoker)
    return 'Kicked %s!' % target.getName()


@magicWord(category=CATEGORY_MODERATION, types=[str])
def getAvId():
    target = spellbook.getTarget()
    return target.getDoId()