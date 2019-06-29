import logging
log = logging.getLogger(__name__)
import warnings
from otp.ai.passlib import hash
from otp.ai.passlib.utils.compat import u
from otp.ai.passlib.tests.utils import TestCase, HandlerCase
from otp.ai.passlib.tests.test_handlers import UPASS_WAV

class ldap_pbkdf2_test(TestCase):

    def test_wrappers(self):
        self.assertTrue(hash.ldap_pbkdf2_sha1.verify('password', '{PBKDF2}1212$OB.dtnSEXZK8U5cgxU/GYQ$y5LKPOplRmok7CZp/aqVDVg8zGI'))
        self.assertTrue(hash.ldap_pbkdf2_sha256.verify('password', '{PBKDF2-SHA256}1212$4vjV83LKPjQzk31VI4E0Vw$hsYF68OiOUPdDZ1Fg.fJPeq1h/gXXY7acBp9/6c.tmQ'))
        self.assertTrue(hash.ldap_pbkdf2_sha512.verify('password', '{PBKDF2-SHA512}1212$RHY0Fr3IDMSVO/RSZyb5ow$eNLfBK.eVozomMr.1gYa17k9B7KIK25NOEshvhrSX.esqY3s.FvWZViXz4KoLlQI.BzY/YTNJOiKc5gBYFYGww'))


class atlassian_pbkdf2_sha1_test(HandlerCase):
    handler = hash.atlassian_pbkdf2_sha1
    known_correct_hashes = [
     ('admin', '{PKCS5S2}c4xaeTQM0lUieMS3V5voiexyX9XhqC2dBd5ecVy60IPksHChwoTAVYFrhsgoq8/p'),
     (
      UPASS_WAV,
      '{PKCS5S2}cE9Yq6Am5tQGdHSHhky2XLeOnURwzaLBG2sur7FHKpvy2u0qDn6GcVGRjlmJoIUy')]
    known_malformed_hashes = [
     '{PKCS5S2}c4xaeTQM0lUieMS3V5voiexyX9XhqC2dBd5ecVy!0IPksHChwoTAVYFrhsgoq8/p{PKCS5S2}c4xaeTQM0lUieMS3V5voiexyX9XhqC2dBd5ecVy60IPksHChwoTAVYFrhsgoq8/{PKCS5S2}c4xaeTQM0lUieMS3V5voiexyX9XhqC2dBd5ecVy60IPksHChwoTAVYFrhsgoq8/=']


class pbkdf2_sha1_test(HandlerCase):
    handler = hash.pbkdf2_sha1
    known_correct_hashes = [
     ('password', '$pbkdf2$1212$OB.dtnSEXZK8U5cgxU/GYQ$y5LKPOplRmok7CZp/aqVDVg8zGI'),
     (
      UPASS_WAV,
      '$pbkdf2$1212$THDqatpidANpadlLeTeOEg$HV3oi1k5C5LQCgG1BMOL.BX4YZc')]
    known_malformed_hashes = [
     '$pbkdf2$01212$THDqatpidANpadlLeTeOEg$HV3oi1k5C5LQCgG1BMOL.BX4YZc',
     '$pbkdf2$$THDqatpidANpadlLeTeOEg$HV3oi1k5C5LQCgG1BMOL.BX4YZc',
     '$pbkdf2$1212$THDqatpidANpadlLeTeOEg$HV3oi1k5C5LQCgG1BMOL.BX4YZc$']


class pbkdf2_sha256_test(HandlerCase):
    handler = hash.pbkdf2_sha256
    known_correct_hashes = [
     ('password', '$pbkdf2-sha256$1212$4vjV83LKPjQzk31VI4E0Vw$hsYF68OiOUPdDZ1Fg.fJPeq1h/gXXY7acBp9/6c.tmQ'),
     (
      UPASS_WAV,
      '$pbkdf2-sha256$1212$3SABFJGDtyhrQMVt1uABPw$WyaUoqCLgvz97s523nF4iuOqZNbp5Nt8do/cuaa7AiI')]


