import sys, zlib
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.stdpy.file import *
from panda3d.core import NodePath, PandaNode, LVector3f
import DNAAnimBuilding, DNAAnimProp, DNABattleCell, DNACornice, DNADoor, DNAError, DNAFlatBuilding, DNAFlatDoor, DNAGroup, DNAInteractiveProp, DNALandmarkBuilding, DNANode, DNAProp, DNASign, DNASignBaseline, DNASignGraphic, DNASignText, DNAStreet, DNASuitPoint, DNAUtil, DNAVisGroup, DNAWall, DNAWindows
JAZZ_ASCII = '.....,,,.............................................:,.........................\nII?IIII~II?........................................+,?=?~:::....................\n?:I=IIII?=:?I:......................................,II+?~?II??~,...............\n7??I?IIIIIIIIII?......................................,=IIIIIIIII?=.............\n=??::++IIIIII?+III7:.. ....+=::,,,............   .....,~:?IIIIII????............\n,.:I=++?+IIIIII=I77II?,.......,=I7IIIIIII:....  .   ....::IIIIIII?II?,..........\n....:.,?II7I?II7I+IIIIII:....,..~,?IIIIIIII:..... .    ..+?~IIIIIIIII+,.........\n.....,,+~?II?IIIIII?IIIIII~:.,??I~+IIIIIIIIIII7I:..... ...~+?IIIIIIIIII:,,......\n.....~.,~,:?77?II?IIII+IIIII?,...:,+==I?IIIIIIIII?:... ....:=:IIIIIIII=I?=,.....\nI:......:.7+I?IIIIIIII+I+IIIIII~...,?III7+IIIIIIIIII~...  .....+IIIIIII+?III=,..\n$Z$7,.....:=I=+?IIIIII?,II?IIIII~,.,~.~:I7I7IIIIIIIII=,... ..:7~77IIIIII???III+:\nOO88OOZ$?7Z.$?IIIIII?:$OI,,::$IIIII~..=+??IIIIII??IIIII:......:II7?IIIIIIIIIIII?\n?I?7IIIII::$ZZOO8II??I:I+~,7O=OO$7III,~?+I?IIIIIII~8$III+.....~=~:IIIIIIII+I7II?\nO$IIIIIIIIII:,7$OZOI~?+II?~..,,8OZZO8I~+=II+=IIIIII7$88III=...~7$Z$I?IIIIIIIIIII\nIOZOIII7IIIIII=+???8ZZOZI??,...,I=8OOOOZ??II+IIIIIOO,~ZOZIII,,77$$$OZ$?IIIIIIIII\n$$I?ZOOIIIIIII?III?III7OOOOZ,...~II7I8OO$O7II?IIIII8$I..88O?I=.=I.I$OOOIIII?I??:\nO$ZO7$OZ$I7IIIIIIII????I7OZZO$?...I?+?I78OZO$IIIIIII8O7=,8OOZI7:?=7+?ZZO8OII7,II\nIIIII.:,.I:?IIIIIII?IIIIII?=ZO,$$...,+?:IIOOOO$II+?IIOZ7+.~+OZOII~Z$+?I7OOOI:+=?\n+II?I~I:...,+I?IIIIIIIIIIIII?II=,Z$?...=~?II7O8O$IIIII88II,,I+ZOOI$$O+IIIIOOO7=I\n+?II?II+=.....II?I?~I??II+I?,I?=+~=.,$..,+~~+?=+ZIOIIIIZII++.~IIOO8$?::II+~IOOIZ\nIIII::7~~?+,.....?,,:+I=I=?:~,:+.......+..,.~:?I?7OZOO7+$~?I:.,I?I?OOZ??IIIIIIO?\nIII+I7:==~+II,....,=~+==++II?==I+=,......=..=++?II?IOO88???II..,+II$ZO8~IIII?II,\n??III+7I=I7I~~,.....=+I+?~+~:??,=.... .. . .....+7IIIIIII?+?I,,,..?+IZOI+I+IIII?\nI+??IIIIII~,I=I:. ...=,,,,..~?~.,I..,...  .......+=I=??II?IIIII,,..=I?III,,II??I\n,.+~~+I+I~+II+:I....................... .     .....,.+?+I7~II=+I,....+I+~~,~?+=,\n...,II?::I::=.?=I,............... .. ...       .. ...,?II+:I++?I: ......=?++,~:?\n.... .,.I==I+,,.:I,....................................~I7??I~:+=:........~,.,.+\n.........,.II=+:.......................................=??III~,:I,..........?...\n..................................................... ..,:?I:~::+=,.,...........\n................................ ................ ... .....,=:?::::.............\n..............................................................I?:~~..,..........\n...............................................................,+~...~=.........\n..................................................................?,=?..........'
sys.setrecursionlimit(10000)
compClassTable = {1: DNAGroup.DNAGroup, 
   2: DNAVisGroup.DNAVisGroup, 
   3: DNANode.DNANode, 
   4: DNAProp.DNAProp, 
   5: DNASign.DNASign, 
   6: DNASignBaseline.DNASignBaseline, 
   7: DNASignText.DNASignText, 
   8: DNASignGraphic.DNASignGraphic, 
   9: DNAFlatBuilding.DNAFlatBuilding, 
   10: DNAWall.DNAWall, 
   11: DNAWindows.DNAWindows, 
   12: DNACornice.DNACornice, 
   13: DNALandmarkBuilding.DNALandmarkBuilding, 
   14: DNAAnimProp.DNAAnimProp, 
   15: DNAInteractiveProp.DNAInteractiveProp, 
   16: DNAAnimBuilding.DNAAnimBuilding, 
   17: DNADoor.DNADoor, 
   18: DNAFlatDoor.DNAFlatDoor, 
   19: DNAStreet.DNAStreet}
