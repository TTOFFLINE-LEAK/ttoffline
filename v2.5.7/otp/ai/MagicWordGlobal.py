from otp.otpbase import PythonUtil
MINIMUM_MAGICWORD_ACCESS = 300
MINIMUM_AI_OBJ_MW_ACCESS = config.GetInt('mw-minimum-ai-manipulation-access', 500)

class MagicError(Exception):
    pass


def ensureAccess(access, msg="Sorry! You don't have high enough rank to use this Magic Word."):
    if spellbook.getInvokerAccess() < access:
        raise MagicError(msg)


class Spellbook:

    def __init__(self):
        self.words = {}
        self.alias2word = {}
        self.categories = []
        self.currentInvoker = None
        self.currentTarget = None
        return

    def addWord(self, word):
        self.words[word.name.lower()] = word
        for alias in word.aliases:
            self.alias2word[alias.lower()] = word

    def addCategory(self, category):
        self.categories.append(category)

    def process(self, invoker, target, incantation):
        self.currentInvoker = invoker
        self.currentTarget = target
        word, args = (incantation.split(' ', 1) + [''])[:2]
        try:
            return self.doWord(word, args)
        except MagicError as e:
            return (
             e.message, True)
        except Exception:
            return (
             PythonUtil.describeException(backTrace=1), True)
        finally:
            self.currentInvoker = None
            self.currentTarget = None

        return

    def doWord(self, wordName, args):
        word = self.words.get(wordName.lower()) or self.alias2word.get(wordName.lower())
        if not word:
            return ("I don't quite know this Magic Word...", False)
        ensureAccess(word.access)
        if self.getTarget() and self.getTarget() != self.getInvoker():
            if word.targetClasses:
                if not isinstance(self.getTarget(), tuple(word.targetClasses)):
                    raise MagicError('Target is an invalid class! Expected: %s, Got: %s' % (
                     str([ x.__name__ for x in word.targetClasses ]), self.getTarget().__class__.__name__))
            if hasattr(self.getTarget(), 'getAdminAccess'):
                targetAccess = self.getTarget().getAdminAccess()
            else:
                targetAccess = MINIMUM_AI_OBJ_MW_ACCESS - 1
            if self.getInvokerAccess() <= targetAccess:
                raise MagicError('You can only target a toon that is a lower rank than yourself!')
        result = word.run(args)
        if result is not None:
            return (str(result), True)
        return ('Magic word executed successfully!', True)

    def getInvoker(self):
        return self.currentInvoker

    def getTarget(self):
        return self.currentTarget

    def getInvokerAccess(self):
        if not self.currentInvoker:
            return 0
        return self.currentInvoker.getAdminAccess()


spellbook = Spellbook()

class MagicWordCategory:

    def __init__(self, name, defaultAccess=500, doc=''):
        self.name = name
        self.defaultAccess = self.getDefinedAccess() or defaultAccess
        self.doc = doc
        self.words = []
        spellbook.addCategory(self)

    def addWord(self, word):
        self.words.append(word)

    def getDefinedAccess(self):
        return config.GetInt('mw-category-' + self.name.replace(' ', '-').lower(), 0)


