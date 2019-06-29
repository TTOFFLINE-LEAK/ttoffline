from __future__ import with_statement
import logging
log = logging.getLogger(__name__)
import os
from warnings import warn
from otp.ai.passlib import exc, registry
from otp.ai.passlib.context import CryptContext
from otp.ai.passlib.exc import ExpectedStringError
from otp.ai.passlib.hash import htdigest
from otp.ai.passlib.utils import render_bytes, to_bytes, is_ascii_codec
from otp.ai.passlib.utils.decor import deprecated_method
from otp.ai.passlib.utils.compat import join_bytes, unicode, BytesIO, PY3
__all__ = [
 'HtpasswdFile',
 'HtdigestFile']
_UNSET = object()
_BCOLON = ':'
_BHASH = '#'
_INVALID_FIELD_CHARS = ':\n\r\t\x00'
_SKIPPED = 'skipped'
_RECORD = 'record'

class _CommonFile(object):
    encoding = None
    return_unicode = None
    _path = None
    _mtime = None
    autosave = False
    _records = None
    _source = None

    @classmethod
    def from_string(cls, data, **kwds):
        if 'path' in kwds:
            raise TypeError("'path' not accepted by from_string()")
        self = cls(**kwds)
        self.load_string(data)
        return self

    @classmethod
    def from_path(cls, path, **kwds):
        self = cls(**kwds)
        self.load(path)
        return self

    def __init__(self, path=None, new=False, autoload=True, autosave=False, encoding='utf-8', return_unicode=PY3):
        if not encoding:
            warn('``encoding=None`` is deprecated as of Passlib 1.6, and will cause a ValueError in Passlib 1.8, use ``return_unicode=False`` instead.', DeprecationWarning, stacklevel=2)
            encoding = 'utf-8'
            return_unicode = False
        else:
            if not is_ascii_codec(encoding):
                raise ValueError('encoding must be 7-bit ascii compatible')
        self.encoding = encoding
        self.return_unicode = return_unicode
        self.autosave = autosave
        self._path = path
        self._mtime = 0
        if not autoload:
            warn('``autoload=False`` is deprecated as of Passlib 1.6, and will be removed in Passlib 1.8, use ``new=True`` instead', DeprecationWarning, stacklevel=2)
            new = True
        if path and not new:
            self.load()
        else:
            self._records = {}
            self._source = []

    def __repr__(self):
        tail = ''
        if self.autosave:
            tail += ' autosave=True'
        if self._path:
            tail += ' path=%r' % self._path
        if self.encoding != 'utf-8':
            tail += ' encoding=%r' % self.encoding
        return '<%s 0x%0x%s>' % (self.__class__.__name__, id(self), tail)

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        if value != self._path:
            self._mtime = 0
        self._path = value

    @property
    def mtime(self):
        return self._mtime

    def load_if_changed(self):
        if not self._path:
            raise RuntimeError('%r is not bound to a local file' % self)
        if self._mtime and self._mtime == os.path.getmtime(self._path):
            return False
        self.load()
        return True

    def load(self, path=None, force=True):
        if path is not None:
            with open(path, 'rb') as (fh):
                self._mtime = 0
                self._load_lines(fh)
        else:
            if not force:
                warn('%(name)s.load(force=False) is deprecated as of Passlib 1.6,and will be removed in Passlib 1.8; use %(name)s.load_if_changed() instead.' % dict(name=self.__class__.__name__), DeprecationWarning, stacklevel=2)
                return self.load_if_changed()
            if self._path:
                with open(self._path, 'rb') as (fh):
                    self._mtime = os.path.getmtime(self._path)
                    self._load_lines(fh)
            else:
                raise RuntimeError('%s().path is not set, an explicit path is required' % self.__class__.__name__)
        return True

    def load_string(self, data):
        data = to_bytes(data, self.encoding, 'data')
        self._mtime = 0
        self._load_lines(BytesIO(data))

    def _load_lines(self, lines):
        parse = self._parse_record
        records = {}
        source = []
        skipped = ''
        for idx, line in enumerate(lines):
            tmp = line.lstrip()
            if not tmp or tmp.startswith(_BHASH):
                skipped += line
                continue
            key, value = parse(line, idx + 1)
            if key in records:
                log.warning('username occurs multiple times in source file: %r' % key)
                skipped += line
                continue
            if skipped:
                source.append((_SKIPPED, skipped))
                skipped = ''
            records[key] = value
            source.append((_RECORD, key))

        if skipped.rstrip():
            source.append((_SKIPPED, skipped))
        self._records = records
        self._source = source

    def _parse_record(self, record, lineno):
        raise NotImplementedError('should be implemented in subclass')

    def _set_record(self, key, value):
        records = self._records
        existing = key in records
        records[key] = value
        if not existing:
            self._source.append((_RECORD, key))
        return existing

    def _autosave(self):
        if self.autosave and self._path:
            self.save()

    def save(self, path=None):
        if path is not None:
            with open(path, 'wb') as (fh):
                fh.writelines(self._iter_lines())
        else:
            if self._path:
                self.save(self._path)
                self._mtime = os.path.getmtime(self._path)
            else:
                raise RuntimeError('%s().path is not set, cannot autosave' % self.__class__.__name__)
        return

    def to_string(self):
        return join_bytes(self._iter_lines())

    def _iter_lines(self):
        records = self._records
        for action, content in self._source:
            if action == _SKIPPED:
                yield content
            else:
                if content not in records:
                    continue
                yield self._render_record(content, records[content])

    def _render_record(self, key, value):
        raise NotImplementedError('should be implemented in subclass')

    def _encode_user(self, user):
        return self._encode_field(user, 'user')

    def _encode_realm(self, realm):
        return self._encode_field(realm, 'realm')

    def _encode_field(self, value, param='field'):
        if isinstance(value, unicode):
            value = value.encode(self.encoding)
        else:
            if not isinstance(value, bytes):
                raise ExpectedStringError(value, param)
        if len(value) > 255:
            raise ValueError('%s must be at most 255 characters: %r' % (
             param, value))
        if any(c in _INVALID_FIELD_CHARS for c in value):
            raise ValueError('%s contains invalid characters: %r' % (
             param, value))
        return value

    def _decode_field(self, value):
        if self.return_unicode:
            return value.decode(self.encoding)
        return value