class pbkdf2_sha512_test(HandlerCase):
    handler = hash.pbkdf2_sha512
    known_correct_hashes = [
     ('password', '$pbkdf2-sha512$1212$RHY0Fr3IDMSVO/RSZyb5ow$eNLfBK.eVozomMr.1gYa17k9B7KIK25NOEshvhrSX.esqY3s.FvWZViXz4KoLlQI.BzY/YTNJOiKc5gBYFYGww'),
     (
      UPASS_WAV,
      '$pbkdf2-sha512$1212$KkbvoKGsAIcF8IslDR6skQ$8be/PRmd88Ps8fmPowCJttH9G3vgxpG.Krjt3KT.NP6cKJ0V4Prarqf.HBwz0dCkJ6xgWnSj2ynXSV7MlvMa8Q')]


class cta_pbkdf2_sha1_test(HandlerCase):
    handler = hash.cta_pbkdf2_sha1
    known_correct_hashes = [
     (
      u('hashy the \\N{SNOWMAN}'), '$p5k2$1000$ZxK4ZBJCfQg=$jJZVscWtO--p1-xIZl6jhO2LKR0='),
     ('password', '$p5k2$1$$h1TDLGSw9ST8UMAPeIE13i0t12c='),
     (
      UPASS_WAV,
      '$p5k2$4321$OTg3NjU0MzIx$jINJrSvZ3LXeIbUdrJkRpN62_WQ=')]


class dlitz_pbkdf2_sha1_test(HandlerCase):
    handler = hash.dlitz_pbkdf2_sha1
    known_correct_hashes = [
     ('cloadm', '$p5k2$$exec$r1EWMCMk7Rlv3L/RNcFXviDefYa0hlql'),
     ('gnu', '$p5k2$c$u9HvcT4d$Sd1gwSVCLZYAuqZ25piRnbBEoAesaa/g'),
     ('dcl', '$p5k2$d$tUsch7fU$nqDkaxMDOFBeJsTSfABsyn.PYUXilHwL'),
     ('spam', '$p5k2$3e8$H0NX9mT/$wk/sE8vv6OMKuMaqazCJYDSUhWY9YB2J'),
     (
      UPASS_WAV,
      '$p5k2$$KosHgqNo$9mjN8gqjt02hDoP0c2J0ABtLIwtot8cQ')]


class grub_pbkdf2_sha512_test(HandlerCase):
    handler = hash.grub_pbkdf2_sha512
    known_correct_hashes = [
     (
      UPASS_WAV,
      'grub.pbkdf2.sha512.10000.BCAC1CEC5E4341C8C511C5297FA877BE91C2817B32A35A3ECF5CA6B8B257F751.6968526A2A5B1AEEE0A29A9E057336B48D388FFB3F600233237223C2104DE1752CEC35B0DD1ED49563398A282C0F471099C2803FBA47C7919CABC43192C68F60'),
     ('toomanysecrets', 'grub.pbkdf2.sha512.10000.9B436BB6978682363D5C449BBEAB322676946C632208BC1294D51F47174A9A3B04A7E4785986CD4EA7470FAB8FE9F6BD522D1FC6C51109A8596FB7AD487C4493.0FE5EF169AFFCB67D86E2581B1E251D88C777B98BA2D3256ECC9F765D84956FC5CA5C4B6FD711AA285F0A04DCF4634083F9A20F4B6F339A52FBD6BED618E527B')]


