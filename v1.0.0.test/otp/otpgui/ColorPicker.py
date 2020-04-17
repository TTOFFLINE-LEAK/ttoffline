from panda3d.core import NodePath, PNMImage, Texture, Xel
from direct.gui.DirectGui import *
from otp.otpbase import OTPGlobals
import colorsys

class ColorPicker(NodePath):

    def __init__(self, parent, minSat, maxSat, minVal, maxVal, callback, pos=(0, 0, 0)):
        NodePath.__init__(self, 'colorPicker')
        self.reparentTo(parent)
        self.setPos(pos)
        self.minSat = minSat
        self.maxSat = maxSat
        self.minVal = minVal
        self.maxVal = maxVal
        self.callback = callback
        self.lastColor = None
        self.image = PNMImage(int((self.maxSat - self.minSat) * 100), int((self.maxVal - self.minVal) * 100))
        self.slider = DirectSlider(self, relief=None, image='phase_3/maps/color_picker_hue.jpg', scale=0.3, pos=(0.2,
                                                                                                                 0,
                                                                                                                 0), image_scale=(0.1,
                                                                                                                                  1.0,
                                                                                                                                  1.0), pageSize=5, orientation=DGG.VERTICAL, command=self.__chooseHue)
        self.button = DirectButton(self, relief=None, image=OTPGlobals.getTransparentTexture(), scale=0.3, pos=(-0.2,
                                                                                                                0,
                                                                                                                0), frameColor=(1,
                                                                                                                                1,
                                                                                                                                1,
                                                                                                                                0.1), pressEffect=0)
        self.button.bind(DGG.B1PRESS, self.__startPick)
        self.button.bind(DGG.B1RELEASE, self.__stopPick)
        self.__chooseHue()
        return

    def uniqueName(self, name):
        return 'ColorPicker-%s-%s' % (id(self), name)

    def removeNode(self):
        NodePath.removeNode(self)
        self.destroy()

    def destroy(self):
        if not self.slider:
            return
        else:
            self.__stopPick()
            self.slider.destroy()
            self.button.destroy()
            self.slider = None
            self.button = None
            self.image = None
            return

    def __calcRelative(self, value, baseMin, baseMax, limitMin, limitMax):
        return (limitMax - limitMin) * (value - baseMin) / (baseMax - baseMin) + limitMin

    def __chooseHue(self):
        for x in xrange(self.image.getXSize()):
            for y in xrange(self.image.getYSize()):
                self.image.setXel(x, y, colorsys.hsv_to_rgb(self.slider['value'], x / 100.0 + self.minSat, y / 100.0 + self.minVal))

        texture = Texture()
        texture.load(self.image)
        self.button['image'] = texture

    def __pickColor(self, task):
        x = base.mouseWatcherNode.getMouseX()
        y = base.mouseWatcherNode.getMouseY()
        win_w, win_h = base.win.getSize()
        if win_w < win_h:
            y *= 1.0 * win_h / win_w
        else:
            x *= 1.0 * win_w / win_h
        x -= self.button.getX(aspect2d)
        y -= self.button.getZ(aspect2d)
        image_scale = self.button['image_scale']
        x = 0.5 + x / (2.0 * self.button.getSx(aspect2d) * image_scale[0])
        y = 0.5 + y / -(2.0 * self.button.getSz(aspect2d) * image_scale[2])
        if not (0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
            return task.cont
        x = self.__calcRelative(x, 0.0, 1.0, self.minSat, self.maxSat)
        y = self.__calcRelative(y, 0.0, 1.0, self.minVal, self.maxVal)
        rgb = colorsys.hsv_to_rgb(self.slider['value'], x, y) + (1, )
        rgb = tuple([ float('%.2f' % x) for x in rgb ])
        if self.lastColor != rgb:
            self.callback(rgb)
            self.lastColor = rgb
        return task.cont

    def __startPick(self, extra=None):
        self.__stopPick()
        taskMgr.add(self.__pickColor, self.uniqueName('colorDragTask'))

    def __stopPick(self, extra=None):
        taskMgr.remove(self.uniqueName('colorDragTask'))