_warn_no_bcrypt = set()

def _init_default_schemes():
    host_best = None
    for name in ['bcrypt', 'sha256_crypt']:
        if registry.has_os_crypt_support(name):
            host_best = name
            break

    bcrypt = 'bcrypt' if registry.has_backend('bcrypt') else None
    _warn_no_bcrypt.clear()
    if not bcrypt:
        _warn_no_bcrypt.update(['portable_apache_24', 'host_apache_24',
         'linux_apache_24', 'portable', 'host'])
    defaults = dict(portable_apache_24=bcrypt or 'apr_md5_crypt', portable_apache_22='apr_md5_crypt', host_apache_24=bcrypt or host_best or 'apr_md5_crypt', host_apache_22=host_best or 'apr_md5_crypt', linux_apache_24=bcrypt or 'sha256_crypt', linux_apache_22='sha256_crypt')
    defaults.update(portable=defaults['portable_apache_24'], host=defaults['host_apache_24'])
    return defaults


htpasswd_defaults = _init_default_schemes()

def _init_htpasswd_context():
    schemes = [
     'bcrypt',
     'sha256_crypt',
     'sha512_crypt',
     'des_crypt',
     'apr_md5_crypt',
     'ldap_sha1',
     'plaintext']
    schemes.extend(registry.get_supported_os_crypt_schemes())
    preferred = schemes[:3] + ['apr_md5_crypt'] + schemes
    schemes = sorted(set(schemes), key=preferred.index)
    return CryptContext(schemes, default=htpasswd_defaults['portable_apache_22'])


htpasswd_context = _init_htpasswd_context()

class HtpasswdFile(_CommonFile):

    def __init__(self, path=None, default_scheme=None, context=htpasswd_context, **kwds):
        if 'default' in kwds:
            warn('``default`` is deprecated as of Passlib 1.6, and will be removed in Passlib 1.8, it has been renamed to ``default_scheem``.', DeprecationWarning, stacklevel=2)
            default_scheme = kwds.pop('default')
        if default_scheme:
            if default_scheme in _warn_no_bcrypt:
                warn('HtpasswdFile: no bcrypt backends available, using fallback for default scheme %r' % default_scheme, exc.PasslibSecurityWarning)
            default_scheme = htpasswd_defaults.get(default_scheme, default_scheme)
            context = context.copy(default=default_scheme)
        self.context = context
        super(HtpasswdFile, self).__init__(path, **kwds)

    def _parse_record(self, record, lineno):
        result = record.rstrip().split(_BCOLON)
        if len(result) != 2:
            raise ValueError('malformed htpasswd file (error reading line %d)' % lineno)
        return result

    def _render_record(self, user, hash):
        return render_bytes('%s:%s\n', user, hash)

    def users(self):
        return [ self._decode_field(user) for user in self._records ]

    def set_password(self, user, password):
        hash = self.context.hash(password)
        return self.set_hash(user, hash)

    @deprecated_method(deprecated='1.6', removed='1.8', replacement='set_password')
    def update(self, user, password):
        return self.set_password(user, password)

    def get_hash(self, user):
        try:
            return self._records[self._encode_user(user)]
        except KeyError:
            return

        return

    def set_hash(self, user, hash):
        if PY3 and isinstance(hash, str):
            hash = hash.encode(self.encoding)
        user = self._encode_user(user)
        existing = self._set_record(user, hash)
        self._autosave()
        return existing

    @deprecated_method(deprecated='1.6', removed='1.8', replacement='get_hash')
    def find(self, user):
        return self.get_hash(user)

    def delete(self, user):
        try:
            del self._records[self._encode_user(user)]
        except KeyError:
            return False

        self._autosave()
        return True

    def check_password(self, user, password):
        user = self._encode_user(user)
        hash = self._records.get(user)
        if hash is None:
            return
        if isinstance(password, unicode):
            password = password.encode(self.encoding)
        ok, new_hash = self.context.verify_and_update(password, hash)
        if ok and new_hash is not None:
            self._records[user] = new_hash
            self._autosave()
        return ok

    @deprecated_method(deprecated='1.6', removed='1.8', replacement='check_password')
    def verify(self, user, password):
        return self.check_password(user, password)


