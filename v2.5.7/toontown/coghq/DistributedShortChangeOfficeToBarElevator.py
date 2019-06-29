from direct.distributed.ClockDelta import *
from direct.interval.IntervalGlobal import *
from toontown.building import ElevatorConstants
from toontown.distributed import DelayDelete
from toontown.building.ElevatorUtils import *
from toontown.building import DistributedElevatorExt
from toontown.building import DistributedElevator
from toontown.toonbase import ToontownGlobals
from direct.fsm import ClassicFSM
from direct.fsm import State
from direct.gui import DirectGui
from toontown.hood import ZoneUtil
from toontown.toonbase import TTLocalizer
from toontown.toontowngui import TTDialog
import CogDisguiseGlobals

class DistributedShortChangeOfficeToBarElevator(DistributedElevatorExt.DistributedElevatorExt):

    def __init__(self, cr):
        DistributedElevatorExt.DistributedElevatorExt.__init__(self, cr)
        self.type = ElevatorConstants.ELEVATOR_NORMAL
        self.countdownTime = ElevatorData[self.type]['countdown']
        self.fillSlotTrack = None
        return

    def generate(self):
        DistributedElevatorExt.DistributedElevatorExt.generate(self)

    def delete(self):
        self.elevatorModel.removeNode()
        del self.elevatorModel
        DistributedElevatorExt.DistributedElevatorExt.delete(self)

    def setupElevator(self):
        self.elevatorModel = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_csa_elevatorB')
        self.elevatorModel.reparentTo(render)
        self.elevatorModel.setPosHpr(0, -49.25, 0, -180, 0, 0)
        self.specialNode = self.elevatorModel.attachNewNode('screwCogDoElevators')
        self.specialNode.setPosHpr(0, 0, 0, 180, 0, 0)
        self.leftDoor = self.elevatorModel.find('**/left_door')
        self.rightDoor = self.elevatorModel.find('**/right_door')
        self.elevatorSphere = CollisionSphere(0, 0, 0, 3)
        self.elevatorSphere.setTangible(1)
        self.elevatorSphereNode = CollisionNode(self.uniqueName('elevatorSphere'))
        self.elevatorSphereNode.setIntoCollideMask(ToontownGlobals.WallBitmask)
        self.elevatorSphereNode.addSolid(self.elevatorSphere)
        self.elevatorSphereNodePath = self.getElevatorModel().attachNewNode(self.elevatorSphereNode)
        self.elevatorSphereNodePath.hide()
        self.elevatorSphereNodePath.reparentTo(self.getElevatorModel())
        self.elevatorSphereNodePath.stash()
        self.boardedAvIds = {}
        self.openDoors = getOpenInterval(self, self.leftDoor, self.rightDoor, self.openSfx, self.finalOpenSfx, self.type)
        self.closeDoors = getCloseInterval(self, self.leftDoor, self.rightDoor, self.closeSfx, self.finalCloseSfx, self.type)
        self.closeDoors = Sequence(self.closeDoors, Func(self.onDoorCloseFinish))
        self.finishSetup()

    def getElevatorModel(self):
        return self.elevatorModel

    def getElevatorModelGhost(self):
        return self.specialNode

    def setBldgDoId(self, bldgDoId):
        self.bldg = None
        self.setupElevator()
        return

    def getZoneId(self):
        return 0

    def fillSlot(self, index, avId, wantBoardingShow=0):
        self.notify.debug('%s.fillSlot(%s, %s, ...)' % (self.doId, index, avId))
        request = self.toonRequests.get(index)
        if request:
            self.cr.relatedObjectMgr.abortRequest(request)
            del self.toonRequests[index]
        if avId == 0:
            pass
        else:
            if not self.cr.doId2do.has_key(avId):
                func = PythonUtil.Functor(self.gotToon, index, avId)
                self.toonRequests[index] = self.cr.relatedObjectMgr.requestObjects([avId], allCallback=func)
            else:
                if not self.isSetup:
                    self.deferredSlots.append((index, avId, wantBoardingShow))
                else:
                    if avId == base.localAvatar.getDoId():
                        place = base.cr.playGame.getPlace()
                        if not place:
                            return
                        place.detectedElevatorCollision(self)
                        elevator = self.getPlaceElevator()
                        if elevator == None:
                            if place.fsm.hasStateNamed('elevator'):
                                place.fsm.request('elevator')
                            else:
                                if place.fsm.hasStateNamed('Elevator'):
                                    place.fsm.request('Elevator')
                            elevator = self.getPlaceElevator()
                        if not elevator:
                            return
                        self.localToonOnBoard = 1
                        if hasattr(localAvatar, 'boardingParty') and localAvatar.boardingParty:
                            localAvatar.boardingParty.forceCleanupInviteePanel()
                            localAvatar.boardingParty.forceCleanupInviterPanels()
                        if hasattr(base.localAvatar, 'elevatorNotifier'):
                            base.localAvatar.elevatorNotifier.cleanup()
                        cameraTrack = Sequence()
                        cameraTrack.append(Func(elevator.fsm.request, 'boarding', [self.getElevatorModelGhost()]))
                        cameraTrack.append(Func(elevator.fsm.request, 'boarded'))
                    toon = self.cr.doId2do[avId]
                    toon.stopSmooth()
                    if not wantBoardingShow:
                        toon.setZ(self.getElevatorModel(), self.elevatorPoints[index][2])
                        toon.setShadowHeight(0)
                    if toon.isDisguised:
                        animInFunc = Sequence(Func(toon.suit.loop, 'walk'))
                        animFunc = Sequence(Func(toon.setAnimState, 'neutral', 1.0), Func(toon.suit.loop, 'neutral'))
                    else:
                        animInFunc = Sequence(Func(toon.setAnimState, 'run', 1.0))
                        animFunc = Func(toon.setAnimState, 'neutral', 1.0)
                    toon.headsUp(self.getElevatorModel(), apply(Point3, self.elevatorPoints[index]))
                    track = Sequence(animInFunc, LerpPosInterval(toon, TOON_BOARD_ELEVATOR_TIME * 0.75, apply(Point3, self.elevatorPoints[index]), other=self.getElevatorModel()), LerpHprInterval(toon, TOON_BOARD_ELEVATOR_TIME * 0.25, Point3(180, 0, 0), other=self.getElevatorModel()), Func(self.clearToonTrack, avId), animFunc, name=toon.uniqueName('fillElevator'), autoPause=1)
                    if wantBoardingShow:
                        boardingTrack, boardingTrackType = self.getBoardingTrack(toon, index, False)
                        track = Sequence(boardingTrack, track)
                        if avId == base.localAvatar.getDoId():
                            cameraWaitTime = 2.5
                            if boardingTrackType == BoardingGroupShow.TRACK_TYPE_RUN:
                                cameraWaitTime = 0.5
                            else:
                                if boardingTrackType == BoardingGroupShow.TRACK_TYPE_POOF:
                                    cameraWaitTime = 1
                            cameraTrack = Sequence(Wait(cameraWaitTime), cameraTrack)
                    if self.canHideBoardingQuitBtn(avId):
                        track = Sequence(Func(localAvatar.boardingParty.groupPanel.disableQuitButton), track)
                    if avId == base.localAvatar.getDoId():
                        track = Parallel(cameraTrack, track)
                    track.delayDelete = DelayDelete.DelayDelete(toon, 'Elevator.fillSlot')
                    self.storeToonTrack(avId, track)
                    track.start()
                    self.fillSlotTrack = track
                    self.boardedAvIds[avId] = None
        return

    def enterClosing(self, ts):
        if self.localToonOnBoard:
            elevator = self.getPlaceElevator()
            if elevator:
                elevator.fsm.request('elevatorClosing')
        if self.localToonOnBoard:
            cm = CardMaker('card')
            cm.setFrameFullscreenQuad()
            self.explosionCard = render2d.attachNewNode(cm.generate())
            self.explosionCard.setTransparency(1)
            self.explosionCard.setColorScale(0, 0, 0, 0)
            self.seq = Sequence(self.explosionCard.colorScaleInterval(2, (0, 0, 0,
                                                                          1)), Wait(3.5), self.explosionCard.colorScaleInterval(1, (0,
                                                                                                                                    0,
                                                                                                                                    0,
                                                                                                                                    0)), Wait(1), Func(self.explosionCard.removeNode), Func(base.localAvatar.disableSleeping), Func(base.localAvatar.invPage.ignoreOnscreenHooks), Func(base.localAvatar.questPage.ignoreOnscreenHooks))
            self.seq.start(ts)
        self.closeDoors.start(ts)

    def exitClosing(self):
        pass

    def __doorsClosed(self, zoneId):
        pass

    def setDestinationZone(self, zoneId):
        if self.localToonOnBoard:
            hoodId = self.cr.playGame.hood.hoodId
            doneStatus = {'loader': 'cogHQLoader', 'where': 'factoryExterior', 
               'how': 'teleportIn', 
               'zoneId': zoneId, 
               'hoodId': hoodId}
            self.cr.playGame.getPlace().elevator.signalDone(doneStatus)

    def setDestinationZoneForce(self, zoneId):
        place = self.cr.playGame.getPlace()
        if place:
            place.fsm.request('elevator', [self, 1])
            hoodId = self.cr.playGame.hood.hoodId
            doneStatus = {'loader': 'cogHQLoader', 'where': 'factoryExterior', 
               'how': 'teleportIn', 
               'zoneId': zoneId, 
               'hoodId': hoodId}
            if hasattr(place, 'elevator') and place.elevator:
                place.elevator.signalDone(doneStatus)
            else:
                self.notify.warning("setDestinationZoneForce: Couldn't find playGame.getPlace().elevator, zoneId: %s" % zoneId)
        else:
            self.notify.warning("setDestinationZoneForce: Couldn't find playGame.getPlace(), zoneId: %s" % zoneId)

    def rejectBoard(self, avId, reason=0):
        print 'rejectBoard %s' % reason
        if hasattr(base.localAvatar, 'elevatorNotifier'):
            if reason == ElevatorConstants.REJECT_SHUFFLE:
                base.localAvatar.elevatorNotifier.showMe(TTLocalizer.ElevatorHoppedOff)
            elif reason == ElevatorConstants.REJECT_MINLAFF:
                base.localAvatar.elevatorNotifier.showMe(TTLocalizer.KartMinLaff % self.minLaff)
            elif reason == ElevatorConstants.REJECT_PROMOTION:
                base.localAvatar.elevatorNotifier.showMe(TTLocalizer.BossElevatorRejectMessage)
            elif reason == ElevatorConstants.REJECT_NOT_YET_AVAILABLE:
                base.localAvatar.elevatorNotifier.showMe(TTLocalizer.NotYetAvailable)
        doneStatus = {'where': 'reject'}
        elevator = self.getPlaceElevator()
        if elevator:
            elevator.signalDone(doneStatus)

    def __handleRejectAck(self):
        doneStatus = self.rejectDialog.doneStatus
        if doneStatus != 'ok':
            self.notify.error('Unrecognized doneStatus: ' + str(doneStatus))
        doneStatus = {'where': 'reject'}
        self.cr.playGame.getPlace().elevator.signalDone(doneStatus)
        self.rejectDialog.cleanup()
        del self.rejectDialog

    def getDestName(self):
        return TTLocalizer.lBar