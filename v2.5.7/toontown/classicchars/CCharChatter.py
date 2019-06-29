from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
GREETING = 0
COMMENT = 1
GOODBYE = 2
DaisyChatter = TTLocalizer.DaisyChatter
MickeyChatter = TTLocalizer.MickeyChatter
VampireMickeyChatter = TTLocalizer.VampireMickeyChatter
MinnieChatter = TTLocalizer.MinnieChatter
GoofyChatter = TTLocalizer.GoofyChatter
GoofySpeedwayChatter = TTLocalizer.GoofySpeedwayChatter
DonaldChatter = TTLocalizer.DonaldChatter
ChipChatter = TTLocalizer.ChipChatter
DaleChatter = TTLocalizer.DaleChatter

def getExtendedChat(chatset, extendedChat):
    newChat = []
    for chatList in chatset:
        newChat.append(list(chatList))

    newChat[1] += extendedChat
    return newChat


def getChatter(charName, chatterType):
    if charName == TTLocalizer.Mickey:
        if chatterType == ToontownGlobals.APRIL_FOOLS_COSTUMES:
            return TTLocalizer.AFMickeyChatter
        if chatterType == ToontownGlobals.WINTER_CAROLING:
            return TTLocalizer.WinterMickeyCChatter
        if chatterType == ToontownGlobals.WINTER_DECORATIONS:
            return TTLocalizer.WinterMickeyDChatter
        if chatterType == ToontownGlobals.WACKY_WINTER_CAROLING:
            return TTLocalizer.WinterMickeyCChatter
        if chatterType == ToontownGlobals.WACKY_WINTER_DECORATIONS:
            return TTLocalizer.WinterMickeyDChatter
        if chatterType == ToontownGlobals.VALENTINES_DAY:
            return TTLocalizer.ValentinesMickeyChatter
        if chatterType == ToontownGlobals.SILLY_CHATTER_ONE:
            SillyMickeyChatter = getExtendedChat(MickeyChatter, TTLocalizer.SillyPhase1Chatter)
            return SillyMickeyChatter
        if chatterType == ToontownGlobals.SILLY_CHATTER_TWO:
            SillyMickeyChatter = getExtendedChat(MickeyChatter, TTLocalizer.SillyPhase2Chatter)
            return SillyMickeyChatter
        if chatterType == ToontownGlobals.SILLY_CHATTER_THREE:
            SillyMickeyChatter = getExtendedChat(MickeyChatter, TTLocalizer.SillyPhase3Chatter)
            return SillyMickeyChatter
        if chatterType == ToontownGlobals.SILLY_CHATTER_FOUR:
            SillyMickeyChatter = getExtendedChat(MickeyChatter, TTLocalizer.SillyPhase4Chatter)
            return SillyMickeyChatter
        if chatterType == ToontownGlobals.SELLBOT_FIELD_OFFICE:
            fieldOfficeMickeyChatter = getExtendedChat(MickeyChatter, TTLocalizer.FieldOfficeMickeyChatter)
            return fieldOfficeMickeyChatter
        return MickeyChatter
    else:
        if charName == TTLocalizer.VampireMickey:
            return VampireMickeyChatter
    if charName == TTLocalizer.Minnie:
        if chatterType == ToontownGlobals.APRIL_FOOLS_COSTUMES:
            return TTLocalizer.AFMinnieChatter
        if chatterType == ToontownGlobals.WINTER_CAROLING:
            return TTLocalizer.WinterMinnieCChatter
        if chatterType == ToontownGlobals.WINTER_DECORATIONS:
            return TTLocalizer.WinterMinnieDChatter
        if chatterType == ToontownGlobals.WACKY_WINTER_CAROLING:
            return TTLocalizer.WinterMinnieCChatter
        if chatterType == ToontownGlobals.WACKY_WINTER_DECORATIONS:
            return TTLocalizer.WinterMinnieDChatter
        if chatterType == ToontownGlobals.VALENTINES_DAY:
            return TTLocalizer.ValentinesMinnieChatter
        if chatterType == ToontownGlobals.SILLY_CHATTER_ONE:
            SillyMinnieChatter = getExtendedChat(MinnieChatter, TTLocalizer.SillyPhase1Chatter)
            return SillyMinnieChatter
        if chatterType == ToontownGlobals.SILLY_CHATTER_TWO:
            SillyMinnieChatter = getExtendedChat(MinnieChatter, TTLocalizer.SillyPhase2Chatter)
            return SillyMinnieChatter
        if chatterType == ToontownGlobals.SILLY_CHATTER_THREE:
            SillyMinnieChatter = getExtendedChat(MinnieChatter, TTLocalizer.SillyPhase3Chatter)
            return SillyMinnieChatter
        if chatterType == ToontownGlobals.SILLY_CHATTER_FOUR:
            SillyMinnieChatter = getExtendedChat(MinnieChatter, TTLocalizer.SillyPhase4Chatter)
            return SillyMinnieChatter
        if chatterType == ToontownGlobals.SELLBOT_FIELD_OFFICE:
            fieldOfficeMinnieChatter = getExtendedChat(MinnieChatter, TTLocalizer.FieldOfficeMinnieChatter)
            return fieldOfficeMinnieChatter
        return MinnieChatter
    else:
        if charName == TTLocalizer.WitchMinnie:
            return TTLocalizer.WitchMinnieChatter
    if charName == TTLocalizer.Daisy or charName == TTLocalizer.SockHopDaisy:
        if chatterType == ToontownGlobals.APRIL_FOOLS_COSTUMES:
            return TTLocalizer.AFDaisyChatter
        if chatterType == ToontownGlobals.HALLOWEEN_COSTUMES:
            return TTLocalizer.HalloweenDaisyChatter
        if chatterType == ToontownGlobals.SPOOKY_COSTUMES:
            return TTLocalizer.HalloweenDaisyChatter
        if chatterType == ToontownGlobals.WINTER_CAROLING:
            return TTLocalizer.WinterDaisyCChatter
        if chatterType == ToontownGlobals.WINTER_DECORATIONS:
            return TTLocalizer.WinterDaisyDChatter
        if chatterType == ToontownGlobals.WACKY_WINTER_CAROLING:
            return TTLocalizer.WinterDaisyCChatter
        if chatterType == ToontownGlobals.WACKY_WINTER_DECORATIONS:
            return TTLocalizer.WinterDaisyDChatter
        if chatterType == ToontownGlobals.VALENTINES_DAY:
            return TTLocalizer.ValentinesDaisyChatter
        if chatterType == ToontownGlobals.SILLY_CHATTER_ONE:
            SillyDaisyChatter = getExtendedChat(DaisyChatter, TTLocalizer.SillyPhase1Chatter)
            return SillyDaisyChatter
        if chatterType == ToontownGlobals.SILLY_CHATTER_TWO:
            SillyDaisyChatter = getExtendedChat(DaisyChatter, TTLocalizer.SillyPhase2Chatter)
            return SillyDaisyChatter
        if chatterType == ToontownGlobals.SILLY_CHATTER_THREE:
            SillyDaisyChatter = getExtendedChat(DaisyChatter, TTLocalizer.SillyPhase3Chatter)
            return SillyDaisyChatter
        if chatterType == ToontownGlobals.SILLY_CHATTER_FOUR:
            SillyDaisyChatter = getExtendedChat(DaisyChatter, TTLocalizer.SillyPhase4Chatter)
            return SillyDaisyChatter
        if chatterType == ToontownGlobals.SELLBOT_FIELD_OFFICE:
            fieldOfficeDaisyChatter = getExtendedChat(DaisyChatter, TTLocalizer.FieldOfficeDaisyChatter)
            return fieldOfficeDaisyChatter
        return DaisyChatter
    else:
        if charName == TTLocalizer.Goofy:
            if chatterType == ToontownGlobals.APRIL_FOOLS_COSTUMES:
                return TTLocalizer.AFGoofySpeedwayChatter
            if chatterType == ToontownGlobals.CRASHED_LEADERBOARD:
                return TTLocalizer.CLGoofySpeedwayChatter
            if chatterType == ToontownGlobals.CIRCUIT_RACING_EVENT:
                return TTLocalizer.GPGoofySpeedwayChatter
            if chatterType == ToontownGlobals.WINTER_DECORATIONS or chatterType == ToontownGlobals.WINTER_CAROLING or chatterType == ToontownGlobals.WACKY_WINTER_DECORATIONS or chatterType == ToontownGlobals.WACKY_WINTER_CAROLING:
                return TTLocalizer.WinterGoofyChatter
            if chatterType == ToontownGlobals.VALENTINES_DAY:
                return TTLocalizer.ValentinesGoofyChatter
            if chatterType == ToontownGlobals.SILLY_CHATTER_ONE:
                SillyGoofySpeedwayChatter = getExtendedChat(GoofySpeedwayChatter, TTLocalizer.SillyPhase1Chatter)
                return SillyGoofySpeedwayChatter
            if chatterType == ToontownGlobals.SILLY_CHATTER_TWO:
                SillyGoofySpeedwayChatter = getExtendedChat(GoofySpeedwayChatter, TTLocalizer.SillyPhase2Chatter)
                return SillyGoofySpeedwayChatter
            if chatterType == ToontownGlobals.SILLY_CHATTER_THREE:
                SillyGoofySpeedwayChatter = getExtendedChat(GoofySpeedwayChatter, TTLocalizer.SillyPhase3Chatter)
                return SillyGoofySpeedwayChatter
            if chatterType == ToontownGlobals.SILLY_CHATTER_FOUR:
                SillyGoofySpeedwayChatter = getExtendedChat(GoofySpeedwayChatter, TTLocalizer.SillyPhase4Chatter)
                return SillyGoofySpeedwayChatter
            if chatterType == ToontownGlobals.PROLOGUE_GOOFY_CHATTER:
                return GoofyChatter
            return GoofySpeedwayChatter
        else:
            if charName == TTLocalizer.SuperGoofy:
                return TTLocalizer.SuperGoofyChatter
        if charName == TTLocalizer.Donald or charName == TTLocalizer.FrankenDonald:
            if chatterType == ToontownGlobals.APRIL_FOOLS_COSTUMES:
                return TTLocalizer.AFDonaldChatter
            if chatterType == ToontownGlobals.HALLOWEEN_COSTUMES:
                return TTLocalizer.HalloweenDreamlandChatter
            if chatterType == ToontownGlobals.SPOOKY_COSTUMES:
                return TTLocalizer.HalloweenDreamlandChatter
            if chatterType == ToontownGlobals.WINTER_CAROLING:
                return TTLocalizer.WinterDreamlandCChatter
            if chatterType == ToontownGlobals.WINTER_DECORATIONS:
                return TTLocalizer.WinterDreamlandDChatter
            if chatterType == ToontownGlobals.WACKY_WINTER_CAROLING:
                return TTLocalizer.WinterDreamlandCChatter
            if chatterType == ToontownGlobals.WACKY_WINTER_DECORATIONS:
                return TTLocalizer.WinterDreamlandDChatter
            if chatterType == ToontownGlobals.VALENTINES_DAY:
                return TTLocalizer.ValentinesDreamlandChatter
            if chatterType == ToontownGlobals.SELLBOT_FIELD_OFFICE:
                fieldOfficeDreamlandChatter = getExtendedChat(DonaldChatter, TTLocalizer.FieldOfficeDreamlandChatter)
                return fieldOfficeDreamlandChatter
            return DonaldChatter
        else:
            if charName == TTLocalizer.DonaldDock:
                if chatterType == ToontownGlobals.APRIL_FOOLS_COSTUMES:
                    return TTLocalizer.AFDonaldDockChatter
                if chatterType == ToontownGlobals.HALLOWEEN_COSTUMES:
                    return TTLocalizer.HalloweenDonaldChatter
                if chatterType == ToontownGlobals.SPOOKY_COSTUMES:
                    return TTLocalizer.HalloweenDonaldChatter
                if chatterType == ToontownGlobals.WINTER_CAROLING:
                    return TTLocalizer.WinterDonaldCChatter
                if chatterType == ToontownGlobals.WINTER_DECORATIONS:
                    return TTLocalizer.WinterDonaldDChatter
                if chatterType == ToontownGlobals.WACKY_WINTER_CAROLING:
                    return TTLocalizer.WinterDonaldCChatter
                if chatterType == ToontownGlobals.WACKY_WINTER_DECORATIONS:
                    return TTLocalizer.WinterDonaldDChatter
                if chatterType == ToontownGlobals.VALENTINES_DAY:
                    return TTLocalizer.ValentinesDonaldChatter
                return
            else:
                if charName == TTLocalizer.Pluto:
                    if chatterType == ToontownGlobals.APRIL_FOOLS_COSTUMES:
                        return TTLocalizer.AFPlutoChatter
                    if chatterType == ToontownGlobals.HALLOWEEN_COSTUMES:
                        return TTLocalizer.WesternPlutoChatter
                    if chatterType == ToontownGlobals.SPOOKY_COSTUMES:
                        return TTLocalizer.WesternPlutoChatter
                    if chatterType == ToontownGlobals.WINTER_CAROLING:
                        return TTLocalizer.WinterPlutoCChatter
                    if chatterType == ToontownGlobals.WINTER_DECORATIONS:
                        return TTLocalizer.WinterPlutoDChatter
                    if chatterType == ToontownGlobals.WACKY_WINTER_CAROLING:
                        return TTLocalizer.WinterPlutoCChatter
                    if chatterType == ToontownGlobals.WACKY_WINTER_DECORATIONS:
                        return TTLocalizer.WinterPlutoDChatter
                    return
                else:
                    if charName == TTLocalizer.WesternPluto:
                        if chatterType == ToontownGlobals.HALLOWEEN_COSTUMES:
                            return TTLocalizer.WesternPlutoChatter
                        if chatterType == ToontownGlobals.SPOOKY_COSTUMES:
                            return TTLocalizer.WesternPlutoChatter
                        return
                    else:
                        if charName == TTLocalizer.Chip or charName == TTLocalizer.PoliceChip:
                            if chatterType == ToontownGlobals.APRIL_FOOLS_COSTUMES:
                                return TTLocalizer.AFChipChatter
                            if chatterType == ToontownGlobals.HALLOWEEN_COSTUMES:
                                return TTLocalizer.HalloweenChipChatter
                            if chatterType == ToontownGlobals.SPOOKY_COSTUMES:
                                return TTLocalizer.HalloweenChipChatter
                            if chatterType == ToontownGlobals.WINTER_DECORATIONS or chatterType == ToontownGlobals.WINTER_CAROLING or chatterType == ToontownGlobals.WACKY_WINTER_DECORATIONS or chatterType == ToontownGlobals.WACKY_WINTER_CAROLING:
                                return TTLocalizer.WinterChipChatter
                            if chatterType == ToontownGlobals.VALENTINES_DAY:
                                return TTLocalizer.ValentinesChipChatter
                            if chatterType == ToontownGlobals.SILLY_CHATTER_ONE:
                                SillyChipChatter = getExtendedChat(ChipChatter, TTLocalizer.SillyPhase1Chatter)
                                return SillyChipChatter
                            if chatterType == ToontownGlobals.SILLY_CHATTER_TWO:
                                SillyChipChatter = getExtendedChat(ChipChatter, TTLocalizer.SillyPhase2Chatter)
                                return SillyChipChatter
                            if chatterType == ToontownGlobals.SILLY_CHATTER_THREE:
                                SillyChipChatter = getExtendedChat(ChipChatter, TTLocalizer.SillyPhase3Chatter)
                                return SillyChipChatter
                            if chatterType == ToontownGlobals.SILLY_CHATTER_FOUR:
                                SillyChipChatter = getExtendedChat(ChipChatter, TTLocalizer.SillyPhase4Chatter)
                                return SillyChipChatter
                            return ChipChatter
                        else:
                            if charName == TTLocalizer.Dale or TTLocalizer.JailbirdDale:
                                if chatterType == ToontownGlobals.APRIL_FOOLS_COSTUMES:
                                    return TTLocalizer.AFDaleChatter
                                if chatterType == ToontownGlobals.HALLOWEEN_COSTUMES:
                                    return TTLocalizer.HalloweenDaleChatter
                                if chatterType == ToontownGlobals.SPOOKY_COSTUMES:
                                    return TTLocalizer.HalloweenDaleChatter
                                if chatterType == ToontownGlobals.WINTER_DECORATIONS or chatterType == ToontownGlobals.WINTER_CAROLING or chatterType == ToontownGlobals.WACKY_WINTER_DECORATIONS or chatterType == ToontownGlobals.WACKY_WINTER_CAROLING:
                                    return TTLocalizer.WinterDaleChatter
                                if chatterType == ToontownGlobals.VALENTINES_DAY:
                                    return TTLocalizer.ValentinesDaleChatter
                                if chatterType == ToontownGlobals.SILLY_CHATTER_ONE:
                                    SillyDaleChatter = getExtendedChat(DaleChatter, TTLocalizer.SillyPhase1Chatter)
                                    return SillyDaleChatter
                                if chatterType == ToontownGlobals.SILLY_CHATTER_TWO:
                                    SillyDaleChatter = getExtendedChat(DaleChatter, TTLocalizer.SillyPhase2Chatter)
                                    return SillyDaleChatter
                                if chatterType == ToontownGlobals.SILLY_CHATTER_THREE:
                                    SillyDaleChatter = getExtendedChat(DaleChatter, TTLocalizer.SillyPhase3Chatter)
                                    return SillyDaleChatter
                                if chatterType == ToontownGlobals.SILLY_CHATTER_FOUR:
                                    SillyDaleChatter = getExtendedChat(DaleChatter, TTLocalizer.SillyPhase4Chatter)
                                    return SillyDaleChatter
                                return DaleChatter
    return