class HtdigestFile(_CommonFile):
    default_realm = None

    def __init__(self, path=None, default_realm=None, **kwds):
        self.default_realm = default_realm
        super(HtdigestFile, self).__init__(path, **kwds)

    def _parse_record(self, record, lineno):
        result = record.rstrip().split(_BCOLON)
        if len(result) != 3:
            raise ValueError('malformed htdigest file (error reading line %d)' % lineno)
        user, realm, hash = result
        return (
         (
          user, realm), hash)

    def _render_record(self, key, hash):
        user, realm = key
        return render_bytes('%s:%s:%s\n', user, realm, hash)

    def _require_realm(self, realm):
        if realm is None:
            realm = self.default_realm
            if realm is None:
                raise TypeError('you must specify a realm explicitly, or set the default_realm attribute')
        return realm

    def _encode_realm(self, realm):
        realm = self._require_realm(realm)
        return self._encode_field(realm, 'realm')

    def _encode_key(self, user, realm):
        return (
         self._encode_user(user), self._encode_realm(realm))

    def realms(self):
        realms = set(key[1] for key in self._records)
        return [ self._decode_field(realm) for realm in realms ]

    def users(self, realm=None):
        realm = self._encode_realm(realm)
        return [ self._decode_field(key[0]) for key in self._records if key[1] == realm
               ]

    def set_password(self, user, realm=None, password=_UNSET):
        if password is _UNSET:
            realm, password = None, realm
        realm = self._require_realm(realm)
        hash = htdigest.hash(password, user, realm, encoding=self.encoding)
        return self.set_hash(user, realm, hash)

    @deprecated_method(deprecated='1.6', removed='1.8', replacement='set_password')
    def update(self, user, realm, password):
        return self.set_password(user, realm, password)

    def get_hash(self, user, realm=None):
        key = self._encode_key(user, realm)
        hash = self._records.get(key)
        if hash is None:
            return
        if PY3:
            hash = hash.decode(self.encoding)
        return hash

    def set_hash(self, user, realm=None, hash=_UNSET):
        if hash is _UNSET:
            realm, hash = None, realm
        if PY3 and isinstance(hash, str):
            hash = hash.encode(self.encoding)
        key = self._encode_key(user, realm)
        existing = self._set_record(key, hash)
        self._autosave()
        return existing

    @deprecated_method(deprecated='1.6', removed='1.8', replacement='get_hash')
    def find(self, user, realm):
        return self.get_hash(user, realm)

    def delete(self, user, realm=None):
        key = self._encode_key(user, realm)
        try:
            del self._records[key]
        except KeyError:
            return False

        self._autosave()
        return True

    def delete_realm(self, realm):
        realm = self._encode_realm(realm)
        records = self._records
        keys = [ key for key in records if key[1] == realm ]
        for key in keys:
            del records[key]

        self._autosave()
        return len(keys)

    def check_password(self, user, realm=None, password=_UNSET):
        if password is _UNSET:
            realm, password = None, realm
        user = self._encode_user(user)
        realm = self._encode_realm(realm)
        hash = self._records.get((user, realm))
        if hash is None:
            return
        return htdigest.verify(password, hash, user, realm, encoding=self.encoding)

    @deprecated_method(deprecated='1.6', removed='1.8', replacement='check_password')
    def verify(self, user, realm, password):
        return self.check_password(user, realm, password)