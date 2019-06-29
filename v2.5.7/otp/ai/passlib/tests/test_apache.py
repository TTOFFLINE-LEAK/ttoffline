from __future__ import with_statement
from logging import getLogger
import os
from otp.ai.passlib import apache
from otp.ai.passlib.exc import MissingBackendError
from otp.ai.passlib.utils.compat import irange
from otp.ai.passlib.tests.utils import TestCase, get_file, set_file, ensure_mtime_changed
from otp.ai.passlib.utils.compat import u
from otp.ai.passlib.utils import to_bytes
log = getLogger(__name__)

def backdate_file_mtime(path, offset=10):
    atime = os.path.getatime(path)
    mtime = os.path.getmtime(path) - offset
    os.utime(path, (atime, mtime))


class HtpasswdFileTest(TestCase):
    descriptionPrefix = 'HtpasswdFile'
    sample_01 = 'user2:2CHkkwa2AtqGs\nuser3:{SHA}3ipNV1GrBtxPmHFC21fCbVCSXIo=\nuser4:pass4\nuser1:$apr1$t4tc7jTh$GPIWVUo8sQKJlUdV8V5vu0\n'
    sample_02 = 'user3:{SHA}3ipNV1GrBtxPmHFC21fCbVCSXIo=\nuser4:pass4\n'
    sample_03 = 'user2:pass2x\nuser3:{SHA}3ipNV1GrBtxPmHFC21fCbVCSXIo=\nuser4:pass4\nuser1:$apr1$t4tc7jTh$GPIWVUo8sQKJlUdV8V5vu0\nuser5:pass5\n'
    sample_04_utf8 = 'user\xc3\xa6:2CHkkwa2AtqGs\n'
    sample_04_latin1 = 'user\xe6:2CHkkwa2AtqGs\n'
    sample_dup = 'user1:pass1\nuser1:pass2\n'
    sample_05 = 'user2:2CHkkwa2AtqGs\nuser3:{SHA}3ipNV1GrBtxPmHFC21fCbVCSXIo=\nuser4:pass4\nuser1:$apr1$t4tc7jTh$GPIWVUo8sQKJlUdV8V5vu0\nuser5:$2a$12$yktDxraxijBZ360orOyCOePFGhuis/umyPNJoL5EbsLk.s6SWdrRO\nuser6:$5$rounds=110000$cCRp/xUUGVgwR4aP$p0.QKFS5qLNRqw1/47lXYiAcgIjJK.WjCO8nrEKuUK.\n'

    def test_00_constructor_autoload(self):
        path = self.mktemp()
        set_file(path, self.sample_01)
        ht = apache.HtpasswdFile(path)
        self.assertEqual(ht.to_string(), self.sample_01)
        self.assertEqual(ht.path, path)
        self.assertTrue(ht.mtime)
        ht.path = path + 'x'
        self.assertEqual(ht.path, path + 'x')
        self.assertFalse(ht.mtime)
        ht = apache.HtpasswdFile(path, new=True)
        self.assertEqual(ht.to_string(), '')
        self.assertEqual(ht.path, path)
        self.assertFalse(ht.mtime)
        with self.assertWarningList('``autoload=False`` is deprecated'):
            ht = apache.HtpasswdFile(path, autoload=False)
        self.assertEqual(ht.to_string(), '')
        self.assertEqual(ht.path, path)
        self.assertFalse(ht.mtime)
        os.remove(path)
        self.assertRaises(IOError, apache.HtpasswdFile, path)

    def test_00_from_path(self):
        path = self.mktemp()
        set_file(path, self.sample_01)
        ht = apache.HtpasswdFile.from_path(path)
        self.assertEqual(ht.to_string(), self.sample_01)
        self.assertEqual(ht.path, None)
        self.assertFalse(ht.mtime)
        return

    def test_01_delete(self):
        ht = apache.HtpasswdFile.from_string(self.sample_01)
        self.assertTrue(ht.delete('user1'))
        self.assertTrue(ht.delete('user2'))
        self.assertFalse(ht.delete('user5'))
        self.assertEqual(ht.to_string(), self.sample_02)
        self.assertRaises(ValueError, ht.delete, 'user:')

    def test_01_delete_autosave(self):
        path = self.mktemp()
        sample = 'user1:pass1\nuser2:pass2\n'
        set_file(path, sample)
        ht = apache.HtpasswdFile(path)
        ht.delete('user1')
        self.assertEqual(get_file(path), sample)
        ht = apache.HtpasswdFile(path, autosave=True)
        ht.delete('user1')
        self.assertEqual(get_file(path), 'user2:pass2\n')

    def test_02_set_password(self):
        ht = apache.HtpasswdFile.from_string(self.sample_01, default_scheme='plaintext')
        self.assertTrue(ht.set_password('user2', 'pass2x'))
        self.assertFalse(ht.set_password('user5', 'pass5'))
        self.assertEqual(ht.to_string(), self.sample_03)
        with self.assertWarningList('``default`` is deprecated'):
            ht = apache.HtpasswdFile.from_string(self.sample_01, default='plaintext')
        self.assertTrue(ht.set_password('user2', 'pass2x'))
        self.assertFalse(ht.set_password('user5', 'pass5'))
        self.assertEqual(ht.to_string(), self.sample_03)
        self.assertRaises(ValueError, ht.set_password, 'user:', 'pass')
        with self.assertWarningList('update\\(\\) is deprecated'):
            ht.update('user2', 'test')
        self.assertTrue(ht.check_password('user2', 'test'))

    def test_02_set_password_autosave(self):
        path = self.mktemp()
        sample = 'user1:pass1\n'
        set_file(path, sample)
        ht = apache.HtpasswdFile(path)
        ht.set_password('user1', 'pass2')
        self.assertEqual(get_file(path), sample)
        ht = apache.HtpasswdFile(path, default_scheme='plaintext', autosave=True)
        ht.set_password('user1', 'pass2')
        self.assertEqual(get_file(path), 'user1:pass2\n')

    def test_02_set_password_default_scheme(self):

        def check(scheme):
            ht = apache.HtpasswdFile(default_scheme=scheme)
            ht.set_password('user1', 'pass1')
            return ht.context.identify(ht.get_hash('user1'))

        self.assertEqual(check('sha256_crypt'), 'sha256_crypt')
        self.assertEqual(check('des_crypt'), 'des_crypt')
        self.assertRaises(KeyError, check, 'xxx')
        self.assertEqual(check('portable'), apache.htpasswd_defaults['portable'])
        self.assertEqual(check('portable_apache_22'), apache.htpasswd_defaults['portable_apache_22'])
        self.assertEqual(check('host_apache_22'), apache.htpasswd_defaults['host_apache_22'])
        self.assertEqual(check(None), apache.htpasswd_defaults['portable_apache_22'])
        return

    def test_03_users(self):
        ht = apache.HtpasswdFile.from_string(self.sample_01)
        ht.set_password('user5', 'pass5')
        ht.delete('user3')
        ht.set_password('user3', 'pass3')
        self.assertEqual(sorted(ht.users()), ['user1', 'user2', 'user3', 'user4', 'user5'])

    def test_04_check_password(self):
        ht = apache.HtpasswdFile.from_string(self.sample_05)
        self.assertRaises(TypeError, ht.check_password, 1, 'pass9')
        self.assertTrue(ht.check_password('user9', 'pass9') is None)
        for i in irange(1, 7):
            i = str(i)
            try:
                self.assertTrue(ht.check_password('user' + i, 'pass' + i))
                self.assertTrue(ht.check_password('user' + i, 'pass9') is False)
            except MissingBackendError:
                if i == '5':
                    continue
                raise

        self.assertRaises(ValueError, ht.check_password, 'user:', 'pass')
        with self.assertWarningList(['verify\\(\\) is deprecated'] * 2):
            self.assertTrue(ht.verify('user1', 'pass1'))
            self.assertFalse(ht.verify('user1', 'pass2'))
        return

    def test_05_load(self):
        path = self.mktemp()
        set_file(path, '')
        backdate_file_mtime(path, 5)
        ha = apache.HtpasswdFile(path, default_scheme='plaintext')
        self.assertEqual(ha.to_string(), '')
        ha.set_password('user1', 'pass1')
        ha.load_if_changed()
        self.assertEqual(ha.to_string(), 'user1:pass1\n')
        set_file(path, self.sample_01)
        ha.load_if_changed()
        self.assertEqual(ha.to_string(), self.sample_01)
        ha.set_password('user5', 'pass5')
        ha.load()
        self.assertEqual(ha.to_string(), self.sample_01)
        hb = apache.HtpasswdFile()
        self.assertRaises(RuntimeError, hb.load)
        self.assertRaises(RuntimeError, hb.load_if_changed)
        set_file(path, self.sample_dup)
        hc = apache.HtpasswdFile()
        hc.load(path)
        self.assertTrue(hc.check_password('user1', 'pass1'))

    def test_06_save(self):
        path = self.mktemp()
        set_file(path, self.sample_01)
        ht = apache.HtpasswdFile(path)
        ht.delete('user1')
        ht.delete('user2')
        ht.save()
        self.assertEqual(get_file(path), self.sample_02)
        hb = apache.HtpasswdFile(default_scheme='plaintext')
        hb.set_password('user1', 'pass1')
        self.assertRaises(RuntimeError, hb.save)
        hb.save(path)
        self.assertEqual(get_file(path), 'user1:pass1\n')

    def test_07_encodings(self):
        self.assertRaises(ValueError, apache.HtpasswdFile, encoding='utf-16')
        ht = apache.HtpasswdFile.from_string(self.sample_04_utf8, encoding='utf-8', return_unicode=True)
        self.assertEqual(ht.users(), [u('user\\u00e6')])
        with self.assertWarningList('``encoding=None`` is deprecated'):
            ht = apache.HtpasswdFile.from_string(self.sample_04_utf8, encoding=None)
        self.assertEqual(ht.users(), ['user\xc3\xa6'])
        ht = apache.HtpasswdFile.from_string(self.sample_04_latin1, encoding='latin-1', return_unicode=True)
        self.assertEqual(ht.users(), [u('user\\u00e6')])
        return

    def test_08_get_hash(self):
        ht = apache.HtpasswdFile.from_string(self.sample_01)
        self.assertEqual(ht.get_hash('user3'), '{SHA}3ipNV1GrBtxPmHFC21fCbVCSXIo=')
        self.assertEqual(ht.get_hash('user4'), 'pass4')
        self.assertEqual(ht.get_hash('user5'), None)
        with self.assertWarningList('find\\(\\) is deprecated'):
            self.assertEqual(ht.find('user4'), 'pass4')
        return

    def test_09_to_string(self):
        ht = apache.HtpasswdFile.from_string(self.sample_01)
        self.assertEqual(ht.to_string(), self.sample_01)
        ht = apache.HtpasswdFile()
        self.assertEqual(ht.to_string(), '')

    def test_10_repr(self):
        ht = apache.HtpasswdFile('fakepath', autosave=True, new=True, encoding='latin-1')
        repr(ht)

    def test_11_malformed(self):
        self.assertRaises(ValueError, apache.HtpasswdFile.from_string, 'realm:user1:pass1\n')
        self.assertRaises(ValueError, apache.HtpasswdFile.from_string, 'pass1\n')

    def test_12_from_string(self):
        self.assertRaises(TypeError, apache.HtpasswdFile.from_string, '', path=None)
        return

    def test_13_whitespace(self):
        source = to_bytes('\nuser2:pass2\nuser4:pass4\nuser7:pass7\r\n \t \nuser1:pass1\n # legacy users\n#user6:pass6\nuser5:pass5\n\n')
        ht = apache.HtpasswdFile.from_string(source)
        self.assertEqual(sorted(ht.users()), ['user1', 'user2', 'user4', 'user5', 'user7'])
        ht.set_hash('user4', 'althash4')
        self.assertEqual(sorted(ht.users()), ['user1', 'user2', 'user4', 'user5', 'user7'])
        ht.set_hash('user6', 'althash6')
        self.assertEqual(sorted(ht.users()), ['user1', 'user2', 'user4', 'user5', 'user6', 'user7'])
        ht.delete('user7')
        self.assertEqual(sorted(ht.users()), ['user1', 'user2', 'user4', 'user5', 'user6'])
        target = to_bytes('\nuser2:pass2\nuser4:althash4\n \t \nuser1:pass1\n # legacy users\n#user6:pass6\nuser5:pass5\nuser6:althash6\n')
        self.assertEqual(ht.to_string(), target)


