from __future__ import absolute_import, division, print_function
import logging
log = logging.getLogger(__name__)
from otp.ai.passlib import hash, exc
from otp.ai.passlib.utils.compat import u
from .utils import UserHandlerMixin, HandlerCase, repeat_string
from .test_handlers import UPASS_TABLE
__all__ = [
 'cisco_pix_test',
 'cisco_asa_test',
 'cisco_type7_test']

class _PixAsaSharedTest(UserHandlerMixin, HandlerCase):
    __unittest_skip = True
    requires_user = False
    pix_asa_shared_hashes = [
     (('cisco', ''), '2KFQnbNIdI.2KYOU'),
     (('hsc', ''), 'YtT8/k6Np8F1yz2c'),
     (('', ''), '8Ry2YjIyt7RRXU24'),
     (('cisco', 'john'), 'hN7LzeyYjw12FSIU'),
     (('cisco', 'jack'), '7DrfeZ7cyOj/PslD'),
     (('ripper', 'alex'), 'h3mJrcH0901pqX/m'),
     (('cisco', 'cisco'), '3USUcOPFUiMCO4Jk'),
     (('cisco', 'cisco1'), '3USUcOPFUiMCO4Jk'),
     (('CscFw-ITC!', 'admcom'), 'lZt7HSIXw3.QP7.R'),
     ('cangetin', 'TynyB./ftknE77QP'),
     (('cangetin', 'rramsey'), 'jgBZqYtsWfGcUKDi'),
     (('phonehome', 'rharris'), 'zyIIMSYjiPm0L7a6'),
     (('cangetin', ''), 'TynyB./ftknE77QP'),
     (('cangetin', 'rramsey'), 'jgBZqYtsWfGcUKDi'),
     ('test1', 'TRPEas6f/aa6JSPL'),
     ('test2', 'OMT6mXmAvGyzrCtp'),
     ('test3', 'gTC7RIy1XJzagmLm'),
     ('test4', 'oWC1WRwqlBlbpf/O'),
     ('password', 'NuLKvvWGg.x9HEKO'),
     ('0123456789abcdef', '.7nfVBEIEu4KbF/1'),
     (('1234567890123456', ''), 'feCkwUGktTCAgIbD'),
     (('watag00s1am', ''), 'jMorNbK0514fadBh'),
     (('cisco1', 'cisco1'), 'jmINXNH6p1BxUppp'),
     (
      UPASS_TABLE, 'CaiIvkLMu2TOHXGT'),
     (('1234', ''), 'RLPMUQ26KL4blgFN'),
     (('01234567', ''), '0T52THgnYdV1tlOF'),
     (('01234567', '3'), '.z0dT9Alkdc7EIGS'),
     (('01234567', '36'), 'CC3Lam53t/mHhoE7'),
     (('01234567', '365'), '8xPrWpNnBdD2DzdZ'),
     (('01234567', '3333'), '.z0dT9Alkdc7EIGS'),
     (('01234567', '3636'), 'CC3Lam53t/mHhoE7'),
     (('01234567', '3653'), '8xPrWpNnBdD2DzdZ'),
     (('01234567', 'adm'), 'dfWs2qiao6KD/P2L'),
     (('01234567', 'adma'), 'dfWs2qiao6KD/P2L'),
     (('01234567', 'admad'), 'dfWs2qiao6KD/P2L'),
     (('01234567', 'user'), 'PNZ4ycbbZ0jp1.j1'),
     (('01234567', 'user1234'), 'PNZ4ycbbZ0jp1.j1'),
     (('0123456789ab', ''), 'S31BxZOGlAigndcJ'),
     (('0123456789ab', '36'), 'wFqSX91X5.YaRKsi'),
     (('0123456789ab', '365'), 'qjgo3kNgTVxExbno'),
     (('0123456789ab', '3333'), 'mcXPL/vIZcIxLUQs'),
     (('0123456789ab', '3636'), 'wFqSX91X5.YaRKsi'),
     (('0123456789ab', '3653'), 'qjgo3kNgTVxExbno'),
     (('0123456789ab', 'user'), 'f.T4BKdzdNkjxQl7'),
     (('0123456789ab', 'user1234'), 'f.T4BKdzdNkjxQl7'),
     (
      (
       u('t\xe1ble').encode('utf-8'), 'user'), 'Og8fB4NyF0m5Ed9c'),
     (
      (
       u('t\xe1ble').encode('utf-8').decode('latin-1').encode('utf-8'),
       'user'), 'cMvFC2XVBmK/68yB')]

    def test_calc_digest_spoiler(self):

        def calc(secret, for_hash=False):
            return self.handler(use_defaults=for_hash)._calc_checksum(secret)

        short_secret = repeat_string('1234', self.handler.truncate_size)
        short_hash = calc(short_secret)
        long_secret = short_secret + 'X'
        long_hash = calc(long_secret)
        self.assertNotEqual(long_hash, short_hash)
        alt_long_secret = short_secret + 'Y'
        alt_long_hash = calc(alt_long_secret)
        self.assertNotEqual(alt_long_hash, short_hash)
        self.assertNotEqual(alt_long_hash, long_hash)
        calc(short_secret, for_hash=True)
        self.assertRaises(exc.PasswordSizeError, calc, long_secret, for_hash=True)
        self.assertRaises(exc.PasswordSizeError, calc, alt_long_secret, for_hash=True)


