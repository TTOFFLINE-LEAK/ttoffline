from direct.fsm import StateData

class GenderShop(StateData.StateData):

    def __init__(self, doneEvent):
        StateData.StateData.__init__(self, doneEvent)
        self.shopsVisited = []
        self.toon = None
        self.gender = 'm'
        return

    def enter(self):
        base.disableMouse()

    def showButtons(self):
        pass

    def exit(self):
        pass

    def load(self):
        pass

    def unload(self):
        pass

    def setGender(self, choice):
        self.__setGender(choice)

    def __setGender(self, choice):
        if choice == -1:
            self.gender = 'm'
        else:
            self.gender = 'f'
        messenger.send(self.doneEvent)