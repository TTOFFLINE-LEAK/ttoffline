import __builtin__, os, sys, glob
from panda3d.core import Filename, Multifile, StringStream, VirtualFile, VirtualFileSystem, loadPrcFile, loadPrcFileData
import aes, argparse, traceback, niraidata, OfflineGlobals
prc = niraidata.CONFIGFILE
iv, key, prc = prc[:32], prc[32:64], prc[64:]
prc = aes.decrypt(prc, key, iv)
for line in prc.split('\n'):
    line = line.strip()
    if line:
        loadPrcFileData('', line)

del prc
del iv
del key
__builtin__.dcStream = StringStream()
dc = niraidata.DCFILE
iv, key, dc = dc[:32], dc[32:64], dc[64:]
dc = aes.decrypt(dc, key, iv)
dcStream.setData(dc)
del dc
del iv
del key
parser = argparse.ArgumentParser()
parser.add_argument('--uberdog', action='store_true', help='Marks the game as an Uberdog instance.')
parser.add_argument('--ai', action='store_true', help='Marks the game as an AI instance.')
parser.add_argument('--dedicated', action='store_true', help='Marks the game as a dedicated instance.')
args = parser.parse_args()
if os.environ.get('TTOFF_GAME_SERVER', None):
    loadPrcFileData('', 'mini-server #t')
    loadPrcFileData('', 'auto-start-local-server #f')
else:
    loadPrcFileData('', 'mini-server #f')
    loadPrcFileData('', 'auto-start-local-server #t')
vfs = VirtualFileSystem.getGlobalPtr()

def mountWithSignature(filename, name):
    if not os.path.isfile(filename):
        return False
    mf = Multifile()
    mf.openRead(Filename(filename))
    if mf.getNumSignatures() != 1:
        return False
    if mf.getSignaturePublicKey(0) != OfflineGlobals.getmfcrt():
        return False
    if name == 14 or name == 14.5:
        mf.setEncryptionPassword(OfflineGlobals.getmfkey(filename))
    return vfs.mount(mf, Filename('/'), 0)


def loadPhases():
    for mf in [3, 3.5, 4, 5, 5.5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 14.5]:
        filenameBase = 'resources/default/phase_%s' % mf
        mounted = mountWithSignature(filenameBase + '.mf', mf)
        if not mounted:
            print ('Unable to mount phase_{0}.').format(mf)
            sys.exit()
            break

    filenameBase = 'resources'
    for pack in os.listdir(filenameBase):
        if pack == 'default':
            continue
        directory = os.path.join(filenameBase, pack)
        if not os.path.isdir(directory):
            continue
        print ('Loading content pack {0}...').format(pack)
        for file in glob.glob('%s/%s/*.mf' % (filenameBase, pack)):
            mf = Multifile()
            mf.openReadWrite(Filename(file))
            names = mf.getSubfileNames()
            for name in names:
                ext = os.path.splitext(name)[1]
                if ext not in ('.jpg', '.jpeg', '.ogg', '.rgb', '.png'):
                    mf.removeSubfile(name)

            vfs.mount(mf, Filename('/'), 0)


loadPhases()
try:
    if args.uberdog:
        pass
    else:
        if args.ai:
            pass
        else:
            if args.dedicated:
                pass
            else:
                import toontown.launcher.TTOffQuickStartLauncher
except:
    traceback.print_exc()