class cisco_pix_test(_PixAsaSharedTest):
    handler = hash.cisco_pix
    known_correct_hashes = _PixAsaSharedTest.pix_asa_shared_hashes + [
     (('0123456789abc', ''), 'eacOpB7vE7ZDukSF'),
     (('0123456789abc', '3'), 'ylJTd/qei66WZe3w'),
     (('0123456789abc', '36'), 'hDx8QRlUhwd6bU8N'),
     (('0123456789abc', '365'), 'vYOOtnkh1HXcMrM7'),
     (('0123456789abc', '3333'), 'ylJTd/qei66WZe3w'),
     (('0123456789abc', '3636'), 'hDx8QRlUhwd6bU8N'),
     (('0123456789abc', '3653'), 'vYOOtnkh1HXcMrM7'),
     (('0123456789abc', 'user'), 'f4/.SALxqDo59mfV'),
     (('0123456789abc', 'user1234'), 'f4/.SALxqDo59mfV'),
     (('0123456789abcd', ''), '6r8888iMxEoPdLp4'),
     (('0123456789abcd', '3'), 'f5lvmqWYj9gJqkIH'),
     (('0123456789abcd', '36'), 'OJJ1Khg5HeAYBH1c'),
     (('0123456789abcd', '365'), 'OJJ1Khg5HeAYBH1c'),
     (('0123456789abcd', '3333'), 'f5lvmqWYj9gJqkIH'),
     (('0123456789abcd', '3636'), 'OJJ1Khg5HeAYBH1c'),
     (('0123456789abcd', '3653'), 'OJJ1Khg5HeAYBH1c'),
     (('0123456789abcd', 'adm'), 'DbPLCFIkHc2SiyDk'),
     (('0123456789abcd', 'adma'), 'DbPLCFIkHc2SiyDk'),
     (('0123456789abcd', 'user'), 'WfO2UiTapPkF/FSn'),
     (('0123456789abcd', 'user1234'), 'WfO2UiTapPkF/FSn'),
     (('0123456789abcde', ''), 'al1e0XFIugTYLai3'),
     (('0123456789abcde', '3'), 'lYbwBu.f82OIApQB'),
     (('0123456789abcde', '36'), 'lYbwBu.f82OIApQB'),
     (('0123456789abcde', '365'), 'lYbwBu.f82OIApQB'),
     (('0123456789abcde', '3333'), 'lYbwBu.f82OIApQB'),
     (('0123456789abcde', '3636'), 'lYbwBu.f82OIApQB'),
     (('0123456789abcde', '3653'), 'lYbwBu.f82OIApQB'),
     (('0123456789abcde', 'adm'), 'KgKx1UQvdR/09i9u'),
     (('0123456789abcde', 'adma'), 'KgKx1UQvdR/09i9u'),
     (('0123456789abcde', 'user'), 'qLopkenJ4WBqxaZN'),
     (('0123456789abcde', 'user1234'), 'qLopkenJ4WBqxaZN'),
     (('0123456789abcdef', ''), '.7nfVBEIEu4KbF/1'),
     (('0123456789abcdef', '36'), '.7nfVBEIEu4KbF/1'),
     (('0123456789abcdef', '365'), '.7nfVBEIEu4KbF/1'),
     (('0123456789abcdef', '3333'), '.7nfVBEIEu4KbF/1'),
     (('0123456789abcdef', '3636'), '.7nfVBEIEu4KbF/1'),
     (('0123456789abcdef', '3653'), '.7nfVBEIEu4KbF/1'),
     (('0123456789abcdef', 'user'), '.7nfVBEIEu4KbF/1'),
     (('0123456789abcdef', 'user1234'), '.7nfVBEIEu4KbF/1')]


