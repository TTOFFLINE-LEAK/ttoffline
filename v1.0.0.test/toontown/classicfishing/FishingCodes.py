from toontown.toonbase import TTLocalizer
NoMovie = 0
EnterMovie = 1
ExitMovie = 2
CastMovie = 3
NibbleMovie = 4
BeginReelMovie = 5
ContinueReelMovie = 6
PullInMovie = 7
CastTime = 2.0
NibbleTime = 3.0
NibbleMinWait = 5.0
NibbleMaxWait = 15.0
PostNibbleWait = 5.0
ReelInTime = 10.0
EmptyReelInTime = 4.0
StandingTimeout = 30.0
CastTimeout = 60.0
ReleaseTimeout = 90.0
CalcCrankSpeed = 0.5
StandardCrankSpeed = 360.0
Nothing = 0
QuestItem = 1
FishItem = 2
TooSoon = 3
TooLate = 4
AutoReel = 5
TooSlow = 6
TooFast = 7
OverLimitFishItem = 8
AutoReelFailure = 20
ManualReelMatch = 20
MaxFishes = 16
FishValues = [
 10,
 40,
 30,
 60,
 40,
 40,
 30,
 20,
 20,
 60,
 40,
 30,
 40,
 40,
 30,
 0,
 5]

def getFishName(fishId):
    return TTLocalizer.ClassicFishNames[fishId][0]


def getPluralFishName(fishId):
    return TTLocalizer.ClassicFishNames[fishId][1]