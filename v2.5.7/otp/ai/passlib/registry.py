import re, logging
log = logging.getLogger(__name__)
from warnings import warn
from otp.ai.passlib import exc
from otp.ai.passlib.exc import ExpectedTypeError, PasslibWarning
from otp.ai.passlib.ifc import PasswordHash
from otp.ai.passlib.utils import is_crypt_handler, has_crypt as os_crypt_present, unix_crypt_schemes as os_crypt_schemes
from otp.ai.passlib.utils.compat import unicode_or_str
from otp.ai.passlib.utils.decor import memoize_single_value
__all__ = [
 'register_crypt_handler_path',
 'register_crypt_handler',
 'get_crypt_handler',
 'list_crypt_handlers']

class _PasslibRegistryProxy(object):
    __name__ = 'otp.ai.passlib.hash'
    __package__ = None

    def __getattr__(self, attr):
        if attr.startswith('_'):
            raise AttributeError('missing attribute: %r' % (attr,))
        handler = get_crypt_handler(attr, None)
        if handler:
            return handler
        raise AttributeError('unknown password hash: %r' % (attr,))
        return

    def __setattr__(self, attr, value):
        if attr.startswith('_'):
            object.__setattr__(self, attr, value)
        else:
            register_crypt_handler(value, _attr=attr)

    def __repr__(self):
        return "<proxy module 'passlib.hash'>"

    def __dir__(self):
        attrs = set(dir(self.__class__))
        attrs.update(self.__dict__)
        attrs.update(_locations)
        return sorted(attrs)