class HtdigestFileTest(TestCase):
    descriptionPrefix = 'HtdigestFile'
    sample_01 = 'user2:realm:549d2a5f4659ab39a80dac99e159ab19\nuser3:realm:a500bb8c02f6a9170ae46af10c898744\nuser4:realm:ab7b5d5f28ccc7666315f508c7358519\nuser1:realm:2a6cf53e7d8f8cf39d946dc880b14128\n'
    sample_02 = 'user3:realm:a500bb8c02f6a9170ae46af10c898744\nuser4:realm:ab7b5d5f28ccc7666315f508c7358519\n'
    sample_03 = 'user2:realm:5ba6d8328943c23c64b50f8b29566059\nuser3:realm:a500bb8c02f6a9170ae46af10c898744\nuser4:realm:ab7b5d5f28ccc7666315f508c7358519\nuser1:realm:2a6cf53e7d8f8cf39d946dc880b14128\nuser5:realm:03c55fdc6bf71552356ad401bdb9af19\n'
    sample_04_utf8 = 'user\xc3\xa6:realm\xc3\xa6:549d2a5f4659ab39a80dac99e159ab19\n'
    sample_04_latin1 = 'user\xe6:realm\xe6:549d2a5f4659ab39a80dac99e159ab19\n'

    def test_00_constructor_autoload(self):
        path = self.mktemp()
        set_file(path, self.sample_01)
        ht = apache.HtdigestFile(path)
        self.assertEqual(ht.to_string(), self.sample_01)
        ht = apache.HtdigestFile(path, new=True)
        self.assertEqual(ht.to_string(), '')
        os.remove(path)
        self.assertRaises(IOError, apache.HtdigestFile, path)

    def test_01_delete(self):
        ht = apache.HtdigestFile.from_string(self.sample_01)
        self.assertTrue(ht.delete('user1', 'realm'))
        self.assertTrue(ht.delete('user2', 'realm'))
        self.assertFalse(ht.delete('user5', 'realm'))
        self.assertFalse(ht.delete('user3', 'realm5'))
        self.assertEqual(ht.to_string(), self.sample_02)
        self.assertRaises(ValueError, ht.delete, 'user:', 'realm')
        self.assertRaises(ValueError, ht.delete, 'user', 'realm:')

    def test_01_delete_autosave(self):
        path = self.mktemp()
        set_file(path, self.sample_01)
        ht = apache.HtdigestFile(path)
        self.assertTrue(ht.delete('user1', 'realm'))
        self.assertFalse(ht.delete('user3', 'realm5'))
        self.assertFalse(ht.delete('user5', 'realm'))
        self.assertEqual(get_file(path), self.sample_01)
        ht.autosave = True
        self.assertTrue(ht.delete('user2', 'realm'))
        self.assertEqual(get_file(path), self.sample_02)

    def test_02_set_password(self):
        ht = apache.HtdigestFile.from_string(self.sample_01)
        self.assertTrue(ht.set_password('user2', 'realm', 'pass2x'))
        self.assertFalse(ht.set_password('user5', 'realm', 'pass5'))
        self.assertEqual(ht.to_string(), self.sample_03)
        self.assertRaises(TypeError, ht.set_password, 'user2', 'pass3')
        ht.default_realm = 'realm2'
        ht.set_password('user2', 'pass3')
        ht.check_password('user2', 'realm2', 'pass3')
        self.assertRaises(ValueError, ht.set_password, 'user:', 'realm', 'pass')
        self.assertRaises(ValueError, ht.set_password, 'u' * 256, 'realm', 'pass')
        self.assertRaises(ValueError, ht.set_password, 'user', 'realm:', 'pass')
        self.assertRaises(ValueError, ht.set_password, 'user', 'r' * 256, 'pass')
        with self.assertWarningList('update\\(\\) is deprecated'):
            ht.update('user2', 'realm2', 'test')
        self.assertTrue(ht.check_password('user2', 'test'))

    def test_03_users(self):
        ht = apache.HtdigestFile.from_string(self.sample_01)
        ht.set_password('user5', 'realm', 'pass5')
        ht.delete('user3', 'realm')
        ht.set_password('user3', 'realm', 'pass3')
        self.assertEqual(sorted(ht.users('realm')), ['user1', 'user2', 'user3', 'user4', 'user5'])
        self.assertRaises(TypeError, ht.users, 1)

    def test_04_check_password(self):
        ht = apache.HtdigestFile.from_string(self.sample_01)
        self.assertRaises(TypeError, ht.check_password, 1, 'realm', 'pass5')
        self.assertRaises(TypeError, ht.check_password, 'user', 1, 'pass5')
        self.assertIs(ht.check_password('user5', 'realm', 'pass5'), None)
        for i in irange(1, 5):
            i = str(i)
            self.assertTrue(ht.check_password('user' + i, 'realm', 'pass' + i))
            self.assertIs(ht.check_password('user' + i, 'realm', 'pass5'), False)

        self.assertRaises(TypeError, ht.check_password, 'user5', 'pass5')
        ht.default_realm = 'realm'
        self.assertTrue(ht.check_password('user1', 'pass1'))
        self.assertIs(ht.check_password('user5', 'pass5'), None)
        with self.assertWarningList(['verify\\(\\) is deprecated'] * 2):
            self.assertTrue(ht.verify('user1', 'realm', 'pass1'))
            self.assertFalse(ht.verify('user1', 'realm', 'pass2'))
        self.assertRaises(ValueError, ht.check_password, 'user:', 'realm', 'pass')
        return

    def test_05_load(self):
        path = self.mktemp()
        set_file(path, '')
        backdate_file_mtime(path, 5)
        ha = apache.HtdigestFile(path)
        self.assertEqual(ha.to_string(), '')
        ha.set_password('user1', 'realm', 'pass1')
        ha.load_if_changed()
        self.assertEqual(ha.to_string(), 'user1:realm:2a6cf53e7d8f8cf39d946dc880b14128\n')
        set_file(path, self.sample_01)
        ha.load_if_changed()
        self.assertEqual(ha.to_string(), self.sample_01)
        ha.set_password('user5', 'realm', 'pass5')
        ha.load()
        self.assertEqual(ha.to_string(), self.sample_01)
        hb = apache.HtdigestFile()
        self.assertRaises(RuntimeError, hb.load)
        self.assertRaises(RuntimeError, hb.load_if_changed)
        hc = apache.HtdigestFile()
        hc.load(path)
        self.assertEqual(hc.to_string(), self.sample_01)
        ensure_mtime_changed(path)
        set_file(path, '')
        with self.assertWarningList('load\\(force=False\\) is deprecated'):
            ha.load(force=False)
        self.assertEqual(ha.to_string(), '')

    def test_06_save(self):
        path = self.mktemp()
        set_file(path, self.sample_01)
        ht = apache.HtdigestFile(path)
        ht.delete('user1', 'realm')
        ht.delete('user2', 'realm')
        ht.save()
        self.assertEqual(get_file(path), self.sample_02)
        hb = apache.HtdigestFile()
        hb.set_password('user1', 'realm', 'pass1')
        self.assertRaises(RuntimeError, hb.save)
        hb.save(path)
        self.assertEqual(get_file(path), hb.to_string())

    def test_07_realms(self):
        ht = apache.HtdigestFile.from_string(self.sample_01)
        self.assertEqual(ht.delete_realm('x'), 0)
        self.assertEqual(ht.realms(), ['realm'])
        self.assertEqual(ht.delete_realm('realm'), 4)
        self.assertEqual(ht.realms(), [])
        self.assertEqual(ht.to_string(), '')

    def test_08_get_hash(self):
        ht = apache.HtdigestFile.from_string(self.sample_01)
        self.assertEqual(ht.get_hash('user3', 'realm'), 'a500bb8c02f6a9170ae46af10c898744')
        self.assertEqual(ht.get_hash('user4', 'realm'), 'ab7b5d5f28ccc7666315f508c7358519')
        self.assertEqual(ht.get_hash('user5', 'realm'), None)
        with self.assertWarningList('find\\(\\) is deprecated'):
            self.assertEqual(ht.find('user4', 'realm'), 'ab7b5d5f28ccc7666315f508c7358519')
        return

    def test_09_encodings(self):
        self.assertRaises(ValueError, apache.HtdigestFile, encoding='utf-16')
        ht = apache.HtdigestFile.from_string(self.sample_04_utf8, encoding='utf-8', return_unicode=True)
        self.assertEqual(ht.realms(), [u('realm\\u00e6')])
        self.assertEqual(ht.users(u('realm\\u00e6')), [u('user\\u00e6')])
        ht = apache.HtdigestFile.from_string(self.sample_04_latin1, encoding='latin-1', return_unicode=True)
        self.assertEqual(ht.realms(), [u('realm\\u00e6')])
        self.assertEqual(ht.users(u('realm\\u00e6')), [u('user\\u00e6')])

    def test_10_to_string(self):
        ht = apache.HtdigestFile.from_string(self.sample_01)
        self.assertEqual(ht.to_string(), self.sample_01)
        ht = apache.HtdigestFile()
        self.assertEqual(ht.to_string(), '')

    def test_11_malformed(self):
        self.assertRaises(ValueError, apache.HtdigestFile.from_string, 'realm:user1:pass1:other\n')
        self.assertRaises(ValueError, apache.HtdigestFile.from_string, 'user1:pass1\n')