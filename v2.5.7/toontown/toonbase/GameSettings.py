from direct.directnotify import DirectNotifyGlobal
from panda3d.core import loadPrcFileData
from otp.otpbase.Settings import Settings

class GameSettings:
    notify = DirectNotifyGlobal.directNotify.newCategory('GameSettings')
    notify.setInfo(True)

    def __init__(self):
        self.settings = Settings()

    def loadFromSettings(self):
        self.notify.info('Loading settings...')
        electionEvent = self.settings.getBool('game', 'elections', False)
        loadPrcFileData('toonBase Settings Election Active', 'want-doomsday %s' % electionEvent)
        loadPrcFileData('toonBase Elections Event Manager', 'want-event-manager %s' % electionEvent)
        self.settings.updateSetting('game', 'elections', electionEvent)
        self.electionEvent = electionEvent
        retroMode = self.settings.getBool('game', 'retro', False)
        loadPrcFileData('toonBase Settings Retro Mode', 'want-retro-mode %s' % retroMode)
        loadPrcFileData('toonBase Settings TTO Map Hover', 'want-map-hover %s' % retroMode)
        loadPrcFileData('toonBase Settings Retro Make-A-Toon', 'want-retro-makeatoon %s' % retroMode)
        loadPrcFileData('toonBase Settings TTO Cog Question', 'want-old-question %s' % retroMode)
        self.settings.updateSetting('game', 'retro', retroMode)
        self.retroMode = retroMode
        miniServer = self.settings.getBool('game', 'mini-server', False)
        loadPrcFileData('toonBase Settings Mini-Servers', 'want-mini-server %s' % miniServer)
        self.settings.updateSetting('game', 'mini-server', miniServer)
        self.miniServer = miniServer
        aspect = self.settings.getBool('game', 'stretched-screen', False)
        loadPrcFileData('toonBase Settings Aspect Ratio', 'aspect-ratio 1.33' if aspect else '0')
        self.settings.updateSetting('game', 'stretched-screen', aspect)
        self.aspect = aspect
        randomInvasions = self.settings.getBool('game', 'random-invasions', True)
        loadPrcFileData('toonBase Settings Random Invasions', 'want-random-invasions %s' % randomInvasions)
        self.settings.updateSetting('game', 'random-invasions', randomInvasions)
        self.randomInvasions = randomInvasions
        software = self.settings.getBool('game', 'software-render', False)
        loadPrcFileData('toonBase Settings Software Rendering', 'framebuffer-hardware %s' % (not software))
        loadPrcFileData('toonBase Settings Software Rendering', 'framebuffer-software %s' % software)
        self.settings.updateSetting('game', 'software-render', software)
        self.software = software
        lerp = self.settings.getBool('game', 'interpolate-animations', True)
        loadPrcFileData('toonBase Settings Interpolated Animations', 'interpolate-animations %s' % lerp)
        self.settings.updateSetting('game', 'interpolate-animations', lerp)
        self.lerp = lerp
        classicCharacters = self.settings.getBool('game', 'classic-characters', True)
        loadPrcFileData('toonBase Settings Classic Characters', 'want-classic-chars %s' % classicCharacters)
        self.settings.updateSetting('game', 'classic-characters', classicCharacters)
        self.classicCharacters = classicCharacters
        stickyScroll = self.settings.getBool('game', 'camera-scroll-select-always-active', False)
        loadPrcFileData('toonBase Settings Sticky Scroll Camera Selection', 'want-sticky-scroll %s' % stickyScroll)
        self.settings.updateSetting('game', 'camera-scroll-select-always-active', stickyScroll)
        self.stickyScroll = stickyScroll
        spawnProps = self.settings.getBool('game', 'view-props', False)
        loadPrcFileData('toonBase Settings View Props', 'want-spawn-prop %s' % spawnProps)
        self.settings.updateSetting('game', 'view-props', spawnProps)
        self.spawnProps = spawnProps
        maxLOD = self.settings.getBool('game', 'always-max-lod', False)
        loadPrcFileData('toonBase Always Max LOD', 'always-max-lod %s' % maxLOD)
        self.settings.updateSetting('game', 'always-max-lod', maxLOD)
        self.maxLOD = maxLOD
        randPic = self.settings.getBool('game', 'random-loading-images', True)
        loadPrcFileData('toonBase Random Loader Images', 'want-random-pics %s' % randPic)
        self.settings.updateSetting('game', 'random-loading-images', randPic)
        self.randPic = randPic
        localServerAutoStartDefaultValue = True
        localServerAutoStart = self.settings.getBool('game', 'auto-start-local-server', localServerAutoStartDefaultValue)
        loadPrcFileData('toonBase Auto Start Local Server', 'auto-start-local-server %s' % localServerAutoStart)
        self.settings.updateSetting('game', 'auto-start-local-server', localServerAutoStart)
        self.localServerAutoStart = localServerAutoStart
        trueFriends = self.settings.getBool('game', 'true-friends', True)
        loadPrcFileData('toonBase True Friends', 'parent-password-set %s' % trueFriends)
        loadPrcFileData('toonBase True Friends', 'allow-secret-chat %s' % trueFriends)
        self.settings.updateSetting('game', 'true-friends', trueFriends)
        self.trueFriends = trueFriends
        whitelist = self.settings.getBool('game', 'whitelist', False)
        loadPrcFileData('toonBase Whitelist', 'want-whitelist %s' % whitelist)
        self.settings.updateSetting('game', 'whitelist', whitelist)
        self.whitelist = whitelist
        blacklist = self.settings.getBool('game', 'blacklist', False)
        loadPrcFileData('toonBase Blacklist', 'want-blacklist %s' % blacklist)
        self.settings.updateSetting('game', 'blacklist', blacklist)
        self.blacklist = blacklist
        sequenceBlacklist = self.settings.getBool('game', 'sequence-blacklist', False)
        loadPrcFileData('toonBase Sequence Blacklist', 'want-blacklist-sequence %s' % sequenceBlacklist)
        self.settings.updateSetting('game', 'sequence-blacklist', sequenceBlacklist)
        self.sequenceBlacklist = sequenceBlacklist
        toonfest = self.settings.getBool('game', 'toonfest-day-night', False)
        loadPrcFileData('toonBase ToonFest Day Night Cycle', 'toonfest-day-night %s' % toonfest)
        self.settings.updateSetting('game', 'toonfest-day-night', toonfest)
        self.toonfest = toonfest
        customMusic = self.settings.getBool('game', 'custom-battle-music', False)
        loadPrcFileData('toonBase Sequence Blacklist', 'custom-battle-music %s' % customMusic)
        self.settings.updateSetting('game', 'custom-battle-music', customMusic)
        self.customMusic = customMusic
        cogFoot = self.settings.getBool('game', 'cog-footsteps', True)
        loadPrcFileData('toonBase Cog Foot', 'cog-footsteps %s' % cogFoot)
        self.settings.updateSetting('game', 'cog-footsteps', cogFoot)
        self.cogFoot = cogFoot
        self.notify.info('Loaded.')