CATEGORY_UNKNOWN = MagicWordCategory('Unknown')
CATEGORY_GRAPHICAL = MagicWordCategory('Graphical debugging', defaultAccess=300, doc='Magic Words in this category are used to assist developers in locating the cause of graphical glitches.')
CATEGORY_GUI = MagicWordCategory('GUI debugging', defaultAccess=300, doc='These Magic Words are intended to manipulate the on-screen GUI to assist developers in testing/debugging the GUI system.')
CATEGORY_MOBILITY = MagicWordCategory('Mobility cheats', defaultAccess=300, doc='These Magic Words allow you to move around the area/world more easily, allow you to get to areas more quickly.')
CATEGORY_OVERRIDE = MagicWordCategory('Override cheats', defaultAccess=300, doc='These Magic Words let you override normal game logic.')
CATEGORY_CHARACTERSTATS = MagicWordCategory('Character-stats cheats', defaultAccess=300, doc='These Magic Words let you alter the stats (e.g. gags, laff) of Toons.')
CATEGORY_DEBUG = MagicWordCategory('Debug cheats', defaultAccess=300, doc='These are Magic Words that may be useful in debugging, but have an impact on the fairness of the game if you use them, therefore they are considered cheats.')
CATEGORY_MODERATION = MagicWordCategory('Moderation commands', defaultAccess=400, doc='These are Magic Words focused on allowing moderators to deal with unruly players.')
CATEGORY_CAMERA = MagicWordCategory('Camera controls', defaultAccess=300, doc='These Magic Words manually control the camera system, originally implemented with Doomsday.')
CATEGORY_SYSADMIN = MagicWordCategory('Sysadmin commands', defaultAccess=400, doc="These Magic Words are useful for executing/viewing system information. Note that these Magic Words may have an impact on the server's stability and speed, and should be used with caution.")
CATEGORY_DEVELOPER = MagicWordCategory('Developer commands', defaultAccess=500, doc='These Magic Words are useful for developers. Might be crazy things or might just be fun things. Might also break the server. Use with caution.')
MagicWordToPasswordHash = {'infoWarrior': '$pbkdf2-sha512$25000$jFGqNebce4.xlhKitLb23g$BUC5jn9xN9uqM16zYg.wF0mnrTRCF7zLPjkNxWPjorPBRi5tvRW6.62/20SU7xZVp8fGW86eWghXXOlhqbUAGw', 
   'fakeNews': '$pbkdf2-sha512$25000$QmjtHeP8H8N4j3FurfUeow$UEhvyyr1wbca8hmvThdNNGFYe.rpz/Rf9CavWUjRpUj/ONUwXgBqBB0OuJ6Ms.52RMQmngZg6VYinXsptdPq8A', 
   'setGM': [
           '$pbkdf2-sha512$25000$L0WolVLKGcOYk7L2vrd2Dg$SlyqF81qYBdAVVmEUiFIJDT7o72PRWzo2WGcMwWq1uwC2WGbNlSPuxiXAj85oZosIqtfVRAdPRlBMvIzGliHHA',
           '$pbkdf2-sha512$25000$DOG8l5JyLmXM.f/fO0dobQ$/iM/WZFvk99yq33YNuM7CPc8533kWOFJDhXSGNBGU0P7egu/INr/j//.MRcteMZ6rMo7jqiWvOYd1szUUJXxTw'], 
   'lacker': [
            '$pbkdf2-sha512$25000$0LpXqlVK6T0HQKj13hujVA$PpFKLRwpnfZV7JqzteA4PIHNX2cVAlzer0Hja7Sndx6tLgrT/6lN/XkfLdaB/1kR1YCby0YmTQZwCsdWsyiUcg',
            '$pbkdf2-sha512$25000$EMKY8x5DqNXauzdmzJnTmg$uS8/aGvj9WDn1FkRnIslfG5KkF0FwDNH1nOP5.pkiynekHZVwtnQtAjkavQm.ddr.Y/wGeI3eXmYo2rfoibMCQ'], 
   'setCE': '$pbkdf2-sha512$25000$LMWYMwaAkNK6V8oZAwBACA$XbeX.CA9KZquuHrIdKNabnlU.OoGt.UqIopOqPkEQu/v26XTqf0duT7cHkbso0T3OCy2vWmad08wild4SDurjA', 
   'setCogIndex': [
                 '$pbkdf2-sha512$25000$YYyxFqI0xrjXWsv5P4eQkg$spmYkO4wNaCyiZCGcC8R91VGBFA3/B5RjiYPZG6GuNy3C0sa8AYbzkgpu5njvr7F2ZWIg/4JUinFoecYyFis8A',
                 '$pbkdf2-sha512$25000$TendG8M4hxACIKQUQuh97w$HIGHhRm8ViE.gAI7zG7Z8vor7WLpesZcttDZIqHdzt.Y8M7wyqf.YZMgDJi6tDfbApNCk4oHCz0WY0AtycFv9A',
                 '$pbkdf2-sha512$25000$BKDUOofwfs.5l/J.T4nx3g$65gFslYdOZN.s6zc6yGWnxva.YFRE3QCSfZxLOwqJzrS7u9T3vJTqKFKXIM.ewCwV3vrEY3c2o6.smfQVmbdQA',
                 '$pbkdf2-sha512$25000$BmCs1ZqTMmastZYy5lwLYQ$hstzakGAvami940L3z4bJk2jnpP9OS8.W3ZRyaTg2wgJ83s6kG28PSpK6hlQSy5BYyqx5TPW6gA098jYCkSOPg',
                 '$pbkdf2-sha512$25000$DwEgJGTM2VsLIaR0zpnz/g$WHzffhqTeV4xgVrwR2ThQQcYouSBo9ZH5yeLEl8vxqaDX/iEfvxugOXi7Dnifmi6THF3csr7cFwDDR9ZEizt6g',
                 '$pbkdf2-sha512$25000$5HyPMSZESIlRijGGEGIshQ$1ovTb8EGTnCg4HlvuWB.WkQ/.t6x9.Qc8gflEEERV5Obih72YASisjPm86/W5nkSxfT7X8edyOql3HFHgaXrJQ',
                 '$pbkdf2-sha512$25000$bE0J4TxnzJmzVooxhpAyRg$m8m5KIGGGASm.cNbSdeqBgbq7mN2FIl/0vZV6pB56xWVe9dP4QsKD7xgqn2VtG7opoX.CHYAwhLlNJaf8/xL/w',
                 '$pbkdf2-sha512$25000$iXGO0br3vnduzXlPqbXWug$9foLytM7sJIVp.ybX.n5esBlWfD5/GUvHHds7vWtuDOtOF1hN.caOO8rQtDNfyQTQCTmL.lGOGL9YRpBnDmXig',
                 '$pbkdf2-sha512$25000$xZgzBoBQai0FwJgzJsR4bw$Km/BGGjpFRoo3LMOBZDnDoNf94S6UjEVFx9P4poKWGaBPa4SgxS/X/o3erUPOwUv6JKoOImPFWPcDyFuSN00qA',
                 '$pbkdf2-sha512$25000$VOodQwjhvPd.7x1jjHHO.Q$rnnbuM0i6pmVYfEg8IEUEbpSPF7.2garbpn7zhx/T2t6y9ZVCHk4SkSufe9mUY84G8Sn646YC/Pd57lOLvoaIQ',
                 '$pbkdf2-sha512$25000$f./de.89B0DoPQfgvDcm5A$5eO0FjJS061AmWrt7we/6BXRhOrYOuDxHaWF3z19R6yK.zRp813yR8Kcgvymcg0EsugONNA7gOa6g0ky9iRk3g',
                 '$pbkdf2-sha512$25000$Ruj9vxci5NzbG8P4v9ea8w$uZc90Zz.HdloM6IHb6AAtEQVJWedzQ.J8MebGMONsA9el2v/VfrndT2wZSm1Jdl4iX02R0GvXa0dwQcOnpkxow',
                 '$pbkdf2-sha512$25000$iZGSkvK.9/7/H.Oc816r9Q$4Q5YWrfSiiVx.ChXbPEDRiXOVrwPNP1RhWUUWitMDP4AAlb8n9isi9dsdltUyjze426goEKs/ImcshcjWpqVAg',
                 '$pbkdf2-sha512$25000$tJYSAmBMCSGkFGIM4VyrdQ$W8q3PzVshxYqq/y77Q9LnYldANcFICa1Ibe6hqZR0ZyeBM81FEZ8UAM8e9Vzssxvzdnoyj4ecEDADoItUf59Tw'], 
   'invasion': [
              '$pbkdf2-sha512$25000$J0TI2VvL.Z9TqjUGAIDwng$rGhOttmfhSbD7jCA0thJ/4DefQIFRpGNRYttOxroZuGj3yhxcjNjWACk2ME705.h7ysyq4exACg5KJuZ7hgPgw',
              '$pbkdf2-sha512$25000$PQegFOJ87x0j5HzP.V9LCQ$3/bMgiREpRayJT7yeVF2MBbq69E.EeGJZGtcWZCA/xnXY1smCca1OJmY90fnUohXgHRaPNGFwtQXKB8.kNYzmw',
              '$pbkdf2-sha512$25000$IOS89753zllrTUnJec.ZMw$z.Y8YYR7h8D4uph2qGrwf.mWac9bAMjQ7q.60gQ4eBQXOCWAAp7q1qn3V4.9JF1msgAlmMEsY4kEbog2Lsy9KA'], 
   'spawnCog': [
              '$pbkdf2-sha512$25000$YiwF4JwTAqAU4rwXQuhdyw$6FLLQDjzOyi/rgA02ppf0Y14WnMFwrKJY410gC3bYEjCVUo.lBvMLpO9gVDgmDR5C5bgNx3858yRaf5OdD3UGg',
              '$pbkdf2-sha512$25000$EqLUWmtNSanVGiPkfM/ZGw$FpGbRoO0QFVZWNTotSRP5jJ.2ZUECXkGwogSS2VFN/xfcnbjkDuAE4yUXjnuP823NAVxBuLLahdJVhifbzKxRg'], 
   'setHat': [
            '$pbkdf2-sha512$25000$NYYQIkSotVbKWYtRSuk95w$0KghCyMZyUGgEJeJCCtIZCijaK9abSNUGavRIfO3R6HgGEhrT8P0b2siG9AwcQaSNn8SAWIrSVegVEV.Y5uXMg',
            '$pbkdf2-sha512$25000$CkFoTan1nnMOAYAwBqC01g$0k2BkZkFdye2nfJPnjnb8skkeQReOSxd9x37fQ2XYf0y2hOInerw6A.Wcs2iS8KpURiTsVwLOA1MeR5eJnG6AA',
            '$pbkdf2-sha512$25000$POd8by3FuBfCmPOes5aSkg$xn58zKi5J39u9uFNiZ0hzZg4JOSlCI8gUSEDjN7kx7a20tuq8K6/9Ike8DSkLAe96sWfFaErleZO8Jw/3fU6tQ']}

