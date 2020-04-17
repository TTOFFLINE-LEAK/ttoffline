from panda3d.core import *
from direct.directnotify import DirectNotifyGlobal
from direct.distributed.ClockDelta import *
from direct.distributed import DistributedObject
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from direct.task.Task import Task
from libotp import WhisperPopup
from otp.otpbase import OTPGlobals
from otp.otpbase import PythonUtil
from otp.otpgui.ColorPicker import ColorPicker
from toontown.battle import BattleProps
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from collections import OrderedDict
import json, os, time

class DistributedPropGenerator(DistributedObject.DistributedObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPropGenerator')

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        self.propTag = 'spawnPropTag'
        self.propNode = None
        self.propList = {}
        self.propData = {}
        self.selectedProp = None
        self.currentPage = 0
        self.currentProp = -1
        self.pages = []
        self.editorGUI = None
        self.generatorGUI = None
        self.propInfoPanels = []
        self.propInfoLabels = []
        self.previewProp = None
        self.previewPropPanel = None
        self.windowOpen = 0
        self.colorPageToggle = False
        self.availablePropPreviews = range(0, len(BattleProps.globalPropPool.propStrings.keys()))
        self.hiddenPropPreviews = []
        self.savedValues = {}
        self.totalPropCount = None
        self.serverPropList = []
        return

    def announceGenerate(self):
        DistributedObject.DistributedObject.announceGenerate(self)
        self.load()

    def disable(self):
        DistributedObject.DistributedObject.disable(self)
        self.unload()

    def load(self):
        base.cr.propGenerator = self
        self.propNode = render.attachNewNode('propNode')
        self.generatePropEditor()
        self.ccPropTrav = CollisionTraverser('PropGenerator.ccTrav')
        self.ccPropQueue = CollisionHandlerQueue()
        pickerNode = CollisionNode('mouseRay')
        pickerNP = base.camera.attachNewNode(pickerNode)
        pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
        self.pickerRay = CollisionRay()
        pickerNode.addSolid(self.pickerRay)
        self.ccPropTrav.addCollider(pickerNP, self.ccPropQueue)
        self.accept('mouse1', self.checkClick)
        self.accept('f11', self.openNewPropWindow)
        self.sendUpdate('requestProps')

    def loadProp(self, prop):
        self.serverPropList.append(prop)

    def loadProps(self):
        propsToReparent = []
        for prop in self.serverPropList:
            if prop[22]:
                propsToReparent.append(prop)
            self.spawnProp(prop)

        for prop in propsToReparent:
            propId = prop[0]
            reparentProp = prop[21]
            reparentState = prop[22]
            propInfo = self.propList[propId]
            secondaryPropInfo = self.propList[reparentProp]
            if reparentState == 1:
                propInfo[1].reparentTo(secondaryPropInfo[1])
            elif reparentState == 2:
                propInfo[1].wrtReparentTo(secondaryPropInfo[1])

    def savePropsToJson(self):
        propData = OrderedDict()
        for prop in self.propData.values():
            propInfo = OrderedDict()
            propInfo['propId'] = prop[0]
            propInfo['propName'] = prop[1]
            propInfo['x'] = prop[2]
            propInfo['y'] = prop[3]
            propInfo['z'] = prop[4]
            propInfo['h'] = prop[5]
            propInfo['p'] = prop[6]
            propInfo['r'] = prop[7]
            propInfo['sX'] = prop[8]
            propInfo['sY'] = prop[9]
            propInfo['sZ'] = prop[10]
            propInfo['csR'] = prop[11]
            propInfo['csG'] = prop[12]
            propInfo['csB'] = prop[13]
            propInfo['csA'] = prop[14]
            propInfo['spawnTime'] = prop[15]
            propInfo['creatorAvId'] = prop[16]
            propInfo['creatorName'] = prop[17]
            propInfo['editorAvId'] = prop[18]
            propInfo['editorName'] = prop[19]
            propInfo['lockedState'] = prop[20]
            propInfo['reparentProp'] = prop[21]
            propInfo['reparentState'] = prop[22]
            propData[prop[0]] = propInfo

        if not os.path.exists('props/'):
            os.mkdir('props/')
        fileName = base.cr.serverName + '-' + str(base.localAvatar.zoneId) + '-' + time.strftime('%Y%m%d-%H%M%S')
        with open('props/' + fileName + '.json', 'w') as (data):
            json.dump(propData, data, indent=4)
            data.close()

    def loadPropsFromJson(self):
        pass

    def unload(self):
        base.cr.propGenerator = None
        if self.propNode:
            self.propNode.removeNode()
            self.propNode = None
        if self.editorGUI:
            self.editorGUI.destroy()
            self.editorGUI = None
        if self.generatorGUI:
            self.generatorGUI.destroy()
            self.generatorGUI = None
        if self.previewProp:
            self.previewProp.removeNode()
            self.previewProp = None
        if self.previewPropPanel:
            self.previewPropPanel.destroy()
            self.previewPropPanel = None
        self.ignoreAll()
        return

    def checkClick(self):
        if not base.mouseWatcherNode.hasMouse():
            return
        mpos = base.mouseWatcherNode.getMouse()
        self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
        self.ccPropTrav.traverse(render)
        if self.ccPropQueue.getNumEntries() > 0:
            self.ccPropQueue.sortEntries()
            pickedObj = self.ccPropQueue.getEntry(0).getIntoNodePath()
            pickedObj = pickedObj.findNetTag(self.propTag)
            if not pickedObj.isEmpty():
                if self.isAccepting('selectSecondaryProp') and pickedObj != self.selectedProp:
                    messenger.send('selectSecondaryProp', [pickedObj])
                    return
                self.openPropEditor(pickedObj)
            elif self.windowOpen == 1:
                if self.isAccepting('selectSecondaryProp'):
                    messenger.send('selectSecondaryProp', [0])
                    return
                self.closePropEditor()
            elif self.windowOpen == 2:
                self.closeNewPropWindow()
            else:
                return

    def d_spawnProp(self):
        if not self.previewProp:
            return
        x, y, z = base.localAvatar.getPos()
        h, p, r = base.localAvatar.getHpr()
        propName = BattleProps.globalPropPool.propStrings.keys()[self.currentProp]
        self.sendUpdate('d_spawnProp', [propName, x, y, z, h, p, r, 1.0, 1.0, 1.0])

    def spawnProp(self, propData):
        self.propData[propData[0]] = propData
        propId, propName, x, y, z, h, p, r, sX, sY, sZ, csR, csG, csB, csA, spawnTime, creatorAvId, creatorName, editorAvId, editorName, lockedState, reparentProp, reparentState = propData
        self.addProp(propId, propName, (x, y, z, h, p, r, sX, sY, sZ), (csR, csG, csB, csA), spawnTime, creatorAvId, creatorName, editorAvId, editorName, lockedState, reparentProp, reparentState)

    def addProp(self, propId, propName, propPosHprScale, propColorScale, spawnTime, creatorAvId, creatorName, editorAvId, editorName, lockedState, reparentProp, reparentState):
        if not BattleProps.globalPropPool.propTypes.get(propName, None):
            return
        else:
            prop = BattleProps.globalPropPool.getProp(propName)
            prop.flattenLight()
            prop.clearTransform()
            prop.reparentTo(self.propNode)
            if BattleProps.globalPropPool.propTypes[propName] == 'actor':
                prop.loop(propName)
            collisions = prop.findAllMatches('**/+CollisionNode')
            if collisions:
                for coll in collisions:
                    coll.stash()

            originalScale = prop.getScale()
            prop.setPosHprScale(*propPosHprScale)
            prop.setScale(prop.getScale().getX() * originalScale.getX(), prop.getScale().getY() * originalScale.getY(), prop.getScale().getZ() * originalScale.getZ())
            prop.setColorScale(*propColorScale)
            propInfo = [
             propName, prop, spawnTime, creatorAvId, creatorName, editorAvId, editorName, lockedState, reparentProp, reparentState]
            self.propList[propId] = propInfo
            prop.setTag(self.propTag, str(propId))
            self.updatePropCount()
            return

    def generatePropEditor(self):
        geom = loader.loadModel('phase_3/models/gui/dialog_box_gui')
        matModel = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui')
        submitButtonGui = loader.loadModel('phase_3/models/gui/quit_button')
        guiClose = loader.loadModel('phase_3.5/models/gui/avatar_panel_gui')
        cdrGui = loader.loadModel('phase_3.5/models/gui/tt_m_gui_sbk_codeRedemptionGui')
        arrow = [ matModel.find('**/tt_t_gui_mat_shuffleArrow' + name) for name in ('Up',
                                                                                    'Down',
                                                                                    'Up',
                                                                                    'Disabled') ]
        self.editorGUI = DirectButton(parent=base.a2dRightCenter, relief=None, pos=(-0.446,
                                                                                    0.0,
                                                                                    -0.22), scale=(0.57,
                                                                                                   0.57,
                                                                                                   0.57), geom=geom, geom_scale=(1.4,
                                                                                                                                 1,
                                                                                                                                 1), geom_color=(1,
                                                                                                                                                 1,
                                                                                                                                                 0.75,
                                                                                                                                                 1))
        self.editorGUI.bind(DGG.B1PRESS, self.dragStart, extraArgs=[0])
        self.editorGUI.bind(DGG.B1RELEASE, self.dragStop, extraArgs=[0])
        editLeftButton = DirectButton(self.editorGUI, relief=None, image_scale=0.7, image=arrow, pos=(-0.455,
                                                                                                      0.0,
                                                                                                      0.3925), command=self.changePage, extraArgs=[-1])
        editRightButton = DirectButton(self.editorGUI, relief=None, image_scale=(-0.7,
                                                                                 1,
                                                                                 0.7), image=arrow, pos=(0.455,
                                                                                                         0,
                                                                                                         0.3925), command=self.changePage, extraArgs=[1])
        self.generatorGUI = DirectButton(parent=base.a2dRightCenter, relief=None, pos=(-0.446,
                                                                                       0.0,
                                                                                       -0.22), scale=(0.57,
                                                                                                      0.57,
                                                                                                      0.57), geom=geom, geom_scale=(1.4,
                                                                                                                                    1,
                                                                                                                                    1), geom_color=(1,
                                                                                                                                                    1,
                                                                                                                                                    0.75,
                                                                                                                                                    1))
        self.generatorGUI.bind(DGG.B1PRESS, self.dragStart, extraArgs=[1])
        self.generatorGUI.bind(DGG.B1RELEASE, self.dragStop, extraArgs=[1])
        propPickerNode = self.generatorGUI.attachNewNode('propPickerNode')
        self.totalPropCount = DirectLabel(parent=propPickerNode, relief=None, text=TTLocalizer.PropGeneratorTotalCount % (
         len(self.propList.keys()), ToontownGlobals.MaxPropCount), text_scale=0.06, text_wordwrap=12, text_align=TextNode.ACenter, textMayChange=1, pos=(-0.175,
                                                                                                                                                         0,
                                                                                                                                                         -0.385))
        generateLeftButton = DirectButton(propPickerNode, relief=None, image_scale=0.7, image=arrow, pos=(-0.555,
                                                                                                          0.0,
                                                                                                          0.3925), command=self.changeProp, extraArgs=[-1])
        generateRightButton = DirectButton(propPickerNode, relief=None, image_scale=(-0.7,
                                                                                     1,
                                                                                     0.7), image=arrow, pos=(0.555,
                                                                                                             0,
                                                                                                             0.3925), command=self.changeProp, extraArgs=[1])
        self.propTitle = DirectButton(parent=propPickerNode, relief=None, text='splat-birthday-cake', text_scale=0.12, textMayChange=1, pos=(0,
                                                                                                                                             0,
                                                                                                                                             0.35), command=self.changeProp, extraArgs=[
         1])
        submitButton = DirectButton(parent=propPickerNode, relief=None, image=(
         submitButtonGui.find('**/QuitBtn_UP'),
         submitButtonGui.find('**/QuitBtn_DN'),
         submitButtonGui.find('**/QuitBtn_RLVR'),
         submitButtonGui.find('**/QuitBtn_UP')), image3_color=Vec4(0.5, 0.5, 0.5, 0.5), image_scale=1.15, state=DGG.NORMAL, text=TTLocalizer.PropGeneratorSpawn, text_scale=0.07, text_align=TextNode.ACenter, text_pos=(0,
                                                                                                                                                                                                                         -0.02), text3_fg=(0.5,
                                                                                                                                                                                                                                           0.5,
                                                                                                                                                                                                                                           0.5,
                                                                                                                                                                                                                                           0.75), textMayChange=0, pos=(0.389,
                                                                                                                                                                                                                                                                        0.0,
                                                                                                                                                                                                                                                                        -0.165), command=self.d_spawnProp)
        toggleSettingsButton = DirectButton(parent=propPickerNode, relief=None, image=(
         submitButtonGui.find('**/QuitBtn_UP'),
         submitButtonGui.find('**/QuitBtn_DN'),
         submitButtonGui.find('**/QuitBtn_RLVR'),
         submitButtonGui.find('**/QuitBtn_UP')), image3_color=Vec4(0.5, 0.5, 0.5, 0.5), image_scale=1.15, state=DGG.NORMAL, text=TTLocalizer.PropGeneratorSettings, text_scale=0.07, text_align=TextNode.ACenter, text_pos=(0,
                                                                                                                                                                                                                            -0.02), text3_fg=(0.5,
                                                                                                                                                                                                                                              0.5,
                                                                                                                                                                                                                                              0.5,
                                                                                                                                                                                                                                              0.75), textMayChange=0, pos=(0.389,
                                                                                                                                                                                                                                                                           0.0,
                                                                                                                                                                                                                                                                           -0.365), command=self.togglePropGeneratorSettings, extraArgs=[
         False])
        if base.localAvatar.getAccessLevel() < OTPGlobals.AccessLevelName2Int.get('MODERATOR'):
            toggleSettingsButton['state'] = DGG.DISABLED
        exitButton = DirectButton(parent=self.generatorGUI, relief=None, image=(
         guiClose.find('**/CloseBtn_UP'),
         guiClose.find('**/CloseBtn_DN'),
         guiClose.find('**/CloseBtn_Rllvr'),
         guiClose.find('**/CloseBtn_UP')), scale=1.5, pos=(-0.55, 0.0, -0.365), command=self.closeNewPropWindow)
        searchLabel = DirectLabel(parent=propPickerNode, relief=None, text=TTLocalizer.WordPageSearch, text_scale=0.08, text_wordwrap=12, text_align=TextNode.ACenter, textMayChange=1, pos=(0.389,
                                                                                                                                                                                             0,
                                                                                                                                                                                             0.2))
        searchBarFrame = DirectFrame(parent=propPickerNode, relief=None, image=cdrGui.find('**/tt_t_gui_sbk_cdrCodeBox'), pos=(0.389,
                                                                                                                               0.0,
                                                                                                                               0.0625), scale=0.7)
        self.searchBarEntry = DirectEntry(parent=propPickerNode, relief=None, text_scale=0.06, width=7.75, textMayChange=1, pos=(0.159,
                                                                                                                                 0,
                                                                                                                                 0.0625), text_align=TextNode.ALeft, backgroundFocus=0, focusInCommand=self.toggleEntryFocus)
        self.searchBarEntry.bind(DGG.TYPE, self.updateWordSearch)
        self.searchBarEntry.bind(DGG.ERASE, self.updateWordSearch)
        propSettingsNode = self.generatorGUI.attachNewNode('propSettingsNode')
        propSettingsNode.hide()
        zoneLabel = DirectLabel(parent=propSettingsNode, relief=None, text=TTLocalizer.PropGeneratorZone, text_scale=0.08, text_wordwrap=12, text_align=TextNode.ACenter, textMayChange=1, pos=(0.339,
                                                                                                                                                                                                0,
                                                                                                                                                                                                0.35))
        globalLabel = DirectLabel(parent=propSettingsNode, relief=None, text=TTLocalizer.PropGeneratorGlobal, text_scale=0.08, text_wordwrap=12, text_align=TextNode.ACenter, textMayChange=1, pos=(-0.369,
                                                                                                                                                                                                    0,
                                                                                                                                                                                                    0.35))
        deletePropsZoneButton = DirectButton(parent=propSettingsNode, relief=None, image=(
         submitButtonGui.find('**/QuitBtn_UP'),
         submitButtonGui.find('**/QuitBtn_DN'),
         submitButtonGui.find('**/QuitBtn_RLVR'),
         submitButtonGui.find('**/QuitBtn_UP')), image3_color=Vec4(0.5, 0.5, 0.5, 0.5), image_scale=1.15, state=DGG.NORMAL, text=TTLocalizer.PropGeneratorDeleteAllProps, text_scale=0.07, text_align=TextNode.ACenter, text_pos=(0,
                                                                                                                                                                                                                                  -0.02), text3_fg=(0.5,
                                                                                                                                                                                                                                                    0.5,
                                                                                                                                                                                                                                                    0.5,
                                                                                                                                                                                                                                                    0.75), textMayChange=0, pos=(0.339,
                                                                                                                                                                                                                                                                                 0,
                                                                                                                                                                                                                                                                                 0.15), command=self.confirmDeleteAllProps, extraArgs=[
         False])
        deletePropsGlobalButton = DirectButton(parent=propSettingsNode, relief=None, image=(
         submitButtonGui.find('**/QuitBtn_UP'),
         submitButtonGui.find('**/QuitBtn_DN'),
         submitButtonGui.find('**/QuitBtn_RLVR'),
         submitButtonGui.find('**/QuitBtn_UP')), image3_color=Vec4(0.5, 0.5, 0.5, 0.5), image_scale=1.15, state=DGG.NORMAL, text=TTLocalizer.PropGeneratorDeleteAllProps, text_scale=0.07, text_align=TextNode.ACenter, text_pos=(0,
                                                                                                                                                                                                                                  -0.02), text3_fg=(0.5,
                                                                                                                                                                                                                                                    0.5,
                                                                                                                                                                                                                                                    0.5,
                                                                                                                                                                                                                                                    0.75), textMayChange=0, pos=(-0.369,
                                                                                                                                                                                                                                                                                 0,
                                                                                                                                                                                                                                                                                 0.15), command=self.confirmDeleteAllProps, extraArgs=[
         True])
        lockPropsZoneButton = DirectButton(parent=propSettingsNode, relief=None, image=(
         submitButtonGui.find('**/QuitBtn_UP'),
         submitButtonGui.find('**/QuitBtn_DN'),
         submitButtonGui.find('**/QuitBtn_RLVR'),
         submitButtonGui.find('**/QuitBtn_UP')), image3_color=Vec4(0.5, 0.5, 0.5, 0.5), image_scale=1.15, state=DGG.NORMAL, text=TTLocalizer.PropGeneratorLockProps, text_scale=0.07, text_align=TextNode.ACenter, text_pos=(0,
                                                                                                                                                                                                                             -0.02), text3_fg=(0.5,
                                                                                                                                                                                                                                               0.5,
                                                                                                                                                                                                                                               0.5,
                                                                                                                                                                                                                                               0.75), textMayChange=0, pos=(0.339,
                                                                                                                                                                                                                                                                            0,
                                                                                                                                                                                                                                                                            -0.05), command=self.confirmLockProps, extraArgs=[False])
        lockPropsGlobalButton = DirectButton(parent=propSettingsNode, relief=None, image=(
         submitButtonGui.find('**/QuitBtn_UP'),
         submitButtonGui.find('**/QuitBtn_DN'),
         submitButtonGui.find('**/QuitBtn_RLVR'),
         submitButtonGui.find('**/QuitBtn_UP')), image3_color=Vec4(0.5, 0.5, 0.5, 0.5), image_scale=1.15, state=DGG.NORMAL, text=TTLocalizer.PropGeneratorLockProps, text_scale=0.07, text_align=TextNode.ACenter, text_pos=(0,
                                                                                                                                                                                                                             -0.02), text3_fg=(0.5,
                                                                                                                                                                                                                                               0.5,
                                                                                                                                                                                                                                               0.5,
                                                                                                                                                                                                                                               0.75), textMayChange=0, pos=(-0.369,
                                                                                                                                                                                                                                                                            0,
                                                                                                                                                                                                                                                                            -0.05), command=self.confirmLockProps, extraArgs=[True])
        toggleGeneratorButton = DirectButton(parent=propSettingsNode, relief=None, image=(
         submitButtonGui.find('**/QuitBtn_UP'),
         submitButtonGui.find('**/QuitBtn_DN'),
         submitButtonGui.find('**/QuitBtn_RLVR'),
         submitButtonGui.find('**/QuitBtn_UP')), image3_color=Vec4(0.5, 0.5, 0.5, 0.5), image_scale=1.15, state=DGG.NORMAL, text=TTLocalizer.PropGeneratorGenerator, text_scale=0.07, text_align=TextNode.ACenter, text_pos=(0,
                                                                                                                                                                                                                             -0.02), text3_fg=(0.5,
                                                                                                                                                                                                                                               0.5,
                                                                                                                                                                                                                                               0.5,
                                                                                                                                                                                                                                               0.75), textMayChange=0, pos=(0.389,
                                                                                                                                                                                                                                                                            0.0,
                                                                                                                                                                                                                                                                            -0.365), command=self.togglePropGeneratorSettings, extraArgs=[
         True])
        dumpPropsButton = DirectButton(parent=propSettingsNode, relief=None, image=(
         submitButtonGui.find('**/QuitBtn_UP'),
         submitButtonGui.find('**/QuitBtn_DN'),
         submitButtonGui.find('**/QuitBtn_RLVR'),
         submitButtonGui.find('**/QuitBtn_UP')), image3_color=Vec4(0.5, 0.5, 0.5, 0.5), image_scale=1.15, state=DGG.NORMAL, text=TTLocalizer.PropGeneratorDump, text_scale=0.07, text_align=TextNode.ACenter, text_pos=(0,
                                                                                                                                                                                                                        -0.02), text3_fg=(0.5,
                                                                                                                                                                                                                                          0.5,
                                                                                                                                                                                                                                          0.5,
                                                                                                                                                                                                                                          0.75), textMayChange=0, pos=(-0.189,
                                                                                                                                                                                                                                                                       0.0,
                                                                                                                                                                                                                                                                       -0.365), command=self.savePropsToJson)
        for title in TTLocalizer.PropEditorTitles:
            pageNode = self.editorGUI.attachNewNode(title + '_pageNode')
            pageNode.hide()
            spellbookTitle = DirectButton(parent=pageNode, relief=None, text=title, text_scale=0.12, textMayChange=1, pos=(0,
                                                                                                                           0,
                                                                                                                           0.35), command=self.changePage, extraArgs=[1])
            self.pages.append(pageNode)

        for effectList in TTLocalizer.PropEditorPages:
            effectPageIndex = TTLocalizer.PropEditorPages.index(effectList)
            infoEntryNode = self.pages[effectPageIndex].attachNewNode('infoEntryNode')
            if effectPageIndex == 0:
                for effect in effectList:
                    effectIndex = effectList.index(effect)
                    effectPageIndex = TTLocalizer.PropEditorPages.index(effectList)
                    infoLabel = DirectLabel(parent=self.pages[effectPageIndex], relief=None, text=effect, text_scale=0.07, textMayChange=1, pos=(
                     -0.629, 0.0, 0.3125 - 0.17 * (effectIndex + 1)), text_align=TextNode.ALeft)
                    self.propInfoLabels.append(infoLabel)

                exitButton = DirectButton(parent=self.pages[effectPageIndex], relief=None, image=(
                 guiClose.find('**/CloseBtn_UP'),
                 guiClose.find('**/CloseBtn_DN'),
                 guiClose.find('**/CloseBtn_Rllvr'),
                 guiClose.find('**/CloseBtn_UP')), scale=1.5, pos=(0.52, 0.0, -0.365), command=self.closePropEditor)
            if effectPageIndex == 1:
                for effect in effectList:
                    effectIndex = effectList.index(effect)
                    effectPageIndex = TTLocalizer.PropEditorPages.index(effectList)
                    if effectIndex in range(2):
                        pos = (
                         -0.3, 0.0, 0.3125 - 0.17 * (effectIndex + 1))
                    elif effectIndex in range(2, 4):
                        pos = (
                         0.3, 0.0, 0.3125 - 0.17 * (effectIndex - 1))
                    elif effectIndex == 4:
                        pos = (
                         -0.3, 0.0, 0.3125 - 0.17 * (effectIndex - 1))
                    settingsButton = DirectButton(parent=self.pages[effectPageIndex], relief=None, image=(
                     submitButtonGui.find('**/QuitBtn_UP'),
                     submitButtonGui.find('**/QuitBtn_DN'),
                     submitButtonGui.find('**/QuitBtn_RLVR'),
                     submitButtonGui.find('**/QuitBtn_UP')), image3_color=Vec4(0.5, 0.5, 0.5, 0.5), image_scale=1.15, state=DGG.NORMAL, text=effect, text_scale=0.07, text_align=TextNode.ACenter, text_pos=(0,
                                                                                                                                                                                                             -0.02), text3_fg=(0.5,
                                                                                                                                                                                                                               0.5,
                                                                                                                                                                                                                               0.5,
                                                                                                                                                                                                                               0.75), textMayChange=1, pos=pos, command=self.togglePropSettings, extraArgs=[effectIndex])
                    self.propInfoLabels.append(settingsButton)

            if 2 <= effectPageIndex < 6:
                for effect in effectList:
                    effectIndex = effectList.index(effect)
                    effectPageIndex = TTLocalizer.PropEditorPages.index(effectList)
                    effect = DirectLabel(parent=infoEntryNode, relief=None, text=effect, text_scale=0.07, textMayChange=1, pos=(-0.629, 0.0, 0.3125 - 0.17 * (effectIndex + 1)), text_align=TextNode.ALeft)
                    codeBoxGui = cdrGui.find('**/tt_t_gui_sbk_cdrCodeBox')
                    codeBox = DirectFrame(parent=infoEntryNode, relief=None, image=codeBoxGui, pos=(
                     0.389, 0.0, 0.3225 - 0.17 * (effectIndex + 1)), scale=(0.5, 0.5,
                                                                            0.7))
                    info = DirectEntry(parent=infoEntryNode, relief=None, text_scale=0.07, width=5, textMayChange=1, pos=(0.229, 0.0, 0.3125 - 0.17 * (effectIndex + 1)), text_align=TextNode.ALeft)
                    info.bind(DGG.TYPE, self.updatePropPreview)
                    self.propInfoPanels.append(info)
                    leftButton = DirectButton(parent=infoEntryNode, relief=None, image_scale=0.5, image=arrow, pos=(
                     0.139, 0.0, 0.3225 - 0.17 * (effectIndex + 1)))
                    leftButton.bind(DGG.B1PRESS, self.infoPanelDown, extraArgs=[self.propInfoPanels.index(info), -1])
                    leftButton.bind(DGG.B1RELEASE, self.infoPanelUp)
                    rightButton = DirectButton(parent=infoEntryNode, relief=None, image_scale=(-0.5,
                                                                                               1,
                                                                                               0.5), image=arrow, pos=(0.639, 0.0, 0.3225 - 0.17 * (effectIndex + 1)))
                    rightButton.bind(DGG.B1PRESS, self.infoPanelDown, extraArgs=[self.propInfoPanels.index(info), 1])
                    rightButton.bind(DGG.B1RELEASE, self.infoPanelUp)
                    submitButton = DirectButton(parent=self.pages[effectPageIndex], relief=None, image=(
                     submitButtonGui.find('**/QuitBtn_UP'),
                     submitButtonGui.find('**/QuitBtn_DN'),
                     submitButtonGui.find('**/QuitBtn_RLVR'),
                     submitButtonGui.find('**/QuitBtn_UP')), image3_color=Vec4(0.5, 0.5, 0.5, 0.5), image_scale=1.15, state=DGG.NORMAL, text=TTLocalizer.NameShopSubmitButton, text_scale=0.07, text_align=TextNode.ACenter, text_pos=(0,
                                                                                                                                                                                                                                       -0.02), text3_fg=(0.5,
                                                                                                                                                                                                                                                         0.5,
                                                                                                                                                                                                                                                         0.5,
                                                                                                                                                                                                                                                         0.75), textMayChange=0, pos=(0.389,
                                                                                                                                                                                                                                                                                      0.0,
                                                                                                                                                                                                                                                                                      -0.365), command=self.confirmUpdateProp)

            if effectPageIndex == 5:
                toggleButton = DirectButton(parent=self.pages[effectPageIndex], relief=None, image=(
                 submitButtonGui.find('**/QuitBtn_UP'),
                 submitButtonGui.find('**/QuitBtn_DN'),
                 submitButtonGui.find('**/QuitBtn_RLVR'),
                 submitButtonGui.find('**/QuitBtn_UP')), image3_color=Vec4(0.5, 0.5, 0.5, 0.5), image_scale=1.15, state=DGG.NORMAL, text=TTLocalizer.PropEditorPage4Toffle, text_scale=0.07, text_align=TextNode.ACenter, text_pos=(0,
                                                                                                                                                                                                                                    -0.02), text3_fg=(0.5,
                                                                                                                                                                                                                                                      0.5,
                                                                                                                                                                                                                                                      0.5,
                                                                                                                                                                                                                                                      0.75), textMayChange=0, pos=(-0.389,
                                                                                                                                                                                                                                                                                   0.0,
                                                                                                                                                                                                                                                                                   -0.365), command=self.toggleColorPage)
                self.colorPicker = ColorPicker(self.pages[effectPageIndex], 0, 1, 0, 1, self.colorProp, (0.135,
                                                                                                         0,
                                                                                                         0))
                self.colorPicker.setScale(0.9)
                self.colorPicker.hide()
            if effectPageIndex == 6:
                for effect in effectList:
                    effectIndex = effectList.index(effect)
                    effectPageIndex = TTLocalizer.PropEditorPages.index(effectList)
                    if effectIndex in range(2):
                        pos = (
                         -0.3, 0.0, 0.3125 - 0.17 * (effectIndex + 1))
                    elif effectIndex in range(2, 4):
                        pos = (
                         0.3, 0.0, 0.3125 - 0.17 * (effectIndex - 1))
                    settingsButton = DirectButton(parent=self.pages[effectPageIndex], relief=None, image=(
                     submitButtonGui.find('**/QuitBtn_UP'),
                     submitButtonGui.find('**/QuitBtn_DN'),
                     submitButtonGui.find('**/QuitBtn_RLVR'),
                     submitButtonGui.find('**/QuitBtn_UP')), image3_color=Vec4(0.5, 0.5, 0.5, 0.5), image_scale=1.15, state=DGG.NORMAL, text=effect, text_scale=0.07, text_align=TextNode.ACenter, text_pos=(0,
                                                                                                                                                                                                             -0.02), text3_fg=(0.5,
                                                                                                                                                                                                                               0.5,
                                                                                                                                                                                                                               0.5,
                                                                                                                                                                                                                               0.75), textMayChange=1, pos=pos, command=self.toggleReparent, extraArgs=[effectIndex])
                    self.propInfoLabels.append(settingsButton)

                reparentLabel = DirectLabel(parent=self.pages[effectPageIndex], relief=None, text='', text_scale=0.08, textMayChange=1, pos=(0,
                                                                                                                                             0,
                                                                                                                                             -0.36))
                self.propInfoLabels.append(reparentLabel)

        geom.removeNode()
        matModel.removeNode()
        submitButtonGui.removeNode()
        guiClose.removeNode()
        cdrGui.removeNode()
        self.pages[0].show()
        self.editorGUI.hide()
        self.generatorGUI.hide()
        return

    def openPropEditor(self, prop):
        messenger.send('wakeup')
        self.selectedProp = prop
        propIndex = int(self.selectedProp.getTag(self.propTag))
        propInfo = self.propList[propIndex]
        if propInfo[7] in (2, 3) and not base.localAvatar.getAccessLevel() >= OTPGlobals.AccessLevelName2Int.get('MODERATOR') and base.localAvatar.getDoId() != propInfo[3] or base.localAvatar.getAccessLevel() == OTPGlobals.AccessLevelName2Int.get('NO_ACCESS'):
            self.selectedProp = None
            return
        else:
            if self.windowOpen == 2:
                self.closeNewPropWindow()
            for cell in base.rightCells:
                base.setCellsAvailable([cell], 0)

            base.localAvatar.chatMgr.fsm.request('otherDialog')
            self.updatePropInfo()
            if self.editorGUI:
                self.editorGUI.show()
            self.windowOpen = 1
            return

    def closePropEditor(self):
        messenger.send('wakeup')
        self.selectedProp = None
        for cell in base.rightCells:
            base.setCellsAvailable([cell], 1)

        base.localAvatar.chatMgr.fsm.request('mainMenu')
        self.ignore('selectSecondaryProp')
        if self.editorGUI:
            self.editorGUI.hide()
        if self.previewProp:
            self.previewProp.removeNode()
            self.previewProp = None
        self.windowOpen = 0
        return

    def openNewPropWindow(self):
        messenger.send('wakeup')
        if base.localAvatar.getAccessLevel() == OTPGlobals.AccessLevelName2Int.get('NO_ACCESS'):
            return
        if self.windowOpen == 2:
            return
        self.closePropEditor()
        for cell in base.rightCells:
            base.setCellsAvailable([cell], 0)

        base.localAvatar.chatMgr.fsm.request('mainMenu')
        if self.currentProp == -1:
            self.changeProp(1)
        else:
            self.createProp(self.currentProp)
        if self.generatorGUI:
            self.generatorGUI.show()
        self.windowOpen = 2

    def closeNewPropWindow(self):
        messenger.send('wakeup')
        for cell in base.rightCells:
            base.setCellsAvailable([cell], 1)

        base.localAvatar.chatMgr.fsm.request('mainMenu')
        if self.generatorGUI:
            self.generatorGUI.hide()
        if self.previewProp:
            propName = BattleProps.globalPropPool.propStrings.keys()[self.currentProp]
            propType = BattleProps.globalPropPool.propTypes[propName]
            if propType == 'actor':
                self.previewProp.cleanup()
            else:
                self.previewProp.removeNode()
            self.previewProp = None
            if self.previewPropPanel:
                self.previewPropPanel.destroy()
                self.previewPropPanel = None
        self.windowOpen = 0
        return

    def changeProp(self, direction):
        if self.previewProp:
            propName = BattleProps.globalPropPool.propStrings.keys()[self.currentProp]
            propType = BattleProps.globalPropPool.propTypes[propName]
            if propType == 'actor':
                self.previewProp.cleanup()
            else:
                self.previewProp.removeNode()
            self.previewProp = None
            if self.previewPropPanel:
                self.previewPropPanel.destroy()
                self.previewPropPanel = None
        nextProp = self.currentProp + 1 * direction
        maxProps = len(self.availablePropPreviews)
        if maxProps == 0:
            self.propTitle.setText(TTLocalizer.WordPageNA)
            self.currentProp = -1
            return
        else:
            while nextProp in self.hiddenPropPreviews:
                nextProp += 1 * direction
                if nextProp > max(self.availablePropPreviews):
                    nextProp = min(self.availablePropPreviews)
                elif nextProp < min(self.availablePropPreviews):
                    nextProp = max(self.availablePropPreviews)

            if nextProp > max(self.availablePropPreviews):
                nextProp = min(self.availablePropPreviews)
            elif nextProp < min(self.availablePropPreviews):
                nextProp = max(self.availablePropPreviews)
            self.currentProp = nextProp
            self.createProp(nextProp)
            return

    def createProp(self, propIndex):
        propName = BattleProps.globalPropPool.propStrings.keys()[propIndex]
        self.previewProp = BattleProps.globalPropPool.getProp(propName)
        self.previewProp.setBin('unsorted', 0, 1)
        self.previewPropPanel, ival = self.makeFrameModel(self.previewProp)
        self.previewPropPanel.reparentTo(self.generatorGUI.find('**/propPickerNode'), -1)
        self.previewPropPanel.setX(-0.35)
        self.previewPropPanel.setScale(0.21)
        ival.loop()
        self.propTitle.setText(propName)

    def makeFrame(self):
        from direct.gui.DirectGui import DirectFrame
        frame = DirectFrame(parent=hidden, frameSize=(-1.0, 1.0, -1.0, 1.0), relief=None)
        return frame

    def makeFrameModel(self, model):
        frame = self.makeFrame()
        ival = None
        if model:
            model.setDepthTest(1)
            model.setDepthWrite(1)
            pitch = frame.attachNewNode('pitch')
            rotate = pitch.attachNewNode('rotate')
            scale = rotate.attachNewNode('scale')
            model.reparentTo(scale)
            bMin, bMax = model.getTightBounds()
            center = (bMin + bMax) / 2.0
            model.setPos(-center[0], -center[1], -center[2])
            pitch.setP(20)
            bMin, bMax = pitch.getTightBounds()
            center = (bMin + bMax) / 2.0
            corner = Vec3(bMax - center)
            scale.setScale(1.0 / max(corner[0], corner[1], corner[2]))
            pitch.setY(2)
            ival = LerpHprInterval(rotate, 10, VBase3(-270, 0, 0), startHpr=VBase3(90, 0, 0))
        return (frame, ival)

    def changePage(self, direction):
        self.pages[self.currentPage].hide()
        nextPage = self.currentPage + 1 * direction
        if nextPage == 7:
            nextPage = 0
        elif nextPage == -1:
            nextPage = 6
        self.currentPage = nextPage
        self.pages[nextPage].show()

    def updatePropInfo(self):
        if not self.selectedProp:
            return
        propIndex = int(self.selectedProp.getTag(self.propTag))
        propInfo = self.propList[propIndex]
        if propInfo[9]:
            secondaryPropIndex = propInfo[8]
            secondaryPropInfo = self.propList[secondaryPropIndex]
            self.propInfoLabels[13].setText(TTLocalizer.PropEditorPage5ReparentedTo % secondaryPropInfo[0] + '_' + str(secondaryPropIndex + 1))
        else:
            self.propInfoLabels[13].setText('')
        propInformation = (propInfo[4] + '\n                   (%s)' % propInfo[3],
         propInfo[6] + '\n              (%s)' % propInfo[5],
         PythonUtil.formatElapsedSeconds(globalClockDelta.localElapsedTime(propInfo[2], bits=32)) + ' ago',
         propInfo[0] + '_' + str(propIndex + 1))
        for infoLabel in self.propInfoLabels:
            index = self.propInfoLabels.index(infoLabel)
            if index == 2:
                if propInfo[5] != 0:
                    infoLabel.setText(TTLocalizer.PropEditorPage6EditedAt + propInformation[index])
                else:
                    infoLabel.setText(TTLocalizer.PropEditorPage6[index] + propInformation[index])
            elif index == 4:
                if (propInfo[7] in (1, 3) or base.localAvatar.getAccessLevel() < OTPGlobals.AccessLevelName2Int.get('USER')) and not base.localAvatar.getAccessLevel() >= OTPGlobals.AccessLevelName2Int.get('MODERATOR'):
                    infoLabel['state'] = DGG.DISABLED
                else:
                    infoLabel['state'] = DGG.NORMAL
            elif index == 5:
                if base.localAvatar.getDoId() != propInfo[3] and not base.localAvatar.getAccessLevel() >= OTPGlobals.AccessLevelName2Int.get('MODERATOR'):
                    infoLabel['state'] = DGG.DISABLED
                if propInfo[7] in (1, 3):
                    infoLabel.setText(TTLocalizer.PropEditorPage7UnlockDeletion)
                else:
                    infoLabel.setText(TTLocalizer.PropEditorPage7[1])
            elif index == 6:
                if base.localAvatar.getDoId() != propInfo[3] and not base.localAvatar.getAccessLevel() >= OTPGlobals.AccessLevelName2Int.get('MODERATOR'):
                    infoLabel['state'] = DGG.DISABLED
                if propInfo[7] in (2, 3):
                    infoLabel.setText(TTLocalizer.PropEditorPage7UnlockEditing)
                else:
                    infoLabel.setText(TTLocalizer.PropEditorPage7[2])
            elif index == 7:
                if base.localAvatar.getAccessLevel() <= OTPGlobals.AccessLevelName2Int.get('MODERATOR'):
                    infoLabel['state'] = DGG.DISABLED
                else:
                    infoLabel['state'] = DGG.NORMAL
            elif index in (8, 9, 10, 11, 12, 13):
                pass
            else:
                infoLabel.setText(TTLocalizer.PropEditorPage6[index] + propInformation[index])

        propPosHprScale = (
         self.selectedProp.getX(), self.selectedProp.getY(), self.selectedProp.getZ(),
         self.selectedProp.getH(), self.selectedProp.getP(), self.selectedProp.getR(),
         self.selectedProp.getScale().getX(), self.selectedProp.getScale().getY(), self.selectedProp.getScale().getZ(),
         self.selectedProp.getColorScale()[0] * 255, self.selectedProp.getColorScale()[1] * 255, self.selectedProp.getColorScale()[2] * 255)
        for infoPanel in self.propInfoPanels:
            infoPanel.enterText('%.2f' % propPosHprScale[self.propInfoPanels.index(infoPanel)])

    def updateInfoPanel(self, infoPanelIndex=None, multiplier=None):
        infoPanel = self.propInfoPanels[infoPanelIndex]
        try:
            input = float(infoPanel.get())
        except:
            return True

        if 3 <= infoPanelIndex <= 5:
            multiplier *= 0.5
        else:
            if 6 <= infoPanelIndex <= 8:
                multiplier *= 0.1
            elif 9 <= infoPanelIndex <= 11:
                multiplier *= 0.5
            input += 1 * multiplier
            inputStr = str(input)
            if len(inputStr) >= 8:
                return True
        if 0 <= infoPanelIndex <= 2:
            if input > 10000:
                input = 9999.0
            elif input < -10000:
                input = -9999.0
        elif 3 <= infoPanelIndex <= 5:
            if input > 360 or input < -360:
                input = 0.0
        elif 6 <= infoPanelIndex <= 8:
            if input > 5:
                input = 5.0
            elif input < 0.1:
                input = 0.1
        elif 9 <= infoPanelIndex <= 11:
            if input > 255:
                input = 255.0
            elif input < 0:
                input = 0.0
        infoPanel.enterText(str(input))
        self.updatePropPreview()

    def infoPanelUp(self, event):
        messenger.send('wakeup')
        taskMgr.remove('propGeneratorRunCounter')

    def infoPanelDown(self, infoPanelIndex, multiplier, event):
        messenger.send('wakeup')
        task = Task(self.runCounter)
        task.delayTime = 0.4
        task.prevTime = 0.0
        hitLimit = self.updateInfoPanel(infoPanelIndex, multiplier)
        if not hitLimit:
            taskMgr.add(task, 'propGeneratorRunCounter', extraArgs=[infoPanelIndex, multiplier], appendTask=True)

    def runCounter(self, infoPanelIndex, multiplier, task):
        if task.time - task.prevTime < task.delayTime:
            return Task.cont
        else:
            task.delayTime = max(0.01, task.delayTime * 0.85)
            task.prevTime = task.time
            hitLimit = self.updateInfoPanel(infoPanelIndex, multiplier)
            if hitLimit:
                return Task.done
            return Task.cont

    def updatePropPreview(self, extraArgs=None):
        if not self.selectedProp:
            return
        else:
            info = []
            for infoPanel in self.propInfoPanels:
                try:
                    input = float(infoPanel.get())
                    info.append(input)
                except:
                    return

            for x in range(len(info)):
                value = info[x]
                if 0 <= x <= 2:
                    if value > 10000:
                        info[x] = 9999.0
                    elif value < -10000:
                        info[x] = -9999.0
                elif 3 <= x <= 5:
                    if value > 360 or value < -360:
                        info[x] = 0.0
                elif 6 <= x <= 8:
                    if value > 5:
                        info[x] = 5.0
                    elif value < 0.1:
                        info[x] = 0.1
                elif 9 <= x <= 11:
                    if value > 255:
                        info[x] = 255.0
                    elif value < 0:
                        info[x] = 0.0

            if self.previewProp:
                self.previewProp.removeNode()
                self.previewProp = None
            self.previewProp = self.selectedProp.copyTo(self.selectedProp.getParent())
            self.previewProp.setPosHprScale(info[0], info[1], info[2], info[3], info[4], info[5], info[6], info[7], info[8])
            self.previewProp.setColorScale(info[9] / 255, info[10] / 255, info[11] / 255, 0.3)
            self.previewProp.setTransparency(1)
            return

    def confirmUpdateProp(self, toggleSettings=None):
        messenger.send('wakeup')
        if not self.selectedProp:
            return
        else:
            propIndex = int(self.selectedProp.getTag(self.propTag))
            propInfo = self.propList[propIndex]
            if toggleSettings == 4:
                self.sendUpdate('d_dupeProp', [propIndex])
                return
            propName = propInfo[0]
            spawnTime = propInfo[2]
            creatorAvId = propInfo[3]
            creatorName = propInfo[4]
            editorAvId = base.localAvatar.getDoId()
            editorName = base.localAvatar.getName()
            lockedState = 0
            if self.propInfoLabels[5]['text'] == TTLocalizer.PropEditorPage7[1] and toggleSettings == 1:
                lockedState += 1
            elif self.propInfoLabels[5]['text'] == TTLocalizer.PropEditorPage7UnlockDeletion and toggleSettings != 1:
                lockedState += 1
            if self.propInfoLabels[6]['text'] == TTLocalizer.PropEditorPage7[2] and toggleSettings == 2:
                lockedState += 2
            else:
                if self.propInfoLabels[6]['text'] == TTLocalizer.PropEditorPage7UnlockEditing and toggleSettings != 2:
                    lockedState += 2
                reparentProp = propInfo[8]
                reparentState = propInfo[9]
                info = []
                for infoPanel in self.propInfoPanels:
                    try:
                        input = float(infoPanel.get())
                        info.append(input)
                    except:
                        return

                for x in range(len(info)):
                    value = info[x]
                    if 0 <= x <= 2:
                        if value > 10000:
                            info[x] = 9999.0
                        elif value < -10000:
                            info[x] = -9999.0
                    elif 3 <= x <= 5:
                        if value > 360 or value < -360:
                            info[x] = 0.0
                    elif 6 <= x <= 8:
                        if value > 5:
                            info[x] = 5.0
                        elif value < 0.1:
                            info[x] = 0.1
                    elif 9 <= x <= 11:
                        if value > 255:
                            info[x] = 255.0
                        elif value < 0:
                            info[x] = 0.0

            if toggleSettings == 3 and self.savedValues:
                pos = self.savedValues['pos']
                info[0], info[1], info[2] = pos[0], pos[1], pos[2]
                hpr = self.savedValues['hpr']
                info[3], info[4], info[5] = hpr[0], hpr[1], hpr[2]
                scale = self.savedValues['scale']
                info[6], info[7], info[8] = scale[0], scale[1], scale[2]
                colorscale = self.savedValues['colorscale']
                info[9], info[10], info[11] = colorscale[0], colorscale[1], colorscale[2]
            self.savedValues['pos'] = (info[0], info[1], info[2])
            self.savedValues['hpr'] = (info[3], info[4], info[5])
            self.savedValues['scale'] = (info[6], info[7], info[8])
            self.savedValues['colorscale'] = (info[9], info[10], info[11])
            if self.previewProp:
                self.previewProp.removeNode()
                self.previewProp = None
            self.sendUpdate('confirmUpdateProp', [
             (propIndex, propName, info[0], info[1], info[2], info[3], info[4],
              info[5], info[6], info[7], info[8], info[9] / 255, info[10] / 255,
              info[11] / 255, 1.0, spawnTime, creatorAvId, creatorName, editorAvId,
              editorName, lockedState, reparentProp, reparentState)])
            return

    def updateProp(self, propData):
        propId, propName, x, y, z, h, p, r, sX, sY, sZ, csR, csG, csB, csA, spawnTime, creatorAvId, creatorName, editorAvId, editorName, lockedState, reparentProp, reparentState = propData
        updatedProp = None
        propPosHprScale = (x, y, z, h, p, r, sX, sY, sZ)
        propColorScale = (csR, csG, csB, csA)
        updatedProp = self.propList.get(propId)
        if not updatedProp:
            self.addProp(propId, propName, propPosHprScale, propColorScale, spawnTime, creatorAvId, creatorName, editorAvId, editorName, lockedState, reparentProp, reparentState)
            return
        else:
            updatedProp[1].setPosHprScale(*propPosHprScale)
            updatedProp[1].setColorScale(*propColorScale)
            updatedProp[2] = spawnTime
            updatedProp[5] = editorAvId
            updatedProp[6] = editorName
            updatedProp[7] = lockedState
            updatedProp[8] = reparentProp
            updatedProp[9] = reparentState
            if reparentState:
                secondaryPropInfo = self.propList.get(reparentProp)
                if secondaryPropInfo:
                    updatedProp[1].reparentTo(secondaryPropInfo[1])
                else:
                    self.notify.warning('Could not find parent prop %d for child prop %s!  Parenting to propNode instead...' % (reparentProp, propName))
                    updatedProp[1].wrtReparentTo(self.propNode)
            else:
                updatedProp[1].wrtReparentTo(self.propNode)
            if self.selectedProp:
                propIndex = int(self.selectedProp.getTag(self.propTag))
                if propIndex == propId:
                    self.updatePropInfo()
            return

    def toggleColorPage(self):
        if not self.colorPageToggle:
            self.colorPageToggle = True
            infoPanel = self.pages[5].find('infoEntryNode')
            infoPanel.hide()
            self.colorPicker.show()
        elif self.colorPageToggle:
            self.colorPageToggle = False
            infoPanel = self.pages[5].find('infoEntryNode')
            infoPanel.show()
            self.colorPicker.hide()

    def colorProp(self, rgb):
        colorIndexes = range(9, 12)
        for x in colorIndexes:
            self.propInfoPanels[x].enterText(str(rgb[colorIndexes.index(x)] * 255))

        self.updatePropPreview()

    def togglePropSettings(self, index):
        if not index:
            self.confirmDeleteProp()
        elif index in range(1, 5):
            self.confirmUpdateProp(index)

    def confirmDeleteProp(self):
        messenger.send('wakeup')
        if not self.selectedProp:
            return
        propIndex = int(self.selectedProp.getTag(self.propTag))
        self.closePropEditor()
        self.sendUpdate('confirmDeleteProp', [propIndex])

    def deleteProp(self, propId):
        propInfo = self.propList[propId]
        propType = BattleProps.globalPropPool.propTypes[propInfo[0]]
        if propType == 'actor':
            propInfo[1].cleanup()
        else:
            propInfo[1].removeNode()
        del self.propList[propId]
        del self.propData[propId]
        self.updatePropCount()

    def toggleReparent(self, index, secondaryProp=None):
        propIndex = int(self.selectedProp.getTag(self.propTag))
        propInfo = self.propList[propIndex]
        if index == 2:
            propInfo[8] = 0
            propInfo[9] = False
            self.propInfoLabels[13].setText('')
            self.confirmUpdateProp()
            return
        else:
            if secondaryProp is None:
                self.acceptOnce('selectSecondaryProp', self.toggleReparent, extraArgs=[index])
                self.propInfoLabels[13].setText(TTLocalizer.PropEditorPage5ChooseProp)
                return
            if secondaryProp == 0:
                if propInfo[9]:
                    secondaryPropIndex = propInfo[8]
                    secondaryPropInfo = self.propList[secondaryPropIndex]
                    self.propInfoLabels[13].setText(TTLocalizer.PropEditorPage5ReparentedTo % secondaryPropInfo[0] + '_' + str(secondaryPropIndex + 1))
                else:
                    self.propInfoLabels[13].setText('')
                return
            secondaryPropIndex = int(secondaryProp.getTag(self.propTag))
            secondaryPropInfo = self.propList[secondaryPropIndex]
            if secondaryPropInfo[8] == propIndex:
                if propInfo[9]:
                    secondaryPropIndex = propInfo[8]
                    secondaryPropInfo = self.propList[secondaryPropIndex]
                    self.propInfoLabels[13].setText(TTLocalizer.PropEditorPage5ReparentedTo % secondaryPropInfo[0] + '_' + str(secondaryPropIndex + 1))
                else:
                    self.propInfoLabels[13].setText('')
                return
            if index == 0:
                propInfo[8] = secondaryPropIndex
                propInfo[9] = True
                self.propInfoLabels[13].setText(TTLocalizer.PropEditorPage5ReparentedTo % secondaryPropInfo[0] + '_' + str(secondaryPropIndex + 1))
                self.confirmUpdateProp()
            elif index == 1:
                self.selectedProp.wrtReparentTo(secondaryProp)
                pos = self.selectedProp.getPos()
                for infoPanelIndex in range(3):
                    infoPanel = self.propInfoPanels[infoPanelIndex]
                    infoPanel.enterText(str(pos[infoPanelIndex]))

                hpr = self.selectedProp.getHpr()
                for infoPanelIndex in range(3):
                    infoPanel = self.propInfoPanels[(infoPanelIndex + 3)]
                    infoPanel.enterText(str(hpr[infoPanelIndex]))

                scale = self.selectedProp.getScale()
                for infoPanelIndex in range(3):
                    infoPanel = self.propInfoPanels[(infoPanelIndex + 6)]
                    infoPanel.enterText(str(scale[infoPanelIndex]))

                propInfo[8] = secondaryPropIndex
                propInfo[9] = True
                self.propInfoLabels[13].setText(TTLocalizer.PropEditorPage5ReparentedTo % secondaryPropInfo[0] + '_' + str(secondaryPropIndex + 1))
                self.confirmUpdateProp()
            elif index == 3:
                self.propInfoLabels[13].setText('')
                pos = secondaryProp.getPos()
                for infoPanelIndex in range(3):
                    infoPanel = self.propInfoPanels[infoPanelIndex]
                    infoPanel.enterText(str(pos[infoPanelIndex]))

                self.confirmUpdateProp()
            return

    def toggleEntryFocus(self, lose=False):
        if lose:
            self.searchBarEntry['focus'] = 0
            base.localAvatar.chatMgr.fsm.request('mainMenu')
        else:
            base.localAvatar.chatMgr.fsm.request('otherDialog')

    def updateWordSearch(self, extraArgs=None):
        propsAvailable = True
        if len(self.availablePropPreviews) == 0:
            propsAvailable = False
        self.hiddenPropPreviews = []
        self.availablePropPreviews = []
        searchTerm = self.searchBarEntry.get().lower()
        for propIndex in range(len(BattleProps.globalPropPool.propStrings.keys())):
            propName = BattleProps.globalPropPool.propStrings.keys()[propIndex]
            if searchTerm not in propName:
                self.hiddenPropPreviews.append(propIndex)
            elif searchTerm in propName:
                self.availablePropPreviews.append(propIndex)

        if self.currentProp in self.hiddenPropPreviews:
            self.changeProp(1)
        if not propsAvailable:
            self.changeProp(1)

    def togglePropGeneratorSettings(self, state):
        if not state:
            self.generatorGUI.find('**/propPickerNode').hide()
            self.generatorGUI.find('**/propSettingsNode').show()
        elif state:
            self.generatorGUI.find('**/propSettingsNode').hide()
            self.generatorGUI.find('**/propPickerNode').show()

    def propMessage(self, index):
        base.localAvatar.setSystemMessage(0, TTLocalizer.PropMessages[index], WhisperPopup.WTEmote)

    def confirmDeleteAllProps(self, state):
        self.sendUpdate('confirmDeleteAllProps', [state])

    def deleteAllProps(self):
        for propId in self.propList.keys():
            self.deleteProp(propId)

        self.propList = {}
        self.updatePropCount()

    def confirmLockProps(self, state):
        self.sendUpdate('confirmLockProps', [state])

    def updatePropCount(self):
        self.totalPropCount.setText(TTLocalizer.PropGeneratorTotalCount % (
         len(self.propList.keys()), ToontownGlobals.MaxPropCount))

    def enableHotkey(self):
        self.accept('f11', self.openNewPropWindow)

    def disableHotkey(self):
        self.ignore('f11')

    def dragStart(self, type, event):
        button = self.getButton(type)
        taskMgr.remove(self.taskName('dragTask'))
        vWidget2render2d = button.getPos(render2d)
        vMouse2render2d = Point3(event.getMouse()[0], 0, event.getMouse()[1])
        editVec = Vec3(vWidget2render2d - vMouse2render2d)
        task = taskMgr.add(self.dragTask, self.taskName('dragTask'), extraArgs=[type], appendTask=True)
        task.editVec = editVec

    def dragTask(self, type, task):
        button = self.getButton(type)
        mwn = base.mouseWatcherNode
        if mwn.hasMouse():
            vMouse2render2d = Point3(mwn.getMouse()[0], 0, mwn.getMouse()[1])
            newPos = vMouse2render2d + task.editVec
            button.setPos(render2d, newPos)
        return Task.cont

    def dragStop(self, type, event):
        button = self.getButton(type)
        taskMgr.remove(self.taskName('dragTask'))

    def getButton(self, type):
        if not type:
            return self.editorGUI
        else:
            return self.generatorGUI