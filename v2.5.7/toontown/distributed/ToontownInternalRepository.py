import __builtin__, sys, traceback, types
from direct.distributed.AstronInternalRepository import AstronInternalRepository
from direct.distributed.MsgTypes import *
from direct.distributed.PyDatagram import PyDatagram
from panda3d.core import *
from otp.distributed.OtpDoGlobals import *
ai_watchdog = ConfigVariableInt('ai-watchdog', 15, 'Specifies the maximum amount of time that a frame may take before the process kills itself.')

class WatchdogError(Exception):
    pass


def watchdogExhausted(signum, frame):
    raise WatchdogError('The process has stalled!')


class ToontownInternalRepository(AstronInternalRepository):
    GameGlobalsId = OTP_DO_ID_TOONTOWN
    dbId = 4003

    def __init__(self, baseChannel, serverId=None, dcFileNames=None, dcSuffix='AI', connectMethod=None, threadedNet=None):
        AstronInternalRepository.__init__(self, baseChannel, serverId, dcFileNames, dcSuffix, connectMethod, threadedNet)
        self._callbacks = {}

    def __resetWatchdog(self, task):
        signal.alarm(ai_watchdog.getValue())
        return task.cont

    def getAvatarIdFromSender(self):
        return self.getMsgSender() & 4294967295L

    def getAccountIdFromSender(self):
        return self.getMsgSender() >> 32 & 4294967295L

    def setAllowClientSend(self, avId, dObj, fieldNameList=[]):
        dg = PyDatagram()
        dg.addServerHeader(dObj.GetPuppetConnectionChannel(avId), self.ourChannel, CLIENTAGENT_SET_FIELDS_SENDABLE)
        fieldIds = []
        for fieldName in fieldNameList:
            field = dObj.dclass.getFieldByName(fieldName)
            if field:
                fieldIds.append(field.getNumber())

        dg.addUint32(dObj.getDoId())
        dg.addUint16(len(fieldIds))
        for fieldId in fieldIds:
            dg.addUint16(fieldId)

        self.send(dg)

    def _isValidPlayerLocation(self, parentId, zoneId):
        if zoneId < 1000 and zoneId != 1:
            return False
        return True

    def readerPollOnce(self):
        try:
            return AstronInternalRepository.readerPollOnce(self)
        except SystemExit as KeyboardInterrupt:
            raise
        except Exception as e:
            if self.getAvatarIdFromSender() > 100000000:
                dg = PyDatagram()
                dg.addServerHeader(self.getMsgSender(), self.ourChannel, CLIENTAGENT_EJECT)
                dg.addUint16(166)
                dg.addString('You were disconnected to prevent a district reset.')
                self.send(dg)
            self.writeServerEvent('INTERNAL-EXCEPTION', self.getAvatarIdFromSender(), self.getAccountIdFromSender(), repr(e), traceback.format_exc())
            self.notify.warning('INTERNAL-EXCEPTION: %s (%s)' % (repr(e), self.getAvatarIdFromSender()))
            print traceback.format_exc()
            sys.exc_clear()

        return 1

    def readDCFile(self, dcFileNames=None):
        dcFile = self.getDcFile()
        dcFile.clear()
        self.dclassesByName = {}
        self.dclassesByNumber = {}
        self.hashVal = 0
        if isinstance(dcFileNames, types.StringTypes):
            dcFileNames = [dcFileNames]
        dcImports = {}
        if dcFileNames == None:
            try:
                readResult = dcFile.read(dcStream, '__dc__')
                del __builtin__.dcStream
            except NameError:
                readResult = dcFile.readAll()

            if not readResult:
                self.notify.error('Could not read dc file.')
        else:
            searchPath = getModelPath().getValue()
            for dcFileName in dcFileNames:
                pathname = Filename(dcFileName)
                vfs.resolveFilename(pathname, searchPath)
                readResult = dcFile.read(pathname)
                if not readResult:
                    self.notify.error('Could not read dc file: %s' % pathname)

        self.hashVal = dcFile.getHash()
        for n in xrange(dcFile.getNumImportModules()):
            moduleName = dcFile.getImportModule(n)[:]
            suffix = moduleName.split('/')
            moduleName = suffix[0]
            suffix = suffix[1:]
            if self.dcSuffix in suffix:
                moduleName += self.dcSuffix
            else:
                if self.dcSuffix == 'UD' and 'AI' in suffix:
                    moduleName += 'AI'
            importSymbols = []
            for i in xrange(dcFile.getNumImportSymbols(n)):
                symbolName = dcFile.getImportSymbol(n, i)
                suffix = symbolName.split('/')
                symbolName = suffix[0]
                suffix = suffix[1:]
                if self.dcSuffix in suffix:
                    symbolName += self.dcSuffix
                else:
                    if self.dcSuffix == 'UD' and 'AI' in suffix:
                        symbolName += 'AI'
                importSymbols.append(symbolName)

            self.importModule(dcImports, moduleName, importSymbols)

        for i in xrange(dcFile.getNumClasses()):
            dclass = dcFile.getClass(i)
            number = dclass.getNumber()
            className = dclass.getName() + self.dcSuffix
            classDef = dcImports.get(className)
            if classDef is None and self.dcSuffix == 'UD':
                className = dclass.getName() + 'AI'
                classDef = dcImports.get(className)
            if classDef == None:
                className = dclass.getName()
                classDef = dcImports.get(className)
            if classDef is None:
                self.notify.debug('No class definition for %s.' % className)
            else:
                if type(classDef) == types.ModuleType:
                    if not hasattr(classDef, className):
                        self.notify.warning('Module %s does not define class %s.' % (className, className))
                        continue
                    classDef = getattr(classDef, className)
                if type(classDef) != types.ClassType and type(classDef) != types.TypeType:
                    self.notify.error('Symbol %s is not a class name.' % className)
                else:
                    dclass.setClassDef(classDef)
            self.dclassesByName[className] = dclass
            if number >= 0:
                self.dclassesByNumber[number] = dclass

        if self.hasOwnerView():
            ownerDcSuffix = self.dcSuffix + 'OV'
            ownerImportSymbols = {}
            for n in xrange(dcFile.getNumImportModules()):
                moduleName = dcFile.getImportModule(n)
                suffix = moduleName.split('/')
                moduleName = suffix[0]
                suffix = suffix[1:]
                if ownerDcSuffix in suffix:
                    moduleName = moduleName + ownerDcSuffix
                importSymbols = []
                for i in xrange(dcFile.getNumImportSymbols(n)):
                    symbolName = dcFile.getImportSymbol(n, i)
                    suffix = symbolName.split('/')
                    symbolName = suffix[0]
                    suffix = suffix[1:]
                    if ownerDcSuffix in suffix:
                        symbolName += ownerDcSuffix
                    importSymbols.append(symbolName)
                    ownerImportSymbols[symbolName] = None

                self.importModule(dcImports, moduleName, importSymbols)

            for i in xrange(dcFile.getNumClasses()):
                dclass = dcFile.getClass(i)
                if dclass.getName() + ownerDcSuffix in ownerImportSymbols:
                    number = dclass.getNumber()
                    className = dclass.getName() + ownerDcSuffix
                    classDef = dcImports.get(className)
                    if classDef is None:
                        self.notify.error('No class definition for %s.' % className)
                    else:
                        if type(classDef) == types.ModuleType:
                            if not hasattr(classDef, className):
                                self.notify.error('Module %s does not define class %s.' % (className, className))
                            classDef = getattr(classDef, className)
                        dclass.setOwnerClassDef(classDef)
                        self.dclassesByName[className] = dclass

        return