import json, os, random, time
from direct.directnotify import DirectNotifyGlobal
from toontown.pets import PetDNA
from toontown.pets import PetNameGenerator
from toontown.pets import PetUtil
from toontown.toonbase import ToontownGlobals
MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR

def getDayId():
    return int(time.time() // DAY)


class PetManagerAI:
    notify = DirectNotifyGlobal.directNotify.newCategory('PetManagerAI')
    NUM_DAILY_PETS = 5
    cachePath = config.GetString('air-pet-cache', 'backups/pets/')

    def __init__(self, air):
        self.air = air
        self.cacheFile = '%spets_%d.json' % (self.cachePath, self.air.districtId)
        if not os.path.exists(self.cachePath):
            os.makedirs(self.cachePath)
        if os.path.isfile(self.cacheFile):
            with open(self.cacheFile, 'rb') as (f):
                data = f.read()
            self.seeds = json.loads(data)
            if self.seeds.get('day', -1) != getDayId() or len(self.seeds.get(ToontownGlobals.ToontownCentral, [])) != self.NUM_DAILY_PETS:
                self.generateSeeds()
        else:
            self.generateSeeds()
        self.nameGen = PetNameGenerator.PetNameGenerator()

    def generateSeeds(self):
        seeds = range(0, 255)
        random.shuffle(seeds)
        self.seeds = {}
        for hood in (ToontownGlobals.ToontownCentral, ToontownGlobals.DonaldsDock, ToontownGlobals.DaisyGardens,
         ToontownGlobals.MinniesMelodyland, ToontownGlobals.TheBrrrgh, ToontownGlobals.DonaldsDreamland):
            self.seeds[hood] = [ seeds.pop() for _ in xrange(self.NUM_DAILY_PETS) ]

        self.seeds['day'] = getDayId()
        with open(self.cacheFile, 'wb') as (f):
            f.write(json.dumps(self.seeds))

    def getAvailablePets(self, seed, safezoneId):
        if self.seeds.get('day', -1) != getDayId():
            self.generateSeeds()
        return list(set(self.seeds.get(safezoneId, [seed])))

    def createNewPetFromSeed(self, avId, seed, nameIndex, gender, safeZoneId):
        av = self.air.doId2do.get(avId)
        if not av:
            return
        name = self.nameGen.getName(nameIndex)
        _, dna, traitSeed = PetUtil.getPetInfoFromSeed(seed, safeZoneId)
        head, ears, nose, tail, body, color, cs, eye, _ = dna
        numGenders = len(PetDNA.PetGenders)
        gender %= numGenders
        fields = {'setOwnerId': avId, 'setPetName': name, 'setTraitSeed': traitSeed, 'setSafeZone': safeZoneId, 'setHead': head, 
           'setEars': ears, 'setNose': nose, 'setTail': tail, 'setBodyTexture': body, 'setColor': color, 
           'setColorScale': cs, 'setEyeColor': eye, 'setGender': gender}

        def response(doId):
            if not doId:
                self.notify.warning('Cannot create pet for %s!' % avId)
                return
            self.air.writeServerEvent('bought-pet', avId=avId, petId=doId)
            av.b_setPetId(doId)

        self.air.dbInterface.createObject(self.air.dbId, self.air.dclassesByName['DistributedPetAI'], {k:(v,) for k, v in fields.items()}, response)

    def deleteToonsPet(self, avId):
        av = self.air.doId2do.get(avId)
        if not av:
            return
        pet = self.air.doId2do.get(av.getPetId())
        if pet:
            pet.requestDelete()
        av.b_setPetId(0)
        self.air.writeServerEvent('returned-pet', avId=avId, pet=pet)