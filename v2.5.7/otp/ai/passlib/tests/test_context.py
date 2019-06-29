from __future__ import with_statement
from otp.ai.passlib.utils.compat import PY3
if PY3:
    from configparser import NoSectionError
else:
    from ConfigParser import NoSectionError
import datetime
from functools import partial
import logging
log = logging.getLogger(__name__)
import os, warnings
from otp.ai.passlib import hash
from otp.ai.passlib.context import CryptContext, LazyCryptContext
from otp.ai.passlib.exc import PasslibConfigWarning, PasslibHashWarning
from otp.ai.passlib.utils import tick, to_unicode
from otp.ai.passlib.utils.compat import irange, u, unicode, str_to_uascii, PY2, PY26
import otp.ai.passlib.utils.handlers as uh
from otp.ai.passlib.tests.utils import TestCase, set_file, TICK_RESOLUTION, quicksleep, time_call, handler_derived_from
from otp.ai.passlib.registry import register_crypt_handler_path, _has_crypt_handler as has_crypt_handler, _unload_handler_name as unload_handler_name, get_crypt_handler
here = os.path.abspath(os.path.dirname(__file__))

def merge_dicts(first, *args, **kwds):
    target = first.copy()
    for arg in args:
        target.update(arg)

    if kwds:
        target.update(kwds)
    return target


class CryptContextTest(TestCase):
    descriptionPrefix = 'CryptContext'
    sample_1_schemes = [
     'des_crypt', 'md5_crypt', 'bsdi_crypt', 'sha512_crypt']
    sample_1_handlers = [ get_crypt_handler(name) for name in sample_1_schemes ]
    sample_1_dict = dict(schemes=sample_1_schemes, default='md5_crypt', all__vary_rounds=0.1, bsdi_crypt__max_rounds=30001, bsdi_crypt__default_rounds=25001, sha512_crypt__max_rounds=50000, sha512_crypt__min_rounds=40000)
    sample_1_resolved_dict = merge_dicts(sample_1_dict, schemes=sample_1_handlers)
    sample_1_unnormalized = u('[passlib]\nschemes = des_crypt, md5_crypt, bsdi_crypt, sha512_crypt\ndefault = md5_crypt\n; this is using %...\nall__vary_rounds = 10%%\nbsdi_crypt__default_rounds = 25001\nbsdi_crypt__max_rounds = 30001\nsha512_crypt__max_rounds = 50000\nsha512_crypt__min_rounds = 40000\n')
    sample_1_unicode = u('[passlib]\nschemes = des_crypt, md5_crypt, bsdi_crypt, sha512_crypt\ndefault = md5_crypt\nall__vary_rounds = 0.1\nbsdi_crypt__default_rounds = 25001\nbsdi_crypt__max_rounds = 30001\nsha512_crypt__max_rounds = 50000\nsha512_crypt__min_rounds = 40000\n\n')
    sample_1_path = os.path.join(here, 'sample1.cfg')
    sample_1b_unicode = sample_1_unicode.replace(u('\n'), u('\r\n'))
    sample_1b_path = os.path.join(here, 'sample1b.cfg')
    sample_1c_bytes = sample_1_unicode.replace(u('[passlib]'), u('[mypolicy]')).encode('utf-16')
    sample_1c_path = os.path.join(here, 'sample1c.cfg')
    if False:
        set_file(sample_1_path, sample_1_unicode)
        set_file(sample_1b_path, sample_1b_unicode)
        set_file(sample_1c_path, sample_1c_bytes)
    sample_2_dict = dict(bsdi_crypt__min_rounds=29001, bsdi_crypt__max_rounds=35001, bsdi_crypt__default_rounds=31001, sha512_crypt__min_rounds=45000)
    sample_2_unicode = '[passlib]\nbsdi_crypt__min_rounds = 29001\nbsdi_crypt__max_rounds = 35001\nbsdi_crypt__default_rounds = 31001\nsha512_crypt__min_rounds = 45000\n'
    sample_12_dict = merge_dicts(sample_1_dict, sample_2_dict)
    sample_3_dict = dict(default='sha512_crypt')
    sample_123_dict = merge_dicts(sample_12_dict, sample_3_dict)
    sample_4_dict = dict(schemes=[
     'des_crypt', 'md5_crypt', 'phpass', 'bsdi_crypt',
     'sha256_crypt'], deprecated=[
     'des_crypt'], default='sha256_crypt', bsdi_crypt__max_rounds=31, bsdi_crypt__default_rounds=25, bsdi_crypt__vary_rounds=0, sha256_crypt__max_rounds=3000, sha256_crypt__min_rounds=2000, sha256_crypt__default_rounds=3000, phpass__ident='H', phpass__default_rounds=7)

    def setUp(self):
        super(CryptContextTest, self).setUp()
        warnings.filterwarnings('ignore', "The 'all' scheme is deprecated.*")
        warnings.filterwarnings('ignore', ".*'scheme' keyword is deprecated as of Passlib 1.7.*")

    def test_01_constructor(self):
        ctx = CryptContext()
        self.assertEqual(ctx.to_dict(), {})
        ctx = CryptContext(**self.sample_1_dict)
        self.assertEqual(ctx.to_dict(), self.sample_1_dict)
        ctx = CryptContext(**self.sample_1_resolved_dict)
        self.assertEqual(ctx.to_dict(), self.sample_1_dict)
        ctx = CryptContext(**self.sample_2_dict)
        self.assertEqual(ctx.to_dict(), self.sample_2_dict)
        ctx = CryptContext(**self.sample_3_dict)
        self.assertEqual(ctx.to_dict(), self.sample_3_dict)
        ctx = CryptContext(schemes=[u('sha256_crypt')])
        self.assertEqual(ctx.schemes(), ('sha256_crypt', ))

    def test_02_from_string(self):
        ctx = CryptContext.from_string(self.sample_1_unicode)
        self.assertEqual(ctx.to_dict(), self.sample_1_dict)
        ctx = CryptContext.from_string(self.sample_1_unnormalized)
        self.assertEqual(ctx.to_dict(), self.sample_1_dict)
        ctx = CryptContext.from_string(self.sample_1_unicode.encode('utf-8'))
        self.assertEqual(ctx.to_dict(), self.sample_1_dict)
        ctx = CryptContext.from_string(self.sample_1b_unicode)
        self.assertEqual(ctx.to_dict(), self.sample_1_dict)
        ctx = CryptContext.from_string(self.sample_1c_bytes, section='mypolicy', encoding='utf-16')
        self.assertEqual(ctx.to_dict(), self.sample_1_dict)
        self.assertRaises(TypeError, CryptContext.from_string, None)
        self.assertRaises(NoSectionError, CryptContext.from_string, self.sample_1_unicode, section='fakesection')
        return

    def test_03_from_path(self):
        if not os.path.exists(self.sample_1_path):
            raise RuntimeError("can't find data file: %r" % self.sample_1_path)
        ctx = CryptContext.from_path(self.sample_1_path)
        self.assertEqual(ctx.to_dict(), self.sample_1_dict)
        ctx = CryptContext.from_path(self.sample_1b_path)
        self.assertEqual(ctx.to_dict(), self.sample_1_dict)
        ctx = CryptContext.from_path(self.sample_1c_path, section='mypolicy', encoding='utf-16')
        self.assertEqual(ctx.to_dict(), self.sample_1_dict)
        self.assertRaises(EnvironmentError, CryptContext.from_path, os.path.join(here, 'sample1xxx.cfg'))
        self.assertRaises(NoSectionError, CryptContext.from_path, self.sample_1_path, section='fakesection')

    def test_04_copy(self):
        cc1 = CryptContext(**self.sample_1_dict)
        cc2 = cc1.copy(**self.sample_2_dict)
        self.assertEqual(cc1.to_dict(), self.sample_1_dict)
        self.assertEqual(cc2.to_dict(), self.sample_12_dict)
        cc2b = cc2.copy(**self.sample_2_dict)
        self.assertEqual(cc1.to_dict(), self.sample_1_dict)
        self.assertEqual(cc2b.to_dict(), self.sample_12_dict)
        cc3 = cc2.copy(**self.sample_3_dict)
        self.assertEqual(cc3.to_dict(), self.sample_123_dict)
        cc4 = cc1.copy()
        self.assertIsNot(cc4, cc1)
        self.assertEqual(cc1.to_dict(), self.sample_1_dict)
        self.assertEqual(cc4.to_dict(), self.sample_1_dict)
        cc4.update(**self.sample_2_dict)
        self.assertEqual(cc1.to_dict(), self.sample_1_dict)
        self.assertEqual(cc4.to_dict(), self.sample_12_dict)

    def test_09_repr(self):
        cc1 = CryptContext(**self.sample_1_dict)
        self.assertRegex(repr(cc1), '^<CryptContext at 0x-?[0-9a-f]+>$')

    def test_10_load(self):
        ctx = CryptContext()
        ctx.load(self.sample_1_dict)
        self.assertEqual(ctx.to_dict(), self.sample_1_dict)
        ctx.load(self.sample_1_unicode)
        self.assertEqual(ctx.to_dict(), self.sample_1_dict)
        ctx.load(self.sample_1_unicode.encode('utf-8'))
        self.assertEqual(ctx.to_dict(), self.sample_1_dict)
        self.assertRaises(TypeError, ctx.load, None)
        ctx = CryptContext(**self.sample_1_dict)
        ctx.load({}, update=True)
        self.assertEqual(ctx.to_dict(), self.sample_1_dict)
        ctx = CryptContext()
        ctx.load(self.sample_1_dict)
        ctx.load(self.sample_2_dict)
        self.assertEqual(ctx.to_dict(), self.sample_2_dict)
        return

    def test_11_load_rollback(self):
        cc = CryptContext(['des_crypt', 'sha256_crypt'], sha256_crypt__default_rounds=5000, all__vary_rounds=0.1)
        result = cc.to_string()
        self.assertRaises(TypeError, cc.update, too__many__key__parts=True)
        self.assertEqual(cc.to_string(), result)
        self.assertRaises(KeyError, cc.update, fake_context_option=True)
        self.assertEqual(cc.to_string(), result)
        self.assertRaises(ValueError, cc.update, sha256_crypt__min_rounds=10000)
        self.assertEqual(cc.to_string(), result)

    def test_12_update(self):
        ctx = CryptContext(**self.sample_1_dict)
        ctx.update()
        self.assertEqual(ctx.to_dict(), self.sample_1_dict)
        ctx = CryptContext(**self.sample_1_dict)
        ctx.update(**self.sample_2_dict)
        self.assertEqual(ctx.to_dict(), self.sample_12_dict)
        ctx.update(**self.sample_3_dict)
        self.assertEqual(ctx.to_dict(), self.sample_123_dict)
        ctx = CryptContext(**self.sample_1_dict)
        ctx.update(self.sample_2_dict)
        self.assertEqual(ctx.to_dict(), self.sample_12_dict)
        ctx = CryptContext(**self.sample_1_dict)
        ctx.update(self.sample_2_unicode)
        self.assertEqual(ctx.to_dict(), self.sample_12_dict)
        self.assertRaises(TypeError, ctx.update, {}, {})
        self.assertRaises(TypeError, ctx.update, {}, schemes=['des_crypt'])
        self.assertRaises(TypeError, ctx.update, None)
        return

    def test_20_options(self):

        def parse(**kwds):
            return CryptContext(**kwds).to_dict()

        self.assertRaises(TypeError, CryptContext, __=0.1)
        self.assertRaises(TypeError, CryptContext, default__scheme__='x')
        self.assertRaises(TypeError, CryptContext, __option='x')
        self.assertRaises(TypeError, CryptContext, default____option='x')
        self.assertRaises(TypeError, CryptContext, __scheme__option='x')
        self.assertRaises(TypeError, CryptContext, category__scheme__option__invalid=30000)
        self.assertRaises(KeyError, parse, **{'admin.context__schemes': 'md5_crypt'})
        ctx = CryptContext(**{'schemes': 'md5_crypt,des_crypt', 'admin.context__default': 'des_crypt'})
        self.assertEqual(ctx.default_scheme('admin'), 'des_crypt')
        result = dict(default='md5_crypt')
        self.assertEqual(parse(default='md5_crypt'), result)
        self.assertEqual(parse(context__default='md5_crypt'), result)
        self.assertEqual(parse(default__context__default='md5_crypt'), result)
        self.assertEqual(parse(**{'context.default': 'md5_crypt'}), result)
        self.assertEqual(parse(**{'default.context.default': 'md5_crypt'}), result)
        result = dict(admin__context__default='md5_crypt')
        self.assertEqual(parse(admin__context__default='md5_crypt'), result)
        self.assertEqual(parse(**{'admin.context.default': 'md5_crypt'}), result)
        result = dict(all__vary_rounds=0.1)
        self.assertEqual(parse(all__vary_rounds=0.1), result)
        self.assertEqual(parse(default__all__vary_rounds=0.1), result)
        self.assertEqual(parse(**{'all.vary_rounds': 0.1}), result)
        self.assertEqual(parse(**{'default.all.vary_rounds': 0.1}), result)
        result = dict(admin__all__vary_rounds=0.1)
        self.assertEqual(parse(admin__all__vary_rounds=0.1), result)
        self.assertEqual(parse(**{'admin.all.vary_rounds': 0.1}), result)
        ctx = CryptContext(['phpass', 'md5_crypt'], phpass__ident='P')
        self.assertRaises(KeyError, ctx.copy, md5_crypt__ident='P')
        self.assertRaises(KeyError, CryptContext, schemes=['des_crypt'], des_crypt__salt='xx')
        self.assertRaises(KeyError, CryptContext, schemes=['des_crypt'], all__salt='xx')

    def test_21_schemes(self):
        cc = CryptContext(schemes=None)
        self.assertEqual(cc.schemes(), ())
        cc = CryptContext(schemes=['des_crypt', 'md5_crypt'])
        self.assertEqual(cc.schemes(), ('des_crypt', 'md5_crypt'))
        cc = CryptContext(schemes=' des_crypt, md5_crypt, ')
        self.assertEqual(cc.schemes(), ('des_crypt', 'md5_crypt'))
        cc = CryptContext(schemes=[hash.des_crypt, hash.md5_crypt])
        self.assertEqual(cc.schemes(), ('des_crypt', 'md5_crypt'))
        self.assertRaises(TypeError, CryptContext, schemes=[uh.StaticHandler])

        class nameless(uh.StaticHandler):
            name = None

        self.assertRaises(ValueError, CryptContext, schemes=[nameless])

        class dummy_1(uh.StaticHandler):
            name = 'dummy_1'

        self.assertRaises(KeyError, CryptContext, schemes=[dummy_1, dummy_1])
        self.assertRaises(KeyError, CryptContext, admin__context__schemes=[
         'md5_crypt'])
        return

    def test_22_deprecated(self):

        def getdep(ctx, category=None):
            return [ name for name in ctx.schemes() if ctx.handler(name, category).deprecated
                   ]

        cc = CryptContext(deprecated=['md5_crypt'])
        cc.update(schemes=['md5_crypt', 'des_crypt'])
        self.assertEqual(getdep(cc), ['md5_crypt'])
        cc = CryptContext(deprecated=['md5_crypt'], schemes=['md5_crypt', 'des_crypt'])
        self.assertEqual(getdep(cc), ['md5_crypt'])
        self.assertRaises(TypeError, CryptContext, deprecated=[hash.md5_crypt], schemes=[
         'md5_crypt', 'des_crypt'])
        cc = CryptContext(deprecated='md5_crypt,des_crypt', schemes=['md5_crypt', 'des_crypt', 'sha256_crypt'])
        self.assertEqual(getdep(cc), ['md5_crypt', 'des_crypt'])
        self.assertRaises(KeyError, CryptContext, schemes=['des_crypt'], deprecated=[
         'md5_crypt'])
        self.assertRaises(ValueError, CryptContext, schemes=[
         'des_crypt'], deprecated=[
         'des_crypt'])
        self.assertRaises(ValueError, CryptContext, schemes=[
         'des_crypt', 'md5_crypt'], admin__context__deprecated=[
         'des_crypt', 'md5_crypt'])
        self.assertRaises(ValueError, CryptContext, schemes=[
         'des_crypt', 'md5_crypt'], default='md5_crypt', deprecated='md5_crypt')
        self.assertRaises(ValueError, CryptContext, schemes=[
         'des_crypt', 'md5_crypt'], default='md5_crypt', admin__context__deprecated='md5_crypt')
        self.assertRaises(ValueError, CryptContext, schemes=[
         'des_crypt', 'md5_crypt'], admin__context__default='md5_crypt', deprecated='md5_crypt')
        self.assertRaises(ValueError, CryptContext, schemes=[
         'des_crypt', 'md5_crypt'], admin__context__default='md5_crypt', admin__context__deprecated='md5_crypt')
        CryptContext(schemes=[
         'des_crypt', 'md5_crypt'], deprecated='md5_crypt', admin__context__default='md5_crypt', admin__context__deprecated=[])
        self.assertRaises(TypeError, CryptContext, deprecated=123)
        cc = CryptContext(deprecated=['md5_crypt'], schemes=[
         'md5_crypt', 'des_crypt'], admin__context__deprecated=[
         'des_crypt'])
        self.assertEqual(getdep(cc), ['md5_crypt'])
        self.assertEqual(getdep(cc, 'user'), ['md5_crypt'])
        self.assertEqual(getdep(cc, 'admin'), ['des_crypt'])
        cc = CryptContext(deprecated=['md5_crypt'], schemes=[
         'md5_crypt', 'des_crypt'], admin__context__deprecated=[])
        self.assertEqual(getdep(cc), ['md5_crypt'])
        self.assertEqual(getdep(cc, 'user'), ['md5_crypt'])
        self.assertEqual(getdep(cc, 'admin'), [])
        return

    def test_23_default(self):
        self.assertEqual(CryptContext(default='md5_crypt').to_dict(), dict(default='md5_crypt'))
        ctx = CryptContext(default='md5_crypt', schemes=['des_crypt', 'md5_crypt'])
        self.assertEqual(ctx.default_scheme(), 'md5_crypt')
        ctx = CryptContext(default=hash.md5_crypt, schemes=['des_crypt', 'md5_crypt'])
        self.assertEqual(ctx.default_scheme(), 'md5_crypt')
        ctx = CryptContext(schemes=['des_crypt', 'md5_crypt'])
        self.assertEqual(ctx.default_scheme(), 'des_crypt')
        ctx.update(deprecated='des_crypt')
        self.assertEqual(ctx.default_scheme(), 'md5_crypt')
        self.assertRaises(KeyError, CryptContext, schemes=['des_crypt'], default='md5_crypt')
        self.assertRaises(TypeError, CryptContext, default=1)
        ctx = CryptContext(default='des_crypt', schemes=[
         'des_crypt', 'md5_crypt'], admin__context__default='md5_crypt')
        self.assertEqual(ctx.default_scheme(), 'des_crypt')
        self.assertEqual(ctx.default_scheme('user'), 'des_crypt')
        self.assertEqual(ctx.default_scheme('admin'), 'md5_crypt')

    def test_24_vary_rounds(self):

        def parse(v):
            return CryptContext(all__vary_rounds=v).to_dict()['all__vary_rounds']

        self.assertEqual(parse(0.1), 0.1)
        self.assertEqual(parse('0.1'), 0.1)
        self.assertEqual(parse('10%'), 0.1)
        self.assertEqual(parse(1000), 1000)
        self.assertEqual(parse('1000'), 1000)

    def assertHandlerDerivedFrom(self, handler, base, msg=None):
        self.assertTrue(handler_derived_from(handler, base), msg=msg)

    def test_30_schemes(self):
        ctx = CryptContext()
        self.assertEqual(ctx.schemes(), ())
        self.assertEqual(ctx.schemes(resolve=True), ())
        ctx = CryptContext(**self.sample_1_dict)
        self.assertEqual(ctx.schemes(), tuple(self.sample_1_schemes))
        self.assertEqual(ctx.schemes(resolve=True, unconfigured=True), tuple(self.sample_1_handlers))
        for result, correct in zip(ctx.schemes(resolve=True), self.sample_1_handlers):
            self.assertTrue(handler_derived_from(result, correct))

        ctx = CryptContext(**self.sample_2_dict)
        self.assertEqual(ctx.schemes(), ())

    def test_31_default_scheme(self):
        ctx = CryptContext()
        self.assertRaises(KeyError, ctx.default_scheme)
        ctx = CryptContext(**self.sample_1_dict)
        self.assertEqual(ctx.default_scheme(), 'md5_crypt')
        self.assertEqual(ctx.default_scheme(resolve=True, unconfigured=True), hash.md5_crypt)
        self.assertHandlerDerivedFrom(ctx.default_scheme(resolve=True), hash.md5_crypt)
        ctx = CryptContext(**self.sample_2_dict)
        self.assertRaises(KeyError, ctx.default_scheme)
        ctx = CryptContext(schemes=self.sample_1_schemes)
        self.assertEqual(ctx.default_scheme(), 'des_crypt')

    def test_32_handler(self):
        ctx = CryptContext()
        self.assertRaises(KeyError, ctx.handler)
        self.assertRaises(KeyError, ctx.handler, 'md5_crypt')
        ctx = CryptContext(**self.sample_1_dict)
        self.assertEqual(ctx.handler(unconfigured=True), hash.md5_crypt)
        self.assertHandlerDerivedFrom(ctx.handler(), hash.md5_crypt)
        self.assertEqual(ctx.handler('des_crypt', unconfigured=True), hash.des_crypt)
        self.assertHandlerDerivedFrom(ctx.handler('des_crypt'), hash.des_crypt)
        self.assertRaises(KeyError, ctx.handler, 'mysql323')
        ctx = CryptContext('sha256_crypt,md5_crypt', admin__context__default='md5_crypt')
        self.assertEqual(ctx.handler(unconfigured=True), hash.sha256_crypt)
        self.assertHandlerDerivedFrom(ctx.handler(), hash.sha256_crypt)
        self.assertEqual(ctx.handler(category='staff', unconfigured=True), hash.sha256_crypt)
        self.assertHandlerDerivedFrom(ctx.handler(category='staff'), hash.sha256_crypt)
        self.assertEqual(ctx.handler(category='admin', unconfigured=True), hash.md5_crypt)
        self.assertHandlerDerivedFrom(ctx.handler(category='staff'), hash.sha256_crypt)
        if PY2:
            self.assertEqual(ctx.handler(category=u('staff'), unconfigured=True), hash.sha256_crypt)
            self.assertEqual(ctx.handler(category=u('admin'), unconfigured=True), hash.md5_crypt)

    def test_33_options(self):

        def options(ctx, scheme, category=None):
            return ctx._config._get_record_options_with_flag(scheme, category)[0]

        cc4 = CryptContext(truncate_error=True, schemes=[
         'sha512_crypt', 'des_crypt', 'bsdi_crypt'], deprecated=[
         'sha512_crypt', 'des_crypt'], all__vary_rounds=0.1, bsdi_crypt__vary_rounds=0.2, sha512_crypt__max_rounds=20000, admin__context__deprecated=[
         'des_crypt', 'bsdi_crypt'], admin__all__vary_rounds=0.05, admin__bsdi_crypt__vary_rounds=0.3, admin__sha512_crypt__max_rounds=40000)
        self.assertEqual(cc4._config.categories, ('admin', ))
        self.assertEqual(options(cc4, 'sha512_crypt'), dict(deprecated=True, vary_rounds=0.1, max_rounds=20000))
        self.assertEqual(options(cc4, 'sha512_crypt', 'user'), dict(deprecated=True, vary_rounds=0.1, max_rounds=20000))
        self.assertEqual(options(cc4, 'sha512_crypt', 'admin'), dict(vary_rounds=0.05, max_rounds=40000))
        self.assertEqual(options(cc4, 'des_crypt'), dict(deprecated=True, truncate_error=True))
        self.assertEqual(options(cc4, 'des_crypt', 'user'), dict(deprecated=True, truncate_error=True))
        self.assertEqual(options(cc4, 'des_crypt', 'admin'), dict(deprecated=True, truncate_error=True))
        self.assertEqual(options(cc4, 'bsdi_crypt'), dict(vary_rounds=0.2))
        self.assertEqual(options(cc4, 'bsdi_crypt', 'user'), dict(vary_rounds=0.2))
        self.assertEqual(options(cc4, 'bsdi_crypt', 'admin'), dict(vary_rounds=0.3, deprecated=True))
        return

    def test_34_to_dict(self):
        ctx = CryptContext(**self.sample_1_dict)
        self.assertEqual(ctx.to_dict(), self.sample_1_dict)
        self.assertEqual(ctx.to_dict(resolve=True), self.sample_1_resolved_dict)

    def test_35_to_string(self):
        ctx = CryptContext(**self.sample_1_dict)
        dump = ctx.to_string()
        if not PY26:
            self.assertEqual(dump, self.sample_1_unicode)
        ctx2 = CryptContext.from_string(dump)
        self.assertEqual(ctx2.to_dict(), self.sample_1_dict)
        other = ctx.to_string(section='password-security')
        self.assertEqual(other, dump.replace('[passlib]', '[password-security]'))
        from otp.ai.passlib.tests.test_utils_handlers import UnsaltedHash
        ctx3 = CryptContext([UnsaltedHash, 'md5_crypt'])
        dump = ctx3.to_string()
        self.assertRegex(dump, "# NOTE: the 'unsalted_test_hash' handler\\(s\\) are not registered with Passlib")

    nonstring_vectors = [
     (
      None, {}),
     (
      None, {'scheme': 'des_crypt'}),
     (
      1, {}),
     (
      (), {})]

    def test_40_basic(self):
        handlers = [
         hash.md5_crypt, hash.des_crypt, hash.bsdi_crypt]
        cc = CryptContext(handlers, bsdi_crypt__default_rounds=5)
        for crypt in handlers:
            h = cc.hash('test', scheme=crypt.name)
            self.assertEqual(cc.identify(h), crypt.name)
            self.assertEqual(cc.identify(h, resolve=True, unconfigured=True), crypt)
            self.assertHandlerDerivedFrom(cc.identify(h, resolve=True), crypt)
            self.assertTrue(cc.verify('test', h))
            self.assertFalse(cc.verify('notest', h))

        h = cc.hash('test')
        self.assertEqual(cc.identify(h), 'md5_crypt')
        h = cc.genhash('secret', cc.genconfig())
        self.assertEqual(cc.identify(h), 'md5_crypt')
        h = cc.genhash('secret', cc.genconfig(), scheme='md5_crypt')
        self.assertEqual(cc.identify(h), 'md5_crypt')
        self.assertRaises(ValueError, cc.genhash, 'secret', cc.genconfig(), scheme='des_crypt')

    def test_41_genconfig(self):
        cc = CryptContext(schemes=['md5_crypt', 'phpass'], phpass__ident='H', phpass__default_rounds=7, admin__phpass__ident='P')
        self.assertTrue(cc.genconfig().startswith('$1$'))
        self.assertTrue(cc.genconfig(scheme='phpass').startswith('$H$5'))
        self.assertTrue(cc.genconfig(scheme='phpass', category='admin').startswith('$P$5'))
        self.assertTrue(cc.genconfig(scheme='phpass', category='staff').startswith('$H$5'))
        self.assertEqual(cc.genconfig(scheme='phpass', salt='........', rounds=8, ident='P'), '$P$6........22zGEuacuPOqEpYPDeR0R/')
        if PY2:
            c2 = cc.copy(default='phpass')
            self.assertTrue(c2.genconfig(category=u('admin')).startswith('$P$5'))
            self.assertTrue(c2.genconfig(category=u('staff')).startswith('$H$5'))
        self.assertRaises(KeyError, CryptContext().genconfig)
        self.assertRaises(KeyError, CryptContext().genconfig, scheme='md5_crypt')
        self.assertRaises(KeyError, cc.genconfig, scheme='fake')
        self.assertRaises(TypeError, cc.genconfig, scheme=1, category='staff')
        self.assertRaises(TypeError, cc.genconfig, scheme=1)
        self.assertRaises(TypeError, cc.genconfig, category=1)

    def test_42_genhash(self):
        cc = CryptContext(['des_crypt'])
        hash = cc.hash('stub')
        for secret, kwds in self.nonstring_vectors:
            self.assertRaises(TypeError, cc.genhash, secret, hash, **kwds)

        cc = CryptContext(['des_crypt'])
        for config, kwds in self.nonstring_vectors:
            if hash is None:
                continue
            self.assertRaises(TypeError, cc.genhash, 'secret', config, **kwds)

        cc = CryptContext(['mysql323'])
        self.assertRaises(TypeError, cc.genhash, 'stub', None)
        self.assertRaises(KeyError, CryptContext().genhash, 'secret', 'hash')
        self.assertRaises(KeyError, cc.genhash, 'secret', hash, scheme='fake')
        self.assertRaises(TypeError, cc.genhash, 'secret', hash, scheme=1)
        self.assertRaises(TypeError, cc.genconfig, 'secret', hash, category=1)
        return

    def test_43_hash(self):
        cc = CryptContext(**self.sample_4_dict)
        hash = cc.hash('password')
        self.assertTrue(hash.startswith('$5$rounds=3000$'))
        self.assertTrue(cc.verify('password', hash))
        self.assertFalse(cc.verify('passwordx', hash))
        self.assertRaises(ValueError, cc.copy, sha256_crypt__default_rounds=4000)
        cc = CryptContext(['des_crypt'])
        for secret, kwds in self.nonstring_vectors:
            self.assertRaises(TypeError, cc.hash, secret, **kwds)

        self.assertRaises(KeyError, CryptContext().hash, 'secret')
        self.assertRaises(TypeError, cc.hash, 'secret', category=1)

    def test_43_hash_legacy(self, use_16_legacy=False):
        cc = CryptContext(**self.sample_4_dict)
        with self.assertWarningList(['passing settings to.*is deprecated']):
            self.assertEqual(cc.hash('password', scheme='phpass', salt='........'), '$H$5........De04R5Egz0aq8Tf.1eVhY/')
        with self.assertWarningList(['passing settings to.*is deprecated']):
            self.assertEqual(cc.hash('password', scheme='phpass', salt='........', ident='P'), '$P$5........De04R5Egz0aq8Tf.1eVhY/')
        with self.assertWarningList(['passing settings to.*is deprecated']):
            self.assertEqual(cc.hash('password', rounds=1999, salt='nacl'), '$5$rounds=1999$nacl$nmfwJIxqj0csloAAvSER0B8LU0ERCAbhmMug4Twl609')
        with self.assertWarningList(['passing settings to.*is deprecated']):
            self.assertEqual(cc.hash('password', rounds=2001, salt='nacl'), '$5$rounds=2001$nacl$8PdeoPL4aXQnJ0woHhqgIw/efyfCKC2WHneOpnvF.31')
        self.assertRaises(KeyError, cc.hash, 'secret', scheme='fake')
        self.assertRaises(TypeError, cc.hash, 'secret', scheme=1)

    def test_44_identify(self):
        handlers = [
         'md5_crypt', 'des_crypt', 'bsdi_crypt']
        cc = CryptContext(handlers, bsdi_crypt__default_rounds=5)
        self.assertEqual(cc.identify('$9$232323123$1287319827'), None)
        self.assertRaises(ValueError, cc.identify, '$9$232323123$1287319827', required=True)
        cc = CryptContext(['des_crypt'])
        for hash, kwds in self.nonstring_vectors:
            self.assertRaises(TypeError, cc.identify, hash, **kwds)

        cc = CryptContext()
        self.assertIs(cc.identify('hash'), None)
        self.assertRaises(KeyError, cc.identify, 'hash', required=True)
        self.assertRaises(TypeError, cc.identify, None, category=1)
        return

    def test_45_verify(self):
        handlers = [
         'md5_crypt', 'des_crypt', 'bsdi_crypt']
        cc = CryptContext(handlers, bsdi_crypt__default_rounds=5)
        h = hash.md5_crypt.hash('test')
        self.assertTrue(cc.verify('test', h))
        self.assertTrue(not cc.verify('notest', h))
        self.assertTrue(cc.verify('test', h, scheme='md5_crypt'))
        self.assertTrue(not cc.verify('notest', h, scheme='md5_crypt'))
        self.assertRaises(ValueError, cc.verify, 'test', h, scheme='bsdi_crypt')
        self.assertRaises(ValueError, cc.verify, 'stub', '$6$232323123$1287319827')
        cc = CryptContext(['des_crypt'])
        h = refhash = cc.hash('stub')
        for secret, kwds in self.nonstring_vectors:
            self.assertRaises(TypeError, cc.verify, secret, h, **kwds)

        self.assertFalse(cc.verify(secret, None))
        cc = CryptContext(['des_crypt'])
        for h, kwds in self.nonstring_vectors:
            if h is None:
                continue
            self.assertRaises(TypeError, cc.verify, 'secret', h, **kwds)

        self.assertRaises(KeyError, CryptContext().verify, 'secret', 'hash')
        self.assertRaises(KeyError, cc.verify, 'secret', refhash, scheme='fake')
        self.assertRaises(TypeError, cc.verify, 'secret', refhash, scheme=1)
        self.assertRaises(TypeError, cc.verify, 'secret', refhash, category=1)
        return

    def test_46_needs_update(self):
        cc = CryptContext(**self.sample_4_dict)
        self.assertTrue(cc.needs_update('9XXD4trGYeGJA'))
        self.assertFalse(cc.needs_update('$1$J8HC2RCr$HcmM.7NxB2weSvlw2FgzU0'))
        self.assertTrue(cc.needs_update('$5$rounds=1999$jD81UCoo.zI.UETs$Y7qSTQ6mTiU9qZB4fRr43wRgQq4V.5AAf7F97Pzxey/'))
        self.assertFalse(cc.needs_update('$5$rounds=2000$228SSRje04cnNCaQ$YGV4RYu.5sNiBvorQDlO0WWQjyJVGKBcJXz3OtyQ2u8'))
        self.assertFalse(cc.needs_update('$5$rounds=3000$fS9iazEwTKi7QPW4$VasgBC8FqlOvD7x2HhABaMXCTh9jwHclPA9j5YQdns.'))
        self.assertTrue(cc.needs_update('$5$rounds=3001$QlFHHifXvpFX4PLs$/0ekt7lSs/lOikSerQ0M/1porEHxYq7W/2hdFpxA3fA'))
        check_state = []

        class dummy(uh.StaticHandler):
            name = 'dummy'
            _hash_prefix = '@'

            @classmethod
            def needs_update(cls, hash, secret=None):
                check_state.append((hash, secret))
                return secret == 'nu'

            def _calc_checksum(self, secret):
                from hashlib import md5
                if isinstance(secret, unicode):
                    secret = secret.encode('utf-8')
                return str_to_uascii(md5(secret).hexdigest())

        ctx = CryptContext([dummy])
        hash = refhash = dummy.hash('test')
        self.assertFalse(ctx.needs_update(hash))
        self.assertEqual(check_state, [(hash, None)])
        del check_state[:]
        self.assertFalse(ctx.needs_update(hash, secret='bob'))
        self.assertEqual(check_state, [(hash, 'bob')])
        del check_state[:]
        self.assertTrue(ctx.needs_update(hash, secret='nu'))
        self.assertEqual(check_state, [(hash, 'nu')])
        del check_state[:]
        cc = CryptContext(['des_crypt'])
        for hash, kwds in self.nonstring_vectors:
            self.assertRaises(TypeError, cc.needs_update, hash, **kwds)

        self.assertRaises(KeyError, CryptContext().needs_update, 'hash')
        self.assertRaises(KeyError, cc.needs_update, refhash, scheme='fake')
        self.assertRaises(TypeError, cc.needs_update, refhash, scheme=1)
        self.assertRaises(TypeError, cc.needs_update, refhash, category=1)
        return

    def test_47_verify_and_update(self):
        cc = CryptContext(**self.sample_4_dict)
        h1 = cc.handler('des_crypt').hash('password')
        h2 = cc.handler('sha256_crypt').hash('password')
        ok, new_hash = cc.verify_and_update('wrongpass', h1)
        self.assertFalse(ok)
        self.assertIs(new_hash, None)
        ok, new_hash = cc.verify_and_update('wrongpass', h2)
        self.assertFalse(ok)
        self.assertIs(new_hash, None)
        ok, new_hash = cc.verify_and_update('password', h1)
        self.assertTrue(ok)
        self.assertTrue(cc.identify(new_hash), 'sha256_crypt')
        ok, new_hash = cc.verify_and_update('password', h2)
        self.assertTrue(ok)
        self.assertIs(new_hash, None)
        cc = CryptContext(['des_crypt'])
        hash = refhash = cc.hash('stub')
        for secret, kwds in self.nonstring_vectors:
            self.assertRaises(TypeError, cc.verify_and_update, secret, hash, **kwds)

        self.assertEqual(cc.verify_and_update(secret, None), (False, None))
        cc = CryptContext(['des_crypt'])
        for hash, kwds in self.nonstring_vectors:
            if hash is None:
                continue
            self.assertRaises(TypeError, cc.verify_and_update, 'secret', hash, **kwds)

        self.assertRaises(KeyError, CryptContext().verify_and_update, 'secret', 'hash')
        self.assertRaises(KeyError, cc.verify_and_update, 'secret', refhash, scheme='fake')
        self.assertRaises(TypeError, cc.verify_and_update, 'secret', refhash, scheme=1)
        self.assertRaises(TypeError, cc.verify_and_update, 'secret', refhash, category=1)
        return

    def test_48_context_kwds(self):
        from otp.ai.passlib.hash import des_crypt, md5_crypt, postgres_md5
        des_hash = des_crypt.hash('stub')
        pg_root_hash = postgres_md5.hash('stub', user='root')
        pg_admin_hash = postgres_md5.hash('stub', user='admin')
        cc1 = CryptContext([des_crypt, md5_crypt])
        self.assertEqual(cc1.context_kwds, set())
        self.assertTrue(des_crypt.identify(cc1.hash('stub')), 'des_crypt')
        self.assertTrue(cc1.verify('stub', des_hash))
        self.assertEqual(cc1.verify_and_update('stub', des_hash), (True, None))
        with self.assertWarningList(['passing settings to.*is deprecated']):
            self.assertRaises(TypeError, cc1.hash, 'stub', user='root')
        self.assertRaises(TypeError, cc1.verify, 'stub', des_hash, user='root')
        self.assertRaises(TypeError, cc1.verify_and_update, 'stub', des_hash, user='root')
        cc2 = CryptContext([des_crypt, postgres_md5])
        self.assertEqual(cc2.context_kwds, set(['user']))
        self.assertTrue(des_crypt.identify(cc2.hash('stub')), 'des_crypt')
        self.assertTrue(cc2.verify('stub', des_hash))
        self.assertEqual(cc2.verify_and_update('stub', des_hash), (True, None))
        self.assertTrue(des_crypt.identify(cc2.hash('stub', user='root')), 'des_crypt')
        self.assertTrue(cc2.verify('stub', des_hash, user='root'))
        self.assertEqual(cc2.verify_and_update('stub', des_hash, user='root'), (True, None))
        with self.assertWarningList(['passing settings to.*is deprecated']):
            self.assertRaises(TypeError, cc2.hash, 'stub', badkwd='root')
        self.assertRaises(TypeError, cc2.verify, 'stub', des_hash, badkwd='root')
        self.assertRaises(TypeError, cc2.verify_and_update, 'stub', des_hash, badkwd='root')
        cc3 = CryptContext([postgres_md5, des_crypt], deprecated='auto')
        self.assertEqual(cc3.context_kwds, set(['user']))
        self.assertRaises(TypeError, cc3.hash, 'stub')
        self.assertRaises(TypeError, cc3.verify, 'stub', pg_root_hash)
        self.assertRaises(TypeError, cc3.verify_and_update, 'stub', pg_root_hash)
        self.assertEqual(cc3.hash('stub', user='root'), pg_root_hash)
        self.assertTrue(cc3.verify('stub', pg_root_hash, user='root'))
        self.assertEqual(cc3.verify_and_update('stub', pg_root_hash, user='root'), (True, None))
        self.assertEqual(cc3.verify_and_update('stub', pg_root_hash, user='admin'), (False, None))
        self.assertEqual(cc3.verify_and_update('stub', des_hash, user='root'), (
         True, pg_root_hash))
        return

    def test_50_rounds_limits(self):
        cc = CryptContext(schemes=['sha256_crypt'], sha256_crypt__min_rounds=2000, sha256_crypt__max_rounds=3000, sha256_crypt__default_rounds=2500)
        STUB = '...........................................'
        custom_handler = cc._get_record('sha256_crypt', None)
        self.assertEqual(custom_handler.min_desired_rounds, 2000)
        self.assertEqual(custom_handler.max_desired_rounds, 3000)
        self.assertEqual(custom_handler.default_rounds, 2500)
        with self.assertWarningList([PasslibHashWarning] * 2):
            c2 = cc.copy(sha256_crypt__min_rounds=500, sha256_crypt__max_rounds=None, sha256_crypt__default_rounds=500)
        self.assertEqual(c2.genconfig(salt='nacl'), '$5$rounds=1000$nacl$' + STUB)
        with self.assertWarningList([]):
            self.assertEqual(cc.genconfig(rounds=1999, salt='nacl'), '$5$rounds=1999$nacl$' + STUB)
        self.assertEqual(cc.genconfig(rounds=2000, salt='nacl'), '$5$rounds=2000$nacl$' + STUB)
        self.assertEqual(cc.genconfig(rounds=2001, salt='nacl'), '$5$rounds=2001$nacl$' + STUB)
        with self.assertWarningList([PasslibHashWarning] * 2):
            c2 = cc.copy(sha256_crypt__max_rounds=int(1000000000.0) + 500, sha256_crypt__min_rounds=None, sha256_crypt__default_rounds=int(1000000000.0) + 500)
        self.assertEqual(c2.genconfig(salt='nacl'), '$5$rounds=999999999$nacl$' + STUB)
        with self.assertWarningList([]):
            self.assertEqual(cc.genconfig(rounds=3001, salt='nacl'), '$5$rounds=3001$nacl$' + STUB)
        self.assertEqual(cc.genconfig(rounds=3000, salt='nacl'), '$5$rounds=3000$nacl$' + STUB)
        self.assertEqual(cc.genconfig(rounds=2999, salt='nacl'), '$5$rounds=2999$nacl$' + STUB)
        self.assertEqual(cc.genconfig(salt='nacl'), '$5$rounds=2500$nacl$' + STUB)
        df = hash.sha256_crypt.default_rounds
        c2 = cc.copy(sha256_crypt__default_rounds=None, sha256_crypt__max_rounds=df << 1)
        self.assertEqual(c2.genconfig(salt='nacl'), '$5$rounds=%d$nacl$%s' % (df, STUB))
        c2 = cc.copy(sha256_crypt__default_rounds=None, sha256_crypt__max_rounds=3000)
        self.assertEqual(c2.genconfig(salt='nacl'), '$5$rounds=3000$nacl$' + STUB)
        self.assertRaises(ValueError, cc.copy, sha256_crypt__default_rounds=1999)
        cc.copy(sha256_crypt__default_rounds=2000)
        cc.copy(sha256_crypt__default_rounds=3000)
        self.assertRaises(ValueError, cc.copy, sha256_crypt__default_rounds=3001)
        c2 = CryptContext(schemes=['sha256_crypt'])
        self.assertRaises(ValueError, c2.copy, sha256_crypt__min_rounds=2000, sha256_crypt__max_rounds=1999)
        self.assertRaises(ValueError, CryptContext, sha256_crypt__min_rounds='x')
        self.assertRaises(ValueError, CryptContext, sha256_crypt__max_rounds='x')
        self.assertRaises(ValueError, CryptContext, all__vary_rounds='x')
        self.assertRaises(ValueError, CryptContext, sha256_crypt__default_rounds='x')
        bad = datetime.datetime.now()
        self.assertRaises(TypeError, CryptContext, 'sha256_crypt', sha256_crypt__min_rounds=bad)
        self.assertRaises(TypeError, CryptContext, 'sha256_crypt', sha256_crypt__max_rounds=bad)
        self.assertRaises(TypeError, CryptContext, 'sha256_crypt', all__vary_rounds=bad)
        self.assertRaises(TypeError, CryptContext, 'sha256_crypt', sha256_crypt__default_rounds=bad)
        return

    def test_51_linear_vary_rounds(self):
        cc = CryptContext(schemes=['sha256_crypt'], sha256_crypt__min_rounds=1995, sha256_crypt__max_rounds=2005, sha256_crypt__default_rounds=2000)
        self.assertRaises(ValueError, cc.copy, all__vary_rounds=-1)
        self.assertRaises(ValueError, cc.copy, all__vary_rounds='-1%')
        self.assertRaises(ValueError, cc.copy, all__vary_rounds='101%')
        c2 = cc.copy(all__vary_rounds=0)
        self.assertEqual(c2._get_record('sha256_crypt', None).vary_rounds, 0)
        self.assert_rounds_range(c2, 'sha256_crypt', 2000, 2000)
        c2 = cc.copy(all__vary_rounds='0%')
        self.assertEqual(c2._get_record('sha256_crypt', None).vary_rounds, 0)
        self.assert_rounds_range(c2, 'sha256_crypt', 2000, 2000)
        c2 = cc.copy(all__vary_rounds=1)
        self.assertEqual(c2._get_record('sha256_crypt', None).vary_rounds, 1)
        self.assert_rounds_range(c2, 'sha256_crypt', 1999, 2001)
        c2 = cc.copy(all__vary_rounds=100)
        self.assertEqual(c2._get_record('sha256_crypt', None).vary_rounds, 100)
        self.assert_rounds_range(c2, 'sha256_crypt', 1995, 2005)
        c2 = cc.copy(all__vary_rounds='0.1%')
        self.assertEqual(c2._get_record('sha256_crypt', None).vary_rounds, 0.001)
        self.assert_rounds_range(c2, 'sha256_crypt', 1998, 2002)
        c2 = cc.copy(all__vary_rounds='100%')
        self.assertEqual(c2._get_record('sha256_crypt', None).vary_rounds, 1.0)
        self.assert_rounds_range(c2, 'sha256_crypt', 1995, 2005)
        return

    def test_52_log2_vary_rounds(self):
        cc = CryptContext(schemes=['bcrypt'], bcrypt__min_rounds=15, bcrypt__max_rounds=25, bcrypt__default_rounds=20)
        self.assertRaises(ValueError, cc.copy, all__vary_rounds=-1)
        self.assertRaises(ValueError, cc.copy, all__vary_rounds='-1%')
        self.assertRaises(ValueError, cc.copy, all__vary_rounds='101%')
        c2 = cc.copy(all__vary_rounds=0)
        self.assertEqual(c2._get_record('bcrypt', None).vary_rounds, 0)
        self.assert_rounds_range(c2, 'bcrypt', 20, 20)
        c2 = cc.copy(all__vary_rounds='0%')
        self.assertEqual(c2._get_record('bcrypt', None).vary_rounds, 0)
        self.assert_rounds_range(c2, 'bcrypt', 20, 20)
        c2 = cc.copy(all__vary_rounds=1)
        self.assertEqual(c2._get_record('bcrypt', None).vary_rounds, 1)
        self.assert_rounds_range(c2, 'bcrypt', 19, 21)
        c2 = cc.copy(all__vary_rounds=100)
        self.assertEqual(c2._get_record('bcrypt', None).vary_rounds, 100)
        self.assert_rounds_range(c2, 'bcrypt', 15, 25)
        c2 = cc.copy(all__vary_rounds='1%')
        self.assertEqual(c2._get_record('bcrypt', None).vary_rounds, 0.01)
        self.assert_rounds_range(c2, 'bcrypt', 20, 20)
        c2 = cc.copy(all__vary_rounds='49%')
        self.assertEqual(c2._get_record('bcrypt', None).vary_rounds, 0.49)
        self.assert_rounds_range(c2, 'bcrypt', 20, 20)
        c2 = cc.copy(all__vary_rounds='50%')
        self.assertEqual(c2._get_record('bcrypt', None).vary_rounds, 0.5)
        self.assert_rounds_range(c2, 'bcrypt', 19, 20)
        c2 = cc.copy(all__vary_rounds='100%')
        self.assertEqual(c2._get_record('bcrypt', None).vary_rounds, 1.0)
        self.assert_rounds_range(c2, 'bcrypt', 15, 21)
        return

    def assert_rounds_range(self, context, scheme, lower, upper):
        handler = context.handler(scheme)
        salt = handler.default_salt_chars[0:1] * handler.max_salt_size
        seen = set()
        for i in irange(300):
            h = context.genconfig(scheme, salt=salt)
            r = handler.from_string(h).rounds
            seen.add(r)

        self.assertEqual(min(seen), lower, 'vary_rounds had wrong lower limit:')
        self.assertEqual(max(seen), upper, 'vary_rounds had wrong upper limit:')

    def test_harden_verify_parsing(self):
        warnings.filterwarnings('ignore', '.*harden_verify.*', category=DeprecationWarning)
        ctx = CryptContext(schemes=['sha256_crypt'])
        self.assertEqual(ctx.harden_verify, None)
        self.assertEqual(ctx.using(harden_verify='').harden_verify, None)
        self.assertEqual(ctx.using(harden_verify='true').harden_verify, None)
        self.assertEqual(ctx.using(harden_verify='false').harden_verify, None)
        return

    def test_dummy_verify(self):
        expected = 0.05
        accuracy = 0.2
        handler = DelayHash.using()
        handler.delay = expected
        ctx = CryptContext(schemes=[handler])
        ctx.dummy_verify()
        elapsed, _ = time_call(ctx.dummy_verify)
        self.assertAlmostEqual(elapsed, expected, delta=expected * accuracy)

    def test_61_autodeprecate(self):

        def getstate(ctx, category=None):
            return [ ctx.handler(scheme, category).deprecated for scheme in ctx.schemes() ]

        ctx = CryptContext('sha256_crypt,md5_crypt,des_crypt', deprecated='auto')
        self.assertEqual(getstate(ctx, None), [False, True, True])
        self.assertEqual(getstate(ctx, 'admin'), [False, True, True])
        ctx.update(default='md5_crypt')
        self.assertEqual(getstate(ctx, None), [True, False, True])
        self.assertEqual(getstate(ctx, 'admin'), [True, False, True])
        ctx.update(admin__context__default='des_crypt')
        self.assertEqual(getstate(ctx, None), [True, False, True])
        self.assertEqual(getstate(ctx, 'admin'), [True, True, False])
        ctx = CryptContext(['sha256_crypt'], deprecated='auto')
        self.assertEqual(getstate(ctx, None), [False])
        self.assertEqual(getstate(ctx, 'admin'), [False])
        self.assertRaises(ValueError, CryptContext, 'sha256_crypt,md5_crypt', deprecated='auto,md5_crypt')
        self.assertRaises(ValueError, CryptContext, 'sha256_crypt,md5_crypt', deprecated='md5_crypt,auto')
        return

    def test_disabled_hashes(self):
        from otp.ai.passlib.hash import md5_crypt, unix_disabled
        ctx = CryptContext(['des_crypt'])
        ctx2 = CryptContext(['des_crypt', 'unix_disabled'])
        h_ref = ctx.hash('foo')
        h_other = md5_crypt.hash('foo')
        self.assertRaisesRegex(RuntimeError, 'no disabled hasher present', ctx.disable)
        self.assertRaisesRegex(RuntimeError, 'no disabled hasher present', ctx.disable, h_ref)
        self.assertRaisesRegex(RuntimeError, 'no disabled hasher present', ctx.disable, h_other)
        h_dis = ctx2.disable()
        self.assertEqual(h_dis, unix_disabled.default_marker)
        h_dis_ref = ctx2.disable(h_ref)
        self.assertEqual(h_dis_ref, unix_disabled.default_marker + h_ref)
        h_dis_other = ctx2.disable(h_other)
        self.assertEqual(h_dis_other, unix_disabled.default_marker + h_other)
        self.assertEqual(ctx2.disable(h_dis_ref), h_dis_ref)
        self.assertTrue(ctx.is_enabled(h_ref))
        HASH_NOT_IDENTIFIED = 'hash could not be identified'
        self.assertRaisesRegex(ValueError, HASH_NOT_IDENTIFIED, ctx.is_enabled, h_other)
        self.assertRaisesRegex(ValueError, HASH_NOT_IDENTIFIED, ctx.is_enabled, h_dis)
        self.assertRaisesRegex(ValueError, HASH_NOT_IDENTIFIED, ctx.is_enabled, h_dis_ref)
        self.assertTrue(ctx2.is_enabled(h_ref))
        self.assertRaisesRegex(ValueError, HASH_NOT_IDENTIFIED, ctx.is_enabled, h_other)
        self.assertFalse(ctx2.is_enabled(h_dis))
        self.assertFalse(ctx2.is_enabled(h_dis_ref))
        self.assertRaisesRegex(ValueError, HASH_NOT_IDENTIFIED, ctx.enable, '')
        self.assertRaises(TypeError, ctx.enable, None)
        self.assertEqual(ctx.enable(h_ref), h_ref)
        self.assertRaisesRegex(ValueError, HASH_NOT_IDENTIFIED, ctx.enable, h_other)
        self.assertRaisesRegex(ValueError, HASH_NOT_IDENTIFIED, ctx.enable, h_dis)
        self.assertRaisesRegex(ValueError, HASH_NOT_IDENTIFIED, ctx.enable, h_dis_ref)
        self.assertRaisesRegex(ValueError, HASH_NOT_IDENTIFIED, ctx.enable, '')
        self.assertRaises(TypeError, ctx2.enable, None)
        self.assertEqual(ctx2.enable(h_ref), h_ref)
        self.assertRaisesRegex(ValueError, HASH_NOT_IDENTIFIED, ctx2.enable, h_other)
        self.assertRaisesRegex(ValueError, 'cannot restore original hash', ctx2.enable, h_dis)
        self.assertEqual(ctx2.enable(h_dis_ref), h_ref)
        return


import hashlib, time

class DelayHash(uh.StaticHandler):
    name = 'delay_hash'
    checksum_chars = uh.LOWER_HEX_CHARS
    checksum_size = 40
    delay = 0
    _hash_prefix = u('$x$')

    def _calc_checksum(self, secret):
        time.sleep(self.delay)
        if isinstance(secret, unicode):
            secret = secret.encode('utf-8')
        return str_to_uascii(hashlib.sha1('prefix' + secret).hexdigest())


class dummy_2(uh.StaticHandler):
    name = 'dummy_2'


class LazyCryptContextTest(TestCase):
    descriptionPrefix = 'LazyCryptContext'

    def setUp(self):
        unload_handler_name('dummy_2')
        self.addCleanup(unload_handler_name, 'dummy_2')

    def test_kwd_constructor(self):
        self.assertFalse(has_crypt_handler('dummy_2'))
        register_crypt_handler_path('dummy_2', 'passlib.tests.test_context')
        cc = LazyCryptContext(iter(['dummy_2', 'des_crypt']), deprecated=['des_crypt'])
        self.assertFalse(has_crypt_handler('dummy_2', True))
        self.assertEqual(cc.schemes(), ('dummy_2', 'des_crypt'))
        self.assertTrue(cc.handler('des_crypt').deprecated)
        self.assertTrue(has_crypt_handler('dummy_2', True))

    def test_callable_constructor(self):
        self.assertFalse(has_crypt_handler('dummy_2'))
        register_crypt_handler_path('dummy_2', 'passlib.tests.test_context')

        def onload(flag=False):
            self.assertTrue(flag)
            return dict(schemes=iter(['dummy_2', 'des_crypt']), deprecated=['des_crypt'])

        cc = LazyCryptContext(onload=onload, flag=True)
        self.assertFalse(has_crypt_handler('dummy_2', True))
        self.assertEqual(cc.schemes(), ('dummy_2', 'des_crypt'))
        self.assertTrue(cc.handler('des_crypt').deprecated)
        self.assertTrue(has_crypt_handler('dummy_2', True))