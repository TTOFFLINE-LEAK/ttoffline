from BattleBase import *
from DistributedBattleAI import *
from toontown.toonbase.ToontownBattleGlobals import *
import random
from toontown.suit import DistributedSuitBaseAI
import SuitBattleGlobals, BattleExperienceAI
from toontown.toon import NPCToons
from toontown.pets import PetTricks, DistributedPetProxyAI
from direct.showbase.PythonUtil import lerp

class BattleCalculatorAI:
    AccuracyBonuses = [
     0, 20, 40, 60]
    DamageBonuses = [
     0, 20, 20, 20]
    AttackExpPerTrack = [
     0, 10, 20, 30, 40, 50, 60]
    NumRoundsLured = [
     2, 2, 3, 3, 4, 4, 15]
    TRAP_CONFLICT = -2
    APPLY_HEALTH_ADJUSTMENTS = 1
    TOONS_TAKE_NO_DAMAGE = 0
    CAP_HEALS = 1
    CLEAR_SUIT_ATTACKERS = 1
    SUITS_UNLURED_IMMEDIATELY = 1
    CLEAR_MULTIPLE_TRAPS = 0
    KBBONUS_LURED_FLAG = 0
    KBBONUS_TGT_LURED = 1
    notify = DirectNotifyGlobal.directNotify.newCategory('BattleCalculatorAI')
    toonsAlwaysHit = simbase.config.GetBool('toons-always-hit', 0)
    toonsAlwaysMiss = simbase.config.GetBool('toons-always-miss', 0)
    toonsAlways5050 = simbase.config.GetBool('toons-always-5050', 0)
    suitsAlwaysHit = simbase.config.GetBool('suits-always-hit', 0)
    suitsAlwaysMiss = simbase.config.GetBool('suits-always-miss', 0)
    immortalSuits = simbase.config.GetBool('immortal-suits', 0)
    propAndOrganicBonusStack = simbase.config.GetBool('prop-and-organic-bonus-stack', 0)

    def __init__(self, battle, tutorialFlag=0):
        self.battle = battle
        self.SuitAttackers = {}
        self.currentlyLuredSuits = {}
        self.successfulLures = {}
        self.toonAtkOrder = []
        self.toonHPAdjusts = {}
        self.toonSkillPtsGained = {}
        self.traps = {}
        self.npcTraps = {}
        self.suitAtkStats = {}
        self.__clearBonuses(hp=1)
        self.__clearBonuses(hp=0)
        self.delayedUnlures = []
        self.__skillCreditMultiplier = 1
        self.tutorialFlag = tutorialFlag
        self.trainTrapTriggered = False

    def setSkillCreditMultiplier(self, mult):
        self.__skillCreditMultiplier = mult

    def getSkillCreditMultiplier(self):
        return self.__skillCreditMultiplier

    def cleanup(self):
        self.battle = None
        return

    def __calcToonAtkHit(self, attackIndex, atkTargets):
        toon = self.battle.getToon(attackIndex)
        if len(atkTargets) == 0:
            return (0, 0)
        if toon.getInstaKill() or toon.getAlwaysHitSuits():
            return (1, 95)
        if self.tutorialFlag:
            return (1, 95)
        if self.toonsAlways5050:
            roll = random.randint(0, 99)
            if roll < 50:
                return (1, 95)
            return (0, 0)
        if self.toonsAlwaysHit:
            return (1, 95)
        if self.toonsAlwaysMiss:
            return (0, 0)
        debug = self.notify.getDebug()
        attack = self.battle.toonAttacks[attackIndex]
        atkTrack, atkLevel = self.__getActualTrackLevel(attack)
        if atkTrack == NPCSOS:
            return (1, 95)
        if atkTrack == FIRE:
            return (1, 95)
        if atkTrack == TRAP:
            if debug:
                self.notify.debug('Attack is a trap, so it hits regardless')
            attack[TOON_ACCBONUS_COL] = 0
            return (1, 100)
        if atkTrack == DROP and attack[TOON_TRACK_COL] == NPCSOS:
            unluredSuits = 0
            for tgt in atkTargets:
                if not self.__suitIsLured(tgt.getDoId()):
                    unluredSuits = 1

            if unluredSuits == 0:
                attack[TOON_ACCBONUS_COL] = 1
                return (0, 0)
        else:
            if atkTrack == DROP:
                allLured = True
                for i in xrange(len(atkTargets)):
                    if self.__suitIsLured(atkTargets[i].getDoId()):
                        pass
                    else:
                        allLured = False

                if toon.getAlwaysHitSuits():
                    return (1, 95)
                if allLured:
                    attack[TOON_ACCBONUS_COL] = 1
                    return (0, 0)
            else:
                if atkTrack == PETSOS:
                    return self.__calculatePetTrickSuccess(attack)
        tgtDef = 0
        numLured = 0
        if atkTrack != HEAL:
            for currTarget in atkTargets:
                thisSuitDef = self.__targetDefense(currTarget, atkTrack)
                if debug:
                    self.notify.debug('Examining suit def for toon attack: ' + str(thisSuitDef))
                tgtDef = min(thisSuitDef, tgtDef)
                if self.__suitIsLured(currTarget.getDoId()):
                    numLured += 1

        trackExp = self.__toonTrackExp(attack[TOON_ID_COL], atkTrack)
        for currOtherAtk in self.toonAtkOrder:
            if currOtherAtk != attack[TOON_ID_COL]:
                nextAttack = self.battle.toonAttacks[currOtherAtk]
                nextAtkTrack = self.__getActualTrack(nextAttack)
                if atkTrack == nextAtkTrack and attack[TOON_TGT_COL] == nextAttack[TOON_TGT_COL]:
                    currTrackExp = self.__toonTrackExp(nextAttack[TOON_ID_COL], atkTrack)
                    if debug:
                        self.notify.debug('Examining toon track exp bonus: ' + str(currTrackExp))
                    trackExp = max(currTrackExp, trackExp)

        if debug:
            if atkTrack == HEAL:
                self.notify.debug('Toon attack is a heal, no target def used')
            else:
                self.notify.debug('Suit defense used for toon attack: ' + str(tgtDef))
            self.notify.debug('Toon track exp bonus used for toon attack: ' + str(trackExp))
        if attack[TOON_TRACK_COL] == NPCSOS:
            randChoice = 0
        else:
            randChoice = random.randint(0, 99)
        propAcc = AvPropAccuracy[atkTrack][atkLevel]
        if atkTrack == LURE:
            treebonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)
            propBonus = self.__checkPropBonus(atkTrack)
            if self.propAndOrganicBonusStack:
                propAcc = 0
                if treebonus:
                    self.notify.debug('using organic bonus lure accuracy')
                    propAcc += AvLureBonusAccuracy[atkLevel]
                if propBonus:
                    self.notify.debug('using prop bonus lure accuracy')
                    propAcc += AvLureBonusAccuracy[atkLevel]
            elif treebonus or propBonus:
                self.notify.debug('using oragnic OR prop bonus lure accuracy')
                propAcc = AvLureBonusAccuracy[atkLevel]
        attackAcc = propAcc + trackExp + tgtDef
        currAtk = self.toonAtkOrder.index(attackIndex)
        if currAtk > 0 and atkTrack != HEAL:
            prevAtkId = self.toonAtkOrder[(currAtk - 1)]
            prevAttack = self.battle.toonAttacks[prevAtkId]
            prevAtkTrack = self.__getActualTrack(prevAttack)
            lure = atkTrack == LURE and (not attackAffectsGroup(atkTrack, atkLevel, attack[TOON_TRACK_COL]) and attack[TOON_TGT_COL] in self.successfulLures or attackAffectsGroup(atkTrack, atkLevel, attack[TOON_TRACK_COL]))
            if atkTrack == prevAtkTrack and (attack[TOON_TGT_COL] == prevAttack[TOON_TGT_COL] or lure):
                if prevAttack[TOON_ACCBONUS_COL] == 1:
                    if debug:
                        self.notify.debug('DODGE: Toon attack track dodged')
                else:
                    if prevAttack[TOON_ACCBONUS_COL] == 0:
                        if debug:
                            self.notify.debug('HIT: Toon attack track hit')
                attack[TOON_ACCBONUS_COL] = prevAttack[TOON_ACCBONUS_COL]
                return (
                 not attack[TOON_ACCBONUS_COL], attackAcc)
        atkAccResult = attackAcc
        if debug:
            self.notify.debug('setting atkAccResult to %d' % atkAccResult)
        acc = attackAcc + self.__calcToonAccBonus(attackIndex)
        if atkTrack != LURE and atkTrack != HEAL:
            if atkTrack != DROP:
                if numLured == len(atkTargets):
                    if debug:
                        self.notify.debug('all targets are lured, attack hits')
                    attack[TOON_ACCBONUS_COL] = 0
                    return (1, 100)
                luredRatio = float(numLured) / float(len(atkTargets))
                accAdjust = 100 * luredRatio
                if accAdjust > 0 and debug:
                    self.notify.debug(str(numLured) + ' out of ' + str(len(atkTargets)) + ' targets are lured, so adding ' + str(accAdjust) + ' to attack accuracy')
                acc += accAdjust
            else:
                if numLured == len(atkTargets):
                    if debug:
                        self.notify.debug('all targets are lured, attack misses')
                    attack[TOON_ACCBONUS_COL] = 0
                    return (0, 0)
        if acc > MaxToonAcc:
            acc = MaxToonAcc
        if randChoice < acc:
            if debug:
                self.notify.debug('HIT: Toon attack rolled' + str(randChoice) + 'to hit with an accuracy of' + str(acc))
            attack[TOON_ACCBONUS_COL] = 0
        else:
            if debug:
                self.notify.debug('MISS: Toon attack rolled' + str(randChoice) + 'to hit with an accuracy of' + str(acc))
            attack[TOON_ACCBONUS_COL] = 1
        return (not attack[TOON_ACCBONUS_COL], atkAccResult)

    def __toonTrackExp(self, toonId, track):
        toon = self.battle.getToon(toonId)
        if toon != None:
            toonExpLvl = toon.experience.getExpLevel(track)
            exp = self.AttackExpPerTrack[toonExpLvl]
            if track == HEAL:
                exp = exp * 0.5
            self.notify.debug('Toon track exp: ' + str(toonExpLvl) + ' and resulting acc bonus: ' + str(exp))
            return exp
        return 0
        return

    def __toonCheckGagBonus(self, toonId, track, level):
        toon = self.battle.getToon(toonId)
        if toon != None:
            return toon.checkGagBonus(track, level)
        return False
        return

    def __checkPropBonus(self, track):
        result = False
        if self.battle.getInteractivePropTrackBonus() == track:
            result = True
        return result

    def __targetDefense(self, suit, atkTrack):
        if atkTrack == HEAL:
            return 0
        suitDef = SuitBattleGlobals.SuitAttributes[suit.dna.name]['def'][suit.getLevel()]
        return -suitDef

    def __createToonTargetList(self, attackIndex):
        attack = self.battle.toonAttacks[attackIndex]
        atkTrack, atkLevel = self.__getActualTrackLevel(attack)
        targetList = []
        if atkTrack == NPCSOS:
            return targetList
        if not attackAffectsGroup(atkTrack, atkLevel, attack[TOON_TRACK_COL]):
            if atkTrack == HEAL:
                target = attack[TOON_TGT_COL]
            else:
                target = self.battle.findSuit(attack[TOON_TGT_COL])
            if target != None:
                targetList.append(target)
        else:
            if atkTrack == HEAL or atkTrack == PETSOS:
                if attack[TOON_TRACK_COL] == NPCSOS or atkTrack == PETSOS:
                    targetList = self.battle.activeToons
                else:
                    for currToon in self.battle.activeToons:
                        if attack[TOON_ID_COL] != currToon:
                            targetList.append(currToon)

            else:
                targetList = self.battle.activeSuits
        return targetList

    def __prevAtkTrack(self, attackerId, toon=1):
        if toon:
            prevAtkIdx = self.toonAtkOrder.index(attackerId) - 1
            if prevAtkIdx >= 0:
                prevAttackerId = self.toonAtkOrder[prevAtkIdx]
                attack = self.battle.toonAttacks[prevAttackerId]
                return self.__getActualTrack(attack)
            return NO_ATTACK

    def getSuitTrapType(self, suitId):
        if suitId in self.traps:
            if self.traps[suitId][0] == self.TRAP_CONFLICT:
                return NO_TRAP
            return self.traps[suitId][0]
        else:
            return NO_TRAP

    def __suitTrapDamage(self, suitId):
        if suitId in self.traps:
            return self.traps[suitId][2]
        return 0

    def addTrainTrapForJoiningSuit(self, suitId):
        self.notify.debug('addTrainTrapForJoiningSuit suit=%d self.traps=%s' % (suitId, self.traps))
        trapInfoToUse = None
        for trapInfo in self.traps.values():
            if trapInfo[0] == UBER_GAG_LEVEL_INDEX:
                trapInfoToUse = trapInfo
                break

        if trapInfoToUse:
            self.traps[suitId] = trapInfoToUse
        else:
            self.notify.warning('huh we did not find a train trap?')
        return

    def __addSuitGroupTrap(self, suitId, trapLvl, attackerId, allSuits, npcDamage=0):
        if npcDamage == 0:
            if suitId in self.traps:
                if self.traps[suitId][0] == self.TRAP_CONFLICT:
                    pass
                else:
                    self.traps[suitId][0] = self.TRAP_CONFLICT
                for suit in allSuits:
                    id = suit.doId
                    if id in self.traps:
                        self.traps[id][0] = self.TRAP_CONFLICT
                    else:
                        self.traps[id] = [
                         self.TRAP_CONFLICT, 0, 0]

            else:
                toon = self.battle.getToon(attackerId)
                organicBonus = toon.checkGagBonus(TRAP, trapLvl)
                propBonus = self.__checkPropBonus(TRAP)
                damage = getAvPropDamage(TRAP, trapLvl, toon.experience.getExp(TRAP), organicBonus, propBonus, self.propAndOrganicBonusStack)
                if self.itemIsCredit(TRAP, trapLvl):
                    self.traps[suitId] = [trapLvl, attackerId, damage]
                else:
                    self.traps[suitId] = [
                     trapLvl, 0, damage]
                self.notify.debug('calling __addLuredSuitsDelayed')
                self.__addLuredSuitsDelayed(attackerId, targetId=-1, ignoreDamageCheck=True)
        else:
            if suitId in self.traps:
                if self.traps[suitId][0] == self.TRAP_CONFLICT:
                    self.traps[suitId] = [trapLvl, 0, npcDamage]
            else:
                if not self.__suitIsLured(suitId):
                    self.traps[suitId] = [trapLvl, 0, npcDamage]

    def __addSuitTrap(self, suitId, trapLvl, attackerId, npcDamage=0):
        if npcDamage == 0:
            if suitId in self.traps:
                if self.traps[suitId][0] == self.TRAP_CONFLICT:
                    pass
                else:
                    self.traps[suitId][0] = self.TRAP_CONFLICT
            else:
                toon = self.battle.getToon(attackerId)
                organicBonus = toon.checkGagBonus(TRAP, trapLvl)
                propBonus = self.__checkPropBonus(TRAP)
                damage = getAvPropDamage(TRAP, trapLvl, toon.experience.getExp(TRAP), organicBonus, propBonus, self.propAndOrganicBonusStack)
                if self.itemIsCredit(TRAP, trapLvl):
                    self.traps[suitId] = [trapLvl, attackerId, damage]
                else:
                    self.traps[suitId] = [
                     trapLvl, 0, damage]
        else:
            if suitId in self.traps:
                if self.traps[suitId][0] == self.TRAP_CONFLICT:
                    self.traps[suitId] = [trapLvl, 0, npcDamage]
            else:
                if not self.__suitIsLured(suitId):
                    self.traps[suitId] = [trapLvl, 0, npcDamage]

    def __removeSuitTrap(self, suitId):
        if suitId in self.traps:
            del self.traps[suitId]

    def __clearTrapCreator(self, creatorId, suitId=None):
        if suitId == None:
            for currTrap in self.traps.keys():
                if creatorId == self.traps[currTrap][1]:
                    self.traps[currTrap][1] = 0

        else:
            if suitId in self.traps:
                self.traps[suitId][1] = 0
        return

    def __trapCreator(self, suitId):
        if suitId in self.traps:
            return self.traps[suitId][1]
        return 0

    def __initTraps(self):
        self.trainTrapTriggered = False
        keysList = self.traps.keys()
        for currTrap in keysList:
            if self.traps[currTrap][0] == self.TRAP_CONFLICT:
                del self.traps[currTrap]

    def __calcToonAtkHp(self, toonId):
        attack = self.battle.toonAttacks[toonId]
        targetList = self.__createToonTargetList(toonId)
        atkHit, atkAcc = self.__calcToonAtkHit(toonId, targetList)
        atkTrack, atkLevel, atkHp = self.__getActualTrackLevelHp(attack)
        if not atkHit and atkTrack != HEAL:
            return
        validTargetAvail = 0
        lureDidDamage = 0
        currLureId = -1
        for currTarget in xrange(len(targetList)):
            attackLevel = -1
            attackTrack = None
            attackDamage = 0
            toonTarget = 0
            targetLured = 0
            if atkTrack == HEAL or atkTrack == PETSOS:
                targetId = targetList[currTarget]
                toonTarget = 1
            else:
                targetId = targetList[currTarget].getDoId()
            if atkTrack == LURE:
                if self.getSuitTrapType(targetId) == NO_TRAP:
                    if self.notify.getDebug():
                        self.notify.debug('Suit lured, but no trap exists')
                    if self.SUITS_UNLURED_IMMEDIATELY:
                        if not self.__suitIsLured(targetId, prevRound=1):
                            if not self.__combatantDead(targetId, toon=toonTarget):
                                validTargetAvail = 1
                            rounds = self.NumRoundsLured[atkLevel]
                            wakeupChance = 100 - atkAcc * 2
                            npcLurer = attack[TOON_TRACK_COL] == NPCSOS
                            currLureId = self.__addLuredSuitInfo(targetId, -1, rounds, wakeupChance, toonId, atkLevel, lureId=currLureId, npc=npcLurer)
                            if self.notify.getDebug():
                                self.notify.debug('Suit lured for ' + str(rounds) + ' rounds max with ' + str(wakeupChance) + '% chance to wake up each round')
                            targetLured = 1
                else:
                    attackTrack = TRAP
                    if targetId in self.traps:
                        trapInfo = self.traps[targetId]
                        attackLevel = trapInfo[0]
                    else:
                        attackLevel = NO_TRAP
                    attackDamage = self.__suitTrapDamage(targetId)
                    trapCreatorId = self.__trapCreator(targetId)
                    if trapCreatorId > 0:
                        self.notify.debug('Giving trap EXP to toon ' + str(trapCreatorId))
                        self.__addAttackExp(attack, track=TRAP, level=attackLevel, attackerId=trapCreatorId)
                    self.__clearTrapCreator(trapCreatorId, targetId)
                    lureDidDamage = 1
                    if self.notify.getDebug():
                        self.notify.debug('Suit lured right onto a trap! (' + str(AvProps[attackTrack][attackLevel]) + ',' + str(attackLevel) + ')')
                    if not self.__combatantDead(targetId, toon=toonTarget):
                        validTargetAvail = 1
                    targetLured = 1
                if not self.SUITS_UNLURED_IMMEDIATELY:
                    if not self.__suitIsLured(targetId, prevRound=1):
                        if not self.__combatantDead(targetId, toon=toonTarget):
                            validTargetAvail = 1
                        rounds = self.NumRoundsLured[atkLevel]
                        wakeupChance = 100 - atkAcc * 2
                        npcLurer = attack[TOON_TRACK_COL] == NPCSOS
                        currLureId = self.__addLuredSuitInfo(targetId, -1, rounds, wakeupChance, toonId, atkLevel, lureId=currLureId, npc=npcLurer)
                        if self.notify.getDebug():
                            self.notify.debug('Suit lured for ' + str(rounds) + ' rounds max with ' + str(wakeupChance) + '% chance to wake up each round')
                        targetLured = 1
                    if attackLevel != -1:
                        self.__addLuredSuitsDelayed(toonId, targetId)
                if targetLured and (targetId not in self.successfulLures or targetId in self.successfulLures and self.successfulLures[targetId][1] < atkLevel):
                    self.notify.debug('Adding target ' + str(targetId) + ' to successfulLures list')
                    self.successfulLures[targetId] = [
                     toonId, atkLevel, atkAcc, -1]
            else:
                if atkTrack == TRAP:
                    npcDamage = 0
                    if attack[TOON_TRACK_COL] == NPCSOS:
                        npcDamage = atkHp
                    if self.CLEAR_MULTIPLE_TRAPS:
                        if self.getSuitTrapType(targetId) != NO_TRAP:
                            self.__clearAttack(toonId)
                            return
                    if atkLevel == UBER_GAG_LEVEL_INDEX:
                        self.__addSuitGroupTrap(targetId, atkLevel, toonId, targetList, npcDamage)
                        if self.__suitIsLured(targetId):
                            self.notify.debug('Train Trap on lured suit %d, \n indicating with KBBONUS_COL flag' % targetId)
                            tgtPos = self.battle.activeSuits.index(targetList[currTarget])
                            attack[TOON_KBBONUS_COL][tgtPos] = self.KBBONUS_LURED_FLAG
                    else:
                        self.__addSuitTrap(targetId, atkLevel, toonId, npcDamage)
                else:
                    if self.__suitIsLured(targetId) and atkTrack == SOUND:
                        self.notify.debug('Sound on lured suit, ' + 'indicating with KBBONUS_COL flag')
                        tgtPos = self.battle.activeSuits.index(targetList[currTarget])
                        attack[TOON_KBBONUS_COL][tgtPos] = self.KBBONUS_LURED_FLAG
                attackLevel = atkLevel
                attackTrack = atkTrack
                toon = self.battle.getToon(toonId)
                if attack[TOON_TRACK_COL] == NPCSOS and lureDidDamage != 1 or attack[TOON_TRACK_COL] == PETSOS:
                    attackDamage = atkHp
                else:
                    if atkTrack == FIRE:
                        suit = self.battle.findSuit(targetId)
                        if suit:
                            costToFire = 1
                            abilityToFire = toon.getPinkSlips()
                            toon.removePinkSlips(costToFire)
                            if costToFire > abilityToFire:
                                commentStr = 'Toon attempting to fire a %s cost cog with %s pinkslips' % (costToFire, abilityToFire)
                                simbase.air.writeServerEvent('suspicious', toonId, commentStr)
                                dislId = toon.DISLid
                                simbase.air.banManager.ban(toonId, dislId, commentStr)
                                print 'Not enough PinkSlips to fire cog - print a warning here'
                            else:
                                suit.skeleRevives = 0
                                attackDamage = suit.getHP()
                        else:
                            attackDamage = 0
                        bonus = 0
                    else:
                        organicBonus = toon.checkGagBonus(attackTrack, attackLevel)
                        propBonus = self.__checkPropBonus(attackTrack)
                        attackDamage = getAvPropDamage(attackTrack, attackLevel, toon.experience.getExp(attackTrack), organicBonus, propBonus, self.propAndOrganicBonusStack)
                if not self.__combatantDead(targetId, toon=toonTarget):
                    if self.__suitIsLured(targetId) and atkTrack == DROP and not toon.getAlwaysHitSuits():
                        self.notify.debug('not setting validTargetAvail, since drop on a lured suit')
                    else:
                        validTargetAvail = 1
            if attackLevel == -1 and not atkTrack == FIRE:
                result = LURE_SUCCEEDED
            else:
                if atkTrack != TRAP:
                    toon = self.battle.getToon(toonId)
                    if toon and toon.getInstaKill() and atkTrack != HEAL:
                        attackDamage = suit = self.battle.findSuit(targetId).getHP()
                    result = attackDamage
                    if atkTrack == HEAL:
                        if not self.__attackHasHit(attack, suit=0):
                            result = result * 0.2
                        if self.notify.getDebug():
                            self.notify.debug('toon does ' + str(result) + ' healing to toon(s)')
                    else:
                        if self.__suitIsLured(targetId) and atkTrack == DROP and not toon.getAlwaysHitSuits():
                            result = 0
                            self.notify.debug('setting damage to 0, since drop on a lured suit')
                        if self.notify.getDebug():
                            self.notify.debug('toon does ' + str(result) + ' damage to suit')
                else:
                    result = 0
            if result != 0 or atkTrack == PETSOS:
                targets = self.__getToonTargets(attack)
                if targetList[currTarget] not in targets:
                    if self.notify.getDebug():
                        self.notify.debug('Target of toon is not accessible!')
                    continue
                targetIndex = targets.index(targetList[currTarget])
                if atkTrack == HEAL:
                    result = result / len(targetList)
                    if self.notify.getDebug():
                        self.notify.debug('Splitting heal among ' + str(len(targetList)) + ' targets')
                if targetId in self.successfulLures and atkTrack == LURE:
                    self.notify.debug('Updating lure damage to ' + str(result))
                    self.successfulLures[targetId][3] = result
                else:
                    attack[TOON_HP_COL][targetIndex] = result
                if result > 0 and atkTrack != HEAL and atkTrack != DROP and atkTrack != PETSOS:
                    attackTrack = LURE
                    lureInfos = self.__getLuredExpInfo(targetId)
                    for currInfo in lureInfos:
                        if currInfo[3]:
                            self.notify.debug('Giving lure EXP to toon ' + str(currInfo[0]))
                            self.__addAttackExp(attack, track=attackTrack, level=currInfo[1], attackerId=currInfo[0])
                        self.__clearLurer(currInfo[0], lureId=currInfo[2])

        if lureDidDamage:
            if self.itemIsCredit(atkTrack, atkLevel):
                self.notify.debug('Giving lure EXP to toon ' + str(toonId))
                self.__addAttackExp(attack)
        if not validTargetAvail and self.__prevAtkTrack(toonId) != atkTrack:
            self.__clearAttack(toonId)
        return

    def __getToonTargets(self, attack):
        track = self.__getActualTrack(attack)
        if track == HEAL or track == PETSOS:
            return self.battle.activeToons
        return self.battle.activeSuits

    def __attackHasHit(self, attack, suit=0):
        if suit == 1:
            for dmg in attack[SUIT_HP_COL]:
                if dmg > 0:
                    return 1

            return 0
        track = self.__getActualTrack(attack)
        return not attack[TOON_ACCBONUS_COL] and track != NO_ATTACK

    def __attackDamage(self, attack, suit=0):
        if suit:
            for dmg in attack[SUIT_HP_COL]:
                if dmg > 0:
                    return dmg

            return 0
        for dmg in attack[TOON_HP_COL]:
            if dmg > 0:
                return dmg

        return 0

    def __attackDamageForTgt(self, attack, tgtPos, suit=0):
        if suit:
            return attack[SUIT_HP_COL][tgtPos]
        return attack[TOON_HP_COL][tgtPos]

    def __calcToonAccBonus(self, attackKey):
        numPrevHits = 0
        attackIdx = self.toonAtkOrder.index(attackKey)
        for currPrevAtk in xrange(attackIdx - 1, -1, -1):
            attack = self.battle.toonAttacks[attackKey]
            atkTrack, atkLevel = self.__getActualTrackLevel(attack)
            prevAttackKey = self.toonAtkOrder[currPrevAtk]
            prevAttack = self.battle.toonAttacks[prevAttackKey]
            prvAtkTrack, prvAtkLevel = self.__getActualTrackLevel(prevAttack)
            if self.__attackHasHit(prevAttack) and (attackAffectsGroup(prvAtkTrack, prvAtkLevel, prevAttack[TOON_TRACK_COL]) or attackAffectsGroup(atkTrack, atkLevel, attack[TOON_TRACK_COL]) or attack[TOON_TGT_COL] == prevAttack[TOON_TGT_COL]) and atkTrack != prvAtkTrack:
                numPrevHits += 1

        if numPrevHits > 0 and self.notify.getDebug():
            self.notify.debug('ACC BONUS: toon attack received accuracy ' + 'bonus of ' + str(self.AccuracyBonuses[numPrevHits]) + ' from previous attack by (' + str(attack[TOON_ID_COL]) + ') which hit')
        return self.AccuracyBonuses[numPrevHits]

    def __applyToonAttackDamages(self, toonId, hpbonus=0, kbbonus=0):
        totalDamages = 0
        if not self.APPLY_HEALTH_ADJUSTMENTS:
            return totalDamages
        attack = self.battle.toonAttacks[toonId]
        track = self.__getActualTrack(attack)
        if track != NO_ATTACK and track != SOS and track != TRAP and track != NPCSOS:
            targets = self.__getToonTargets(attack)
            for position in xrange(len(targets)):
                if hpbonus:
                    if targets[position] in self.__createToonTargetList(toonId):
                        damageDone = attack[TOON_HPBONUS_COL]
                    else:
                        damageDone = 0
                else:
                    if kbbonus:
                        if targets[position] in self.__createToonTargetList(toonId):
                            damageDone = attack[TOON_KBBONUS_COL][position]
                        else:
                            damageDone = 0
                    else:
                        damageDone = attack[TOON_HP_COL][position]
                if damageDone <= 0 or self.immortalSuits:
                    continue
                if track == HEAL or track == PETSOS:
                    currTarget = targets[position]
                    if self.CAP_HEALS:
                        toonHp = self.__getToonHp(currTarget)
                        toonMaxHp = self.__getToonMaxHp(currTarget)
                        if toonHp + damageDone > toonMaxHp:
                            damageDone = toonMaxHp - toonHp
                            attack[TOON_HP_COL][position] = damageDone
                    self.toonHPAdjusts[currTarget] += damageDone
                    totalDamages = totalDamages + damageDone
                    continue
                currTarget = targets[position]
                currTarget.setHP(currTarget.getHP() - damageDone)
                targetId = currTarget.getDoId()
                if self.notify.getDebug():
                    if hpbonus:
                        self.notify.debug(str(targetId) + ': suit takes ' + str(damageDone) + ' damage from HP-Bonus')
                    elif kbbonus:
                        self.notify.debug(str(targetId) + ': suit takes ' + str(damageDone) + ' damage from KB-Bonus')
                    else:
                        self.notify.debug(str(targetId) + ': suit takes ' + str(damageDone) + ' damage')
                totalDamages = totalDamages + damageDone
                if currTarget.getHP() <= 0:
                    if currTarget.getSkeleRevives() >= 1:
                        currTarget.useSkeleRevive()
                        attack[SUIT_REVIVE_COL] = attack[SUIT_REVIVE_COL] | 1 << position
                    else:
                        self.suitLeftBattle(targetId)
                        attack[SUIT_DIED_COL] = attack[SUIT_DIED_COL] | 1 << position
                        if self.notify.getDebug():
                            self.notify.debug('Suit' + str(targetId) + 'bravely expired in combat')

        return totalDamages

    def __combatantDead(self, avId, toon):
        if toon:
            if self.__getToonHp(avId) <= 0:
                return 1
        else:
            suit = self.battle.findSuit(avId)
            if suit.getHP() <= 0:
                return 1
        return 0

    def __combatantJustRevived(self, avId):
        suit = self.battle.findSuit(avId)
        if suit.reviveCheckAndClear():
            return 1
        return 0

    def __addAttackExp(self, attack, track=-1, level=-1, attackerId=-1):
        trk = -1
        lvl = -1
        id = -1
        if track != -1 and level != -1 and attackerId != -1:
            trk = track
            lvl = level
            id = attackerId
        else:
            if self.__attackHasHit(attack):
                if self.notify.getDebug():
                    self.notify.debug('Attack ' + repr(attack) + ' has hit')
                trk = attack[TOON_TRACK_COL]
                lvl = attack[TOON_LVL_COL]
                id = attack[TOON_ID_COL]
        if trk != -1 and trk != NPCSOS and trk != PETSOS and lvl != -1 and id != -1:
            expList = self.toonSkillPtsGained.get(id, None)
            if expList == None:
                expList = [
                 0,
                 0,
                 0,
                 0,
                 0,
                 0,
                 0]
                self.toonSkillPtsGained[id] = expList
            expList[trk] = min(ExperienceCap, expList[trk] + (lvl + 1) * self.__skillCreditMultiplier)
        return

    def __clearTgtDied(self, tgt, lastAtk, currAtk):
        position = self.battle.activeSuits.index(tgt)
        currAtkTrack = self.__getActualTrack(currAtk)
        lastAtkTrack = self.__getActualTrack(lastAtk)
        if currAtkTrack == lastAtkTrack and lastAtk[SUIT_DIED_COL] & 1 << position and self.__attackHasHit(currAtk, suit=0):
            if self.notify.getDebug():
                self.notify.debug('Clearing suit died for ' + str(tgt.getDoId()) + ' at position ' + str(position) + ' from toon attack ' + str(lastAtk[TOON_ID_COL]) + ' and setting it for ' + str(currAtk[TOON_ID_COL]))
            lastAtk[SUIT_DIED_COL] = lastAtk[SUIT_DIED_COL] ^ 1 << position
            self.suitLeftBattle(tgt.getDoId())
            currAtk[SUIT_DIED_COL] = currAtk[SUIT_DIED_COL] | 1 << position

    def __addDmgToBonuses(self, dmg, attackIndex, hp=1):
        toonId = self.toonAtkOrder[attackIndex]
        attack = self.battle.toonAttacks[toonId]
        atkTrack = self.__getActualTrack(attack)
        if atkTrack == HEAL or atkTrack == PETSOS:
            return
        tgts = self.__createToonTargetList(toonId)
        for currTgt in tgts:
            tgtPos = self.battle.suits.index(currTgt)
            attackerId = self.toonAtkOrder[attackIndex]
            attack = self.battle.toonAttacks[attackerId]
            track = self.__getActualTrack(attack)
            if hp:
                if track in self.hpBonuses[tgtPos]:
                    self.hpBonuses[tgtPos][track].append([attackIndex, dmg])
                else:
                    self.hpBonuses[tgtPos][track] = [[attackIndex, dmg]]
            elif self.__suitIsLured(currTgt.getDoId()):
                if track in self.kbBonuses[tgtPos]:
                    self.kbBonuses[tgtPos][track].append([attackIndex, dmg])
                else:
                    self.kbBonuses[tgtPos][track] = [[attackIndex, dmg]]

    def __clearBonuses(self, hp=1):
        if hp:
            self.hpBonuses = [{}, {}, {}, {}]
        else:
            self.kbBonuses = [{}, {}, {}, {}]

    def __bonusExists(self, tgtSuit, hp=1):
        tgtPos = self.activeSuits.index(tgtSuit)
        if hp:
            bonusLen = len(self.hpBonuses[tgtPos])
        else:
            bonusLen = len(self.kbBonuses[tgtPos])
        if bonusLen > 0:
            return 1
        return 0

    def __processBonuses(self, hp=1):
        if hp:
            bonusList = self.hpBonuses
            self.notify.debug('Processing hpBonuses: ' + repr(self.hpBonuses))
        else:
            bonusList = self.kbBonuses
            self.notify.debug('Processing kbBonuses: ' + repr(self.kbBonuses))
        tgtPos = 0
        for currTgt in bonusList:
            for currAtkType in currTgt.keys():
                if len(currTgt[currAtkType]) > 1 or not hp and len(currTgt[currAtkType]) > 0:
                    totalDmgs = 0
                    for currDmg in currTgt[currAtkType]:
                        totalDmgs += currDmg[1]

                    numDmgs = len(currTgt[currAtkType])
                    attackIdx = currTgt[currAtkType][(numDmgs - 1)][0]
                    attackerId = self.toonAtkOrder[attackIdx]
                    attack = self.battle.toonAttacks[attackerId]
                    if hp:
                        attack[TOON_HPBONUS_COL] = math.ceil(totalDmgs * (self.DamageBonuses[(numDmgs - 1)] * 0.01))
                        if self.notify.getDebug():
                            self.notify.debug('Applying hp bonus to track ' + str(attack[TOON_TRACK_COL]) + ' of ' + str(attack[TOON_HPBONUS_COL]))
                    elif len(attack[TOON_KBBONUS_COL]) > tgtPos:
                        attack[TOON_KBBONUS_COL][tgtPos] = totalDmgs * 0.5
                        if self.notify.getDebug():
                            self.notify.debug('Applying kb bonus to track ' + str(attack[TOON_TRACK_COL]) + ' of ' + str(attack[TOON_KBBONUS_COL][tgtPos]) + ' to target ' + str(tgtPos))
                    else:
                        self.notify.warning('invalid tgtPos for knock back bonus: %d' % tgtPos)

            tgtPos += 1

        if hp:
            self.__clearBonuses()
        else:
            self.__clearBonuses(hp=0)

    def __handleBonus(self, attackIdx, hp=1):
        attackerId = self.toonAtkOrder[attackIdx]
        attack = self.battle.toonAttacks[attackerId]
        atkDmg = self.__attackDamage(attack, suit=0)
        atkTrack = self.__getActualTrack(attack)
        if atkDmg > 0:
            if hp:
                if atkTrack != LURE:
                    self.notify.debug('Adding dmg of ' + str(atkDmg) + ' to hpBonuses list')
                    self.__addDmgToBonuses(atkDmg, attackIdx)
            elif self.__knockBackAtk(attackerId, toon=1):
                self.notify.debug('Adding dmg of ' + str(atkDmg) + ' to kbBonuses list')
                self.__addDmgToBonuses(atkDmg, attackIdx, hp=0)

    def __clearAttack(self, attackIdx, toon=1):
        if toon:
            if self.notify.getDebug():
                self.notify.debug('clearing out toon attack for toon ' + str(attackIdx) + '...')
            attack = self.battle.toonAttacks[attackIdx]
            self.battle.toonAttacks[attackIdx] = getToonAttack(attackIdx)
            longest = max(len(self.battle.activeToons), len(self.battle.activeSuits))
            taList = self.battle.toonAttacks
            for j in xrange(longest):
                taList[attackIdx][TOON_HP_COL].append(-1)
                taList[attackIdx][TOON_KBBONUS_COL].append(-1)

            if self.notify.getDebug():
                self.notify.debug('toon attack is now ' + repr(self.battle.toonAttacks[attackIdx]))
        else:
            self.notify.warning('__clearAttack not implemented for suits!')

    def __rememberToonAttack(self, suitId, toonId, damage):
        if suitId not in self.SuitAttackers:
            self.SuitAttackers[suitId] = {toonId: damage}
        else:
            if toonId not in self.SuitAttackers[suitId]:
                self.SuitAttackers[suitId][toonId] = damage
            else:
                if self.SuitAttackers[suitId][toonId] <= damage:
                    self.SuitAttackers[suitId] = [toonId, damage]

    def __postProcessToonAttacks--- This code section failed: ---

 875       0  LOAD_FAST             0  'self'
           3  LOAD_ATTR             0  'notify'
           6  LOAD_ATTR             1  'debug'
           9  LOAD_CONST               '__postProcessToonAttacks()'
          12  CALL_FUNCTION_1       1  None
          15  POP_TOP          

 876      16  LOAD_CONST               -1
          19  STORE_FAST            1  'lastTrack'

 877      22  BUILD_LIST_0          0 
          25  STORE_FAST            2  'lastAttacks'

 878      28  LOAD_FAST             0  'self'
          31  LOAD_ATTR             2  '__clearBonuses'
          34  CALL_FUNCTION_0       0  None
          37  POP_TOP          

 879      38  SETUP_LOOP         1177  'to 1218'
          41  LOAD_FAST             0  'self'
          44  LOAD_ATTR             3  'toonAtkOrder'
          47  GET_ITER         
          48  FOR_ITER           1166  'to 1217'
          51  STORE_FAST            3  'currToonAttack'

 880      54  LOAD_FAST             3  'currToonAttack'
          57  LOAD_CONST               -1
          60  COMPARE_OP            3  !=
          63  POP_JUMP_IF_FALSE    48  'to 48'

 881      66  LOAD_FAST             0  'self'
          69  LOAD_ATTR             4  'battle'
          72  LOAD_ATTR             5  'toonAttacks'
          75  LOAD_FAST             3  'currToonAttack'
          78  BINARY_SUBSCR    
          79  STORE_FAST            4  'attack'

 882      82  LOAD_FAST             0  'self'
          85  LOAD_ATTR             6  '__getActualTrackLevel'
          88  LOAD_FAST             4  'attack'
          91  CALL_FUNCTION_1       1  None
          94  UNPACK_SEQUENCE_2     2 
          97  STORE_FAST            5  'atkTrack'
         100  STORE_FAST            6  'atkLevel'

 883     103  LOAD_FAST             5  'atkTrack'
         106  LOAD_GLOBAL           7  'HEAL'
         109  COMPARE_OP            3  !=
         112  POP_JUMP_IF_FALSE   975  'to 975'
         115  LOAD_FAST             5  'atkTrack'
         118  LOAD_GLOBAL           8  'SOS'
         121  COMPARE_OP            3  !=
         124  POP_JUMP_IF_FALSE   975  'to 975'
         127  LOAD_FAST             5  'atkTrack'
         130  LOAD_GLOBAL           9  'NO_ATTACK'
         133  COMPARE_OP            3  !=
         136  POP_JUMP_IF_FALSE   975  'to 975'
         139  LOAD_FAST             5  'atkTrack'
         142  LOAD_GLOBAL          10  'NPCSOS'
         145  COMPARE_OP            3  !=
         148  POP_JUMP_IF_FALSE   975  'to 975'
         151  LOAD_FAST             5  'atkTrack'
         154  LOAD_GLOBAL          11  'PETSOS'
         157  COMPARE_OP            3  !=
       160_0  COME_FROM           148  '148'
       160_1  COME_FROM           136  '136'
       160_2  COME_FROM           124  '124'
       160_3  COME_FROM           112  '112'
         160  POP_JUMP_IF_FALSE   975  'to 975'

 884     163  LOAD_FAST             0  'self'
         166  LOAD_ATTR            12  '__createToonTargetList'
         169  LOAD_FAST             3  'currToonAttack'
         172  CALL_FUNCTION_1       1  None
         175  STORE_FAST            7  'targets'

 885     178  LOAD_CONST               1
         181  STORE_FAST            8  'allTargetsDead'

 886     184  SETUP_LOOP          660  'to 847'
         187  LOAD_FAST             7  'targets'
         190  GET_ITER         
         191  FOR_ITER            652  'to 846'
         194  STORE_FAST            9  'currTgt'

 887     197  LOAD_FAST             0  'self'
         200  LOAD_ATTR            13  '__attackDamage'
         203  LOAD_FAST             4  'attack'
         206  LOAD_CONST               'suit'
         209  LOAD_CONST               0
         212  CALL_FUNCTION_257   257  None
         215  STORE_FAST           10  'damageDone'

 888     218  LOAD_FAST            10  'damageDone'
         221  LOAD_CONST               0
         224  COMPARE_OP            4  >
         227  POP_JUMP_IF_FALSE   262  'to 262'

 889     230  LOAD_FAST             0  'self'
         233  LOAD_ATTR            14  '__rememberToonAttack'
         236  LOAD_FAST             9  'currTgt'
         239  LOAD_ATTR            15  'getDoId'
         242  CALL_FUNCTION_0       0  None
         245  LOAD_FAST             4  'attack'
         248  LOAD_GLOBAL          16  'TOON_ID_COL'
         251  BINARY_SUBSCR    
         252  LOAD_FAST            10  'damageDone'
         255  CALL_FUNCTION_3       3  None
         258  POP_TOP          
         259  JUMP_FORWARD          0  'to 262'
       262_0  COME_FROM           259  '259'

 890     262  LOAD_FAST             5  'atkTrack'
         265  LOAD_GLOBAL          17  'TRAP'
         268  COMPARE_OP            2  ==
         271  POP_JUMP_IF_FALSE   327  'to 327'

 891     274  LOAD_FAST             9  'currTgt'
         277  LOAD_ATTR            18  'doId'
         280  LOAD_FAST             0  'self'
         283  LOAD_ATTR            19  'traps'
         286  COMPARE_OP            6  in
         289  POP_JUMP_IF_FALSE   327  'to 327'

 892     292  LOAD_FAST             0  'self'
         295  LOAD_ATTR            19  'traps'
         298  LOAD_FAST             9  'currTgt'
         301  LOAD_ATTR            18  'doId'
         304  BINARY_SUBSCR    
         305  STORE_FAST           11  'trapInfo'

 893     308  LOAD_FAST            11  'trapInfo'
         311  LOAD_CONST               0
         314  BINARY_SUBSCR    
         315  LOAD_FAST             9  'currTgt'
         318  STORE_ATTR           20  'battleTrap'
         321  JUMP_ABSOLUTE       327  'to 327'
         324  JUMP_FORWARD          0  'to 327'
       327_0  COME_FROM           324  '324'

 894     327  LOAD_CONST               0
         330  STORE_FAST           12  'targetDead'

 895     333  LOAD_FAST             9  'currTgt'
         336  LOAD_ATTR            21  'getHP'
         339  CALL_FUNCTION_0       0  None
         342  LOAD_CONST               0
         345  COMPARE_OP            4  >
         348  POP_JUMP_IF_FALSE   360  'to 360'

 896     351  LOAD_CONST               0
         354  STORE_FAST            8  'allTargetsDead'
         357  JUMP_FORWARD         57  'to 417'

 898     360  LOAD_CONST               1
         363  STORE_FAST           12  'targetDead'

 899     366  LOAD_FAST             5  'atkTrack'
         369  LOAD_GLOBAL          22  'LURE'
         372  COMPARE_OP            3  !=
         375  POP_JUMP_IF_FALSE   417  'to 417'

 900     378  SETUP_LOOP           36  'to 417'
         381  LOAD_FAST             2  'lastAttacks'
         384  GET_ITER         
         385  FOR_ITER             25  'to 413'
         388  STORE_FAST           13  'currLastAtk'

 901     391  LOAD_FAST             0  'self'
         394  LOAD_ATTR            23  '__clearTgtDied'
         397  LOAD_FAST             9  'currTgt'
         400  LOAD_FAST            13  'currLastAtk'
         403  LOAD_FAST             4  'attack'
         406  CALL_FUNCTION_3       3  None
         409  POP_TOP          
         410  JUMP_BACK           385  'to 385'
         413  POP_BLOCK        
       414_0  COME_FROM           378  '378'
         414  JUMP_FORWARD          0  'to 417'
       417_0  COME_FROM           378  '378'
       417_1  COME_FROM           357  '357'

 903     417  LOAD_FAST             9  'currTgt'
         420  LOAD_ATTR            15  'getDoId'
         423  CALL_FUNCTION_0       0  None
         426  STORE_FAST           14  'tgtId'

 904     429  LOAD_FAST            14  'tgtId'
         432  LOAD_FAST             0  'self'
         435  LOAD_ATTR            24  'successfulLures'
         438  COMPARE_OP            6  in
         441  POP_JUMP_IF_FALSE   681  'to 681'
         444  LOAD_FAST             5  'atkTrack'
         447  LOAD_GLOBAL          22  'LURE'
         450  COMPARE_OP            2  ==
       453_0  COME_FROM           441  '441'
         453  POP_JUMP_IF_FALSE   681  'to 681'

 905     456  LOAD_FAST             0  'self'
         459  LOAD_ATTR            24  'successfulLures'
         462  LOAD_FAST            14  'tgtId'
         465  BINARY_SUBSCR    
         466  STORE_FAST           15  'lureInfo'

 906     469  LOAD_FAST             0  'self'
         472  LOAD_ATTR             0  'notify'
         475  LOAD_ATTR             1  'debug'
         478  LOAD_CONST               'applying lure data: '
         481  LOAD_GLOBAL          25  'repr'
         484  LOAD_FAST            15  'lureInfo'
         487  CALL_FUNCTION_1       1  None
         490  BINARY_ADD       
         491  CALL_FUNCTION_1       1  None
         494  POP_TOP          

 907     495  LOAD_FAST            15  'lureInfo'
         498  LOAD_CONST               0
         501  BINARY_SUBSCR    
         502  STORE_FAST           16  'toonId'

 908     505  LOAD_FAST             0  'self'
         508  LOAD_ATTR             4  'battle'
         511  LOAD_ATTR             5  'toonAttacks'
         514  LOAD_FAST            16  'toonId'
         517  BINARY_SUBSCR    
         518  STORE_FAST           17  'lureAtk'

 909     521  LOAD_FAST             0  'self'
         524  LOAD_ATTR             4  'battle'
         527  LOAD_ATTR            26  'activeSuits'
         530  LOAD_ATTR            27  'index'
         533  LOAD_FAST             9  'currTgt'
         536  CALL_FUNCTION_1       1  None
         539  STORE_FAST           18  'tgtPos'

 910     542  LOAD_FAST             9  'currTgt'
         545  LOAD_ATTR            18  'doId'
         548  LOAD_FAST             0  'self'
         551  LOAD_ATTR            19  'traps'
         554  COMPARE_OP            6  in
         557  POP_JUMP_IF_FALSE   630  'to 630'

 911     560  LOAD_FAST             0  'self'
         563  LOAD_ATTR            19  'traps'
         566  LOAD_FAST             9  'currTgt'
         569  LOAD_ATTR            18  'doId'
         572  BINARY_SUBSCR    
         573  STORE_FAST           11  'trapInfo'

 912     576  LOAD_FAST            11  'trapInfo'
         579  LOAD_CONST               0
         582  BINARY_SUBSCR    
         583  LOAD_GLOBAL          28  'UBER_GAG_LEVEL_INDEX'
         586  COMPARE_OP            2  ==
         589  POP_JUMP_IF_FALSE   630  'to 630'

 913     592  LOAD_FAST             0  'self'
         595  LOAD_ATTR             0  'notify'
         598  LOAD_ATTR             1  'debug'
         601  LOAD_CONST               'train trap triggered for %d'
         604  LOAD_FAST             9  'currTgt'
         607  LOAD_ATTR            18  'doId'
         610  BINARY_MODULO    
         611  CALL_FUNCTION_1       1  None
         614  POP_TOP          

 914     615  LOAD_GLOBAL          29  'True'
         618  LOAD_FAST             0  'self'
         621  STORE_ATTR           30  'trainTrapTriggered'
         624  JUMP_ABSOLUTE       630  'to 630'
         627  JUMP_FORWARD          0  'to 630'
       630_0  COME_FROM           627  '627'

 915     630  LOAD_FAST             0  'self'
         633  LOAD_ATTR            31  '__removeSuitTrap'
         636  LOAD_FAST            14  'tgtId'
         639  CALL_FUNCTION_1       1  None
         642  POP_TOP          

 916     643  LOAD_FAST             0  'self'
         646  LOAD_ATTR            32  'KBBONUS_TGT_LURED'
         649  LOAD_FAST            17  'lureAtk'
         652  LOAD_GLOBAL          33  'TOON_KBBONUS_COL'
         655  BINARY_SUBSCR    
         656  LOAD_FAST            18  'tgtPos'
         659  STORE_SUBSCR     

 917     660  LOAD_FAST            15  'lureInfo'
         663  LOAD_CONST               3
         666  BINARY_SUBSCR    
         667  LOAD_FAST            17  'lureAtk'
         670  LOAD_GLOBAL          34  'TOON_HP_COL'
         673  BINARY_SUBSCR    
         674  LOAD_FAST            18  'tgtPos'
         677  STORE_SUBSCR     
         678  JUMP_FORWARD         92  'to 773'

 918     681  LOAD_FAST             0  'self'
         684  LOAD_ATTR            35  '__suitIsLured'
         687  LOAD_FAST            14  'tgtId'
         690  CALL_FUNCTION_1       1  None
         693  POP_JUMP_IF_FALSE   773  'to 773'
         696  LOAD_FAST             5  'atkTrack'
         699  LOAD_GLOBAL          36  'DROP'
         702  COMPARE_OP            2  ==
       705_0  COME_FROM           693  '693'
         705  POP_JUMP_IF_FALSE   773  'to 773'

 919     708  LOAD_FAST             0  'self'
         711  LOAD_ATTR             0  'notify'
         714  LOAD_ATTR             1  'debug'
         717  LOAD_CONST               'Drop on lured suit, '
         720  LOAD_CONST               'indicating with KBBONUS_COL '
         723  BINARY_ADD       
         724  LOAD_CONST               'flag'
         727  BINARY_ADD       
         728  CALL_FUNCTION_1       1  None
         731  POP_TOP          

 920     732  LOAD_FAST             0  'self'
         735  LOAD_ATTR             4  'battle'
         738  LOAD_ATTR            26  'activeSuits'
         741  LOAD_ATTR            27  'index'
         744  LOAD_FAST             9  'currTgt'
         747  CALL_FUNCTION_1       1  None
         750  STORE_FAST           18  'tgtPos'

 921     753  LOAD_FAST             0  'self'
         756  LOAD_ATTR            37  'KBBONUS_LURED_FLAG'
         759  LOAD_FAST             4  'attack'
         762  LOAD_GLOBAL          33  'TOON_KBBONUS_COL'
         765  BINARY_SUBSCR    
         766  LOAD_FAST            18  'tgtPos'
         769  STORE_SUBSCR     
         770  JUMP_FORWARD          0  'to 773'
       773_0  COME_FROM           770  '770'
       773_1  COME_FROM           678  '678'

 922     773  LOAD_FAST            12  'targetDead'
         776  POP_JUMP_IF_FALSE   191  'to 191'
         779  LOAD_FAST             5  'atkTrack'
         782  LOAD_FAST             1  'lastTrack'
         785  COMPARE_OP            3  !=
       788_0  COME_FROM           776  '776'
         788  POP_JUMP_IF_FALSE   191  'to 191'

 923     791  LOAD_FAST             0  'self'
         794  LOAD_ATTR             4  'battle'
         797  LOAD_ATTR            26  'activeSuits'
         800  LOAD_ATTR            27  'index'
         803  LOAD_FAST             9  'currTgt'
         806  CALL_FUNCTION_1       1  None
         809  STORE_FAST           18  'tgtPos'

 924     812  LOAD_CONST               0
         815  LOAD_FAST             4  'attack'
         818  LOAD_GLOBAL          34  'TOON_HP_COL'
         821  BINARY_SUBSCR    
         822  LOAD_FAST            18  'tgtPos'
         825  STORE_SUBSCR     

 925     826  LOAD_CONST               -1
         829  LOAD_FAST             4  'attack'
         832  LOAD_GLOBAL          33  'TOON_KBBONUS_COL'
         835  BINARY_SUBSCR    
         836  LOAD_FAST            18  'tgtPos'
         839  STORE_SUBSCR     
         840  JUMP_BACK           191  'to 191'
         843  JUMP_BACK           191  'to 191'
         846  POP_BLOCK        
       847_0  COME_FROM           184  '184'

 927     847  LOAD_FAST             8  'allTargetsDead'
         850  POP_JUMP_IF_FALSE   975  'to 975'
         853  LOAD_FAST             5  'atkTrack'
         856  LOAD_FAST             1  'lastTrack'
         859  COMPARE_OP            3  !=
       862_0  COME_FROM           850  '850'
         862  POP_JUMP_IF_FALSE   975  'to 975'

 928     865  LOAD_FAST             0  'self'
         868  LOAD_ATTR             0  'notify'
         871  LOAD_ATTR            38  'getDebug'
         874  CALL_FUNCTION_0       0  None
         877  POP_JUMP_IF_FALSE   913  'to 913'

 929     880  LOAD_FAST             0  'self'
         883  LOAD_ATTR             0  'notify'
         886  LOAD_ATTR             1  'debug'
         889  LOAD_CONST               'all targets of toon attack '
         892  LOAD_GLOBAL          39  'str'
         895  LOAD_FAST             3  'currToonAttack'
         898  CALL_FUNCTION_1       1  None
         901  BINARY_ADD       
         902  LOAD_CONST               ' are dead'
         905  BINARY_ADD       
         906  CALL_FUNCTION_1       1  None
         909  POP_TOP          
         910  JUMP_FORWARD          0  'to 913'
       913_0  COME_FROM           910  '910'

 930     913  LOAD_FAST             0  'self'
         916  LOAD_ATTR            40  '__clearAttack'
         919  LOAD_FAST             3  'currToonAttack'
         922  LOAD_CONST               'toon'
         925  LOAD_CONST               1
         928  CALL_FUNCTION_257   257  None
         931  POP_TOP          

 931     932  LOAD_FAST             0  'self'
         935  LOAD_ATTR             4  'battle'
         938  LOAD_ATTR             5  'toonAttacks'
         941  LOAD_FAST             3  'currToonAttack'
         944  BINARY_SUBSCR    
         945  STORE_FAST            4  'attack'

 932     948  LOAD_FAST             0  'self'
         951  LOAD_ATTR             6  '__getActualTrackLevel'
         954  LOAD_FAST             4  'attack'
         957  CALL_FUNCTION_1       1  None
         960  UNPACK_SEQUENCE_2     2 
         963  STORE_FAST            5  'atkTrack'
         966  STORE_FAST            6  'atkLevel'
         969  JUMP_ABSOLUTE       975  'to 975'
         972  JUMP_FORWARD          0  'to 975'
       975_0  COME_FROM           972  '972'

 933     975  LOAD_FAST             0  'self'
         978  LOAD_ATTR            41  '__applyToonAttackDamages'
         981  LOAD_FAST             3  'currToonAttack'
         984  CALL_FUNCTION_1       1  None
         987  STORE_FAST           19  'damagesDone'

 934     990  LOAD_FAST             0  'self'
         993  LOAD_ATTR            41  '__applyToonAttackDamages'
         996  LOAD_FAST             3  'currToonAttack'
         999  LOAD_CONST               'hpbonus'
        1002  LOAD_CONST               1
        1005  CALL_FUNCTION_257   257  None
        1008  POP_TOP          

 935    1009  LOAD_FAST             5  'atkTrack'
        1012  LOAD_GLOBAL          22  'LURE'
        1015  COMPARE_OP            3  !=
        1018  POP_JUMP_IF_FALSE  1067  'to 1067'
        1021  LOAD_FAST             5  'atkTrack'
        1024  LOAD_GLOBAL          36  'DROP'
        1027  COMPARE_OP            3  !=
        1030  POP_JUMP_IF_FALSE  1067  'to 1067'
        1033  LOAD_FAST             5  'atkTrack'
        1036  LOAD_GLOBAL          42  'SOUND'
        1039  COMPARE_OP            3  !=
      1042_0  COME_FROM          1030  '1030'
      1042_1  COME_FROM          1018  '1018'
        1042  POP_JUMP_IF_FALSE  1067  'to 1067'

 936    1045  LOAD_FAST             0  'self'
        1048  LOAD_ATTR            41  '__applyToonAttackDamages'
        1051  LOAD_FAST             3  'currToonAttack'
        1054  LOAD_CONST               'kbbonus'
        1057  LOAD_CONST               1
        1060  CALL_FUNCTION_257   257  None
        1063  POP_TOP          
        1064  JUMP_FORWARD          0  'to 1067'
      1067_0  COME_FROM          1064  '1064'

 937    1067  LOAD_FAST             1  'lastTrack'
        1070  LOAD_FAST             5  'atkTrack'
        1073  COMPARE_OP            3  !=
        1076  POP_JUMP_IF_FALSE  1094  'to 1094'

 938    1079  BUILD_LIST_0          0 
        1082  STORE_FAST            2  'lastAttacks'

 939    1085  LOAD_FAST             5  'atkTrack'
        1088  STORE_FAST            1  'lastTrack'
        1091  JUMP_FORWARD          0  'to 1094'
      1094_0  COME_FROM          1091  '1091'

 940    1094  LOAD_FAST             2  'lastAttacks'
        1097  LOAD_ATTR            43  'append'
        1100  LOAD_FAST             4  'attack'
        1103  CALL_FUNCTION_1       1  None
        1106  POP_TOP          

 941    1107  LOAD_FAST             0  'self'
        1110  LOAD_ATTR            44  'itemIsCredit'
        1113  LOAD_FAST             5  'atkTrack'
        1116  LOAD_FAST             6  'atkLevel'
        1119  CALL_FUNCTION_2       2  None
        1122  POP_JUMP_IF_FALSE  1214  'to 1214'

 942    1125  LOAD_FAST             5  'atkTrack'
        1128  LOAD_GLOBAL          17  'TRAP'
        1131  COMPARE_OP            2  ==
        1134  POP_JUMP_IF_TRUE   1208  'to 1208'
        1137  LOAD_FAST             5  'atkTrack'
        1140  LOAD_GLOBAL          22  'LURE'
        1143  COMPARE_OP            2  ==
        1146  POP_JUMP_IF_FALSE  1152  'to 1152'

 943    1149  JUMP_ABSOLUTE      1211  'to 1211'

 944    1152  LOAD_FAST             5  'atkTrack'
        1155  LOAD_GLOBAL           7  'HEAL'
        1158  COMPARE_OP            2  ==
        1161  POP_JUMP_IF_FALSE  1195  'to 1195'

 945    1164  LOAD_FAST            19  'damagesDone'
        1167  LOAD_CONST               0
        1170  COMPARE_OP            3  !=
        1173  POP_JUMP_IF_FALSE  1208  'to 1208'

 946    1176  LOAD_FAST             0  'self'
        1179  LOAD_ATTR            45  '__addAttackExp'
        1182  LOAD_FAST             4  'attack'
        1185  CALL_FUNCTION_1       1  None
        1188  POP_TOP          
        1189  JUMP_ABSOLUTE      1208  'to 1208'
        1192  JUMP_ABSOLUTE      1211  'to 1211'

 948    1195  LOAD_FAST             0  'self'
        1198  LOAD_ATTR            45  '__addAttackExp'
        1201  LOAD_FAST             4  'attack'
        1204  CALL_FUNCTION_1       1  None
        1207  POP_TOP          
        1208  JUMP_ABSOLUTE      1214  'to 1214'
        1211  JUMP_BACK            48  'to 48'
        1214  JUMP_BACK            48  'to 48'
        1217  POP_BLOCK        
      1218_0  COME_FROM            38  '38'

 950    1218  LOAD_FAST             0  'self'
        1221  LOAD_ATTR            30  'trainTrapTriggered'
        1224  POP_JUMP_IF_FALSE  1304  'to 1304'

 951    1227  SETUP_LOOP           74  'to 1304'
        1230  LOAD_FAST             0  'self'
        1233  LOAD_ATTR             4  'battle'
        1236  LOAD_ATTR            26  'activeSuits'
        1239  GET_ITER         
        1240  FOR_ITER             57  'to 1300'
        1243  STORE_FAST           20  'suit'

 952    1246  LOAD_FAST            20  'suit'
        1249  LOAD_ATTR            18  'doId'
        1252  STORE_FAST           21  'suitId'

 953    1255  LOAD_FAST             0  'self'
        1258  LOAD_ATTR            31  '__removeSuitTrap'
        1261  LOAD_FAST            21  'suitId'
        1264  CALL_FUNCTION_1       1  None
        1267  POP_TOP          

 954    1268  LOAD_GLOBAL          46  'NO_TRAP'
        1271  LOAD_FAST            20  'suit'
        1274  STORE_ATTR           20  'battleTrap'

 955    1277  LOAD_FAST             0  'self'
        1280  LOAD_ATTR             0  'notify'
        1283  LOAD_ATTR             1  'debug'
        1286  LOAD_CONST               'train trap triggered, removing trap from %d'
        1289  LOAD_FAST            21  'suitId'
        1292  BINARY_MODULO    
        1293  CALL_FUNCTION_1       1  None
        1296  POP_TOP          
        1297  JUMP_BACK          1240  'to 1240'
        1300  POP_BLOCK        
      1301_0  COME_FROM          1227  '1227'
        1301  JUMP_FORWARD          0  'to 1304'
      1304_0  COME_FROM          1227  '1227'

 957    1304  LOAD_FAST             0  'self'
        1307  LOAD_ATTR             0  'notify'
        1310  LOAD_ATTR            38  'getDebug'
        1313  CALL_FUNCTION_0       0  None
        1316  POP_JUMP_IF_FALSE  1384  'to 1384'

 958    1319  SETUP_LOOP           62  'to 1384'
        1322  LOAD_FAST             0  'self'
        1325  LOAD_ATTR             3  'toonAtkOrder'
        1328  GET_ITER         
        1329  FOR_ITER             48  'to 1380'
        1332  STORE_FAST            3  'currToonAttack'

 959    1335  LOAD_FAST             0  'self'
        1338  LOAD_ATTR             4  'battle'
        1341  LOAD_ATTR             5  'toonAttacks'
        1344  LOAD_FAST             3  'currToonAttack'
        1347  BINARY_SUBSCR    
        1348  STORE_FAST            4  'attack'

 960    1351  LOAD_FAST             0  'self'
        1354  LOAD_ATTR             0  'notify'
        1357  LOAD_ATTR             1  'debug'
        1360  LOAD_CONST               'Final Toon attack: '
        1363  LOAD_GLOBAL          39  'str'
        1366  LOAD_FAST             4  'attack'
        1369  CALL_FUNCTION_1       1  None
        1372  BINARY_ADD       
        1373  CALL_FUNCTION_1       1  None
        1376  POP_TOP          
        1377  JUMP_BACK          1329  'to 1329'
        1380  POP_BLOCK        
      1381_0  COME_FROM          1319  '1319'
        1381  JUMP_FORWARD          0  'to 1384'
      1384_0  COME_FROM          1319  '1319'