class cisco_asa_test(_PixAsaSharedTest):
    handler = hash.cisco_asa
    known_correct_hashes = _PixAsaSharedTest.pix_asa_shared_hashes + [
     (('0123456789abc', ''), 'eacOpB7vE7ZDukSF'),
     (('0123456789abc', '36'), 'FRV9JG18UBEgX0.O'),
     (('0123456789abc', '365'), 'NIwkusG9hmmMy6ZQ'),
     (('0123456789abc', '3333'), 'NmrkP98nT7RAeKZz'),
     (('0123456789abc', '3636'), 'FRV9JG18UBEgX0.O'),
     (('0123456789abc', '3653'), 'NIwkusG9hmmMy6ZQ'),
     (('0123456789abc', 'user'), '8Q/FZeam5ai1A47p'),
     (('0123456789abc', 'user1234'), '8Q/FZeam5ai1A47p'),
     (('0123456789abcd', ''), '6r8888iMxEoPdLp4'),
     (('0123456789abcd', '3'), 'yxGoujXKPduTVaYB'),
     (('0123456789abcd', '36'), 'W0jckhnhjnr/DiT/'),
     (('0123456789abcd', '365'), 'HuVOxfMQNahaoF8u'),
     (('0123456789abcd', '3333'), 'yxGoujXKPduTVaYB'),
     (('0123456789abcd', '3636'), 'W0jckhnhjnr/DiT/'),
     (('0123456789abcd', '3653'), 'HuVOxfMQNahaoF8u'),
     (('0123456789abcd', 'adm'), 'RtOmSeoCs4AUdZqZ'),
     (('0123456789abcd', 'adma'), 'RtOmSeoCs4AUdZqZ'),
     (('0123456789abcd', 'user'), 'rrucwrcM0h25pr.m'),
     (('0123456789abcd', 'user1234'), 'rrucwrcM0h25pr.m'),
     (('0123456789abcde', ''), 'al1e0XFIugTYLai3'),
     (('0123456789abcde', '3'), 'nAZrQoHaL.fgrIqt'),
     (('0123456789abcde', '36'), '2GxIQ6ICE795587X'),
     (('0123456789abcde', '365'), 'QmDsGwCRBbtGEKqM'),
     (('0123456789abcde', '3333'), 'nAZrQoHaL.fgrIqt'),
     (('0123456789abcde', '3636'), '2GxIQ6ICE795587X'),
     (('0123456789abcde', '3653'), 'QmDsGwCRBbtGEKqM'),
     (('0123456789abcde', 'adm'), 'Aj2aP0d.nk62wl4m'),
     (('0123456789abcde', 'adma'), 'Aj2aP0d.nk62wl4m'),
     (('0123456789abcde', 'user'), 'etxiXfo.bINJcXI7'),
     (('0123456789abcde', 'user1234'), 'etxiXfo.bINJcXI7'),
     (('0123456789abcdef', ''), '.7nfVBEIEu4KbF/1'),
     (('0123456789abcdef', '36'), 'GhI8.yFSC5lwoafg'),
     (('0123456789abcdef', '365'), 'KFBI6cNQauyY6h/G'),
     (('0123456789abcdef', '3333'), 'Ghdi1IlsswgYzzMH'),
     (('0123456789abcdef', '3636'), 'GhI8.yFSC5lwoafg'),
     (('0123456789abcdef', '3653'), 'KFBI6cNQauyY6h/G'),
     (('0123456789abcdef', 'user'), 'IneB.wc9sfRzLPoh'),
     (('0123456789abcdef', 'user1234'), 'IneB.wc9sfRzLPoh'),
     (('0123456789abcdefq', ''), 'bKshl.EN.X3CVFRQ'),
     (('0123456789abcdefq', '36'), 'JAeTXHs0n30svlaG'),
     (('0123456789abcdefq', '365'), '4fKSSUBHT1ChGqHp'),
     (('0123456789abcdefq', '3333'), 'USEJbxI6.VY4ecBP'),
     (('0123456789abcdefq', '3636'), 'JAeTXHs0n30svlaG'),
     (('0123456789abcdefq', '3653'), '4fKSSUBHT1ChGqHp'),
     (('0123456789abcdefq', 'user'), '/dwqyD7nGdwSrDwk'),
     (('0123456789abcdefq', 'user1234'), '/dwqyD7nGdwSrDwk'),
     (('0123456789abcdefqwertyuiopa', ''), '4wp19zS3OCe.2jt5'),
     (('0123456789abcdefqwertyuiopa', '36'), 'PjUoGqWBKPyV9qOe'),
     (('0123456789abcdefqwertyuiopa', '365'), 'bfCy6xFAe5O/gzvM'),
     (('0123456789abcdefqwertyuiopa', '3333'), 'rd/ZMuGTJFIb2BNG'),
     (('0123456789abcdefqwertyuiopa', '3636'), 'PjUoGqWBKPyV9qOe'),
     (('0123456789abcdefqwertyuiopa', '3653'), 'bfCy6xFAe5O/gzvM'),
     (('0123456789abcdefqwertyuiopa', 'user'), 'zynfWw3UtszxLMgL'),
     (('0123456789abcdefqwertyuiopa', 'user1234'), 'zynfWw3UtszxLMgL'),
     (('0123456789abcdefqwertyuiopas', ''), 'W6nbOddI0SutTK7m'),
     (('0123456789abcdefqwertyuiopas', '36'), 'W6nbOddI0SutTK7m'),
     (('0123456789abcdefqwertyuiopas', '365'), 'W6nbOddI0SutTK7m'),
     (('0123456789abcdefqwertyuiopas', 'user'), 'W6nbOddI0SutTK7m'),
     (('0123456789abcdefqwertyuiopas', 'user1234'), 'W6nbOddI0SutTK7m'),
     (('0123456789abcdefqwertyuiopasdfgh', ''), '5hPT/iC6DnoBxo6a'),
     (('0123456789abcdefqwertyuiopasdfgh', '36'), '5hPT/iC6DnoBxo6a'),
     (('0123456789abcdefqwertyuiopasdfgh', '365'), '5hPT/iC6DnoBxo6a'),
     (('0123456789abcdefqwertyuiopasdfgh', 'user'), '5hPT/iC6DnoBxo6a'),
     (('0123456789abcdefqwertyuiopasdfgh', 'user1234'), '5hPT/iC6DnoBxo6a')]


