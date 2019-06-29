import TTStreet
from toontown.toonbase import TTLocalizer, ToontownGlobals

class TutorialStreet(TTStreet.TTStreet):

    def enter(self, requestStatus):
        TTStreet.TTStreet.enter(self, requestStatus, visibilityFlag=0, arrowsOn=0)
        base.cr.discordManager.setInfo(base.cr.discordManager.getState(), TTLocalizer.GlobalStreetNames.get(ToontownGlobals.TutorialHood)[2], ToontownGlobals.Zone2String.get(ToontownGlobals.ToontownCentral), None, None, None, ToontownGlobals.ToontownCentral)
        return

    def exit(self):
        TTStreet.TTStreet.exit(self, visibilityFlag=0)

    def enterTeleportIn(self, requestStatus):
        TTStreet.TTStreet.enterTeleportIn(self, requestStatus)

    def enterTownBattle(self, event):
        self.loader.townBattle.enter(event, self.fsm.getStateNamed('battle'), tutorialFlag=1)

    def handleEnterTunnel(self, requestStatus, collEntry):
        messenger.send('stopTutorial')
        TTStreet.TTStreet.handleEnterTunnel(self, requestStatus, collEntry)

    def exitDoorIn(self):
        base.localAvatar.obscureMoveFurnitureButton(-1)