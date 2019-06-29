import logging
log = logging.getLogger(__name__)
import warnings
warnings.filterwarnings('ignore', '.*using builtin scrypt backend.*')
from otp.ai.passlib import hash
from otp.ai.passlib.tests.utils import HandlerCase, TEST_MODE
from otp.ai.passlib.tests.test_handlers import UPASS_TABLE, PASS_TABLE_UTF8

class _scrypt_test(HandlerCase):
    handler = hash.scrypt
    known_correct_hashes = [
     ('', '$scrypt$ln=4,r=1,p=1$$d9ZXYjhleyA7GcpCwYoEl/FrSETjB0ro39/6P+3iFEI'),
     ('password', '$scrypt$ln=10,r=8,p=16$TmFDbA$/bq+HJ00cgB4VucZDQHp/nxq18vII3gw53N2Y0s3MWI'),
     ('test', '$scrypt$ln=8,r=8,p=1$wlhLyXmP8b53bm1NKYVQqg$mTpvG8lzuuDk+DWz8HZIB6Vum6erDuUm0As5yU+VxWA'),
     ('password', '$scrypt$ln=8,r=2,p=1$dO6d0xoDoLT2PofQGoNQag$g/Wf2A0vhHhaJM+addK61QPBthSmYB6uVTtQzh8CM3o'),
     (
      UPASS_TABLE, '$scrypt$ln=7,r=8,p=1$jjGmtDamdA4BQAjBeA9BSA$OiWRHhQtpDx7M/793x6UXK14AD512jg/qNm/hkWZG4M'),
     (
      PASS_TABLE_UTF8, '$scrypt$ln=7,r=8,p=1$jjGmtDamdA4BQAjBeA9BSA$OiWRHhQtpDx7M/793x6UXK14AD512jg/qNm/hkWZG4M'),
     ('nacl', '$scrypt$ln=1,r=4,p=2$yhnD+J+Tci4lZCwFgHCuVQ$fAsEWmxSHuC0cHKMwKVFPzrQukgvK09Sj+NueTSxKds')]
    if TEST_MODE('full'):
        known_correct_hashes.extend([
         ('pleaseletmein', '$scrypt$ln=14,r=8,p=1$U29kaXVtQ2hsb3JpZGU$cCO9yzr9c0hGHAbNgf046/2o+7qQT44+qbVD9lRdofI'),
         ('pleaseletmein', '$7$C6..../....SodiumChloride$kBGj9fHznVYFQMEn/qDCfrDevf9YDtcDdKvEqHJLV8D')])
    known_malformed_hashes = [
     '$scrypt$ln=10,r=1$wvif8/4fg1Cq9V7L2dv73w$bJcLia1lyfQ1X2x0xflehwVXPzWIUQWWdnlGwfVzBeQ',
     '$scrypt$ln=0,r=1,p=1$wvif8/4fg1Cq9V7L2dv73w$bJcLia1lyfQ1X2x0xflehwVXPzWIUQWWdnlGwfVzBeQ',
     '$scrypt$ln=10,r=A,p=1$wvif8/4fg1Cq9V7L2dv73w$bJcLia1lyfQ1X2x0xflehwVXPzWIUQWWdnlGwfVzBeQ',
     '$scrypt$ln=10,r=134217728,p=8$wvif8/4fg1Cq9V7L2dv73w$bJcLia1lyfQ1X2x0xflehwVXPzWIUQWWdnlGwfVzBeQ']

    def setUpWarnings(self):
        super(_scrypt_test, self).setUpWarnings()
        warnings.filterwarnings('ignore', '.*using builtin scrypt backend.*')

    def populate_settings(self, kwds):
        if self.backend == 'builtin':
            kwds.setdefault('rounds', 6)
        super(_scrypt_test, self).populate_settings(kwds)

    class FuzzHashGenerator(HandlerCase.FuzzHashGenerator):

        def random_rounds(self):
            return self.randintgauss(4, 10, 6, 1)


scrypt_scrypt_test = _scrypt_test.create_backend_case('scrypt')
scrypt_builtin_test = _scrypt_test.create_backend_case('builtin')