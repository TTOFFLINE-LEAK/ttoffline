from panda3d.core import VirtualFileSystem, ConfigVariableList, Filename
import sys
sys.path = [
 '']
vfs = VirtualFileSystem.getGlobalPtr()
mounts = ConfigVariableList('vfs-mount')
for mount in mounts:
    mountFile, mountPoint = (mount.split(' ', 2) + [None, None, None])[:2]
    vfs.mount(Filename(mountFile), Filename(mountPoint), 0)

from toontown.launcher.TTOffQuickLauncher import TTOffQuickLauncher
launcher = TTOffQuickLauncher()
launcher.notify.info('Reached end of StartTTOffQuickLauncher.py.')