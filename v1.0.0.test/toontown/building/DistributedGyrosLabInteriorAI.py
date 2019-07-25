from toontown.building import DistributedToonInteriorAI

class DistributedGyrosLabInteriorAI(DistributedToonInteriorAI.DistributedToonInteriorAI):

    def __init__(self, block, air, zoneId, building):
        DistributedToonInteriorAI.DistributedToonInteriorAI.__init__(self, block, air, zoneId, building)