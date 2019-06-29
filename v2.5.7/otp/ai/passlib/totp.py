from __future__ import absolute_import, division, print_function
from otp.ai.passlib.utils.compat import PY3
import base64, collections, calendar, json, logging
log = logging.getLogger(__name__)
import math, struct, sys, time as _time, re
if PY3:
    from urllib.parse import urlparse, parse_qsl, quote, unquote
else:
    from urllib import quote, unquote
    from urlparse import urlparse, parse_qsl
from warnings import warn
try:
    from cryptography.hazmat.backends import default_backend as _cg_default_backend
    import cryptography.hazmat.primitives.ciphers.algorithms, cryptography.hazmat.primitives.ciphers.modes
    from cryptography.hazmat.primitives import ciphers as _cg_ciphers
    del cryptography
except ImportError:
    log.debug("can't import 'cryptography' package, totp encryption disabled")
    _cg_ciphers = _cg_default_backend = None

from otp.ai.passlib import exc
from otp.ai.passlib.exc import TokenError, MalformedTokenError, InvalidTokenError, UsedTokenError
from otp.ai.passlib.utils import to_unicode, to_bytes, consteq, getrandbytes, rng, SequenceMixin, xor_bytes, getrandstr
from otp.ai.passlib.utils.binary import BASE64_CHARS, b32encode, b32decode
from otp.ai.passlib.utils.compat import u, unicode, native_string_types, bascii_to_str, int_types, num_types, irange, byte_elem_value, UnicodeIO, suppress_cause
from otp.ai.passlib.utils.decor import hybrid_method, memoized_property
from otp.ai.passlib.crypto.digest import lookup_hash, compile_hmac, pbkdf2_hmac
from otp.ai.passlib.hash import pbkdf2_sha256
__all__ = [
 'AppWallet',
 'TOTP',
 'TokenError',
 'MalformedTokenError',
 'InvalidTokenError',
 'UsedTokenError',
 'TotpToken',
 'TotpMatch']
if sys.version_info < (2, 7, 4):
    from urlparse import uses_query
    if 'otpauth' not in uses_query:
        uses_query.append('otpauth')
        log.debug("registered 'otpauth' scheme with urlparse.uses_query")
    del uses_query
_clean_re = re.compile(u('\\s|[-=]'), re.U)
_chunk_sizes = [
 4, 6, 5]

def _get_group_size(klen):
    for size in _chunk_sizes:
        if not klen % size:
            return size

    best = _chunk_sizes[0]
    rem = 0
    for size in _chunk_sizes:
        if klen % size > rem:
            best = size
            rem = klen % size

    return best


def group_string(value, sep='-'):
    klen = len(value)
    size = _get_group_size(klen)
    return sep.join(value[o:o + size] for o in irange(0, klen, size))


def _decode_bytes(key, format):
    if format == 'raw':
        if not isinstance(key, bytes):
            raise exc.ExpectedTypeError(key, 'bytes', 'key')
        return key
    key = to_unicode(key, param='key')
    key = _clean_re.sub('', key).encode('utf-8')
    if format == 'hex' or format == 'base16':
        return base64.b16decode(key.upper())
    if format == 'base32':
        return b32decode(key)
    raise ValueError('unknown byte-encoding format: %r' % (format,))


AES_SUPPORT = bool(_cg_ciphers)
_tag_re = re.compile('(?i)^[a-z0-9][a-z0-9_.-]*$')