class scram_test(HandlerCase):
    handler = hash.scram
    known_correct_hashes = [
     ('pencil', '$scram$4096$QSXCR.Q6sek8bf92$sha-1=HZbuOlKbWl.eR8AfIposuKbhX30'),
     ('pencil', '$scram$4096$QSXCR.Q6sek8bf92$sha-1=HZbuOlKbWl.eR8AfIposuKbhX30,sha-256=qXUXrlcvnaxxWG00DdRgVioR2gnUpuX5r.3EZ1rdhVY,sha-512=lzgniLFcvglRLS0gt.C4gy.NurS3OIOVRAU1zZOV4P.qFiVFO2/edGQSu/kD1LwdX0SNV/KsPdHSwEl5qRTuZQ'),
     (
      u('IX \xe0'), '$scram$6400$0BojBCBE6P2/N4bQ$sha-1=YniLes.b8WFMvBhtSACZyyvxeCc'),
     (
      u('\\u2168\\u3000a\\u0300'), '$scram$6400$0BojBCBE6P2/N4bQ$sha-1=YniLes.b8WFMvBhtSACZyyvxeCc'),
     (
      u('\\u00ADIX \xe0'), '$scram$6400$0BojBCBE6P2/N4bQ$sha-1=YniLes.b8WFMvBhtSACZyyvxeCc')]
    known_malformed_hashes = [
     '$scram$04096$QSXCR.Q6sek8bf92$sha-1=HZbuOlKbWl.eR8AfIposuKbhX30',
     '$scram$409A$QSXCR.Q6sek8bf92$sha-1=HZbuOlKbWl.eR8AfIposuKbhX30',
     '$scram$4096$QSXCR.Q6sek8bf9-$sha-1=HZbuOlKbWl.eR8AfIposuKbhX30',
     '$scram$4096$QSXCR.Q6sek8bf92$sha-1=HZbuOlKbWl.eR8AfIposuKbhX3-',
     '$scram$4096$QSXCR.Q6sek8bf92',
     '$scram$4096$QSXCR.Q6sek8bf92$',
     '$scram$4096$QSXCR.Q6sek8bf92$sha-1=HZbuOlKbWl.eR8AfIposuKbhX30$',
     '$scram$4096$QSXCR.Q6sek8bf92$sha-1=HZbuOlKbWl.eR8AfIposuKbhX30sha-256=qXUXrlcvnaxxWG00DdRgVioR2gnUpuX5r.3EZ1rdhVY',
     '$scram$4096$QSXCR.Q6sek8bf92$sha-1=HZbuOlKbWl.eR8AfIposuKbhX30,shaxxx-190=HZbuOlKbWl.eR8AfIposuKbhX30',
     '$scram$4096$QSXCR.Q6sek8bf92$sha-256=HZbuOlKbWl.eR8AfIposuKbhX30',
     '$scram$4096$QSXCR.Q6sek8bf92$sha1=HZbuOlKbWl.eR8AfIposuKbhX30']

    def setUp(self):
        super(scram_test, self).setUp()
        self.require_stringprep()
        warnings.filterwarnings('ignore', 'norm_hash_name\\(\\): unknown hash')

    def test_90_algs(self):
        defaults = dict(salt='AAAAAAAAAA', rounds=1000)

        def parse(algs, **kwds):
            for k in defaults:
                kwds.setdefault(k, defaults[k])

            return self.handler(algs=algs, **kwds).algs

        self.assertEqual(parse(None, use_defaults=True), hash.scram.default_algs)
        self.assertRaises(TypeError, parse, None)
        self.assertEqual(parse('sha1'), ['sha-1'])
        self.assertEqual(parse('sha1, sha256, md5'), ['md5', 'sha-1', 'sha-256'])
        self.assertEqual(parse(['sha-1', 'sha256']), ['sha-1', 'sha-256'])
        self.assertRaises(ValueError, parse, ['sha-256'])
        self.assertRaises(ValueError, parse, algs=[], use_defaults=True)
        self.assertRaises(ValueError, parse, ['sha-1', 'shaxxx-190'])
        self.assertRaises(RuntimeError, parse, ['sha-1'], checksum={'sha-1': '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'})
        return

    def test_90_checksums(self):
        self.assertRaises(TypeError, self.handler, use_defaults=True, checksum={'sha-1': u('X') * 20})
        self.assertRaises(ValueError, self.handler, use_defaults=True, checksum={'sha-256': 'X' * 32})

    def test_91_extract_digest_info(self):
        edi = self.handler.extract_digest_info
        h = '$scram$10$AAAAAA$sha-1=AQ,bbb=Ag,ccc=Aw'
        s = '\x00\x00\x00\x00'
        self.assertEqual(edi(h, 'SHA1'), (s, 10, '\x01'))
        self.assertEqual(edi(h, 'bbb'), (s, 10, '\x02'))
        self.assertEqual(edi(h, 'ccc'), (s, 10, '\x03'))
        self.assertRaises(KeyError, edi, h, 'ddd')
        c = '$scram$10$....$sha-1,bbb,ccc'
        self.assertRaises(ValueError, edi, c, 'sha-1')
        self.assertRaises(ValueError, edi, c, 'bbb')
        self.assertRaises(ValueError, edi, c, 'ddd')

    def test_92_extract_digest_algs(self):
        eda = self.handler.extract_digest_algs
        self.assertEqual(eda('$scram$4096$QSXCR.Q6sek8bf92$sha-1=HZbuOlKbWl.eR8AfIposuKbhX30'), [
         'sha-1'])
        self.assertEqual(eda('$scram$4096$QSXCR.Q6sek8bf92$sha-1=HZbuOlKbWl.eR8AfIposuKbhX30', format='hashlib'), [
         'sha1'])
        self.assertEqual(eda('$scram$4096$QSXCR.Q6sek8bf92$sha-1=HZbuOlKbWl.eR8AfIposuKbhX30,sha-256=qXUXrlcvnaxxWG00DdRgVioR2gnUpuX5r.3EZ1rdhVY,sha-512=lzgniLFcvglRLS0gt.C4gy.NurS3OIOVRAU1zZOV4P.qFiVFO2/edGQSu/kD1LwdX0SNV/KsPdHSwEl5qRTuZQ'), [
         'sha-1', 'sha-256', 'sha-512'])

    def test_93_derive_digest(self):
        hash = self.handler.derive_digest
        s1 = '\x01\x02\x03'
        d1 = '\xb2\xfb\xab\x82[tNuPnI\x8aZZ\x19\x87\xcen\xe9\xd3'
        self.assertEqual(hash(u('\\u2168'), s1, 1000, 'sha-1'), d1)
        self.assertEqual(hash('\xe2\x85\xa8', s1, 1000, 'SHA-1'), d1)
        self.assertEqual(hash(u('IX'), s1, 1000, 'sha1'), d1)
        self.assertEqual(hash('IX', s1, 1000, 'SHA1'), d1)
        self.assertEqual(hash('IX', s1, 1000, 'md5'), '3\x19\x18\xc0\x1c/\xa8\xbf\xe4\xa3\xc2\x8eM\xe8od')
        self.assertRaises(ValueError, hash, 'IX', s1, 1000, 'sha-666')
        self.assertRaises(ValueError, hash, 'IX', s1, 0, 'sha-1')
        self.assertEqual(hash(u('IX'), s1.decode('latin-1'), 1000, 'sha1'), d1)

    def test_94_saslprep(self):
        h = self.do_encrypt(u('I\\u00ADX'))
        self.assertTrue(self.do_verify(u('IX'), h))
        self.assertTrue(self.do_verify(u('\\u2168'), h))
        h = self.do_encrypt(u('\xf3'))
        self.assertTrue(self.do_verify(u('o\\u0301'), h))
        self.assertTrue(self.do_verify(u('\\u200Do\\u0301'), h))
        self.assertRaises(ValueError, self.do_encrypt, u('\\uFDD0'))
        self.assertRaises(ValueError, self.do_verify, u('\\uFDD0'), h)

    def test_94_using_w_default_algs(self, param='default_algs'):
        handler = self.handler
        orig = list(handler.default_algs)
        subcls = handler.using(**{param: 'sha1,md5'})
        self.assertEqual(handler.default_algs, orig)
        self.assertEqual(subcls.default_algs, ['md5', 'sha-1'])
        h1 = subcls.hash('dummy')
        self.assertEqual(handler.extract_digest_algs(h1), ['md5', 'sha-1'])

    def test_94_using_w_algs(self):
        self.test_94_using_w_default_algs(param='algs')

    def test_94_needs_update_algs(self):
        handler1 = self.handler.using(algs='sha1,md5')
        h1 = handler1.hash('dummy')
        self.assertFalse(handler1.needs_update(h1))
        handler2 = handler1.using(algs='sha1')
        self.assertFalse(handler2.needs_update(h1))
        handler3 = handler1.using(algs='sha1,sha256')
        self.assertTrue(handler3.needs_update(h1))

    def test_95_context_algs(self):
        handler = self.handler
        from otp.ai.passlib.context import CryptContext
        c1 = CryptContext(['scram'], scram__algs='sha1,md5')
        h = c1.hash('dummy')
        self.assertEqual(handler.extract_digest_algs(h), ['md5', 'sha-1'])
        self.assertFalse(c1.needs_update(h))
        c2 = c1.copy(scram__algs='sha1')
        self.assertFalse(c2.needs_update(h))
        c2 = c1.copy(scram__algs='sha1,sha256')
        self.assertTrue(c2.needs_update(h))

    def test_96_full_verify(self):

        def vpart(s, h):
            return self.handler.verify(s, h)

        def vfull(s, h):
            return self.handler.verify(s, h, full=True)

        h = '$scram$4096$QSXCR.Q6sek8bf92$sha-1=HZbuOlKbWl.eR8AfIposuKbhX30,sha-256=qXUXrlcvnaxxWG00DdRgVioR2gnUpuX5r.3EZ1rdhVY,sha-512=lzgniLFcvglRLS0gt.C4gy.NurS3OIOVRAU1zZOV4P.qFiVFO2/edGQSu/kD1LwdX0SNV/KsPdHSwEl5qRTuZQ'
        self.assertTrue(vfull('pencil', h))
        self.assertFalse(vfull('tape', h))
        h = '$scram$4096$QSXCR.Q6sek8bf92$sha-1=HZbuOlKbWl.eR8AfIposuKbhX30,sha-256=qXUXrlcvnaxxWG00DdRgVioR2gnUpuX5r.3EZ1rdhV,sha-512=lzgniLFcvglRLS0gt.C4gy.NurS3OIOVRAU1zZOV4P.qFiVFO2/edGQSu/kD1LwdX0SNV/KsPdHSwEl5qRTuZQ'
        self.assertRaises(ValueError, vfull, 'pencil', h)
        h = '$scram$4096$QSXCR.Q6sek8bf92$sha-1=HZbuOlKbWl.eR8AfIposuKbhX30,sha-256=qXUXrlcvnaxxWG00DdRgVioR2gnUpuX5r.3EZ1rdhVYa,sha-512=lzgniLFcvglRLS0gt.C4gy.NurS3OIOVRAU1zZOV4P.qFiVFO2/edGQSu/kD1LwdX0SNV/KsPdHSwEl5qRTuZQ'
        self.assertRaises(ValueError, vfull, 'pencil', h)
        h = '$scram$4096$QSXCR.Q6sek8bf92$sha-1=HZbuOlKbWl.eR8AfIposuKbhX30,sha-256=R7RJDWIbeKRTFwhE9oxh04kab0CllrQ3kCcpZUcligc,sha-512=lzgniLFcvglRLS0gt.C4gy.NurS3OIOVRAU1zZOV4P.qFiVFO2/edGQSu/kD1LwdX0SNV/KsPdHSwEl5qRTuZQ'
        self.assertTrue(vpart('tape', h))
        self.assertFalse(vpart('pencil', h))
        self.assertRaises(ValueError, vfull, 'pencil', h)
        self.assertRaises(ValueError, vfull, 'tape', h)