from toontown.makeatoon import ClothesGUI
import ToonDNA

class TailorClothesGUI(ClothesGUI.ClothesGUI):
    notify = directNotify.newCategory('MakeClothesGUI')

    def __init__(self, doneEvent, swapEvent, tailorId):
        ClothesGUI.ClothesGUI.__init__(self, ClothesGUI.CLOTHES_TAILOR, doneEvent, swapEvent)
        self.tailorId = tailorId

    def setupScrollInterface(self):
        self.dna = self.toon.getStyle()
        gender = self.dna.getGender()
        if self.swapEvent != None:
            self.topStyles = ToonDNA.getTopStyles(gender, tailorId=self.tailorId)
            self.tops = ToonDNA.getTops(gender, tailorId=self.tailorId)
            self.bottomStyles = ToonDNA.getBottomStyles(gender, tailorId=self.tailorId)
            self.bottoms = ToonDNA.getBottoms(gender, tailorId=self.tailorId)
            self.gender = gender
            self.topChoice = -1
            self.topStyleChoice = -1
            self.topColorChoice = -1
            self.bottomChoice = -1
            self.bottomStyleChoice = -1
            self.bottomColorChoice = -1
        self.setupButtons()
        return