class AppWallet(object):
    salt_size = 12
    encrypt_cost = 14
    _secrets = None
    default_tag = None

    def __init__(self, secrets=None, default_tag=None, encrypt_cost=None, secrets_path=None):
        if encrypt_cost is not None:
            if isinstance(encrypt_cost, native_string_types):
                encrypt_cost = int(encrypt_cost)
            self.encrypt_cost = encrypt_cost
        if secrets_path is not None:
            if secrets is not None:
                raise TypeError("'secrets' and 'secrets_path' are mutually exclusive")
            secrets = open(secrets_path, 'rt').read()
        secrets = self._secrets = self._parse_secrets(secrets)
        if secrets:
            if default_tag is not None:
                self.get_secret(default_tag)
            else:
                if all(tag.isdigit() for tag in secrets):
                    default_tag = max(secrets, key=int)
                else:
                    default_tag = max(secrets)
            self.default_tag = default_tag
        return

    def _parse_secrets(self, source):
        check_type = True
        if isinstance(source, native_string_types):
            if source.lstrip().startswith(('[', '{')):
                source = json.loads(source)
            elif '\n' in source and ':' in source:

                def iter_pairs(source):
                    for line in source.splitlines():
                        line = line.strip()
                        if line and not line.startswith('#'):
                            tag, secret = line.split(':', 1)
                            yield (tag.strip(), secret.strip())

                source = iter_pairs(source)
                check_type = False
            else:
                raise ValueError('unrecognized secrets string format')
        if source is None:
            return {}
        if isinstance(source, dict):
            source = source.items()
        else:
            if check_type:
                raise TypeError("'secrets' must be mapping, or list of items")
        return dict(self._parse_secret_pair(tag, value) for tag, value in source)

    def _parse_secret_pair(self, tag, value):
        if isinstance(tag, native_string_types):
            pass
        else:
            if isinstance(tag, int):
                tag = str(tag)
            else:
                raise TypeError('tag must be unicode/string: %r' % (tag,))
        if not _tag_re.match(tag):
            raise ValueError('tag contains invalid characters: %r' % (tag,))
        if not isinstance(value, bytes):
            value = to_bytes(value, param='secret %r' % (tag,))
        if not value:
            raise ValueError('tag contains empty secret: %r' % (tag,))
        return (tag, value)

    @property
    def has_secrets(self):
        return self.default_tag is not None

    def get_secret(self, tag):
        secrets = self._secrets
        if not secrets:
            raise KeyError('no application secrets configured')
        try:
            return secrets[tag]
        except KeyError:
            raise suppress_cause(KeyError('unknown secret tag: %r' % (tag,)))

    @staticmethod
    def _cipher_aes_key(value, secret, salt, cost, decrypt=False):
        if _cg_ciphers is None:
            raise RuntimeError("TOTP encryption requires 'cryptography' package (https://cryptography.io)")
        keyiv = pbkdf2_hmac('sha256', secret, salt=salt, rounds=1 << cost, keylen=48)
        cipher = _cg_ciphers.Cipher(_cg_ciphers.algorithms.AES(keyiv[:32]), _cg_ciphers.modes.CTR(keyiv[32:]), _cg_default_backend())
        ctx = cipher.decryptor() if decrypt else cipher.encryptor()
        return ctx.update(value) + ctx.finalize()

    def encrypt_key(self, key):
        if not key:
            raise ValueError('no key provided')
        salt = getrandbytes(rng, self.salt_size)
        cost = self.encrypt_cost
        tag = self.default_tag
        if not tag:
            raise TypeError("no application secrets configured, can't encrypt OTP key")
        ckey = self._cipher_aes_key(key, self.get_secret(tag), salt, cost)
        return dict(v=1, c=cost, t=tag, s=b32encode(salt), k=b32encode(ckey))

    def decrypt_key(self, enckey):
        if not isinstance(enckey, dict):
            raise TypeError("'enckey' must be dictionary")
        version = enckey.get('v', None)
        needs_recrypt = False
        if version == 1:
            _cipher_key = self._cipher_aes_key
        else:
            raise ValueError("missing / unrecognized 'enckey' version: %r" % (version,))
        tag = enckey['t']
        cost = enckey['c']
        key = _cipher_key(value=b32decode(enckey['k']), secret=self.get_secret(tag), salt=b32decode(enckey['s']), cost=cost)
        if cost != self.encrypt_cost or tag != self.default_tag:
            needs_recrypt = True
        return (key, needs_recrypt)


