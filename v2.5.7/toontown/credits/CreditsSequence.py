from otp.ai.MagicWordGlobal import *
from toontown.credits.AlphaCredits import *

class CreditsSequence:

    def __init__(self, sequence):
        self.loaded = False
        self.sequence = sequence
        self.interval = None
        self.localToonName = None
        self.creditsScenes = CreditsScenes
        return

    def load(self):
        if self.loaded:
            return
        if self.localToonName is not None:
            self.creditsScenes.append(Credits(self.localToonName, 'Supporting Toontown Offline\nDoomsday Survivor', '03-4-19_you.jpg', 'left', special='final'))
        for scene in self.creditsScenes:
            scene.load()

        self.loaded = True
        return

    def unload(self):
        if not self.loaded:
            return
        for scene in self.creditsScenes:
            scene.unload()

        self.loaded = False

    def setLocalToonDetails(self, name, dna):
        self.localToonName = name
        self.localToonDNA = dna

    def enter(self):
        if self.interval:
            return
        if not self.loaded:
            self.load()
        self.interval = Sequence()
        for scene in self.creditsScenes:
            self.interval.append(scene.makeInterval())

        self.interval.append(Wait(1))
        self.interval.append(Func(base.cr.killClientAlphaIsOver))
        self.interval.start()

    def exit(self):
        if self.interval:
            self.interval.finish()
            self.interval = None
        return


@magicWord()
def rollCredits():
    taskMgr.doMethodLater(0.1, base.cr.loginFSM.request, 'rollCredits-magic-word', extraArgs=[
     'credits'])