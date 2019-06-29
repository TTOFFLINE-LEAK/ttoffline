from direct.gui.DirectGui import *
from panda3d.core import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from direct.interval.IntervalGlobal import *
import random, time
isHalloween = time.localtime().tm_mon == 10 and time.localtime().tm_mday >= 24
isAprilFoolsWeek = time.localtime().tm_mon == 3 and time.localtime().tm_mday >= 31 or time.localtime().tm_mon == 4 and time.localtime().tm_mday <= 8
isAprilFools = time.localtime().tm_mon == 4 and time.localtime().tm_mday == 1
isWinter = time.localtime().tm_mon == 12

class TTOffLoadingScreen:

    def __init__(self):
        self.__expectedCount = 0
        self.__count = 0
        self.firstInit = 0
        if config.GetBool('want-random-pics', True):
            self.backgroundList = [
             (
              'phase_4/maps/loading/loading_toons_', 33,
              ('Toontown Central', 'Silly Street', 'Loopy Lane', 'Punchline Place', "Donald's Dock",
 'Barnacle Boulevard', 'Seaweed Street', 'Lighthouse Lane', 'Daisy Gardens', 'Elm Street',
 'Maple Street', 'Oak Street', 'Daisy Gardens - 2003', "Minnie's Melodyland", 'Alto Avenue',
 'Baritone Boulevard', 'Tenor Terrace', 'The Brrrgh', 'Walrus Way', 'Sleet Street',
 'Polar Place', "Donald's Dreamland", 'Lullaby Lane', 'Pajama Place', 'Goofy Speedway',
 "Chip 'n Dale's Acorn Acres", "Chip 'n Dale's MiniGolf", 'Event Grounds', "Mille's Meadow")),
             (
              'phase_4/maps/loading/loading_cogs_', 20,
              ('Sellbot HQ', 'Sellbot Cog Factory', "Swag Foreman's Factory", 'Cashbot HQ', 'Lawbot HQ',
 'Bossbot HQ'))]
        else:
            self.backgroundList = [
             (
              'phase_4/maps/loading/loading_toons_', (3, 7, 9, 15, 20, 25, 27, 30, 31, 32, 33), ('Toontown Central', 'Silly Street', 'Loopy Lane', 'Punchline Place')),
             (
              'phase_4/maps/loading/loading_toons_', (1, 2, 9), ("Donald's Dock", 'Barnacle Boulevard', 'Seaweed Street', 'Lighthouse Lane')),
             (
              'phase_4/maps/loading/loading_toons_', (12, 22), ('Daisy Gardens', 'Elm Street', 'Maple Street', 'Oak Street', 'Daisy Gardens - 2003')),
             (
              'phase_4/maps/loading/loading_toons_', (13, 14, 28), ("Minnie's Melodyland", 'Alto Avenue', 'Baritone Boulevard', 'Tenor Terrace')),
             (
              'phase_4/maps/loading/loading_toons_', (5, 11, 29), ('The Brrrgh', 'Walrus Way', 'Sleet Street', 'Polar Place')),
             (
              'phase_4/maps/loading/loading_toons_', (6, 10, 16, 21, 24), ("Donald's Dreamland", 'Lullaby Lane', 'Pajama Place')),
             (
              'phase_4/maps/loading/loading_toons_', (4, 15, 23), ('Goofy Speedway', )),
             (
              'phase_4/maps/loading/loading_toons_', (14, ), ("Chip 'n Dale's Acorn Acres", "Chip 'n Dale's MiniGolf")),
             (
              'phase_4/maps/loading/loading_toons_', (11, 19, 25), ('Event Grounds', )),
             (
              'phase_4/maps/loading/loading_cogs_', (4, 5, 12, 17, 18), ('Sellbot HQ', 'Sellbot Cog Factory', "Smokin' Foreman's Factory")),
             (
              'phase_4/maps/loading/loading_cogs_', (1, 2, 3, 8, 9, 14), ('Cashbot HQ', )),
             (
              'phase_4/maps/loading/loading_cogs_', (6, 7, 10, 11, 15), ('Lawbot HQ', )),
             (
              'phase_4/maps/loading/loading_cogs_', (13, 16, 19, 20), ('Bossbot HQ', )),
             (
              'phase_4/maps/loading/loading_toons_', (8, 17, 18), ('Somewhere Over The Rainbow', ))]
        self.episodeDict = {'short_work': ('phase_4/maps/loading/loading_episode_', (2, ), ('Cashbot HQ', )), 'squirting_flower': ('phase_4/maps/loading/loading_episode_', (1, 3), ('Oak Street', )), 'prologue': (
                      'phase_4/maps/loading/loading_episode_', (4, 5, 6), ('Moneybin', 'Daisy Gardens - 2003', 'Oak Street')), 
           'gyro_tale': (
                       'phase_4/maps/loading/loading_episode_', (7, 8, 9), ('Toontown Central', 'Oak Street'))}
        self.holidayDict = {'april': ('phase_4/maps/loading/loading_april_', 14, ('boos babby', )), 'halloween': (
                       'phase_4/maps/loading/loading_halloween_', 3, ('Boo!', )), 
           'winter': (
                    'phase_4/maps/loading/loading_winter_', 6, ('Merry Christmas!', ))}
        self.backgroundImages = []
        self.backgroundImage = None
        self.zoneBg = 12
        for d in self.backgroundList:
            rc = 1
            if config.GetBool('want-random-pics', True):
                picIds = xrange(d[1])
            else:
                picIds = d[1]
            for x in picIds:
                if config.GetBool('want-random-pics', True):
                    picId = rc
                else:
                    picId = x
                img = d[0] + str(picId) + '.png'
                self.backgroundImages.append(img)
                rc = rc + 1

        self.gui = aspect2d.attachNewNode('loading_gui')
        self.coolRender = render2d.attachNewNode('loading_bg')
        self.title = DirectLabel(guiId='ToontownLoadingScreenTitle', parent=self.gui, relief=None, pos=(-1.06,
                                                                                                        0,
                                                                                                        -0.77), text='', textMayChange=1, text_scale=0.08, text_fg=(1,
                                                                                                                                                                    0.941,
                                                                                                                                                                    0.09,
                                                                                                                                                                    1), text_style=3, text_align=TextNode.ALeft)
        self.titleTTR = DirectLabel(guiId='ToontownLoadingScreenTitleTTR', parent=self.gui, relief=None, pos=(0,
                                                                                                              0,
                                                                                                              -0.77), text='', textMayChange=1, text_scale=0.15, text_fg=(1,
                                                                                                                                                                          0.941,
                                                                                                                                                                          0.09,
                                                                                                                                                                          1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
        self.waitBar = DirectWaitBar(guiId='ToontownLoadingScreenWaitBar', parent=self.gui, frameSize=(-1.06,
                                                                                                       1.06,
                                                                                                       -0.03,
                                                                                                       0.03), pos=(0,
                                                                                                                   0,
                                                                                                                   -0.85), text='')
        self.tip = DirectLabel(guiId='ToontownLoadingScreenTip', parent=self.gui, relief=None, text='', text_scale=0.05, textMayChange=1, pos=(0.0,
                                                                                                                                               0.0,
                                                                                                                                               -0.95), text_fg=(1,
                                                                                                                                                                0.941,
                                                                                                                                                                0.09,
                                                                                                                                                                1), text_style=3, text_align=TextNode.ACenter)
        self.logo = None
        self.serverVersion = config.GetString('server-version', 'no_version_set')
        if config.GetBool('want-retro-mode', False):
            self.ttofflogo = loader.loadModel('phase_3/models/gui/loading-background-new')
            self.ttofflogo.find('**/bg').setTexture(loader.loadTexture('phase_3/maps/loading_bg_clouds.jpg'), 1)
            self.credit = DirectLabel(text='', relief=None, pos=(1.3, 0, 0.935), scale=0.06, text_fg=Vec4(0, 0, 1, 0.6), text_align=TextNode.ARight)
            self.version = DirectLabel(text='', parent=self.gui, relief=None, pos=(0.85,
                                                                                   0.0,
                                                                                   -0.55), scale=0.069, text_fg=Vec4(1, 0.941, 0.09, 1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
            self.gui = loader.loadModel('phase_3/models/gui/progress-background-tto')
            self.banner = loader.loadModel('phase_3/models/gui/toon_council').find('**/scroll')
            self.banner.reparentTo(self.gui)
            self.banner.setScale(0.4, 0.4, 0.4)
            self.tip = DirectLabel(guiId='ToontownLoadingScreenTip', parent=self.banner, relief=None, text='', text_scale=TTLocalizer.TLStip, textMayChange=1, pos=(-1.2,
                                                                                                                                                                    0.0,
                                                                                                                                                                    0.1), text_fg=(0.4,
                                                                                                                                                                                   0.3,
                                                                                                                                                                                   0.2,
                                                                                                                                                                                   1), text_wordwrap=13, text_align=TextNode.ALeft)
            self.title = DirectLabel(guiId='ToontownLoadingScreenTitle', parent=self.gui, relief=None, pos=(-1.06,
                                                                                                            0,
                                                                                                            -0.77), text='', textMayChange=1, text_scale=0.08, text_fg=(0,
                                                                                                                                                                        0,
                                                                                                                                                                        0.5,
                                                                                                                                                                        1), text_align=TextNode.ALeft)
            self.titleTTR = DirectLabel(guiId='ToontownLoadingScreenTitleTTR', parent=self.gui, relief=None, pos=(0,
                                                                                                                  0,
                                                                                                                  -0.77), text='', textMayChange=1, text_scale=0.15, text_fg=(1,
                                                                                                                                                                              0.941,
                                                                                                                                                                              0.09,
                                                                                                                                                                              1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
        else:
            if config.GetBool('want-doomsday', False):
                self.ttofflogo = loader.loadModel('phase_3/models/gui/loading-background-new')
                self.credit = DirectLabel(text=TTLocalizer.CreditElections, parent=self.gui, relief=None, pos=(0.0,
                                                                                                               0.0,
                                                                                                               -0.96), scale=0.069, text_fg=Vec4(1, 0.941, 0.09, 1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
                self.version = DirectLabel(text=self.serverVersion, parent=self.gui, relief=None, pos=(0.85,
                                                                                                       0.0,
                                                                                                       -0.55), scale=0.069, text_fg=Vec4(1, 0.941, 0.09, 1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
            else:
                if isHalloween:
                    self.ttofflogo = loader.loadModel('phase_3/models/gui/loading-background-new_HW')
                    self.credit = DirectLabel(text=TTLocalizer.CreditHalloween, relief=None, pos=(0.0,
                                                                                                  0.0,
                                                                                                  -0.96), scale=0.069, text_fg=Vec4(1, 0.5, 0, 1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
                    self.version = DirectLabel(text=self.serverVersion, parent=self.gui, relief=None, pos=(0.85,
                                                                                                           0.0,
                                                                                                           -0.55), scale=0.069, text_fg=Vec4(1, 0.5, 0, 1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
                    self.title = DirectLabel(guiId='ToontownLoadingScreenTitle', parent=self.gui, relief=None, pos=(-1.06,
                                                                                                                    0,
                                                                                                                    -0.77), text='', textMayChange=1, text_scale=0.08, text_fg=(1,
                                                                                                                                                                                0.5,
                                                                                                                                                                                0,
                                                                                                                                                                                1), text_style=3, text_align=TextNode.ALeft)
                    self.titleTTR = DirectLabel(guiId='ToontownLoadingScreenTitleTTR', parent=self.gui, relief=None, pos=(0,
                                                                                                                          0,
                                                                                                                          -0.77), text='', textMayChange=1, text_scale=0.15, text_fg=(1,
                                                                                                                                                                                      0.5,
                                                                                                                                                                                      0,
                                                                                                                                                                                      1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
                    self.tip = DirectLabel(guiId='ToontownLoadingScreenTip', parent=self.gui, relief=None, text='', text_scale=0.05, textMayChange=1, pos=(0.0,
                                                                                                                                                           0.0,
                                                                                                                                                           -0.95), text_fg=(1,
                                                                                                                                                                            0.5,
                                                                                                                                                                            0,
                                                                                                                                                                            1), text_style=3, text_align=TextNode.ACenter)
                else:
                    if isAprilFoolsWeek:
                        bgTexture = loader.loadTexture('phase_3/maps/loading_background_af.png')
                        self.ttofflogo = loader.loadModel('phase_14/models/gui/loading-background-aprilfools')
                        ts = self.ttofflogo.find('**/bg').findTextureStage('*')
                        self.ttofflogo.find('**/bg').setTexture(ts, bgTexture, 1)
                        self.credit = DirectLabel(text=TTLocalizer.CreditAprilFools, parent=self.gui, relief=None, pos=(0.0,
                                                                                                                        0.0,
                                                                                                                        -0.96), scale=0.069, text_fg=Vec4(1, 0, 1, 1), text_shadow=(0.75,
                                                                                                                                                                                    1,
                                                                                                                                                                                    0,
                                                                                                                                                                                    1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getComicFont())
                        self.version = DirectLabel(text=self.serverVersion, parent=self.gui, relief=None, pos=(0.85,
                                                                                                               0.0,
                                                                                                               -0.55), scale=0.069, text_fg=Vec4(1, 0, 1, 1), text_shadow=(0.75,
                                                                                                                                                                           1,
                                                                                                                                                                           0,
                                                                                                                                                                           1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getComicFont())
                        self.logo = OnscreenImage(image='phase_14/maps/cuckhunt.png', scale=(0.35,
                                                                                             0.47,
                                                                                             0.25), pos=(0.85,
                                                                                                         0.0,
                                                                                                         0.7))
                        self.logo.setTransparency(TransparencyAttrib.MAlpha)
                    else:
                        if isWinter:
                            self.ttofflogo = loader.loadModel('phase_3/models/gui/loading-background-new_HD')
                            self.credit = DirectLabel(text=TTLocalizer.CreditWinter, parent=self.gui, relief=None, pos=(0.0,
                                                                                                                        0.0,
                                                                                                                        -0.96), scale=0.069, text_fg=Vec4(0.8, 0.1, 0.1, 1), text_shadow=(0.1,
                                                                                                                                                                                          0.8,
                                                                                                                                                                                          0.1,
                                                                                                                                                                                          1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
                            self.version = DirectLabel(text=self.serverVersion, parent=self.gui, relief=None, pos=(0.85,
                                                                                                                   0.0,
                                                                                                                   -0.55), scale=0.069, text_fg=Vec4(1, 0.941, 0.09, 1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
                        else:
                            self.ttofflogo = loader.loadModel('phase_3/models/gui/loading-background-new')
                            self.credit = DirectLabel(text=TTLocalizer.Credit, parent=self.gui, relief=None, pos=(0.0,
                                                                                                                  0.0,
                                                                                                                  -0.96), scale=0.069, text_fg=Vec4(1, 0.941, 0.09, 1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
                            self.version = DirectLabel(text=self.serverVersion, parent=self.gui, relief=None, pos=(0.85,
                                                                                                                   0.0,
                                                                                                                   -0.55), scale=0.069, text_fg=Vec4(1, 0.941, 0.09, 1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
        self.ttofflogo.setScale(1.33, 1, 1)
        self.ttofflogo.find('**/bg').setBin('fixed', 10)
        self.ttofflogo.find('**/bg').reparentTo(self.coolRender)
        return

    def destroy(self):
        self.title.destroy()
        self.titleTTR.destroy()
        self.waitBar.destroy()
        self.tip.destroy()
        self.ttofflogo.removeNode()
        self.gui.removeNode()
        self.version.destroy()
        del self.version
        self.credit.destroy()
        del self.credit
        if config.GetBool('want-retro-mode', False):
            self.banner.removeNode()

    def getTip(self, tipCategory):
        if config.GetBool('want-retro-mode', False):
            if time.localtime().tm_mon == 3 and time.localtime().tm_mday >= 31 or time.localtime().tm_mon == 4 and time.localtime().tm_mday <= 8:
                return TTLocalizer.TipTitleAF + '\n' + random.choice(TTLocalizer.TipDictAF.get(tipCategory))
            return TTLocalizer.TipTitle + '\n' + random.choice(TTLocalizer.TipDict.get(tipCategory))
        else:
            if time.localtime().tm_mon == 3 and time.localtime().tm_mday >= 31 or time.localtime().tm_mon == 4 and time.localtime().tm_mday <= 8:
                return TTLocalizer.TipTitleAF + random.choice(TTLocalizer.TipDictAF.get(tipCategory))
            return TTLocalizer.TipTitle + random.choice(TTLocalizer.TipDict.get(tipCategory))

    def generalReset(self):
        pass

    def highRiseReset(self):
        pass

    def begin(self, range, label, gui, tipCategory):
        self.waitBar['range'] = range
        if tipCategory:
            self.tip['text'] = self.getTip(tipCategory)
        else:
            self.tip['text'] = ''
        if label == 'Loading...':
            if config.GetBool('want-retro-mode', False):
                self.title['text'] = label
                self.titleTTR['text'] = ''
            else:
                self.titleTTR['text'] = label
            if isAprilFools:
                self.titleTTR['text_fg'] = Vec4(1, 0, 1, 1)
                self.titleTTR['text_shadow'] = (0.75, 1, 0, 1)
                self.titleTTR['text_font'] = ToontownGlobals.getComicFont()
        else:
            if label == 'Toontown Offline':
                self.title['text'] = 'Loading...'
                self.titleTTR['text'] = ''
            else:
                self.title['text'] = label
                self.titleTTR['text'] = ''
        self.__count = 0
        self.__expectedCount = range
        if gui:
            if not config.GetBool('want-retro-mode', False):
                done = False
                no = -1
                if label == 'The Playground':
                    d = self.backgroundList[self.zoneBg]
                    if config.GetBool('want-random-pics', True):
                        rc = random.choice(xrange(d[1])) + 1
                    else:
                        rc = random.choice(d[1])
                    self.imgPath = d[0] + str(rc) + '.png'
                else:
                    if base.cr.currentEpisode in self.episodeDict:
                        d = self.episodeDict[base.cr.currentEpisode]
                        rc = random.choice(d[1])
                        self.imgPath = d[0] + str(rc) + '.png'
                    else:
                        for d in self.backgroundList:
                            if config.GetBool('want-random-pics', True):
                                rc = random.choice(xrange(d[1])) + 1
                            else:
                                rc = random.choice(d[1])
                            no = no + 1
                            for e in d[2]:
                                if label == e:
                                    self.imgPath = d[0] + str(rc) + '.png'
                                    self.zoneBg = no
                                    done = True
                                    break

                            if done:
                                break
                            else:
                                self.imgPath = random.choice(self.backgroundImages)

                if isAprilFoolsWeek:
                    self.imgPath = self.holidayDict['april'][0] + str(random.choice(xrange(self.holidayDict['april'][1])) + 1) + '.png'
                if isHalloween:
                    if random.randint(0, 1) == 50:
                        self.imgPath = self.holidayDict['halloween'][0] + str(random.choice(xrange(self.holidayDict['halloween'][1])) + 1) + '.png'
                if isWinter:
                    if random.randint(0, 1) == 50:
                        self.imgPath = self.holidayDict['winter'][0] + str(random.choice(xrange(self.holidayDict['winter'][1])) + 1) + '.png'
                self.backgroundImage = OnscreenImage(image=self.imgPath, pos=(0, 0,
                                                                              0), scale=(1.888,
                                                                                         1,
                                                                                         1))
                self.backgroundImage.reparentTo(self.gui)
                self.tip.reparentTo(self.gui)
                self.ttofflogo.reparentTo(self.gui)
                self.ttofflogo.find('**/fg').setScale(0.7)
                self.ttofflogo.find('**/fg').setPos(0, 0, 0.55)
            if config.GetBool('want-retro-mode', False):
                self.credit.reparentTo(hidden)
                self.version.reparentTo(hidden)
                self.ttofflogo.reparentTo(hidden)
            self.waitBar.reparentTo(self.gui)
            self.title.reparentTo(self.gui)
            self.titleTTR.reparentTo(self.gui)
            self.gui.reparentTo(aspect2dp, DGG.NO_FADE_SORT_INDEX)
        else:
            if not config.GetBool('want-retro-mode', False):
                self.tip.reparentTo(aspect2dp, DGG.NO_FADE_SORT_INDEX)
            if config.GetBool('want-retro-mode', False):
                self.ttofflogo.reparentTo(hidden)
            self.credit.reparentTo(aspect2dp, DGG.NO_FADE_SORT_INDEX)
            self.version.reparentTo(aspect2dp, DGG.NO_FADE_SORT_INDEX)
            self.ttofflogo.reparentTo(aspect2dp, DGG.NO_FADE_SORT_INDEX)
            self.waitBar.reparentTo(aspect2dp, DGG.NO_FADE_SORT_INDEX)
            self.title.reparentTo(aspect2dp, DGG.NO_FADE_SORT_INDEX)
            self.titleTTR.reparentTo(aspect2dp, DGG.NO_FADE_SORT_INDEX)
            self.gui.reparentTo(hidden)
        self.waitBar.update(self.__count)

    def endStuff(self):
        if self.backgroundImage:
            self.backgroundImage.reparentTo(self.gui)
        if not config.GetBool('want-retro-mode', False):
            self.tip.reparentTo(self.gui)
            self.ttofflogo.reparentTo(self.gui)
            self.ttofflogo.find('**/fg').setScale(0.7)
            self.ttofflogo.find('**/fg').setPos(0, 0, 0.55)
        else:
            self.ttofflogo.reparentTo(hidden)
            if self.coolRender:
                self.coolRender.removeNode()
                self.coolRender = None
        self.credit.reparentTo(self.gui)
        self.version.reparentTo(self.gui)
        self.waitBar.finish()
        self.waitBar.reparentTo(self.gui)
        self.title.reparentTo(self.gui)
        self.titleTTR.reparentTo(self.gui)
        self.gui.reparentTo(hidden)
        return (
         self.__expectedCount, self.__count)

    def end(self, name):
        if isAprilFoolsWeek:
            if self.logo:
                self.logo.destroy()
                del self.logo
                self.logo = None
        if base.cr.loadingStuff == 69:
            seq = Sequence(Wait(2.5), Func(self.endStuff))
            seq.start()
        else:
            if base.cr.currentEpisode == 'short_work':
                chSeq = Sequence(Wait(8), Func(self.endStuff))
                chSeq.start()
            else:
                if self.backgroundImage:
                    self.backgroundImage.reparentTo(self.gui)
                if not config.GetBool('want-retro-mode', False):
                    self.tip.reparentTo(self.gui)
                    self.ttofflogo.reparentTo(self.gui)
                    self.ttofflogo.find('**/fg').setScale(0.7)
                    self.ttofflogo.find('**/fg').setPos(0, 0, 0.55)
                else:
                    self.ttofflogo.reparentTo(hidden)
                    if self.coolRender:
                        self.coolRender.removeNode()
                        self.coolRender = None
                self.waitBar.finish()
                self.waitBar.reparentTo(self.gui)
                self.title.reparentTo(self.gui)
                self.titleTTR.reparentTo(self.gui)
                self.credit.reparentTo(self.gui)
                self.version.reparentTo(self.gui)
                self.gui.reparentTo(hidden)
                return (
                 self.__expectedCount, self.__count)
        return

    def abort(self):
        self.gui.reparentTo(hidden)

    def tick(self):
        self.__count = self.__count + 1
        self.waitBar.update(self.__count)