_pack_uint64 = struct.Struct('>Q').pack
_unpack_uint32 = struct.Struct('>I').unpack
_DUMMY_KEY = '\x00' * 16

class TOTP(object):
    _min_key_size = 10
    min_json_version = json_version = 1
    wallet = None
    now = _time.time
    _key = None
    _encrypted_key = None
    _keyed_hmac = None
    digits = 6
    alg = 'sha1'
    label = None
    issuer = None
    period = 30
    changed = False

    @classmethod
    def using(cls, digits=None, alg=None, period=None, issuer=None, wallet=None, now=None, **kwds):
        subcls = type('TOTP', (cls,), {})

        def norm_param(attr, value):
            kwds = dict(key=_DUMMY_KEY, format='raw')
            kwds[attr] = value
            obj = subcls(**kwds)
            return getattr(obj, attr)

        if digits is not None:
            subcls.digits = norm_param('digits', digits)
        if alg is not None:
            subcls.alg = norm_param('alg', alg)
        if period is not None:
            subcls.period = norm_param('period', period)
        if issuer is not None:
            subcls.issuer = norm_param('issuer', issuer)
        if kwds:
            subcls.wallet = AppWallet(**kwds)
            if wallet:
                raise TypeError("'wallet' and 'secrets' keywords are mutually exclusive")
        else:
            if wallet is not None:
                if not isinstance(wallet, AppWallet):
                    raise exc.ExpectedTypeError(wallet, AppWallet, 'wallet')
                subcls.wallet = wallet
        if now is not None:
            subcls.now = staticmethod(now)
        return subcls

    @classmethod
    def new(cls, **kwds):
        return cls(new=True, **kwds)

    def __init__(self, key=None, format='base32', new=False, digits=None, alg=None, size=None, period=None, label=None, issuer=None, changed=False, **kwds):
        super(TOTP, self).__init__(**kwds)
        if changed:
            self.changed = changed
        info = lookup_hash(alg or self.alg)
        self.alg = info.name
        digest_size = info.digest_size
        if digest_size < 4:
            raise RuntimeError('%r hash digest too small' % alg)
        if new:
            if key:
                raise TypeError("'key' and 'new=True' are mutually exclusive")
            if size is None:
                size = digest_size
            else:
                if size > digest_size:
                    raise ValueError("'size' should be less than digest size (%d)" % digest_size)
            self.key = getrandbytes(rng, size)
        else:
            if not key:
                raise TypeError("must specify either an existing 'key', or 'new=True'")
            else:
                if format == 'encrypted':
                    self.encrypted_key = key
                else:
                    if key:
                        self.key = _decode_bytes(key, format)
        if len(self.key) < self._min_key_size:
            msg = 'for security purposes, secret key must be >= %d bytes' % self._min_key_size
            if new:
                raise ValueError(msg)
            else:
                warn(msg, exc.PasslibSecurityWarning, stacklevel=1)
        if digits is None:
            digits = self.digits
        if not isinstance(digits, int_types):
            raise TypeError('digits must be an integer, not a %r' % type(digits))
        if digits < 6 or digits > 10:
            raise ValueError('digits must in range(6,11)')
        self.digits = digits
        if label:
            self._check_label(label)
            self.label = label
        if issuer:
            self._check_issuer(issuer)
            self.issuer = issuer
        if period is not None:
            self._check_serial(period, 'period', minval=1)
            self.period = period
        return

    @staticmethod
    def _check_serial(value, param, minval=0):
        if not isinstance(value, int_types):
            raise exc.ExpectedTypeError(value, 'int', param)
        if value < minval:
            raise ValueError('%s must be >= %d' % (param, minval))

    @staticmethod
    def _check_label(label):
        if label and ':' in label:
            raise ValueError("label may not contain ':'")

    @staticmethod
    def _check_issuer(issuer):
        if issuer and ':' in issuer:
            raise ValueError("issuer may not contain ':'")

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        if not isinstance(value, bytes):
            raise exc.ExpectedTypeError(value, bytes, 'key')
        self._key = value
        self._encrypted_key = self._keyed_hmac = None
        return

    @property
    def encrypted_key(self):
        enckey = self._encrypted_key
        if enckey is None:
            wallet = self.wallet
            if not wallet:
                raise TypeError("no application secrets present, can't encrypt TOTP key")
            enckey = self._encrypted_key = wallet.encrypt_key(self.key)
        return enckey

    @encrypted_key.setter
    def encrypted_key(self, value):
        wallet = self.wallet
        if not wallet:
            raise TypeError("no application secrets present, can't decrypt TOTP key")
        self.key, needs_recrypt = wallet.decrypt_key(value)
        if needs_recrypt:
            self.changed = True
        else:
            self._encrypted_key = value

    @property
    def hex_key(self):
        return bascii_to_str(base64.b16encode(self.key)).lower()

    @property
    def base32_key(self):
        return b32encode(self.key)

    def pretty_key(self, format='base32', sep='-'):
        if format == 'hex' or format == 'base16':
            key = self.hex_key
        else:
            if format == 'base32':
                key = self.base32_key
            else:
                raise ValueError('unknown byte-encoding format: %r' % (format,))
        if sep:
            key = group_string(key, sep)
        return key

    @classmethod
    def normalize_time(cls, time):
        if isinstance(time, int_types):
            return time
        if isinstance(time, float):
            return int(time)
        if time is None:
            return int(cls.now())
        if hasattr(time, 'utctimetuple'):
            return calendar.timegm(time.utctimetuple())
        raise exc.ExpectedTypeError(time, 'int, float, or datetime', 'time')
        return

    def _time_to_counter(self, time):
        return time // self.period

    def _counter_to_time(self, counter):
        return counter * self.period

    @hybrid_method
    def normalize_token(self_or_cls, token):
        digits = self_or_cls.digits
        if isinstance(token, int_types):
            token = u('%0*d') % (digits, token)
        else:
            token = to_unicode(token, param='token')
            token = _clean_re.sub(u(''), token)
            if not token.isdigit():
                raise MalformedTokenError('Token must contain only the digits 0-9')
        if len(token) != digits:
            raise MalformedTokenError('Token must have exactly %d digits' % digits)
        return token

    def generate(self, time=None):
        time = self.normalize_time(time)
        counter = self._time_to_counter(time)
        if counter < 0:
            raise ValueError('timestamp must be >= 0')
        token = self._generate(counter)
        return TotpToken(self, token, counter)

    def _generate(self, counter):
        keyed_hmac = self._keyed_hmac
        if keyed_hmac is None:
            keyed_hmac = self._keyed_hmac = compile_hmac(self.alg, self.key)
        digest = keyed_hmac(_pack_uint64(counter))
        digest_size = keyed_hmac.digest_info.digest_size
        offset = byte_elem_value(digest[(-1)]) & 15
        value = _unpack_uint32(digest[offset:offset + 4])[0] & 2147483647
        digits = self.digits
        return (u('%0*d') % (digits, value))[-digits:]

    @classmethod
    def verify(cls, token, source, **kwds):
        return cls.from_source(source).match(token, **kwds)

    def match(self, token, time=None, window=30, skew=0, last_counter=None):
        time = self.normalize_time(time)
        self._check_serial(window, 'window')
        client_time = time + skew
        if last_counter is None:
            last_counter = -1
        start = max(last_counter, self._time_to_counter(client_time - window))
        end = self._time_to_counter(client_time + window) + 1
        counter = self._find_match(token, start, end)
        if counter == last_counter:
            raise UsedTokenError(expire_time=(last_counter + 1) * self.period)
        return TotpMatch(self, counter, time, window)

    def _find_match(self, token, start, end, expected=None):
        token = self.normalize_token(token)
        if start < 0:
            start = 0
        if end <= start:
            raise InvalidTokenError()
        generate = self._generate
        if not (expected is None or expected < start) and consteq(token, generate(expected)):
            return expected
        counter = start
        while counter < end:
            if consteq(token, generate(counter)):
                return counter
            counter += 1

        raise InvalidTokenError()
        return

    @classmethod
    def from_source(cls, source):
        if isinstance(source, TOTP):
            if cls.wallet == source.wallet:
                return source
            source = source.to_dict(encrypt=False)
        if isinstance(source, dict):
            return cls.from_dict(source)
        source = to_unicode(source, param='totp source')
        if source.startswith('otpauth://'):
            return cls.from_uri(source)
        return cls.from_json(source)

    @classmethod
    def from_uri(cls, uri):
        uri = to_unicode(uri, param='uri').strip()
        result = urlparse(uri)
        if result.scheme != 'otpauth':
            raise cls._uri_parse_error('wrong uri scheme')
        cls._check_otp_type(result.netloc)
        return cls._from_parsed_uri(result)

    @classmethod
    def _check_otp_type(cls, type):
        if type == 'totp':
            return True
        if type == 'hotp':
            raise NotImplementedError('HOTP not supported')
        raise ValueError('unknown otp type: %r' % type)

    @classmethod
    def _from_parsed_uri(cls, result):
        label = result.path
        if label.startswith('/') and len(label) > 1:
            label = unquote(label[1:])
        else:
            raise cls._uri_parse_error('missing label')
        if ':' in label:
            try:
                issuer, label = label.split(':')
            except ValueError:
                raise cls._uri_parse_error('malformed label')

        else:
            issuer = None
        if label:
            label = label.strip() or None
        params = dict(label=label)
        for k, v in parse_qsl(result.query):
            if k in params:
                raise cls._uri_parse_error('duplicate parameter (%r)' % k)
            params[k] = v

        if issuer:
            if 'issuer' not in params:
                params['issuer'] = issuer
            elif params['issuer'] != issuer:
                raise cls._uri_parse_error('conflicting issuer identifiers')
        return cls(**cls._adapt_uri_params(**params))

    @classmethod
    def _adapt_uri_params(cls, label=None, secret=None, issuer=None, digits=None, algorithm=None, period=None, **extra):
        if not secret:
            raise cls._uri_parse_error("missing 'secret' parameter")
        kwds = dict(label=label, issuer=issuer, key=secret, format='base32')
        if digits:
            kwds['digits'] = cls._uri_parse_int(digits, 'digits')
        if algorithm:
            kwds['alg'] = algorithm
        if period:
            kwds['period'] = cls._uri_parse_int(period, 'period')
        if extra:
            warn('%s: unexpected parameters encountered in otp uri: %r' % (
             cls, extra), exc.PasslibRuntimeWarning)
        return kwds

    @staticmethod
    def _uri_parse_error(reason):
        return ValueError('Invalid otpauth uri: %s' % (reason,))

    @classmethod
    def _uri_parse_int(cls, source, param):
        try:
            return int(source)
        except ValueError:
            raise cls._uri_parse_error('Malformed %r parameter' % param)

    def to_uri(self, label=None, issuer=None):
        if label is None:
            label = self.label
        if not label:
            raise ValueError('a label must be specified as argument, or in the constructor')
        self._check_label(label)
        label = quote(label, '@')
        args = self._to_uri_params()
        if issuer is None:
            issuer = self.issuer
        if issuer:
            self._check_issuer(issuer)
            args.append(('issuer', issuer))
        argstr = u('&').join(u('%s=%s') % (key, quote(value, '')) for key, value in args)
        return u('otpauth://totp/%s?%s') % (label, argstr)

    def _to_uri_params(self):
        args = [
         (
          'secret', self.base32_key)]
        if self.alg != 'sha1':
            args.append(('algorithm', self.alg.upper()))
        if self.digits != 6:
            args.append(('digits', str(self.digits)))
        if self.period != 30:
            args.append(('period', str(self.period)))
        return args

    @classmethod
    def from_json(cls, source):
        source = to_unicode(source, param='json source')
        return cls.from_dict(json.loads(source))

    def to_json(self, encrypt=None):
        state = self.to_dict(encrypt=encrypt)
        return json.dumps(state, sort_keys=True, separators=(',', ':'))

    @classmethod
    def from_dict(cls, source):
        if not isinstance(source, dict) or 'type' not in source:
            raise cls._dict_parse_error('unrecognized format')
        return cls(**cls._adapt_dict_kwds(**source))

    @classmethod
    def _adapt_dict_kwds(cls, type, **kwds):
        ver = kwds.pop('v', None)
        if not ver or ver < cls.min_json_version or ver > cls.json_version:
            raise cls._dict_parse_error('missing/unsupported version (%r)' % (ver,))
        else:
            if ver != cls.json_version:
                kwds['changed'] = True
        if 'enckey' in kwds:
            kwds.update(key=kwds.pop('enckey'), format='encrypted')
        else:
            if 'key' not in kwds:
                raise cls._dict_parse_error("missing 'enckey' / 'key'")
        kwds.pop('last_counter', None)
        return kwds

    @staticmethod
    def _dict_parse_error(reason):
        return ValueError('Invalid totp data: %s' % (reason,))

    def to_dict(self, encrypt=None):
        state = dict(v=self.json_version, type='totp')
        if self.alg != 'sha1':
            state['alg'] = self.alg
        if self.digits != 6:
            state['digits'] = self.digits
        if self.period != 30:
            state['period'] = self.period
        if self.label:
            state['label'] = self.label
        issuer = self.issuer
        if issuer and issuer != type(self).issuer:
            state['issuer'] = issuer
        if encrypt is None:
            wallet = self.wallet
            encrypt = wallet and wallet.has_secrets
        if encrypt:
            state['enckey'] = self.encrypted_key
        else:
            state['key'] = self.base32_key
        return state


