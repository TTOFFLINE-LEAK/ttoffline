from direct.directnotify import DirectNotifyGlobal
from panda3d.core import loadPrcFileData
from otp.settings.Settings import Settings

class ToontownSettings(Settings):
    notify = DirectNotifyGlobal.directNotify.newCategory('ToontownSettings')

    def loadFromSettings(self):
        softwareMode = self.getBool('game', 'software-mode', False)
        if softwareMode:
            loadPrcFileData('toonBase Settings Software Mode', 'software-mode %d' % softwareMode)
        else:
            self.updateSetting('game', 'software-mode', softwareMode)
        gamemode = self.getInt('game', 'gamemode', 0)
        loadPrcFileData('toonBase Settings Gamemode', 'gamemode %d' % gamemode)
        self.updateSetting('game', 'gamemode', gamemode)
        classicVisuals = self.getInt('game', 'classic-visuals', 0)
        loadPrcFileData('toonBase Settings Classic Visuals', 'classic-visuals %d' % classicVisuals)
        self.updateSetting('game', 'classic-visuals', classicVisuals)
        judgeVisuals = classicVisuals
        if classicVisuals == 0:
            judgeVisuals = gamemode
        else:
            judgeVisuals -= 1
        stretchedScreen = self.getInt('game', 'stretched-screen', 0)
        doStretch = True
        if stretchedScreen == 0 and judgeVisuals == 0:
            doStretch = False
        elif stretchedScreen == 2:
            doStretch = False
        if doStretch:
            loadPrcFileData('toonBase Settings Stretched Screen', 'aspect-ratio 1.333')
        self.updateSetting('game', 'stretched-screen', stretchedScreen)
        smoothAnims = self.getBool('game', 'smooth-animations', False)
        loadPrcFileData('toonBase Settings SmoothAnims', 'smooth-animations %s' % smoothAnims)
        self.updateSetting('game', 'smooth-animations', smoothAnims)
        magicWordActivator = self.getInt('game', 'magic-word-activator', 0)
        loadPrcFileData('toonBase Settings Magic Word Activator', 'magic-word-activator %d' % magicWordActivator)
        self.updateSetting('game', 'magic-word-activator', magicWordActivator)
        localServerAutoStartDefaultValue = True
        localServerAutoStart = self.getBool('game', 'auto-start-local-server', localServerAutoStartDefaultValue)
        loadPrcFileData('toonBase Auto Start Local Server', 'auto-start-local-server %s' % localServerAutoStart)
        self.updateSetting('game', 'auto-start-local-server', localServerAutoStart)