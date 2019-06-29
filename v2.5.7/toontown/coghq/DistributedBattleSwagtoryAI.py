import random
from direct.directnotify import DirectNotifyGlobal
from otp.otpbase.PythonUtil import addListsByValue
from toontown.battle.BattleBase import *
from toontown.suit import SuitDNA
from toontown.toonbase import ToontownGlobals
import DistributedBattleFactoryAI

class DistributedBattleSwagtoryAI(DistributedBattleFactoryAI.DistributedBattleFactoryAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedBattleSwagtoryAI')

    def handleToonsWon(self, toons):
        for toon in toons:
            recovered, notRecovered = self.air.questManager.recoverItems(toon, self.suitsKilled, self.getTaskZoneId())
            self.toonItems[toon.doId][0].extend(recovered)
            self.toonItems[toon.doId][1].extend(notRecovered)
            meritArray = self.air.promotionMgr.recoverMerits(toon, self.suitsKilled, self.getTaskZoneId(), getFactoryMeritMultiplier(self.getTaskZoneId()))
            if toon.doId in self.helpfulToons:
                self.toonMerits[toon.doId] = addListsByValue(self.toonMerits[toon.doId], meritArray)
            else:
                self.notify.debug('toon %d not helpful, skipping merits' % toon.doId)
            if self.bossBattle:
                preferredDept = random.randrange(len(SuitDNA.suitDepts) - 1)
                typeWeights = ['single'] * 70 + ['invasion'] * 3
                preferredSummonType = random.choice(typeWeights)
                self.giveCogSummonReward(toon, preferredDept, preferredSummonType)

    def giveCogSummonReward(self, toon, prefDeptIndex, prefSummonType):
        cogLevel = SuitDNA.suitsPerDept - 1
        deptIndex = prefDeptIndex
        summonType = prefSummonType
        hasSummon = toon.hasParticularCogSummons(prefDeptIndex, cogLevel, prefSummonType)
        if hasSummon:
            self.notify.debug('trying to find another reward')
            if not toon.hasParticularCogSummons(prefDeptIndex, cogLevel, 'single'):
                summonType = 'single'
            elif not toon.hasParticularCogSummons(prefDeptIndex, cogLevel, 'invasion'):
                summonType = 'invasion'
            else:
                foundOne = False
                for curDeptIndex in range(len(SuitDNA.suitDepts) - 1):
                    if not toon.hasParticularCogSummons(curDeptIndex, cogLevel, prefSummonType):
                        deptIndex = curDeptIndex
                        foundOne = True
                        break
                    elif not toon.hasParticularCogSummons(curDeptIndex, cogLevel, 'single'):
                        deptIndex = curDeptIndex
                        summonType = 'single'
                        foundOne = True
                        break
                    elif not toon.hasParticularCogSummons(curDeptIndex, cogLevel, 'invasion'):
                        summonType = 'invasion'
                        deptIndex = curDeptIndex
                        foundOne = True
                        break

                possibleDeptIndex = range(len(SuitDNA.suitDepts) - 1)
                possibleSummonType = ['single', 'invasion']
                typeWeights = ['single'] * 70 + ['invasion'] * 3
                if not foundOne:
                    for i in range(5):
                        randomSummonType = random.choice(typeWeights)
                        randomDeptIndex = random.choice(possibleDeptIndex)
                        if not toon.hasParticularCogSummons(randomDeptIndex, cogLevel, randomSummonType):
                            foundOne = True
                            cogLevel = cogLevel
                            summonType = randomSummonType
                            deptIndex = randomDeptIndex
                            break

                for curType in possibleSummonType:
                    if foundOne:
                        break
                    for curDeptIndex in possibleDeptIndex:
                        if foundOne:
                            break
                        if not toon.hasParticularCogSummons(curDeptIndex, cogLevel, curType):
                            foundOne = True
                            cogLevel = cogLevel
                            summonType = curType
                            deptIndex = curDeptIndex

                if not foundOne:
                    cogLevel = None
                    summonType = None
                    deptIndex = None
        toon.assignNewCogSummons(cogLevel, summonType, deptIndex)
        rankNinesUnlocked = toon.getRankNinesUnlocked()
        if deptIndex and not rankNinesUnlocked[deptIndex]:
            rankNinesUnlocked[deptIndex] = 1
        toon.d_setRankNinesUnlocked(rankNinesUnlocked)
        if summonType == None:
            summonType = -1
        if deptIndex == None:
            deptIndex = -1
        self.sendUpdateToAvatarId(toon.doId, 'informAboutReward', [summonType, deptIndex])
        return