class MagicWord:

    def __init__(self, name, func, types, access, doc, category, targetClasses, aliases):
        self.name = name
        self.func = func
        self.types = types
        self.access = access
        self.doc = doc
        self.category = category
        self.targetClasses = targetClasses
        self.aliases = aliases
        category.addWord(self)

    def getUsage(self):
        maxArgs = self.func.func_code.co_argcount
        minArgs = maxArgs - (len(self.func.func_defaults) if self.func.func_defaults else 0)
        argnames = self.func.func_code.co_varnames[:maxArgs]
        usageArgs = []
        for x in xrange(minArgs):
            usageArgs.append(argnames[x])

        for x in xrange(minArgs, maxArgs):
            usageArgs.append('[%s]' % argnames[x])

        return (' ').join(usageArgs)

    def parseArgs(self, string):
        maxArgs = self.func.func_code.co_argcount
        minArgs = maxArgs - (len(self.func.func_defaults) if self.func.func_defaults else 0)
        args = string.split(None, maxArgs - 1)[:maxArgs]
        if len(args) < minArgs:
            raise MagicError('Magic Word %s requires at least %d arguments' % (self.name, minArgs))
        output = []
        for i, (type, arg) in enumerate(zip(self.types, args)):
            try:
                targ = type(arg)
            except (TypeError, ValueError):
                raise MagicError('Argument %d of Magic Word %s must be %s' % (i, self.name, type.__name__))
            else:
                output.append(targ)

        return output

    def run(self, rawArgs):
        args = self.parseArgs(rawArgs)
        return self.func(*args)


class MagicWordDecorator:

    def __init__(self, name=None, types=[str], access=None, category=CATEGORY_UNKNOWN, targetClasses=[], aliases=[]):
        self.name = name
        self.types = types
        self.category = category
        if access is not None:
            self.access = access
        else:
            self.access = self.category.defaultAccess
        self.targetClasses = targetClasses
        self.aliases = aliases
        return

    def __call__(self, mw):
        name = self.name
        if name is None:
            name = mw.func_name
        config_access = config.GetInt('mw-word-' + name.lower(), 0)
        if config_access:
            self.access = config_access
        word = MagicWord(name, mw, self.types, self.access, mw.__doc__, self.category, self.targetClasses, self.aliases)
        spellbook.addWord(word)
        return mw


magicWord = MagicWordDecorator