class TotpToken(SequenceMixin):
    totp = None
    token = None
    counter = None

    def __init__(self, totp, token, counter):
        self.totp = totp
        self.token = token
        self.counter = counter

    @memoized_property
    def start_time(self):
        return self.totp._counter_to_time(self.counter)

    @memoized_property
    def expire_time(self):
        return self.totp._counter_to_time(self.counter + 1)

    @property
    def remaining(self):
        return max(0, self.expire_time - self.totp.now())

    @property
    def valid(self):
        return bool(self.remaining)

    def _as_tuple(self):
        return (
         self.token, self.expire_time)

    def __repr__(self):
        expired = '' if self.remaining else ' expired'
        return "<TotpToken token='%s' expire_time=%d%s>" % (
         self.token, self.expire_time, expired)


class TotpMatch(SequenceMixin):
    totp = None
    counter = 0
    time = 0
    window = 30

    def __init__(self, totp, counter, time, window=30):
        self.totp = totp
        self.counter = counter
        self.time = time
        self.window = window

    @memoized_property
    def expected_counter(self):
        return self.totp._time_to_counter(self.time)

    @memoized_property
    def skipped(self):
        return self.counter - self.expected_counter

    @memoized_property
    def expire_time(self):
        return self.totp._counter_to_time(self.counter + 1)

    @memoized_property
    def cache_seconds(self):
        return self.totp.period + self.window

    @memoized_property
    def cache_time(self):
        return self.expire_time + self.window

    def _as_tuple(self):
        return (
         self.counter, self.time)

    def __repr__(self):
        args = (
         self.counter, self.time, self.cache_seconds)
        return '<TotpMatch counter=%d time=%d cache_seconds=%d>' % args


def generate_secret(entropy=256, charset=BASE64_CHARS[:-2]):
    count = int(math.ceil(entropy * math.log(2, len(charset))))
    return getrandstr(rng, charset, count)