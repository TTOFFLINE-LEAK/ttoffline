import sys
from panda3d.core import *
import __builtin__

class game:
    name = 'toontown'
    process = 'client'


__builtin__.game = game()
import time, os, random, __builtin__
try:
    launcher
except:
    from toontown.launcher.TTOffDummyLauncher import TTOffDummyLauncher
    launcher = TTOffDummyLauncher()
    __builtin__.launcher = launcher
else:
    launcher.setRegistry('EXIT_PAGE', 'normal')
    pollingDelay = 0.5
    print 'ToontownStart: Polling for game2 to finish...'
    while not launcher.getGame2Done():
        time.sleep(pollingDelay)

    print 'ToontownStart: Game2 is finished.'
    print 'ToontownStart: Starting the game.'
    if launcher.isDummy():
        http = HTTPClient()
    else:
        http = launcher.http
    tempLoader = Loader()
    backgroundNode = tempLoader.loadSync(Filename('phase_3/models/gui/loading-background'))
    from direct.gui import DirectGuiGlobals
    print 'ToontownStart: setting default font'
    import ToontownGlobals
    DirectGuiGlobals.setDefaultFontFunc(ToontownGlobals.getInterfaceFont)
    launcher.setPandaErrorCode(7)
    import ToonBase
    ToonBase.ToonBase()
    if base.win == None:
        print 'Unable to open window; aborting.'
        sys.exit()
    launcher.setPandaErrorCode(0)
    launcher.setPandaWindowOpen()
    ConfigVariableDouble('decompressor-step-time').setValue(0.01)
    ConfigVariableDouble('extractor-step-time').setValue(0.01)
    backgroundNodePath = aspect2d.attachNewNode(backgroundNode, 0)
    backgroundNodePath.setPos(0.0, 0.0, 0.0)
    backgroundNodePath.setScale(render2d, VBase3(1))
    num = 0
    bgNodesNames = ['default', 'halloween', 'holiday', 'aprilfools', 'retro']
    bgNodes = []
    for nodeName in bgNodesNames:
        node = backgroundNodePath.find('**/bg_' + nodeName)
        node.hide()
        bgNodes.append(node)

    bgNodes[num].show()
    bgNodes[num].setBin('fixed', 10)
    backgroundNodePath.find('**/logo').setBin('fixed', 20)
    backgroundNodePath.find('**/logo').setScale(0.8)
    base.graphicsEngine.renderFrame()
    DirectGuiGlobals.setDefaultRolloverSound(base.loader.loadSfx('phase_3/audio/sfx/GUI_rollover.ogg'))
    DirectGuiGlobals.setDefaultClickSound(base.loader.loadSfx('phase_3/audio/sfx/GUI_create_toon_fwd.ogg'))
    DirectGuiGlobals.setDefaultDialogGeom(loader.loadModel('phase_3/models/gui/dialog_box_gui'))
    import TTLocalizer
    from otp.otpbase import OTPGlobals
    OTPGlobals.setDefaultProductPrefix(TTLocalizer.ProductPrefix)
    if base.musicManagerIsValid:
        themeNames = [
         '', 'halloween_']
        themeName = themeNames[num]
        music = base.musicManager.getSound('phase_3/audio/bgm/ttoff_' + themeName + 'theme.ogg')
        if music:
            music.setLoop(1)
            music.setVolume(0.9)
            music.play()
        print 'ToontownStart: Loading default gui sounds'
        DirectGuiGlobals.setDefaultRolloverSound(base.loader.loadSfx('phase_3/audio/sfx/GUI_rollover.ogg'))
        DirectGuiGlobals.setDefaultClickSound(base.loader.loadSfx('phase_3/audio/sfx/GUI_create_toon_fwd.ogg'))
    else:
        music = None
    import ToontownLoader
    from direct.gui.DirectGui import *
    serverVersion = base.config.GetString('server-version', 'no_version_set')
    print 'ToontownStart: serverVersion: ', serverVersion
    loader.beginBulkLoad('init', TTLocalizer.LoaderLabel, 138, 0, TTLocalizer.TIP_NONE)
    from ToonBaseGlobal import *
    from direct.showbase.MessengerGlobal import *
    from toontown.distributed import ToontownClientRepository
    cr = ToontownClientRepository.ToontownClientRepository(serverVersion, launcher)
    cr.music = music
    del music
    base.initNametagGlobals()
    base.cr = cr
    loader.endBulkLoad('init')
    from otp.friends import FriendManager
    from otp.distributed.OtpDoGlobals import *
    cr.generateGlobalObject(OTP_DO_ID_FRIEND_MANAGER, 'FriendManager')
    if not launcher.isDummy() and config.GetBool('mini-server', False):
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
    backgroundNodePath.reparentTo(hidden)
    backgroundNodePath.removeNode()
    del backgroundNodePath
    del backgroundNode
    del tempLoader
    base.loader = base.loader
    __builtin__.loader = base.loader
    try:
        base.run()
    except SystemExit:
        raise
    except:
        import traceback
        traceback.print_exc()