childlessComps = (7, 11, 12, 17, 18, 19)

class DNALoader:

    def __init__(self):
        self.dnaStorage = None
        self.prop = None
        return

    def destroy(self):
        del self.dnaStorage
        del self.prop

    def handleStorageData(self, dgi):
        numRoots = dgi.getUint16()
        for _ in xrange(numRoots):
            root = DNAUtil.dgiExtractString8(dgi)
            numCodes = dgi.getUint8()
            for i in xrange(numCodes):
                code = DNAUtil.dgiExtractString8(dgi)
                self.dnaStorage.storeCatalogCode(root, code)

        numTextures = dgi.getUint16()
        for _ in xrange(numTextures):
            code = DNAUtil.dgiExtractString8(dgi)
            filename = DNAUtil.dgiExtractString8(dgi)
            self.dnaStorage.storeTexture(code, loader.jazzTexture(filename, okMissing=True))

        numFonts = dgi.getUint16()
        for _ in xrange(numFonts):
            code = DNAUtil.dgiExtractString8(dgi)
            filename = DNAUtil.dgiExtractString8(dgi)
            self.dnaStorage.storeFont(code, loader.jazzFont(filename))

        self.handleNode(dgi, target=self.dnaStorage.storeNode)
        self.handleNode(dgi, target=self.dnaStorage.storeHoodNode)
        self.handleNode(dgi, target=self.dnaStorage.storePlaceNode)
        numBlocks = dgi.getUint16()
        for _ in xrange(numBlocks):
            number = dgi.getUint8()
            zone = dgi.getUint16()
            title = DNAUtil.dgiExtractString8(dgi)
            article = DNAUtil.dgiExtractString8(dgi)
            bldgType = DNAUtil.dgiExtractString8(dgi)
            self.dnaStorage.storeBlock(number, title, article, bldgType, zone)

        numPoints = dgi.getUint16()
        for _ in xrange(numPoints):
            index = dgi.getUint16()
            pointType = dgi.getUint8()
            x, y, z = (dgi.getInt32() / 100.0 for i in xrange(3))
            graph = dgi.getUint8()
            landmarkBuildingIndex = dgi.getInt8()
            self.dnaStorage.storeSuitPoint(DNASuitPoint.DNASuitPoint(index, pointType, LVector3f(x, y, z), landmarkBuildingIndex))

        numEdges = dgi.getUint16()
        for _ in xrange(numEdges):
            index = dgi.getUint16()
            numPoints = dgi.getUint16()
            for i in xrange(numPoints):
                endPoint = dgi.getUint16()
                zoneId = dgi.getUint16()
                self.dnaStorage.storeSuitEdge(index, endPoint, zoneId)

        numCells = dgi.getUint16()
        for _ in xrange(numCells):
            w = dgi.getUint8()
            h = dgi.getUint8()
            x, y, z = (dgi.getInt32() / 100.0 for i in xrange(3))
            self.dnaStorage.storeBattleCell(DNABattleCell.DNABattleCell(w, h, LVector3f(x, y, z)))

    def handleCompData(self, dgi):
        while True:
            propCode = dgi.getUint8()
            if propCode == 255:
                if self.prop == None:
                    raise DNAError.DNAError('Unexpected 255 found.')
                prop = self.prop.getParent()
                if prop is not None:
                    self.prop = prop
            else:
                if propCode in compClassTable:
                    propClass = compClassTable[propCode]
                    if propClass.__init__.func_code.co_argcount > 1:
                        newComp = propClass('unnamed_comp')
                    else:
                        newComp = propClass()
                    if propCode == 2:
                        newComp.makeFromDGI(dgi, self.dnaStorage)
                        self.dnaStorage.storeDNAVisGroup(newComp)
                    else:
                        newComp.makeFromDGI(dgi)
                else:
                    raise DNAError.DNAError('Invalid prop code: %d' % propCode)
            if dgi.getRemainingSize():
                if propCode != 255:
                    if self.prop is not None:
                        newComp.setParent(self.prop)
                        self.prop.add(newComp)
                    if propCode not in childlessComps:
                        self.prop = newComp
                continue
            break

        return

    def handleNode(self, dgi, target=None):
        if target is None:
            return
        numNodes = dgi.getUint16()
        for _ in xrange(numNodes):
            code = DNAUtil.dgiExtractString8(dgi)
            file = DNAUtil.dgiExtractString8(dgi)
            node = DNAUtil.dgiExtractString8(dgi)
            np = NodePath(loader.jazzModel(file))
            if node:
                newNode = np.find('**/' + node).copyTo(NodePath())
                np.removeNode()
                np = newNode
            np.setTag('DNACode', code)
            np.setTag('DNARoot', node)
            target(np, code)

        return

    def loadDNAFileBase(self, dnaStorage, file):
        self.dnaStorage = dnaStorage
        dnaFile = open(file, 'rb')
        dnaData = dnaFile.read()
        dg = PyDatagram(dnaData)
        dgi = PyDatagramIterator(dg)
        dnaFile.close()
        header = dgi.extractBytes(2673)
        if header != JAZZ_ASCII + '\n':
            raise DNAError.DNAError('Invalid header: %s' % header)
        compressed = dgi.getBool()
        dgi.skipBytes(1)
        if compressed:
            data = dgi.getRemainingBytes()
            data = zlib.decompress(data)
            dg = PyDatagram(data)
            dgi = PyDatagramIterator(dg)
        self.handleStorageData(dgi)
        self.handleCompData(dgi)

    def loadDNAFile(self, dnaStorage, file):
        self.loadDNAFileBase(dnaStorage, file)
        nodePath = NodePath(PandaNode('dna'))
        self.prop.traverse(nodePath, self.dnaStorage)
        return nodePath

    def loadDNAFileAI(self, dnaStorage, file):
        self.loadDNAFileBase(dnaStorage, file)
        return self.prop