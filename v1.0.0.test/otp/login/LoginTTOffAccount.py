from direct.directnotify import DirectNotifyGlobal
from otp.login.LoginBase import LoginBase

class LoginTTOffAccount(LoginBase):
    notify = DirectNotifyGlobal.directNotify.newCategory('LoginTTOffAccount')

    def __init__(self, cr):
        LoginBase.__init__(self, cr)
        self.cr.whiteListChatEnabled = 1

    def supportsRelogin(self):
        return 0

    def supportsAuthenticateDelete(self):
        return 0