from direct.directnotify import DirectNotifyGlobal
from toontown.building.DistributedToonInteriorAI import DistributedToonInteriorAI
from otp.ai.MagicWordGlobal import *

class DistributedToonHallInteriorAI(DistributedToonInteriorAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedToonHallInteriorAI')