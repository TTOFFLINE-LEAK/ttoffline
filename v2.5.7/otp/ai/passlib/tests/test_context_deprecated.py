from __future__ import with_statement
from logging import getLogger
import os, warnings
try:
    from pkg_resources import resource_filename
except ImportError:
    resource_filename = None

from otp.ai.passlib import hash
from otp.ai.passlib.context import CryptContext, CryptPolicy, LazyCryptContext
from otp.ai.passlib.utils import to_bytes, to_unicode
import otp.ai.passlib.utils.handlers as uh
from otp.ai.passlib.tests.utils import TestCase, set_file
from otp.ai.passlib.registry import register_crypt_handler_path, _has_crypt_handler as has_crypt_handler, _unload_handler_name as unload_handler_name
log = getLogger(__name__)

class CryptPolicyTest(TestCase):
    descriptionPrefix = 'CryptPolicy'
    sample_config_1s = '[passlib]\nschemes = des_crypt, md5_crypt, bsdi_crypt, sha512_crypt\ndefault = md5_crypt\nall.vary_rounds = 10%%\nbsdi_crypt.max_rounds = 30000\nbsdi_crypt.default_rounds = 25000\nsha512_crypt.max_rounds = 50000\nsha512_crypt.min_rounds = 40000\n'
    sample_config_1s_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_config_1s.cfg'))
    if not os.path.exists(sample_config_1s_path) and resource_filename:
        sample_config_1s_path = resource_filename('passlib.tests', 'sample_config_1s.cfg')
    sample_config_1pd = dict(schemes=[
     'des_crypt', 'md5_crypt', 'bsdi_crypt', 'sha512_crypt'], default='md5_crypt', all__vary_rounds=0.1, bsdi_crypt__max_rounds=30000, bsdi_crypt__default_rounds=25000, sha512_crypt__max_rounds=50000, sha512_crypt__min_rounds=40000)
    sample_config_1pid = {'schemes': 'des_crypt, md5_crypt, bsdi_crypt, sha512_crypt', 
       'default': 'md5_crypt', 
       'all.vary_rounds': 0.1, 
       'bsdi_crypt.max_rounds': 30000, 
       'bsdi_crypt.default_rounds': 25000, 
       'sha512_crypt.max_rounds': 50000, 
       'sha512_crypt.min_rounds': 40000}
    sample_config_1prd = dict(schemes=[
     hash.des_crypt, hash.md5_crypt, hash.bsdi_crypt, hash.sha512_crypt], default='md5_crypt', all__vary_rounds=0.1, bsdi_crypt__max_rounds=30000, bsdi_crypt__default_rounds=25000, sha512_crypt__max_rounds=50000, sha512_crypt__min_rounds=40000)
    sample_config_2s = '[passlib]\nbsdi_crypt.min_rounds = 29000\nbsdi_crypt.max_rounds = 35000\nbsdi_crypt.default_rounds = 31000\nsha512_crypt.min_rounds = 45000\n'
    sample_config_2pd = dict(bsdi_crypt__min_rounds=29000, bsdi_crypt__max_rounds=35000, bsdi_crypt__default_rounds=31000, sha512_crypt__min_rounds=45000)
    sample_config_12pd = dict(schemes=[
     'des_crypt', 'md5_crypt', 'bsdi_crypt', 'sha512_crypt'], default='md5_crypt', all__vary_rounds=0.1, bsdi_crypt__min_rounds=29000, bsdi_crypt__max_rounds=35000, bsdi_crypt__default_rounds=31000, sha512_crypt__max_rounds=50000, sha512_crypt__min_rounds=45000)
    sample_config_3pd = dict(default='sha512_crypt')
    sample_config_123pd = dict(schemes=[
     'des_crypt', 'md5_crypt', 'bsdi_crypt', 'sha512_crypt'], default='sha512_crypt', all__vary_rounds=0.1, bsdi_crypt__min_rounds=29000, bsdi_crypt__max_rounds=35000, bsdi_crypt__default_rounds=31000, sha512_crypt__max_rounds=50000, sha512_crypt__min_rounds=45000)
    sample_config_4s = '\n[passlib]\nschemes = sha512_crypt\nall.vary_rounds = 10%%\ndefault.sha512_crypt.max_rounds = 20000\nadmin.all.vary_rounds = 5%%\nadmin.sha512_crypt.max_rounds = 40000\n'
    sample_config_4pd = dict(schemes=[
     'sha512_crypt'], all__vary_rounds=0.1, sha512_crypt__max_rounds=20000, admin__all__vary_rounds=0.05, admin__sha512_crypt__max_rounds=40000)
    sample_config_5s = sample_config_1s + 'deprecated = des_crypt\nadmin__context__deprecated = des_crypt, bsdi_crypt\n'
    sample_config_5pd = sample_config_1pd.copy()
    sample_config_5pd.update(deprecated=[
     'des_crypt'], admin__context__deprecated=[
     'des_crypt', 'bsdi_crypt'])
    sample_config_5pid = sample_config_1pid.copy()
    sample_config_5pid.update({'deprecated': 'des_crypt', 
       'admin.context.deprecated': 'des_crypt, bsdi_crypt'})
    sample_config_5prd = sample_config_1prd.copy()
    sample_config_5prd.update({'deprecated': [
                    'des_crypt'], 
       'admin__context__deprecated': [
                                    'des_crypt', 'bsdi_crypt']})

    def setUp(self):
        TestCase.setUp(self)
        warnings.filterwarnings('ignore', 'The CryptPolicy class has been deprecated')
        warnings.filterwarnings('ignore', 'the method.*hash_needs_update.*is deprecated')
        warnings.filterwarnings('ignore', "The 'all' scheme is deprecated.*")
        warnings.filterwarnings('ignore', 'bsdi_crypt rounds should be odd')

    def test_00_constructor(self):
        policy = CryptPolicy(**self.sample_config_1pd)
        self.assertEqual(policy.to_dict(), self.sample_config_1pd)
        policy = CryptPolicy(self.sample_config_1pd)
        self.assertEqual(policy.to_dict(), self.sample_config_1pd)
        self.assertRaises(TypeError, CryptPolicy, {}, {})
        self.assertRaises(TypeError, CryptPolicy, {}, dummy=1)
        self.assertRaises(TypeError, CryptPolicy, schemes=[
         'des_crypt', 'md5_crypt', 'bsdi_crypt', 'sha512_crypt'], bad__key__bsdi_crypt__max_rounds=30000)

        class nameless(uh.StaticHandler):
            name = None

        self.assertRaises(ValueError, CryptPolicy, schemes=[nameless])
        self.assertRaises(TypeError, CryptPolicy, schemes=[uh.StaticHandler])

        class dummy_1(uh.StaticHandler):
            name = 'dummy_1'

        self.assertRaises(KeyError, CryptPolicy, schemes=[dummy_1, dummy_1])
        self.assertRaises(KeyError, CryptPolicy, schemes=[
         'des_crypt'], deprecated=[
         'md5_crypt'])
        self.assertRaises(KeyError, CryptPolicy, schemes=[
         'des_crypt'], default='md5_crypt')

    def test_01_from_path_simple(self):
        path = self.sample_config_1s_path
        policy = CryptPolicy.from_path(path)
        self.assertEqual(policy.to_dict(), self.sample_config_1pd)
        self.assertRaises(EnvironmentError, CryptPolicy.from_path, path + 'xxx')

    def test_01_from_path(self):
        path = self.mktemp()
        set_file(path, self.sample_config_1s)
        policy = CryptPolicy.from_path(path)
        self.assertEqual(policy.to_dict(), self.sample_config_1pd)
        set_file(path, self.sample_config_1s.replace('\n', '\r\n'))
        policy = CryptPolicy.from_path(path)
        self.assertEqual(policy.to_dict(), self.sample_config_1pd)
        uc2 = to_bytes(self.sample_config_1s, 'utf-16', source_encoding='utf-8')
        set_file(path, uc2)
        policy = CryptPolicy.from_path(path, encoding='utf-16')
        self.assertEqual(policy.to_dict(), self.sample_config_1pd)

    def test_02_from_string(self):
        policy = CryptPolicy.from_string(self.sample_config_1s)
        self.assertEqual(policy.to_dict(), self.sample_config_1pd)
        policy = CryptPolicy.from_string(self.sample_config_1s.replace('\n', '\r\n'))
        self.assertEqual(policy.to_dict(), self.sample_config_1pd)
        data = to_unicode(self.sample_config_1s)
        policy = CryptPolicy.from_string(data)
        self.assertEqual(policy.to_dict(), self.sample_config_1pd)
        uc2 = to_bytes(self.sample_config_1s, 'utf-16', source_encoding='utf-8')
        policy = CryptPolicy.from_string(uc2, encoding='utf-16')
        self.assertEqual(policy.to_dict(), self.sample_config_1pd)
        policy = CryptPolicy.from_string(self.sample_config_4s)
        self.assertEqual(policy.to_dict(), self.sample_config_4pd)

    def test_03_from_source(self):
        policy = CryptPolicy.from_source(self.sample_config_1s_path)
        self.assertEqual(policy.to_dict(), self.sample_config_1pd)
        policy = CryptPolicy.from_source(self.sample_config_1s)
        self.assertEqual(policy.to_dict(), self.sample_config_1pd)
        policy = CryptPolicy.from_source(self.sample_config_1pd.copy())
        self.assertEqual(policy.to_dict(), self.sample_config_1pd)
        p2 = CryptPolicy.from_source(policy)
        self.assertIs(policy, p2)
        self.assertRaises(TypeError, CryptPolicy.from_source, 1)
        self.assertRaises(TypeError, CryptPolicy.from_source, [])

    def test_04_from_sources(self):
        self.assertRaises(ValueError, CryptPolicy.from_sources, [])
        policy = CryptPolicy.from_sources([self.sample_config_1s])
        self.assertEqual(policy.to_dict(), self.sample_config_1pd)
        policy = CryptPolicy.from_sources([
         self.sample_config_1s_path,
         self.sample_config_2s,
         self.sample_config_3pd])
        self.assertEqual(policy.to_dict(), self.sample_config_123pd)

    def test_05_replace(self):
        p1 = CryptPolicy(**self.sample_config_1pd)
        p2 = p1.replace(**self.sample_config_2pd)
        self.assertEqual(p2.to_dict(), self.sample_config_12pd)
        p2b = p2.replace(**self.sample_config_2pd)
        self.assertEqual(p2b.to_dict(), self.sample_config_12pd)
        p3 = p2.replace(self.sample_config_3pd)
        self.assertEqual(p3.to_dict(), self.sample_config_123pd)

    def test_06_forbidden(self):
        self.assertRaises(KeyError, CryptPolicy, schemes=[
         'des_crypt'], des_crypt__salt='xx')
        self.assertRaises(KeyError, CryptPolicy, schemes=[
         'des_crypt'], all__salt='xx')
        self.assertRaises(KeyError, CryptPolicy, schemes=[
         'des_crypt'], user__context__schemes=[
         'md5_crypt'])

    def test_10_has_schemes(self):
        p1 = CryptPolicy(**self.sample_config_1pd)
        self.assertTrue(p1.has_schemes())
        p3 = CryptPolicy(**self.sample_config_3pd)
        self.assertTrue(not p3.has_schemes())

    def test_11_iter_handlers(self):
        p1 = CryptPolicy(**self.sample_config_1pd)
        s = self.sample_config_1prd['schemes']
        self.assertEqual(list(p1.iter_handlers()), s)
        p3 = CryptPolicy(**self.sample_config_3pd)
        self.assertEqual(list(p3.iter_handlers()), [])

    def test_12_get_handler(self):
        p1 = CryptPolicy(**self.sample_config_1pd)
        self.assertIs(p1.get_handler('bsdi_crypt'), hash.bsdi_crypt)
        self.assertIs(p1.get_handler('sha256_crypt'), None)
        self.assertRaises(KeyError, p1.get_handler, 'sha256_crypt', required=True)
        self.assertIs(p1.get_handler(), hash.md5_crypt)
        return

    def test_13_get_options(self):
        p12 = CryptPolicy(**self.sample_config_12pd)
        self.assertEqual(p12.get_options('bsdi_crypt'), dict(vary_rounds=0.1, min_rounds=29000, max_rounds=35000, default_rounds=31000))
        self.assertEqual(p12.get_options('sha512_crypt'), dict(vary_rounds=0.1, min_rounds=45000, max_rounds=50000))
        p4 = CryptPolicy.from_string(self.sample_config_4s)
        self.assertEqual(p4.get_options('sha512_crypt'), dict(vary_rounds=0.1, max_rounds=20000))
        self.assertEqual(p4.get_options('sha512_crypt', 'user'), dict(vary_rounds=0.1, max_rounds=20000))
        self.assertEqual(p4.get_options('sha512_crypt', 'admin'), dict(vary_rounds=0.05, max_rounds=40000))

    def test_14_handler_is_deprecated(self):
        pa = CryptPolicy(**self.sample_config_1pd)
        pb = CryptPolicy(**self.sample_config_5pd)
        self.assertFalse(pa.handler_is_deprecated('des_crypt'))
        self.assertFalse(pa.handler_is_deprecated(hash.bsdi_crypt))
        self.assertFalse(pa.handler_is_deprecated('sha512_crypt'))
        self.assertTrue(pb.handler_is_deprecated('des_crypt'))
        self.assertFalse(pb.handler_is_deprecated(hash.bsdi_crypt))
        self.assertFalse(pb.handler_is_deprecated('sha512_crypt'))
        self.assertTrue(pb.handler_is_deprecated('des_crypt', 'user'))
        self.assertFalse(pb.handler_is_deprecated('bsdi_crypt', 'user'))
        self.assertTrue(pb.handler_is_deprecated('des_crypt', 'admin'))
        self.assertTrue(pb.handler_is_deprecated('bsdi_crypt', 'admin'))
        pc = CryptPolicy(schemes=[
         'md5_crypt', 'des_crypt'], deprecated=[
         'md5_crypt'], user__context__deprecated=[
         'des_crypt'])
        self.assertTrue(pc.handler_is_deprecated('md5_crypt'))
        self.assertFalse(pc.handler_is_deprecated('des_crypt'))
        self.assertFalse(pc.handler_is_deprecated('md5_crypt', 'user'))
        self.assertTrue(pc.handler_is_deprecated('des_crypt', 'user'))

    def test_15_min_verify_time(self):
        warnings.filterwarnings('ignore', category=DeprecationWarning)
        pa = CryptPolicy()
        self.assertEqual(pa.get_min_verify_time(), 0)
        self.assertEqual(pa.get_min_verify_time('admin'), 0)
        pb = pa.replace(min_verify_time=0.1)
        self.assertEqual(pb.get_min_verify_time(), 0)
        self.assertEqual(pb.get_min_verify_time('admin'), 0)

    def test_20_iter_config(self):
        p5 = CryptPolicy(**self.sample_config_5pd)
        self.assertEqual(dict(p5.iter_config()), self.sample_config_5pd)
        self.assertEqual(dict(p5.iter_config(resolve=True)), self.sample_config_5prd)
        self.assertEqual(dict(p5.iter_config(ini=True)), self.sample_config_5pid)

    def test_21_to_dict(self):
        p5 = CryptPolicy(**self.sample_config_5pd)
        self.assertEqual(p5.to_dict(), self.sample_config_5pd)
        self.assertEqual(p5.to_dict(resolve=True), self.sample_config_5prd)

    def test_22_to_string(self):
        pa = CryptPolicy(**self.sample_config_5pd)
        s = pa.to_string()
        pb = CryptPolicy.from_string(s)
        self.assertEqual(pb.to_dict(), self.sample_config_5pd)
        s = pa.to_string(encoding='latin-1')
        self.assertIsInstance(s, bytes)


class CryptContextTest(TestCase):
    descriptionPrefix = 'CryptContext'

    def setUp(self):
        TestCase.setUp(self)
        warnings.filterwarnings('ignore', 'CryptContext\\(\\)\\.replace\\(\\) has been deprecated.*')
        warnings.filterwarnings('ignore', 'The CryptContext ``policy`` keyword has been deprecated.*')
        warnings.filterwarnings('ignore', '.*(CryptPolicy|context\\.policy).*(has|have) been deprecated.*')
        warnings.filterwarnings('ignore', 'the method.*hash_needs_update.*is deprecated')

    def test_00_constructor(self):
        cc = CryptContext([hash.md5_crypt, hash.bsdi_crypt, hash.des_crypt])
        c, b, a = cc.policy.iter_handlers()
        self.assertIs(a, hash.des_crypt)
        self.assertIs(b, hash.bsdi_crypt)
        self.assertIs(c, hash.md5_crypt)
        cc = CryptContext(['md5_crypt', 'bsdi_crypt', 'des_crypt'])
        c, b, a = cc.policy.iter_handlers()
        self.assertIs(a, hash.des_crypt)
        self.assertIs(b, hash.bsdi_crypt)
        self.assertIs(c, hash.md5_crypt)
        policy = cc.policy
        cc = CryptContext(policy=policy)
        self.assertEqual(cc.to_dict(), policy.to_dict())
        cc = CryptContext(policy=policy, default='bsdi_crypt')
        self.assertNotEqual(cc.to_dict(), policy.to_dict())
        self.assertEqual(cc.to_dict(), dict(schemes=['md5_crypt', 'bsdi_crypt', 'des_crypt'], default='bsdi_crypt'))
        self.assertRaises(TypeError, setattr, cc, 'policy', None)
        self.assertRaises(TypeError, CryptContext, policy='x')
        return

    def test_01_replace(self):
        cc = CryptContext(['md5_crypt', 'bsdi_crypt', 'des_crypt'])
        self.assertIs(cc.policy.get_handler(), hash.md5_crypt)
        cc2 = cc.replace()
        self.assertIsNot(cc2, cc)
        cc3 = cc.replace(default='bsdi_crypt')
        self.assertIsNot(cc3, cc)
        self.assertIs(cc3.policy.get_handler(), hash.bsdi_crypt)

    def test_02_no_handlers(self):
        cc = CryptContext()
        self.assertRaises(KeyError, cc.identify, 'hash', required=True)
        self.assertRaises(KeyError, cc.hash, 'secret')
        self.assertRaises(KeyError, cc.verify, 'secret', 'hash')
        cc = CryptContext(['md5_crypt'])
        p = CryptPolicy(schemes=[])
        cc.policy = p
        self.assertRaises(KeyError, cc.identify, 'hash', required=True)
        self.assertRaises(KeyError, cc.hash, 'secret')
        self.assertRaises(KeyError, cc.verify, 'secret', 'hash')

    sample_policy_1 = dict(schemes=[
     'des_crypt', 'md5_crypt', 'phpass', 'bsdi_crypt',
     'sha256_crypt'], deprecated=[
     'des_crypt'], default='sha256_crypt', bsdi_crypt__max_rounds=30, bsdi_crypt__default_rounds=25, bsdi_crypt__vary_rounds=0, sha256_crypt__max_rounds=3000, sha256_crypt__min_rounds=2000, sha256_crypt__default_rounds=3000, phpass__ident='H', phpass__default_rounds=7)

    def test_12_hash_needs_update(self):
        cc = CryptContext(**self.sample_policy_1)
        self.assertTrue(cc.hash_needs_update('9XXD4trGYeGJA'))
        self.assertFalse(cc.hash_needs_update('$1$J8HC2RCr$HcmM.7NxB2weSvlw2FgzU0'))
        self.assertTrue(cc.hash_needs_update('$5$rounds=1999$jD81UCoo.zI.UETs$Y7qSTQ6mTiU9qZB4fRr43wRgQq4V.5AAf7F97Pzxey/'))
        self.assertFalse(cc.hash_needs_update('$5$rounds=2000$228SSRje04cnNCaQ$YGV4RYu.5sNiBvorQDlO0WWQjyJVGKBcJXz3OtyQ2u8'))
        self.assertFalse(cc.hash_needs_update('$5$rounds=3000$fS9iazEwTKi7QPW4$VasgBC8FqlOvD7x2HhABaMXCTh9jwHclPA9j5YQdns.'))
        self.assertTrue(cc.hash_needs_update('$5$rounds=3001$QlFHHifXvpFX4PLs$/0ekt7lSs/lOikSerQ0M/1porEHxYq7W/2hdFpxA3fA'))

    def test_30_nonstring_hash(self):
        warnings.filterwarnings('ignore', ".*needs_update.*'scheme' keyword is deprecated.*")
        cc = CryptContext(['des_crypt'])
        for hash, kwds in [
         (
          None, {}),
         (
          None, {'scheme': 'des_crypt'}),
         (
          1, {}),
         (
          (), {})]:
            self.assertRaises(TypeError, cc.hash_needs_update, hash, **kwds)

        cc2 = CryptContext(['mysql323'])
        self.assertRaises(TypeError, cc2.hash_needs_update, None)
        return


class dummy_2(uh.StaticHandler):
    name = 'dummy_2'


class LazyCryptContextTest(TestCase):
    descriptionPrefix = 'LazyCryptContext'

    def setUp(self):
        TestCase.setUp(self)
        unload_handler_name('dummy_2')
        self.addCleanup(unload_handler_name, 'dummy_2')
        warnings.filterwarnings('ignore', 'CryptContext\\(\\)\\.replace\\(\\) has been deprecated')
        warnings.filterwarnings('ignore', '.*(CryptPolicy|context\\.policy).*(has|have) been deprecated.*')

    def test_kwd_constructor(self):
        self.assertFalse(has_crypt_handler('dummy_2'))
        register_crypt_handler_path('dummy_2', 'passlib.tests.test_context')
        cc = LazyCryptContext(iter(['dummy_2', 'des_crypt']), deprecated=['des_crypt'])
        self.assertFalse(has_crypt_handler('dummy_2', True))
        self.assertTrue(cc.policy.handler_is_deprecated('des_crypt'))
        self.assertEqual(cc.policy.schemes(), ['dummy_2', 'des_crypt'])
        self.assertTrue(has_crypt_handler('dummy_2', True))

    def test_callable_constructor(self):
        self.assertFalse(has_crypt_handler('dummy_2'))
        register_crypt_handler_path('dummy_2', 'passlib.tests.test_context')

        def create_policy(flag=False):
            self.assertTrue(flag)
            return CryptPolicy(schemes=iter(['dummy_2', 'des_crypt']), deprecated=['des_crypt'])

        cc = LazyCryptContext(create_policy=create_policy, flag=True)
        self.assertFalse(has_crypt_handler('dummy_2', True))
        self.assertTrue(cc.policy.handler_is_deprecated('des_crypt'))
        self.assertEqual(cc.policy.schemes(), ['dummy_2', 'des_crypt'])
        self.assertTrue(has_crypt_handler('dummy_2', True))