_proxy = _PasslibRegistryProxy()
_UNSET = object()
_handlers = _proxy.__dict__
_locations = dict(apr_md5_crypt='otp.ai.passlib.handlers.md5_crypt', argon2='otp.ai.passlib.handlers.argon2', atlassian_pbkdf2_sha1='otp.ai.passlib.handlers.pbkdf2', bcrypt='otp.ai.passlib.handlers.bcrypt', bcrypt_sha256='otp.ai.passlib.handlers.bcrypt', bigcrypt='otp.ai.passlib.handlers.des_crypt', bsd_nthash='otp.ai.passlib.handlers.windows', bsdi_crypt='otp.ai.passlib.handlers.des_crypt', cisco_pix='otp.ai.passlib.handlers.cisco', cisco_asa='otp.ai.passlib.handlers.cisco', cisco_type7='otp.ai.passlib.handlers.cisco', cta_pbkdf2_sha1='otp.ai.passlib.handlers.pbkdf2', crypt16='otp.ai.passlib.handlers.des_crypt', des_crypt='otp.ai.passlib.handlers.des_crypt', django_argon2='otp.ai.passlib.handlers.django', django_bcrypt='otp.ai.passlib.handlers.django', django_bcrypt_sha256='otp.ai.passlib.handlers.django', django_pbkdf2_sha256='otp.ai.passlib.handlers.django', django_pbkdf2_sha1='otp.ai.passlib.handlers.django', django_salted_sha1='otp.ai.passlib.handlers.django', django_salted_md5='otp.ai.passlib.handlers.django', django_des_crypt='otp.ai.passlib.handlers.django', django_disabled='otp.ai.passlib.handlers.django', dlitz_pbkdf2_sha1='otp.ai.passlib.handlers.pbkdf2', fshp='otp.ai.passlib.handlers.fshp', grub_pbkdf2_sha512='otp.ai.passlib.handlers.pbkdf2', hex_md4='otp.ai.passlib.handlers.digests', hex_md5='otp.ai.passlib.handlers.digests', hex_sha1='otp.ai.passlib.handlers.digests', hex_sha256='otp.ai.passlib.handlers.digests', hex_sha512='otp.ai.passlib.handlers.digests', htdigest='otp.ai.passlib.handlers.digests', ldap_plaintext='otp.ai.passlib.handlers.ldap_digests', ldap_md5='otp.ai.passlib.handlers.ldap_digests', ldap_sha1='otp.ai.passlib.handlers.ldap_digests', ldap_hex_md5='otp.ai.passlib.handlers.roundup', ldap_hex_sha1='otp.ai.passlib.handlers.roundup', ldap_salted_md5='otp.ai.passlib.handlers.ldap_digests', ldap_salted_sha1='otp.ai.passlib.handlers.ldap_digests', ldap_des_crypt='otp.ai.passlib.handlers.ldap_digests', ldap_bsdi_crypt='otp.ai.passlib.handlers.ldap_digests', ldap_md5_crypt='otp.ai.passlib.handlers.ldap_digests', ldap_bcrypt='otp.ai.passlib.handlers.ldap_digests', ldap_sha1_crypt='otp.ai.passlib.handlers.ldap_digests', ldap_sha256_crypt='otp.ai.passlib.handlers.ldap_digests', ldap_sha512_crypt='otp.ai.passlib.handlers.ldap_digests', ldap_pbkdf2_sha1='otp.ai.passlib.handlers.pbkdf2', ldap_pbkdf2_sha256='otp.ai.passlib.handlers.pbkdf2', ldap_pbkdf2_sha512='otp.ai.passlib.handlers.pbkdf2', lmhash='otp.ai.passlib.handlers.windows', md5_crypt='otp.ai.passlib.handlers.md5_crypt', msdcc='otp.ai.passlib.handlers.windows', msdcc2='otp.ai.passlib.handlers.windows', mssql2000='otp.ai.passlib.handlers.mssql', mssql2005='otp.ai.passlib.handlers.mssql', mysql323='otp.ai.passlib.handlers.mysql', mysql41='otp.ai.passlib.handlers.mysql', nthash='otp.ai.passlib.handlers.windows', oracle10='otp.ai.passlib.handlers.oracle', oracle11='otp.ai.passlib.handlers.oracle', pbkdf2_sha1='otp.ai.passlib.handlers.pbkdf2', pbkdf2_sha256='otp.ai.passlib.handlers.pbkdf2', pbkdf2_sha512='otp.ai.passlib.handlers.pbkdf2', phpass='otp.ai.passlib.handlers.phpass', plaintext='otp.ai.passlib.handlers.misc', postgres_md5='otp.ai.passlib.handlers.postgres', roundup_plaintext='otp.ai.passlib.handlers.roundup', scram='otp.ai.passlib.handlers.scram', scrypt='otp.ai.passlib.handlers.scrypt', sha1_crypt='otp.ai.passlib.handlers.sha1_crypt', sha256_crypt='otp.ai.passlib.handlers.sha2_crypt', sha512_crypt='otp.ai.passlib.handlers.sha2_crypt', sun_md5_crypt='otp.ai.passlib.handlers.sun_md5_crypt', unix_disabled='otp.ai.passlib.handlers.misc', unix_fallback='otp.ai.passlib.handlers.misc')
_name_re = re.compile('^[a-z][a-z0-9_]+[a-z0-9]$')
_forbidden_names = frozenset(['onload', 'policy', 'context', 'all',
 'default', 'none', 'auto'])

def _validate_handler_name(name):
    if not name:
        raise ValueError('handler name cannot be empty: %r' % (name,))
    if name.lower() != name:
        raise ValueError('name must be lower-case: %r' % (name,))
    if not _name_re.match(name):
        raise ValueError('invalid name (must be 3+ characters,  begin with a-z, and contain only underscore, a-z, 0-9): %r' % (
         name,))
    if '__' in name:
        raise ValueError('name may not contain double-underscores: %r' % (
         name,))
    if name in _forbidden_names:
        raise ValueError('that name is not allowed: %r' % (name,))
    return True


def register_crypt_handler_path(name, path):
    _validate_handler_name(name)
    if path.startswith('.'):
        raise ValueError("path cannot start with '.'")
    if ':' in path:
        if path.count(':') > 1:
            raise ValueError("path cannot have more than one ':'")
        if path.find('.', path.index(':')) > -1:
            raise ValueError("path cannot have '.' to right of ':'")
    _locations[name] = path
    log.debug('registered path to %r handler: %r', name, path)