class cisco_type7_test(HandlerCase):
    handler = hash.cisco_type7
    salt_bits = 4
    salt_type = int
    known_correct_hashes = [
     ('secure ', '04480E051A33490E'),
     ('Its time to go to lunch!', '153B1F1F443E22292D73212D5300194315591954465A0D0B59'),
     ('t35t:pa55w0rd', '08351F1B1D431516475E1B54382F'),
     ('hiImTesting:)', '020E0D7206320A325847071E5F5E'),
     ('cisco123', '060506324F41584B56'),
     ('cisco123', '1511021F07257A767B'),
     ('Supe&8ZUbeRp4SS', '06351A3149085123301517391C501918'),
     (
      UPASS_TABLE, '0958EDC8A9F495F6F8A5FD')]
    known_unidentified_hashes = [
     '0A480E051A33490E',
     '99400E4812']

    def test_90_decode(self):
        from otp.ai.passlib.utils import to_unicode, to_bytes
        handler = self.handler
        for secret, hash in self.known_correct_hashes:
            usecret = to_unicode(secret)
            bsecret = to_bytes(secret)
            self.assertEqual(handler.decode(hash), usecret)
            self.assertEqual(handler.decode(hash, None), bsecret)

        self.assertRaises(UnicodeDecodeError, handler.decode, '0958EDC8A9F495F6F8A5FD', 'ascii')
        return

    def test_91_salt(self):
        handler = self.handler
        self.assertRaises(TypeError, handler, salt=None)
        handler(salt=None, use_defaults=True)
        self.assertRaises(TypeError, handler, salt='abc')
        self.assertRaises(ValueError, handler, salt=-10)
        self.assertRaises(ValueError, handler, salt=100)
        self.assertRaises(TypeError, handler.using, salt='abc')
        self.assertRaises(ValueError, handler.using, salt=-10)
        self.assertRaises(ValueError, handler.using, salt=100)
        with self.assertWarningList('salt/offset must be.*'):
            subcls = handler.using(salt=100, relaxed=True)
        self.assertEqual(subcls(use_defaults=True).salt, 52)
        return