from otp.avatar.AvatarHandle import AvatarHandle

class AvatarFriendInfo(AvatarHandle):

    def __init__(self, avatarName='', playerName='', playerId=0, onlineYesNo=0, openChatEnabledYesNo=0, openChatFriendshipYesNo=0, wlChatEnabledYesNo=0):
        self.avatarName = avatarName
        self.playerName = playerName
        self.playerId = playerId
        self.onlineYesNo = onlineYesNo
        self.openChatEnabledYesNo = openChatEnabledYesNo
        self.openChatFriendshipYesNo = openChatFriendshipYesNo
        self.wlChatEnabledYesNo = wlChatEnabledYesNo
        self.understandableYesNo = self.isUnderstandable()

    def calcUnderstandableYesNo(self):
        self.understandableYesNo = self.isUnderstandable()

    def getName(self):
        if self.avatarName:
            return self.avatarName
        if self.playerName:
            return self.playerName
        return ''

    def isUnderstandable(self):
        result = False
        try:
            if self.openChatFriendshipYesNo:
                result = True
            else:
                if self.openChatEnabledYesNo and base.cr.openChatEnabled:
                    result = True
                else:
                    if self.wlChatEnabledYesNo and base.cr.whiteListChatEnabled:
                        result = True
        except:
            pass

        return result

    def isOnline(self):
        return self.onlineYesNo