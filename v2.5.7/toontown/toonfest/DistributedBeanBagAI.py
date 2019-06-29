from toontown.safezone.DistributedTreasureAI import DistributedTreasureAI

class DistributedBeanBagAI(DistributedTreasureAI):

    def __init__(self, air, treasurePlanner, x, y, z, value):
        DistributedTreasureAI.__init__(self, air, treasurePlanner, 0, x, y, z, None)
        self.value = value
        return

    def getValue(self):
        return self.value

    def setValue(self, value):
        self.value = value