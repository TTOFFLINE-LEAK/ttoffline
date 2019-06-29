from direct.directnotify import DirectNotifyGlobal
from DNAStorage import DNAStorage
from toontown.classicfishing.DistributedClassicFishingSpotAI import DistributedClassicFishingSpotAI
from toontown.fishing import FishingTargetGlobals
from toontown.fishing.DistributedFishingPondAI import DistributedFishingPondAI
from toontown.fishing.DistributedFishingTargetAI import DistributedFishingTargetAI
from toontown.fishing.DistributedPondBingoManagerAI import DistributedPondBingoManagerAI
from toontown.racing import RaceGlobals
from toontown.racing.DistributedRacePadAI import DistributedRacePadAI
from toontown.racing.DistributedStartingBlockAI import DistributedStartingBlockAI, DistributedViewingBlockAI
from toontown.racing.DistributedViewPadAI import DistributedViewPadAI
from toontown.safezone import DistributedPicnicBasketAI, DistributedPicnicTableAI, DistributedGolfKartAI
from toontown.safezone.DistributedFishingSpotAI import DistributedFishingSpotAI
from toontown.safezone.DistributedPartyGateAI import DistributedPartyGateAI
from toontown.toon import NPCToons

class DNASpawnerAI:
    notify = DirectNotifyGlobal.directNotify.newCategory('DNASpawnerAI')

    def spawnObjects(self, filename, baseZone):
        dnaStore = DNAStorage()
        dnaData = simbase.air.loadDNAFileAI(dnaStore, filename)
        self._createObjects(dnaData, baseZone)

    def _createObjects(self, group, zone):
        if not group:
            self.notify.warning(('Bad group in zone {0}!').format(zone))
            return
        if group.getName()[:13] == 'fishing_pond_':
            visGroup = group.getVisGroup()
            if visGroup is None:
                pondZone = zone
            else:
                pondZone = int(visGroup.getName().split(':')[0])
            pond = DistributedFishingPondAI(simbase.air)
            pond.setArea(zone)
            pond.generateWithRequired(pondZone)
            bingoManager = DistributedPondBingoManagerAI(simbase.air)
            bingoManager.setPondDoId(pond.getDoId())
            bingoManager.generateWithRequired(pondZone)
            bingoManager.createGame()
            pond.bingoMgr = bingoManager
            simbase.air.fishManager.ponds[zone] = pond
            for i in range(FishingTargetGlobals.getNumTargets(zone)):
                target = DistributedFishingTargetAI(simbase.air)
                target.setPondDoId(pond.getDoId())
                target.generateWithRequired(pondZone)

            for i in range(group.getNumChildren()):
                posSpot = group.at(i)
                if posSpot.getName()[:13] == 'fishing_spot_':
                    spot = DistributedFishingSpotAI(simbase.air)
                    spot.setPondDoId(pond.getDoId())
                    x, y, z = posSpot.getPos()
                    h, p, r = posSpot.getHpr()
                    spot.setPosHpr(x, y, z, h, p, r)
                    spot.generateWithRequired(pondZone)
                elif posSpot.getName()[:21] == 'classic_fishing_spot_':
                    spot = DistributedClassicFishingSpotAI(simbase.air)
                    spot.setPondDoId(pond.getDoId())
                    x, y, z = posSpot.getPos()
                    h, p, r = posSpot.getHpr()
                    spot.setPosHpr(x, y, z, h, p, r)
                    spot.generateWithRequired(pondZone)

            NPCToons.createNpcsInZone(simbase.air, pondZone)
        else:
            if group.getName()[:10] == 'racing_pad':
                index, dest = group.getName()[11:].split('_', 2)
                index = int(index)
                pad = DistributedRacePadAI(simbase.air)
                pad.setArea(zone)
                pad.nameType = dest
                pad.index = index
                nri = RaceGlobals.getNextRaceInfo(-1, dest, index)
                pad.setTrackInfo([nri[0], nri[1]])
                pad.generateWithRequired(zone)
                for i in range(group.getNumChildren()):
                    posSpot = group.at(i)
                    if posSpot.getName()[:14] == 'starting_block':
                        x, y, z = posSpot.getPos()
                        h, p, r = posSpot.getHpr()
                        startingBlock = DistributedStartingBlockAI(simbase.air)
                        startingBlock.setPosHpr(x, y, z, h, p, r)
                        startingBlock.setPadDoId(pad.getDoId())
                        startingBlock.setPadLocationId(index)
                        startingBlock.generateWithRequired(zone)
                        pad.addStartingBlock(startingBlock)

            else:
                if group.getName()[:11] == 'viewing_pad':
                    pad = DistributedViewPadAI(simbase.air)
                    pad.setArea(zone)
                    pad.generateWithRequired(zone)
                    for i in range(group.getNumChildren()):
                        posSpot = group.at(i)
                        if posSpot.getName()[:14] == 'starting_block':
                            x, y, z = posSpot.getPos()
                            h, p, r = posSpot.getHpr()
                            startingBlock = DistributedViewingBlockAI(simbase.air)
                            startingBlock.setPosHpr(x, y, z, h, p, r)
                            startingBlock.setPadDoId(pad.getDoId())
                            startingBlock.setPadLocationId(0)
                            startingBlock.generateWithRequired(zone)
                            pad.addStartingBlock(startingBlock)

                else:
                    if group.getName()[:13] == 'picnic_table_':
                        pos = group.getPos()
                        hpr = group.getHpr()
                        nameInfo = group.getName().split('_')
                        picnicTable = DistributedPicnicBasketAI.DistributedPicnicBasketAI(simbase.air, nameInfo[2], pos[0], pos[1], pos[2], hpr[0], hpr[1], hpr[2])
                        picnicTable.generateWithRequired(zone)
                        picnicTable.start()
                    else:
                        if (group.getName() == 'prop_game_table_DNARoot' or group.getName()[:13] == 'game_table_') and config.GetBool('want-picnic-games', True):
                            pos = group.getPos()
                            hpr = group.getHpr()
                            nameInfo = group.getName().split('_')
                            tableIndex = int(group.getParent().getName().split('_')[(-1)])
                            picnicTable = DistributedPicnicTableAI.DistributedPicnicTableAI(simbase.air, zone, nameInfo[2], pos[0], pos[1], pos[2], hpr[0], hpr[1], hpr[2])
                            picnicTable.setTableIndex(tableIndex)
                            picnicTable.generateOtpObject(simbase.air.districtId, zone, [
                             'setX', 'setY', 'setZ', 'setH', 'setP', 'setR'])
                        else:
                            if group.getName()[:9] == 'golf_kart' and config.GetBool('want-golf-karts', True):
                                info = group.getName()[10:].split('_')
                                golfCourse = int(info[0])
                                for i in range(group.getNumChildren()):
                                    prop = group.at(i)
                                    if prop.getName()[:15] == 'starting_block_':
                                        pos, hpr = prop.getPos(), prop.getHpr()

                                kart = DistributedGolfKartAI.DistributedGolfKartAI(simbase.air, golfCourse, pos[0], pos[1], pos[2], hpr[0], hpr[1], hpr[2])
                                kart.generateWithRequired(zone)
                                kart.sendUpdate('setGolfCourse', [golfCourse])
                                kart.sendUpdate('setPosHpr', [pos[0], pos[1], pos[2], hpr[0], hpr[1], hpr[2]])
                                color = kart.getColor()
                                kart.sendUpdate('setColor', [color[0], color[1], color[2]])
                                kart.start()
        if group.getName()[:15] == 'prop_party_gate' and config.GetBool('want-parties', True):
            gate = DistributedPartyGateAI(simbase.air)
            gate.setArea(zone)
            gate.generateWithRequired(zone)
        for i in range(group.getNumChildren()):
            child = group.at(i)
            self._createObjects(child, zone)

        return