def register_crypt_handler(handler, force=False, _attr=None):
    if not is_crypt_handler(handler):
        raise ExpectedTypeError(handler, 'password hash handler', 'handler')
    if not handler:
        raise AssertionError('``bool(handler)`` must be True')
    name = handler.name
    _validate_handler_name(name)
    if _attr and _attr != name:
        raise ValueError('handlers must be stored only under their own name (%r != %r)' % (
         _attr, name))
    other = _handlers.get(name)
    if other:
        if other is handler:
            log.debug('same %r handler already registered: %r', name, handler)
            return
        if force:
            log.warning('overriding previously registered %r handler: %r', name, other)
        else:
            raise KeyError('another %r handler has already been registered: %r' % (
             name, other))
    _handlers[name] = handler
    log.debug('registered %r handler: %r', name, handler)


def get_crypt_handler(name, default=_UNSET):
    if name.startswith('_'):
        if default is _UNSET:
            raise KeyError('invalid handler name: %r' % (name,))
        else:
            return default
    try:
        return _handlers[name]
    except KeyError:
        pass
    else:
        alt = name.replace('-', '_').lower()
        if alt != name:
            warn('handler names should be lower-case, and use underscores instead of hyphens: %r => %r' % (
             name, alt), PasslibWarning, stacklevel=2)
            name = alt
            try:
                return _handlers[name]
            except KeyError:
                pass

        path = _locations.get(name)
        if path:
            if ':' in path:
                modname, modattr = path.split(':')
            else:
                modname, modattr = path, name
            mod = __import__(modname, fromlist=[modattr], level=0)
            handler = _handlers.get(name)
            if handler:
                return handler
            handler = getattr(mod, modattr)
            register_crypt_handler(handler, _attr=name)
            return handler

    if default is _UNSET:
        raise KeyError('no crypt handler found for algorithm: %r' % (name,))
    else:
        return default


def list_crypt_handlers(loaded_only=False):
    names = set(_handlers)
    if not loaded_only:
        names.update(_locations)
    return sorted(name for name in names if not name.startswith('_'))


def _has_crypt_handler(name, loaded_only=False):
    return name in _handlers or not loaded_only and name in _locations


def _unload_handler_name(name, locations=True):
    if name in _handlers:
        del _handlers[name]
    if locations and name in _locations:
        del _locations[name]


def _resolve(hasher, param='value'):
    if is_crypt_handler(hasher):
        return hasher
    if isinstance(hasher, unicode_or_str):
        return get_crypt_handler(hasher)
    raise exc.ExpectedTypeError(hasher, unicode_or_str, param)


ANY = 'any'
BUILTIN = 'builtin'
OS_CRYPT = 'os_crypt'

def has_backend(hasher, backend=ANY, safe=False):
    hasher = _resolve(hasher)
    if backend == ANY:
        if not hasattr(hasher, 'get_backend'):
            return True
        try:
            hasher.get_backend()
            return True
        except exc.MissingBackendError:
            return False

    if hasattr(hasher, 'has_backend'):
        if safe and backend not in hasher.backends:
            return
        return hasher.has_backend(backend)
    if backend == BUILTIN:
        return True
    if safe:
        return
    raise exc.UnknownBackendError(hasher, backend)
    return


@memoize_single_value
def get_supported_os_crypt_schemes():
    if not os_crypt_present:
        return ()
    cache = tuple(name for name in os_crypt_schemes if get_crypt_handler(name).has_backend(OS_CRYPT))
    if not cache:
        warn("crypt.crypt() function is present, but doesn't support any formats known to passlib!", exc.PasslibRuntimeWarning)
    return cache


def has_os_crypt_support(hasher):
    return os_crypt_present and has_backend(hasher, OS_CRYPT, safe=True)