from toontown.toonbase import ToontownGlobals
import SellbotLegFactorySpec, SellbotLegFactoryCogs, LawbotLegFactorySpec, LawbotLegFactoryCogs

def getFactorySpecModule(factoryId):
    return FactorySpecModules[factoryId]


def getCogSpecModule(factoryId):
    return CogSpecModules[factoryId]


FactorySpecModules = {ToontownGlobals.SellbotFactoryInt: SellbotLegFactorySpec, ToontownGlobals.LawbotOfficeInt: LawbotLegFactorySpec}
CogSpecModules = {ToontownGlobals.SellbotFactoryInt: SellbotLegFactoryCogs, ToontownGlobals.LawbotOfficeInt: LawbotLegFactoryCogs}
if __dev__:
    import FactoryMockupSpec
    FactorySpecModules[ToontownGlobals.MockupFactoryId] = FactoryMockupSpec
    import FactoryMockupCogs
    CogSpecModules[ToontownGlobals.MockupFactoryId] = FactoryMockupCogs