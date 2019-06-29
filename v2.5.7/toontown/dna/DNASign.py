from panda3d.core import LVector4f, ModelNode
import DNANode, DNAUtil

class DNASign(DNANode.DNANode):
    COMPONENT_CODE = 5

    def __init__(self):
        DNANode.DNANode.__init__(self, '')
        self.code = ''
        self.color = LVector4f(1, 1, 1, 1)

    def getCode(self):
        return self.code

    def setCode(self, code):
        self.code = code

    def getColor(self):
        return self.color

    def setColor(self, color):
        self.color = color

    def makeFromDGI(self, dgi):
        DNANode.DNANode.makeFromDGI(self, dgi)
        self.code = DNAUtil.dgiExtractString8(dgi)
        self.color = DNAUtil.dgiExtractColor(dgi)

    def traverse(self, nodePath, dnaStorage):
        decalNode = nodePath.find('**/sign_decal')
        if decalNode.isEmpty():
            decalNode = nodePath.find('**/*_front')
        if decalNode.isEmpty() or not decalNode.getNode(0).isGeomNode():
            decalNode = nodePath.find('**/+GeomNode')
        if self.code:
            node = dnaStorage.findNode(self.code)
            node = node.copyTo(decalNode)
            node.setName('sign')
        else:
            node = ModelNode('sign')
            node = decalNode.attachNewNode(node)
        if 'linktunnel_' in nodePath.getName() and 'hq_' in nodePath.getName():
            node.setDepthOffset(1000)
        else:
            node.setDepthOffset(50)
        signOrigin = nodePath.find('**/*sign_origin')
        node.setPosHprScale(signOrigin, self.pos, self.hpr, self.scale)
        node.setColor(self.color)
        node.wrtReparentTo(signOrigin, 0)
        for child in self.children:
            child.traverse(node, dnaStorage)

        node.flattenStrong()