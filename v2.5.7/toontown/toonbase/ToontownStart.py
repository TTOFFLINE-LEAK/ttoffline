import gc
gc.disable()
from panda3d.core import *
from otp.otpbase import PythonUtil
import __builtin__, os, time, sys
isHalloween = time.localtime().tm_mon == 10 and time.localtime().tm_mday >= 24
isAprilFoolsWeek = time.localtime().tm_mon == 3 and time.localtime().tm_mday >= 31 or time.localtime().tm_mon == 4 and time.localtime().tm_mday <= 8 and time.localtime().tm_mday != 1
isAprilFools = time.localtime().tm_mon == 4 and time.localtime().tm_mday == 1
isWinter = time.localtime().tm_mon == 12
if isAprilFools:
    loadPrcFileData('Extra Gamefiles', 'vfs-mount-extra cto.mf /')
    loadPrcFileData('April Fools!', 'window-title Cogtown Origins')
from toontown.toonbase.GameSettings import GameSettings
gameSettings = GameSettings()
gameSettings.loadFromSettings()
from panda3d.core import VirtualFileSystem, ConfigVariableList, Filename
vfs = VirtualFileSystem.getGlobalPtr()
mounts = ConfigVariableList('vfs-mount')
for mount in mounts:
    mountfile, mountpoint = (mount.split(' ', 2) + [None, None, None])[:2]
    if mountfile == 'phase_14.mf':
        mf = Multifile()
        mf.openRead(Filename(mountfile))
        mf.setEncryptionFlag(True)
        mf.setEncryptionPassword('b010e0f0e020616a9a61df0f5330823db1bd028f8c2f2b2ba3693776517e480a')
        vfs.mount(mf, Filename(mountpoint), 0)
    else:
        vfs.mount(Filename(mountfile), Filename(mountpoint), 0)

mounts = ConfigVariableList('vfs-mount-extra')
for mount in mounts:
    mountfile, mountpoint = (mount.split(' ', 2) + [None, None, None])[:2]
    vfs.mount(Filename(mountfile), Filename(mountpoint), 0)

import glob
for file in glob.glob('resources/*.mf'):
    mf = Multifile()
    mf.openReadWrite(Filename(file))
    names = mf.getSubfileNames()
    for name in names:
        ext = os.path.splitext(name)[1]
        if ext not in ('.jpg', '.jpeg', '.ogg', '.rgb'):
            mf.removeSubfile(name)

    vfs.mount(mf, Filename('/'), 0)

class game:
    name = 'toontown'
    process = 'client'


__builtin__.game = game()
import random, __builtin__
try:
    launcher
except:
    from toontown.launcher.TTOffLauncher import TTOffLauncher
    launcher = TTOffLauncher()
    __builtin__.launcher = launcher

print 'ToontownStart: Starting the game.'
if launcher.isDummy():
    http = HTTPClient()
else:
    http = launcher.http
tempLoader = Loader()
from direct.gui import DirectGuiGlobals
print 'ToontownStart: Setting the default font.'
import ToontownGlobals
if isAprilFools:
    DirectGuiGlobals.setDefaultFontFunc(ToontownGlobals.getSuitFont)
else:
    DirectGuiGlobals.setDefaultFontFunc(ToontownGlobals.getInterfaceFont)
launcher.setPandaErrorCode(7)
import ToonBase
ToonBase.ToonBase()
from panda3d.core import *
if base.win == None:
    print 'Unable to open window; aborting.'
    sys.exit()
launcher.setPandaErrorCode(0)
launcher.setPandaWindowOpen()
ConfigVariableDouble('decompressor-step-time').setValue(0.01)
ConfigVariableDouble('extractor-step-time').setValue(0.01)
base.graphicsEngine.renderFrame()
if config.GetBool('want-retro-mode', False):
    DirectGuiGlobals.setDefaultRolloverSound(base.loader.loadSfx('phase_3/audio/sfx/GUI_rollover_retro.ogg'))
else:
    DirectGuiGlobals.setDefaultRolloverSound(base.loader.loadSfx('phase_3/audio/sfx/GUI_rollover.ogg'))
