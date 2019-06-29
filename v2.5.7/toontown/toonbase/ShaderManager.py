from panda3d.core import *
from direct.directnotify import DirectNotifyGlobal
from direct.showbase import DirectObject
from direct.task import Task

class ShaderManager(DirectObject.DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('ShaderManager')

    def __init__(self):
        DirectObject.DirectObject.__init__(self)
        self.shader = None
        self.framebuffer = None
        self.framebufferDims = (-1, -1)
        self.txBuff = None
        return

    def hasDynamicFramebuffer(self):
        return self.framebuffer is not None and self.txBuff is not None and self.framebufferDims == (0,
                                                                                                     0)

    def enableRetroShader(self):
        if self.shader:
            self.notify.warning(('Tried to enable retro shader when shader {0} is already in use').format(self.shader.getFilename()))
            return
        self.shader = Shader.load(Shader.SL_GLSL, 'phase_3/models/shaders/retro.vert.glsl', 'phase_3/models/shaders/retro.frag.glsl')
        self.makeFramebuffer(320, 224, self.updateRetroShader)

    def makeFramebuffer(self, x=0, y=0, updateTask=None):
        if self.framebuffer is not None and self.framebufferDims == (x, y):
            self.notify.info('Sufficient framebuffer exists, skipping call to makeFramebuffer')
            return
        if self.framebuffer is not None:
            self.removeFramebuffer()
        cm = CardMaker('card')
        cm.setFrameFullscreenQuad()
        if x and y:
            self.txBuff = base.win.makeTextureBuffer('shaderfb', x, y)
            self.framebufferDims = (x, y)
        else:
            self.txBuff = base.win.makeTextureBuffer('shaderfb', base.win.getXSize(), base.win.getYSize())
            self.framebufferDims = (0, 0)
        cm.setUvRange(self.txBuff.getTexture())
        self.framebuffer = render2d.attachNewNode(cm.generate())
        self.framebuffer.setTexture(self.txBuff.getTexture())
        if updateTask is not None:
            updateTask(None)
            taskMgr.add(updateTask, self.taskName('updateShader'))
        self.framebuffer.setShader(self.shader)
        base.makeCamera(self.txBuff, useCamera=base.cam)
        return

    def removeShader(self):
        taskMgr.remove(self.taskName('updateShader'))
        if self.shader is None:
            return
        if self.framebuffer is not None:
            self.framebuffer.clearShader()
            self.removeFramebuffer()
        self.shader.releaseAll()
        self.shader = None
        return

    def removeFramebuffer(self):
        taskMgr.remove(self.taskName('updateShader'))
        if self.txBuff is not None:
            self.txBuff.clearRenderTextures()
            self.txBuff = None
        if self.framebuffer is not None:
            self.framebuffer.removeNode()
            self.framebuffer = None
        self.framebufferDims = (-1, -1)
        return

    def taskName(self, task):
        return ('{0}-{1}').format(task, id(self))

    def updateRetroShader(self, task):
        self.framebuffer.setShaderInput('sourceDims', (base.win.getXSize(), base.win.getYSize()))
        return Task.cont