import __builtin__, argparse, aes, niraidata
from panda3d.core import *
parser = argparse.ArgumentParser(description='Toontown Offline - Game & Server Runtime')
group = parser.add_mutually_exclusive_group()
group.add_argument('-g', '--game', help='Starts the game client.', action='store_true')
group.add_argument('-d', '--dedicated', help='Starts the dedicated server.', action='store_true')
group.add_argument('-u', '--uberdog', help=argparse.SUPPRESS, action='store_true')
group.add_argument('-a', '--ai', help=argparse.SUPPRESS, action='store_true')
args = parser.parse_args()
if not (args.dedicated or args.uberdog or args.ai) and not args.game:
    args.game = True
prc = niraidata.CONFIG
iv, key, prc = prc[:16], prc[16:32], prc[32:]
prc = aes.decrypt(prc, key, iv)
for line in prc.split('\n'):
    line = line.strip()
    if line:
        loadPrcFileData('nirai config', line)

del prc
del iv
del key
__builtin__.dcStream = StringStream()
dc = niraidata.DC
iv, key, dc = dc[:16], dc[16:32], dc[32:]
dc = aes.decrypt(dc, key, iv)
dcStream.setData(dc)
del dc
del iv
del key
if args.game:
    try:
        import toontown.toonbase.ToontownStart
    except SystemExit:
        pass

else:
    if args.dedicated:
        try:
            import toontown.server.DedicatedServerStart
        except SystemExit:
            pass

    else:
        if args.uberdog:
            try:
                import toontown.uberdog.ServiceStart
            except SystemExit:
                pass

        else:
            if args.ai:
                try:
                    import toontown.ai.ServiceStart
                except SystemExit:
                    pass