DirectGuiGlobals.setDefaultClickSound(base.loader.loadSfx('phase_3/audio/sfx/GUI_create_toon_fwd.ogg'))
DirectGuiGlobals.setDefaultDialogGeom(loader.loadModel('phase_3/models/gui/dialog_box_gui'))
import TTLocalizer
from otp.otpbase import OTPGlobals
OTPGlobals.setDefaultProductPrefix(TTLocalizer.ProductPrefix)
if base.musicManagerIsValid:
    if config.GetBool('want-retro-mode', False):
        music = base.musicManager.getSound('phase_3/audio/bgm/tt_theme.ogg')
    else:
        if config.GetBool('want-doomsday', False):
            music = base.musicManager.getSound('phase_3/audio/bgm/ttoff_theme.ogg')
        else:
            if isHalloween:
                music = base.musicManager.getSound('phase_3/audio/bgm/ttoff_theme.ogg')
            else:
                if isAprilFoolsWeek:
                    music = base.musicManager.getSound('phase_3/audio/bgm/ttoff_theme.ogg')
                else:
                    if isWinter:
                        music = base.musicManager.getSound('phase_3/audio/bgm/ttoff_theme.ogg')
                    else:
                        music = base.musicManager.getSound('phase_3/audio/bgm/ttoff_theme.ogg')
    if music:
        music.setLoop(True)
        music.setVolume(0.9)
        music.play()
    print 'ToontownStart: Loading the default GUI sounds.'
    if config.GetBool('want-retro-mode', False):
        DirectGuiGlobals.setDefaultRolloverSound(base.loader.loadSfx('phase_3/audio/sfx/GUI_rollover_retro.ogg'))
    else:
        DirectGuiGlobals.setDefaultRolloverSound(base.loader.loadSfx('phase_3/audio/sfx/GUI_rollover.ogg'))
    DirectGuiGlobals.setDefaultClickSound(base.loader.loadSfx('phase_3/audio/sfx/GUI_create_toon_fwd.ogg'))
else:
    music = None
from direct.gui.DirectGui import *
serverVersion = config.GetString('server-version', 'no_version_set')
print 'ToontownStart: Game Version: ', serverVersion
if config.GetBool('want-retro-mode', False):
    credit = OnscreenText(text='Powered by the Fabulous Toontown Rewritten Engine', pos=(1.3,
                                                                                         0.935), scale=0.06, fg=Vec4(0, 0, 1, 0.6), align=TextNode.ARight)
    credit.setPos(-0.033, -0.065)
    credit.reparentTo(base.a2dTopRight)
    version = OnscreenText(serverVersion, pos=(-1.3, -0.975), scale=0.06, fg=Vec4(0, 0, 1, 0.6), align=TextNode.ALeft)
    version.setPos(0.033, 0.025)
    version.reparentTo(base.a2dBottomLeft)
if isAprilFoolsWeek:
    loader.beginBulkLoad('init', random.choice(TTLocalizer.AprilFoolsLoaderLabel), 138, 0, TTLocalizer.TIP_NONE)
else:
    loader.beginBulkLoad('init', TTLocalizer.LoaderLabel, 138, 0, TTLocalizer.TIP_NONE)
from ToonBaseGlobal import *
from toontown.distributed import ToontownClientRepository
cr = ToontownClientRepository.ToontownClientRepository(serverVersion, launcher)
cr.music = music
del music
base.initNametagGlobals()
base.cr = cr
base.cr.isHalloween = isHalloween
base.cr.isAprilFools = isAprilFoolsWeek
base.cr.oranges = isAprilFools
base.cr.isWinter = isWinter
loader.endBulkLoad('init')
from otp.distributed.OtpDoGlobals import *
cr.generateGlobalObject(OTP_DO_ID_FRIEND_MANAGER, 'FriendManager')
if not launcher.isDummy() and config.GetBool('want-mini-server', False):
    print 'ToontownStart: Mini-server mode enabled! Connecting to defined game server...'
    base.startShow(cr, launcher.getGameServer())
else:
    if config.GetBool('auto-start-local-server', False):
        print 'ToontownStart: Mini-server mode disabled! Starting local server...'
        from otp.otpbase.OTPLocalizer import CRLoadingGameServices
        dialogClass = ToontownGlobals.getGlobalDialogClass()
        __builtin__.gameServicesDialog = dialogClass(message=CRLoadingGameServices)
        __builtin__.gameServicesDialog.show()
        from toontown.server.DedicatedServer import DedicatedServer
        __builtin__.localServer = DedicatedServer(isLocal=True)
        __builtin__.localServer.start()

        def localServerReady():
            __builtin__.gameServicesDialog.cleanup()
            del __builtin__.gameServicesDialog
            base.startShow(cr)


        base.accept('localServerReady', localServerReady)
    else:
        print 'ToontownStart: Mini-server mode disabled! Connecting to localhost (127.0.0.1)...'
        base.startShow(cr)
del tempLoader
if config.GetBool('want-retro-mode', False):
    credit.cleanup()
    del credit
    version.cleanup()
    del version
base.loader = base.loader
__builtin__.loader = base.loader
autoRun = ConfigVariableBool('toontown-auto-run', 1)
gc.enable()
gc.collect()
if autoRun:
    try:
        base.run()
    except SystemExit:
        raise
    except:
        print PythonUtil.describeException()
        raise