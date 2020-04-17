import ClothesGUI
from toontown.toon import ToonDNA

class MakeClothesGUI(ClothesGUI.ClothesGUI):
    notify = directNotify.newCategory('MakeClothesGUI')

    def __init__(self, doneEvent):
        ClothesGUI.ClothesGUI.__init__(self, ClothesGUI.CLOTHES_MAKETOON, doneEvent)

    def setupScrollInterface(self):
        self.dna = self.toon.getStyle()
        gender = self.dna.getGender()
        self.topStyles = ToonDNA.getTopStyles(gender, tailorId=ToonDNA.MAKE_A_TOON)
        self.tops = ToonDNA.getTops(gender, tailorId=ToonDNA.MAKE_A_TOON)
        self.bottomStyles = ToonDNA.getBottomStyles(gender, tailorId=ToonDNA.MAKE_A_TOON)
        self.bottoms = ToonDNA.getBottoms(gender, tailorId=ToonDNA.MAKE_A_TOON)
        self.gender = gender
        if gender == 'm':
            gId = 'b'
        else:
            gId = 'g'
        self.topChoice = 0
        for style in ToonDNA.ShirtStyles.keys():
            if style[0] == gId:
                if (
                 ToonDNA.ShirtStyles[style][0], ToonDNA.ShirtStyles[style][1]) == (self.dna.topTex, self.dna.sleeveTex):
                    self.topColorChoice = ToonDNA.ShirtStyles[style][2].index((self.dna.topTexColor, self.dna.sleeveTexColor))

        self.topStyleChoice = self.topStyles.index((self.dna.topTex, self.dna.sleeveTex))
        self.bottomChoice = 0
        for style in ToonDNA.BottomStyles.keys():
            if style[0] == gId:
                if ToonDNA.BottomStyles[style][0] == self.dna.botTex:
                    self.bottomColorChoice = ToonDNA.BottomStyles[style][1].index(self.dna.botTexColor)

        self.bottomStyleChoice = self.bottomStyles.index(self.dna.botTex)
        self.setupButtons()

    def setupButtons(self):
        ClothesGUI.ClothesGUI.setupButtons(self)
        if len(self.dna.torso) == 1 and not self.nude:
            if self.gender == 'm':
                torsoStyle = 's'
            elif self.girlInShorts == 1:
                torsoStyle = 's'
            else:
                torsoStyle = 'd'
            self.toon.swapToonTorso(self.dna.torso[0] + torsoStyle)
            self.toon.loop('neutral', 0)
            self.toon.swapToonColor(self.dna)
            self.swapTop(0)
            self.swapBottom(0)
        return