Parse error at or near `JUMP_BACK' instruction at offset 1214

    def __allTargetsDead(self, attackIdx, toon=1):
        allTargetsDead = 1
        if toon:
            targets = self.__createToonTargetList(attackIdx)
            for currTgt in targets:
                if currTgt.getHp() > 0:
                    allTargetsDead = 0
                    break

        else:
            self.notify.warning('__allTargetsDead: suit ver. not implemented!')
        return allTargetsDead

    def __clearLuredSuitsByAttack(self, toonId, kbBonusReq=0, targetId=-1):
        if self.notify.getDebug():
            self.notify.debug('__clearLuredSuitsByAttack')
        if targetId != -1 and self.__suitIsLured(t.getDoId()):
            self.__removeLured(t.getDoId())
        else:
            tgtList = self.__createToonTargetList(toonId)
            for t in tgtList:
                if self.__suitIsLured(t.getDoId()) and (not kbBonusReq or self.__bonusExists(t, hp=0)):
                    self.__removeLured(t.getDoId())
                    if self.notify.getDebug():
                        self.notify.debug('Suit %d stepping from lured spot' % t.getDoId())
                else:
                    self.notify.debug('Suit ' + str(t.getDoId()) + ' not found in currently lured suits')

    def __clearLuredSuitsDelayed(self):
        if self.notify.getDebug():
            self.notify.debug('__clearLuredSuitsDelayed')
        for t in self.delayedUnlures:
            if self.__suitIsLured(t):
                self.__removeLured(t)
                if self.notify.getDebug():
                    self.notify.debug('Suit %d stepping back from lured spot' % t)
            else:
                self.notify.debug('Suit ' + str(t) + ' not found in currently lured suits')

        self.delayedUnlures = []

    def __addLuredSuitsDelayed(self, toonId, targetId=-1, ignoreDamageCheck=False):
        if self.notify.getDebug():
            self.notify.debug('__addLuredSuitsDelayed')
        if targetId != -1:
            self.delayedUnlures.append(targetId)
        else:
            tgtList = self.__createToonTargetList(toonId)
            for t in tgtList:
                if self.__suitIsLured(t.getDoId()) and t.getDoId() not in self.delayedUnlures and (self.__attackDamageForTgt(self.battle.toonAttacks[toonId], self.battle.activeSuits.index(t), suit=0) > 0 or ignoreDamageCheck):
                    self.delayedUnlures.append(t.getDoId())

    def __calculateToonAttacks(self):
        self.notify.debug('__calculateToonAttacks()')
        self.__clearBonuses(hp=0)
        currTrack = None
        self.notify.debug('Traps: ' + str(self.traps))
        maxSuitLevel = 0
        for cog in self.battle.activeSuits:
            maxSuitLevel = max(maxSuitLevel, cog.getActualLevel())

        self.creditLevel = maxSuitLevel
        for toonId in self.toonAtkOrder:
            if self.__combatantDead(toonId, toon=1):
                if self.notify.getDebug():
                    self.notify.debug("Toon %d is dead and can't attack" % toonId)
                continue
            attack = self.battle.toonAttacks[toonId]
            atkTrack = self.__getActualTrack(attack)
            if atkTrack != NO_ATTACK and atkTrack != SOS and atkTrack != NPCSOS:
                if self.notify.getDebug():
                    self.notify.debug('Calculating attack for toon: %d' % toonId)
                if self.SUITS_UNLURED_IMMEDIATELY:
                    if currTrack and atkTrack != currTrack:
                        self.__clearLuredSuitsDelayed()
                currTrack = atkTrack
                self.__calcToonAtkHp(toonId)
                attackIdx = self.toonAtkOrder.index(toonId)
                self.__handleBonus(attackIdx, hp=0)
                self.__handleBonus(attackIdx, hp=1)
                lastAttack = self.toonAtkOrder.index(toonId) >= len(self.toonAtkOrder) - 1
                unlureAttack = self.__attackHasHit(attack, suit=0) and self.__unlureAtk(toonId, toon=1)
                if unlureAttack:
                    if lastAttack:
                        self.__clearLuredSuitsByAttack(toonId)
                    else:
                        self.__addLuredSuitsDelayed(toonId)
                if lastAttack:
                    self.__clearLuredSuitsDelayed()

        self.__processBonuses(hp=0)
        self.__processBonuses(hp=1)
        self.__postProcessToonAttacks()
        return

    def __knockBackAtk(self, attackIndex, toon=1):
        if toon and (self.battle.toonAttacks[attackIndex][TOON_TRACK_COL] == THROW or self.battle.toonAttacks[attackIndex][TOON_TRACK_COL] == SQUIRT):
            if self.notify.getDebug():
                self.notify.debug('attack is a knockback')
            return 1
        return 0

    def __unlureAtk(self, attackIndex, toon=1):
        attack = self.battle.toonAttacks[attackIndex]
        track = self.__getActualTrack(attack)
        if toon and (track == THROW or track == SQUIRT or track == SOUND):
            if self.notify.getDebug():
                self.notify.debug('attack is an unlure')
            return 1
        return 0

    def __calcSuitAtkType(self, attackIndex):
        theSuit = self.battle.activeSuits[attackIndex]
        attacks = SuitBattleGlobals.SuitAttributes[theSuit.dna.name]['attacks']
        atk = SuitBattleGlobals.pickSuitAttack(attacks, theSuit.getLevel())
        return atk

    def __calcSuitTarget(self, attackIndex):
        attack = self.battle.suitAttacks[attackIndex]
        suitId = attack[SUIT_ID_COL]
        if suitId in self.SuitAttackers and random.randint(0, 99) < 75:
            totalDamage = 0
            for currToon in self.SuitAttackers[suitId].keys():
                totalDamage += self.SuitAttackers[suitId][currToon]

            dmgs = []
            for currToon in self.SuitAttackers[suitId].keys():
                dmgs.append(self.SuitAttackers[suitId][currToon] / totalDamage * 100)

            dmgIdx = SuitBattleGlobals.pickFromFreqList(dmgs)
            if dmgIdx == None:
                toonId = self.__pickRandomToon(suitId)
            else:
                toonId = self.SuitAttackers[suitId].keys()[dmgIdx]
            if toonId == -1 or toonId not in self.battle.activeToons:
                return -1
            self.notify.debug('Suit attacking back at toon ' + str(toonId))
            return self.battle.activeToons.index(toonId)
        return self.__pickRandomToon(suitId)
        return

    def __pickRandomToon(self, suitId):
        liveToons = []
        for currToon in self.battle.activeToons:
            if not self.__combatantDead(currToon, toon=1):
                liveToons.append(self.battle.activeToons.index(currToon))

        if len(liveToons) == 0:
            self.notify.debug('No tgts avail. for suit ' + str(suitId))
            return -1
        chosen = random.choice(liveToons)
        self.notify.debug('Suit randomly attacking toon ' + str(self.battle.activeToons[chosen]))
        return chosen

    def __suitAtkHit(self, attackIndex):
        if self.suitsAlwaysHit:
            return 1
        if self.suitsAlwaysMiss:
            return 0
        theSuit = self.battle.activeSuits[attackIndex]
        atkType = self.battle.suitAttacks[attackIndex][SUIT_ATK_COL]
        atkInfo = SuitBattleGlobals.getSuitAttack(theSuit.dna.name, theSuit.getLevel(), atkType)
        atkAcc = atkInfo['acc']
        suitAcc = SuitBattleGlobals.SuitAttributes[theSuit.dna.name]['acc'][theSuit.getLevel()]
        acc = atkAcc
        randChoice = random.randint(0, 99)
        if self.notify.getDebug():
            self.notify.debug('Suit attack rolled ' + str(randChoice) + ' to hit with an accuracy of ' + str(acc) + ' (attackAcc: ' + str(atkAcc) + ' suitAcc: ' + str(suitAcc) + ')')
        if randChoice < acc:
            return 1
        return 0

    def __suitAtkAffectsGroup(self, attack):
        atkType = attack[SUIT_ATK_COL]
        theSuit = self.battle.findSuit(attack[SUIT_ID_COL])
        atkInfo = SuitBattleGlobals.getSuitAttack(theSuit.dna.name, theSuit.getLevel(), atkType)
        return atkInfo['group'] != SuitBattleGlobals.ATK_TGT_SINGLE

    def __createSuitTargetList(self, attackIndex):
        attack = self.battle.suitAttacks[attackIndex]
        targetList = []
        if attack[SUIT_ATK_COL] == NO_ATTACK:
            self.notify.debug('No attack, no targets')
            return targetList
        debug = self.notify.getDebug()
        if not self.__suitAtkAffectsGroup(attack):
            targetList.append(self.battle.activeToons[attack[SUIT_TGT_COL]])
            if debug:
                self.notify.debug('Suit attack is single target')
        else:
            if debug:
                self.notify.debug('Suit attack is group target')
            for currToon in self.battle.activeToons:
                if debug:
                    self.notify.debug('Suit attack will target toon' + str(currToon))
                targetList.append(currToon)

        return targetList

    def __calcSuitAtkHp(self, attackIndex):
        targetList = self.__createSuitTargetList(attackIndex)
        attack = self.battle.suitAttacks[attackIndex]
        for currTarget in xrange(len(targetList)):
            toonId = targetList[currTarget]
            toon = self.battle.getToon(toonId)
            result = 0
            if toon and toon.immortalMode:
                result = 1
            else:
                if self.TOONS_TAKE_NO_DAMAGE:
                    result = 0
                else:
                    if self.__suitAtkHit(attackIndex):
                        atkType = attack[SUIT_ATK_COL]
                        theSuit = self.battle.findSuit(attack[SUIT_ID_COL])
                        atkInfo = SuitBattleGlobals.getSuitAttack(theSuit.dna.name, theSuit.getLevel(), atkType)
                        result = atkInfo['hp']
            targetIndex = self.battle.activeToons.index(toonId)
            attack[SUIT_HP_COL][targetIndex] = result

    def __getToonHp(self, toonDoId):
        handle = self.battle.getToon(toonDoId)
        if handle != None and toonDoId in self.toonHPAdjusts:
            return handle.hp + self.toonHPAdjusts[toonDoId]
        return 0
        return

    def __getToonMaxHp(self, toonDoId):
        handle = self.battle.getToon(toonDoId)
        if handle != None:
            return handle.maxHp
        return 0
        return

    def __applySuitAttackDamages(self, attackIndex):
        attack = self.battle.suitAttacks[attackIndex]
        if self.APPLY_HEALTH_ADJUSTMENTS:
            for t in self.battle.activeToons:
                position = self.battle.activeToons.index(t)
                if attack[SUIT_HP_COL][position] <= 0:
                    continue
                toonHp = self.__getToonHp(t)
                if toonHp - attack[SUIT_HP_COL][position] <= 0:
                    if self.notify.getDebug():
                        self.notify.debug('Toon %d has died, removing' % t)
                    self.toonLeftBattle(t)
                    attack[TOON_DIED_COL] = attack[TOON_DIED_COL] | 1 << position
                if self.notify.getDebug():
                    self.notify.debug('Toon ' + str(t) + ' takes ' + str(attack[SUIT_HP_COL][position]) + ' damage')
                self.toonHPAdjusts[t] -= attack[SUIT_HP_COL][position]
                self.notify.debug('Toon ' + str(t) + ' now has ' + str(self.__getToonHp(t)) + ' health')

    def __suitCanAttack(self, suitId):
        if self.__combatantDead(suitId, toon=0) or self.__suitIsLured(suitId) or self.__combatantJustRevived(suitId):
            return 0
        return 1

    def __updateSuitAtkStat(self, toonId):
        if toonId in self.suitAtkStats:
            self.suitAtkStats[toonId] += 1
        else:
            self.suitAtkStats[toonId] = 1

    def __printSuitAtkStats(self):
        self.notify.debug('Suit Atk Stats:')
        for currTgt in self.suitAtkStats.keys():
            if currTgt not in self.battle.activeToons:
                continue
            tgtPos = self.battle.activeToons.index(currTgt)
            self.notify.debug(' toon ' + str(currTgt) + ' at position ' + str(tgtPos) + ' was attacked ' + str(self.suitAtkStats[currTgt]) + ' times')

        self.notify.debug('\n')

    def __calculateSuitAttacks(self):
        for i in xrange(len(self.battle.suitAttacks)):
            if i < len(self.battle.activeSuits):
                suitId = self.battle.activeSuits[i].doId
                self.battle.suitAttacks[i][SUIT_ID_COL] = suitId
                if not self.__suitCanAttack(suitId):
                    if self.notify.getDebug():
                        self.notify.debug("Suit %d can't attack" % suitId)
                    continue
                if self.battle.pendingSuits.count(self.battle.activeSuits[i]) > 0 or self.battle.joiningSuits.count(self.battle.activeSuits[i]) > 0:
                    continue
                attack = self.battle.suitAttacks[i]
                attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                attack[SUIT_ATK_COL] = self.__calcSuitAtkType(i)
                attack[SUIT_TGT_COL] = self.__calcSuitTarget(i)
                if attack[SUIT_TGT_COL] == -1:
                    self.battle.suitAttacks[i] = getDefaultSuitAttack()
                    attack = self.battle.suitAttacks[i]
                    self.notify.debug('clearing suit attack, no avail targets')
                self.__calcSuitAtkHp(i)
                if attack[SUIT_ATK_COL] != NO_ATTACK:
                    if self.__suitAtkAffectsGroup(attack):
                        for currTgt in self.battle.activeToons:
                            self.__updateSuitAtkStat(currTgt)

                    else:
                        tgtId = self.battle.activeToons[attack[SUIT_TGT_COL]]
                        self.__updateSuitAtkStat(tgtId)
                targets = self.__createSuitTargetList(i)
                allTargetsDead = 1
                for currTgt in targets:
                    if self.__getToonHp(currTgt) > 0:
                        allTargetsDead = 0
                        break

                if allTargetsDead:
                    self.battle.suitAttacks[i] = getDefaultSuitAttack()
                    if self.notify.getDebug():
                        self.notify.debug('clearing suit attack, targets dead')
                        self.notify.debug('suit attack is now ' + repr(self.battle.suitAttacks[i]))
                        self.notify.debug('all attacks: ' + repr(self.battle.suitAttacks))
                    attack = self.battle.suitAttacks[i]
                if self.__attackHasHit(attack, suit=1):
                    self.__applySuitAttackDamages(i)
                if self.notify.getDebug():
                    self.notify.debug('Suit attack: ' + str(self.battle.suitAttacks[i]))
                attack[SUIT_BEFORE_TOONS_COL] = 0

    def __updateLureTimeouts(self):
        if self.notify.getDebug():
            self.notify.debug('__updateLureTimeouts()')
            self.notify.debug('Lured suits: ' + str(self.currentlyLuredSuits))
        noLongerLured = []
        for currLuredSuit in self.currentlyLuredSuits.keys():
            self.__incLuredCurrRound(currLuredSuit)
            if self.__luredMaxRoundsReached(currLuredSuit) or self.__luredWakeupTime(currLuredSuit):
                noLongerLured.append(currLuredSuit)

        for currLuredSuit in noLongerLured:
            self.__removeLured(currLuredSuit)

        if self.notify.getDebug():
            self.notify.debug('Lured suits: ' + str(self.currentlyLuredSuits))

    def __initRound(self):
        if self.CLEAR_SUIT_ATTACKERS:
            self.SuitAttackers = {}
        self.toonAtkOrder = []
        attacks = findToonAttack(self.battle.activeToons, self.battle.toonAttacks, PETSOS)
        for atk in attacks:
            self.toonAtkOrder.append(atk[TOON_ID_COL])

        attacks = findToonAttack(self.battle.activeToons, self.battle.toonAttacks, FIRE)
        for atk in attacks:
            self.toonAtkOrder.append(atk[TOON_ID_COL])

        for track in xrange(HEAL, DROP + 1):
            attacks = findToonAttack(self.battle.activeToons, self.battle.toonAttacks, track)
            if track == TRAP:
                sortedTraps = []
                for atk in attacks:
                    if atk[TOON_TRACK_COL] == TRAP:
                        sortedTraps.append(atk)

                for atk in attacks:
                    if atk[TOON_TRACK_COL] == NPCSOS:
                        sortedTraps.append(atk)

                attacks = sortedTraps
            for atk in attacks:
                self.toonAtkOrder.append(atk[TOON_ID_COL])

        specials = findToonAttack(self.battle.activeToons, self.battle.toonAttacks, NPCSOS)
        toonsHit = 0
        cogsMiss = 0
        for special in specials:
            npc_track = NPCToons.getNPCTrack(special[TOON_TGT_COL])
            if npc_track == NPC_TOONS_HIT:
                BattleCalculatorAI.toonsAlwaysHit = 1
                toonsHit = 1
            elif npc_track == NPC_COGS_MISS:
                BattleCalculatorAI.suitsAlwaysMiss = 1
                cogsMiss = 1

        if self.notify.getDebug():
            self.notify.debug('Toon attack order: ' + str(self.toonAtkOrder))
            self.notify.debug('Active toons: ' + str(self.battle.activeToons))
            self.notify.debug('Toon attacks: ' + str(self.battle.toonAttacks))
            self.notify.debug('Active suits: ' + str(self.battle.activeSuits))
            self.notify.debug('Suit attacks: ' + str(self.battle.suitAttacks))
        self.toonHPAdjusts = {}
        for t in self.battle.activeToons:
            self.toonHPAdjusts[t] = 0

        self.__clearBonuses()
        self.__updateActiveToons()
        self.delayedUnlures = []
        self.__initTraps()
        self.successfulLures = {}
        return (
         toonsHit, cogsMiss)

    def calculateRound(self):
        longest = max(len(self.battle.activeToons), len(self.battle.activeSuits))
        for t in self.battle.activeToons:
            for j in xrange(longest):
                self.battle.toonAttacks[t][TOON_HP_COL].append(-1)
                self.battle.toonAttacks[t][TOON_KBBONUS_COL].append(-1)

        for i in xrange(4):
            for j in xrange(len(self.battle.activeToons)):
                self.battle.suitAttacks[i][SUIT_HP_COL].append(-1)

        toonsHit, cogsMiss = self.__initRound()
        for suit in self.battle.activeSuits:
            if suit.isGenerated():
                suit.b_setHP(suit.getHP())

        for suit in self.battle.activeSuits:
            if not hasattr(suit, 'dna'):
                self.notify.warning('a removed suit is in this battle!')
                return

        self.__calculateToonAttacks()
        self.__updateLureTimeouts()
        self.__calculateSuitAttacks()
        if toonsHit == 1:
            BattleCalculatorAI.toonsAlwaysHit = 0
        if cogsMiss == 1:
            BattleCalculatorAI.suitsAlwaysMiss = 0
        if self.notify.getDebug():
            self.notify.debug('Toon skills gained after this round: ' + repr(self.toonSkillPtsGained))
            self.__printSuitAtkStats()
        return

    def __calculateFiredCogs():
        import pdb
        pdb.set_trace()

    def toonLeftBattle(self, toonId):
        if self.notify.getDebug():
            self.notify.debug('toonLeftBattle()' + str(toonId))
        if toonId in self.toonSkillPtsGained:
            del self.toonSkillPtsGained[toonId]
        if toonId in self.suitAtkStats:
            del self.suitAtkStats[toonId]
        if not self.CLEAR_SUIT_ATTACKERS:
            oldSuitIds = []
            for s in self.SuitAttackers.keys():
                if toonId in self.SuitAttackers[s]:
                    del self.SuitAttackers[s][toonId]
                    if len(self.SuitAttackers[s]) == 0:
                        oldSuitIds.append(s)

            for oldSuitId in oldSuitIds:
                del self.SuitAttackers[oldSuitId]

        self.__clearTrapCreator(toonId)
        self.__clearLurer(toonId)

    def suitLeftBattle(self, suitId):
        if self.notify.getDebug():
            self.notify.debug('suitLeftBattle(): ' + str(suitId))
        self.__removeLured(suitId)
        if suitId in self.SuitAttackers:
            del self.SuitAttackers[suitId]
        self.__removeSuitTrap(suitId)

    def __updateActiveToons(self):
        if self.notify.getDebug():
            self.notify.debug('updateActiveToons()')
        if not self.CLEAR_SUIT_ATTACKERS:
            oldSuitIds = []
            for s in self.SuitAttackers.keys():
                for t in self.SuitAttackers[s].keys():
                    if t not in self.battle.activeToons:
                        del self.SuitAttackers[s][t]
                        if len(self.SuitAttackers[s]) == 0:
                            oldSuitIds.append(s)

            for oldSuitId in oldSuitIds:
                del self.SuitAttackers[oldSuitId]

        for trap in self.traps.keys():
            if self.traps[trap][1] not in self.battle.activeToons:
                self.notify.debug('Trap for toon ' + str(self.traps[trap][1]) + ' will no longer give exp')
                self.traps[trap][1] = 0

    def getSkillGained(self, toonId, track):
        return BattleExperienceAI.getSkillGained(self.toonSkillPtsGained, toonId, track)

    def getLuredSuits(self):
        luredSuits = self.currentlyLuredSuits.keys()
        self.notify.debug('Lured suits reported to battle: ' + repr(luredSuits))
        return luredSuits

    def __suitIsLured(self, suitId, prevRound=0):
        inList = suitId in self.currentlyLuredSuits
        if prevRound:
            return inList and self.currentlyLuredSuits[suitId][0] != -1
        return inList

    def __findAvailLureId(self, lurerId):
        luredSuits = self.currentlyLuredSuits.keys()
        lureIds = []
        for currLured in luredSuits:
            lurerInfo = self.currentlyLuredSuits[currLured][3]
            lurers = lurerInfo.keys()
            for currLurer in lurers:
                currId = lurerInfo[currLurer][1]
                if currLurer == lurerId and currId not in lureIds:
                    lureIds.append(currId)

        lureIds.sort()
        currId = 1
        for currLureId in lureIds:
            if currLureId != currId:
                return currId
            currId += 1

        return currId

    def __addLuredSuitInfo(self, suitId, currRounds, maxRounds, wakeChance, lurer, lureLvl, lureId=-1, npc=0):
        if lureId == -1:
            availLureId = self.__findAvailLureId(lurer)
        else:
            availLureId = lureId
        if npc == 1:
            credit = 0
        else:
            credit = self.itemIsCredit(LURE, lureLvl)
        if suitId in self.currentlyLuredSuits:
            lureInfo = self.currentlyLuredSuits[suitId]
            if lurer not in lureInfo[3]:
                lureInfo[1] += maxRounds
                if wakeChance < lureInfo[2]:
                    lureInfo[2] = wakeChance
                lureInfo[3][lurer] = [lureLvl, availLureId, credit]
        else:
            lurerInfo = {lurer: [lureLvl, availLureId, credit]}
            self.currentlyLuredSuits[suitId] = [
             currRounds, maxRounds, wakeChance, lurerInfo]
        self.notify.debug('__addLuredSuitInfo: currLuredSuits -> %s' % repr(self.currentlyLuredSuits))
        return availLureId

    def __getLurers(self, suitId):
        if self.__suitIsLured(suitId):
            return self.currentlyLuredSuits[suitId][3].keys()
        return []

    def __getLuredExpInfo(self, suitId):
        returnInfo = []
        lurers = self.__getLurers(suitId)
        if len(lurers) == 0:
            return returnInfo
        lurerInfo = self.currentlyLuredSuits[suitId][3]
        for currLurer in lurers:
            returnInfo.append([currLurer, lurerInfo[currLurer][0], lurerInfo[currLurer][1], lurerInfo[currLurer][2]])

        return returnInfo

    def __clearLurer(self, lurerId, lureId=-1):
        luredSuits = self.currentlyLuredSuits.keys()
        for currLured in luredSuits:
            lurerInfo = self.currentlyLuredSuits[currLured][3]
            lurers = lurerInfo.keys()
            for currLurer in lurers:
                if currLurer == lurerId and (lureId == -1 or lureId == lurerInfo[currLurer][1]):
                    del lurerInfo[currLurer]

    def __setLuredMaxRounds(self, suitId, rounds):
        if self.__suitIsLured(suitId):
            self.currentlyLuredSuits[suitId][1] = rounds

    def __setLuredWakeChance(self, suitId, chance):
        if self.__suitIsLured(suitId):
            self.currentlyLuredSuits[suitId][2] = chance

    def __incLuredCurrRound(self, suitId):
        if self.__suitIsLured(suitId):
            self.currentlyLuredSuits[suitId][0] += 1

    def __removeLured(self, suitId):
        if self.__suitIsLured(suitId):
            del self.currentlyLuredSuits[suitId]

    def __luredMaxRoundsReached(self, suitId):
        return self.__suitIsLured(suitId) and self.currentlyLuredSuits[suitId][0] >= self.currentlyLuredSuits[suitId][1]

    def __luredWakeupTime(self, suitId):
        return self.__suitIsLured(suitId) and self.currentlyLuredSuits[suitId][0] > 0 and random.randint(0, 99) < self.currentlyLuredSuits[suitId][2]

    def itemIsCredit(self, track, level):
        if track == PETSOS:
            return 0
        return level < self.creditLevel

    def __getActualTrack(self, toonAttack):
        if toonAttack[TOON_TRACK_COL] == NPCSOS:
            track = NPCToons.getNPCTrack(toonAttack[TOON_TGT_COL])
            if track != None:
                return track
            self.notify.warning('No NPC with id: %d' % toonAttack[TOON_TGT_COL])
        return toonAttack[TOON_TRACK_COL]

    def __getActualTrackLevel(self, toonAttack):
        if toonAttack[TOON_TRACK_COL] == NPCSOS:
            track, level, hp = NPCToons.getNPCTrackLevelHp(toonAttack[TOON_TGT_COL])
            if track != None:
                return (track, level)
            self.notify.warning('No NPC with id: %d' % toonAttack[TOON_TGT_COL])
        return (
         toonAttack[TOON_TRACK_COL], toonAttack[TOON_LVL_COL])

    def __getActualTrackLevelHp(self, toonAttack):
        if toonAttack[TOON_TRACK_COL] == NPCSOS:
            track, level, hp = NPCToons.getNPCTrackLevelHp(toonAttack[TOON_TGT_COL])
            if track != None:
                return (track, level, hp)
            self.notify.warning('No NPC with id: %d' % toonAttack[TOON_TGT_COL])
        else:
            if toonAttack[TOON_TRACK_COL] == PETSOS:
                trick = toonAttack[TOON_LVL_COL]
                petProxyId = toonAttack[TOON_TGT_COL]
                trickId = toonAttack[TOON_LVL_COL]
                healRange = PetTricks.TrickHeals[trickId]
                hp = 0
                if petProxyId in simbase.air.doId2do:
                    petProxy = simbase.air.doId2do[petProxyId]
                    if trickId < len(petProxy.trickAptitudes):
                        aptitude = petProxy.trickAptitudes[trickId]
                        hp = int(lerp(healRange[0], healRange[1], aptitude))
                else:
                    self.notify.warning('pet proxy: %d not in doId2do!' % petProxyId)
                return (toonAttack[TOON_TRACK_COL], toonAttack[TOON_LVL_COL], hp)
        return (toonAttack[TOON_TRACK_COL], toonAttack[TOON_LVL_COL], 0)

    def __calculatePetTrickSuccess(self, toonAttack):
        petProxyId = toonAttack[TOON_TGT_COL]
        if petProxyId not in simbase.air.doId2do:
            self.notify.warning('pet proxy %d not in doId2do!' % petProxyId)
            toonAttack[TOON_ACCBONUS_COL] = 1
            return (0, 0)
        petProxy = simbase.air.doId2do[petProxyId]
        trickId = toonAttack[TOON_LVL_COL]
        toonAttack[TOON_ACCBONUS_COL] = petProxy.attemptBattleTrick(trickId)
        if toonAttack[TOON_ACCBONUS_COL] == 1:
            return (0, 0)
        return (1, 100)