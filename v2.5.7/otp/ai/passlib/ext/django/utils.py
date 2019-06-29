from functools import update_wrapper, wraps
import logging
log = logging.getLogger(__name__)
import sys, weakref
from warnings import warn
try:
    from django import VERSION as DJANGO_VERSION
    log.debug('found django %r installation', DJANGO_VERSION)
except ImportError:
    log.debug('django installation not found')
    DJANGO_VERSION = ()

from otp.ai.passlib import exc, registry
from otp.ai.passlib.context import CryptContext
from otp.ai.passlib.exc import PasslibRuntimeWarning
from otp.ai.passlib.utils.compat import get_method_function, iteritems, OrderedDict, unicode
from otp.ai.passlib.utils.decor import memoized_property
__all__ = [
 'DJANGO_VERSION',
 'MIN_DJANGO_VERSION',
 'get_preset_config',
 'get_django_hasher']
MIN_DJANGO_VERSION = (
 1, 8)
_preset_map = {'django-1.0': 'django10_context', 
   'django-1.4': 'django14_context', 
   'django-1.6': 'django16_context', 
   'django-latest': 'django_context'}

def get_preset_config(name):
    if name == 'django-default':
        if not DJANGO_VERSION:
            raise ValueError("can't resolve django-default preset, django not installed")
        name = 'django-1.6'
    if name == 'passlib-default':
        return PASSLIB_DEFAULT
    try:
        attr = _preset_map[name]
    except KeyError:
        raise ValueError('unknown preset config name: %r' % name)

    import otp.ai.passlib.apps
    return getattr(otp.ai.passlib.apps, attr).to_string()


PASSLIB_DEFAULT = '\n[passlib]\n\n; list of schemes supported by configuration\n; currently all django 1.6, 1.4, and 1.0 hashes,\n; and three common modular crypt format hashes.\nschemes =\n    django_pbkdf2_sha256, django_pbkdf2_sha1, django_bcrypt, django_bcrypt_sha256,\n    django_salted_sha1, django_salted_md5, django_des_crypt, hex_md5,\n    sha512_crypt, bcrypt, phpass\n\n; default scheme to use for new hashes\ndefault = django_pbkdf2_sha256\n\n; hashes using these schemes will automatically be re-hashed\n; when the user logs in (currently all django 1.0 hashes)\ndeprecated =\n    django_pbkdf2_sha1, django_salted_sha1, django_salted_md5,\n    django_des_crypt, hex_md5\n\n; sets some common options, including minimum rounds for two primary hashes.\n; if a hash has less than this number of rounds, it will be re-hashed.\nsha512_crypt__min_rounds = 80000\ndjango_pbkdf2_sha256__min_rounds = 10000\n\n; set somewhat stronger iteration counts for ``User.is_staff``\nstaff__sha512_crypt__default_rounds = 100000\nstaff__django_pbkdf2_sha256__default_rounds = 12500\n\n; and even stronger ones for ``User.is_superuser``\nsuperuser__sha512_crypt__default_rounds = 120000\nsuperuser__django_pbkdf2_sha256__default_rounds = 15000\n'
PASSLIB_WRAPPER_PREFIX = 'passlib_'
DJANGO_COMPAT_PREFIX = 'django_'
_other_django_hashes = set(['hex_md5'])

def _wrap_method(method):

    @wraps(method)
    def wrapper(*args, **kwds):
        return method(*args, **kwds)

    return wrapper


class DjangoTranslator(object):
    context = None
    _django_hasher_cache = None
    _django_unsalted_sha1 = None
    _passlib_hasher_cache = None

    def __init__(self, context=None, **kwds):
        super(DjangoTranslator, self).__init__(**kwds)
        if context is not None:
            self.context = context
        self._django_hasher_cache = weakref.WeakKeyDictionary()
        self._passlib_hasher_cache = weakref.WeakValueDictionary()
        return

    def reset_hashers(self):
        self._django_hasher_cache.clear()
        self._passlib_hasher_cache.clear()
        self._django_unsalted_sha1 = None
        return

    def _get_passlib_hasher(self, passlib_name):
        context = self.context
        if context is None:
            return registry.get_crypt_handler(passlib_name)
        return context.handler(passlib_name)
        return

    def passlib_to_django_name(self, passlib_name):
        return self.passlib_to_django(passlib_name).algorithm

    def passlib_to_django(self, passlib_hasher, cached=True):
        if not hasattr(passlib_hasher, 'name'):
            passlib_hasher = self._get_passlib_hasher(passlib_hasher)
        if cached:
            cache = self._django_hasher_cache
            try:
                return cache[passlib_hasher]
            except KeyError:
                pass

            result = cache[passlib_hasher] = self.passlib_to_django(passlib_hasher, cached=False)
            return result
        django_name = getattr(passlib_hasher, 'django_name', None)
        if django_name:
            return self._create_django_hasher(django_name)
        return _PasslibHasherWrapper(passlib_hasher)
        return

    _builtin_django_hashers = dict(md5='MD5PasswordHasher')

    def _create_django_hasher(self, django_name):
        module = sys.modules.get('passlib.ext.django.models')
        if module is None or not module.adapter.patched:
            from django.contrib.auth.hashers import get_hasher
            return get_hasher(django_name)
        get_hashers = module.adapter._manager.getorig('django.contrib.auth.hashers:get_hashers').__wrapped__
        for hasher in get_hashers():
            if hasher.algorithm == django_name:
                return hasher

        path = self._builtin_django_hashers.get(django_name)
        if path:
            if '.' not in path:
                path = 'django.contrib.auth.hashers.' + path
            from django.utils.module_loading import import_string
            return import_string(path)()
        raise ValueError('unknown hasher: %r' % django_name)
        return

    def django_to_passlib_name(self, django_name):
        return self.django_to_passlib(django_name).name

    def django_to_passlib(self, django_name, cached=True):
        if hasattr(django_name, 'algorithm'):
            if isinstance(django_name, _PasslibHasherWrapper):
                return django_name.passlib_handler
            django_name = django_name.algorithm
        if cached:
            cache = self._passlib_hasher_cache
            try:
                return cache[django_name]
            except KeyError:
                pass

            result = cache[django_name] = self.django_to_passlib(django_name, cached=False)
            return result
        if django_name.startswith(PASSLIB_WRAPPER_PREFIX):
            passlib_name = django_name[len(PASSLIB_WRAPPER_PREFIX):]
            return self._get_passlib_hasher(passlib_name)
        if django_name == 'default':
            context = self.context
            if context is None:
                raise TypeError("can't determine default scheme w/ context")
            return context.handler()
        if django_name == 'unsalted_sha1':
            django_name = 'sha1'
        context = self.context
        if context is None:
            candidates = (((passlib_name.startswith(DJANGO_COMPAT_PREFIX) or passlib_name in _other_django_hashes) and registry).get_crypt_handler(passlib_name) for passlib_name in registry.list_crypt_handlers())
        else:
            candidates = context.schemes(resolve=True)
        for handler in candidates:
            if getattr(handler, 'django_name', None) == django_name:
                return handler

        raise ValueError("can't translate django name to passlib name: %r" % (
         django_name,))
        return

    def resolve_django_hasher(self, django_name, cached=True):
        if hasattr(django_name, 'algorithm'):
            return django_name
        passlib_hasher = self.django_to_passlib(django_name, cached=cached)
        if django_name == 'unsalted_sha1' and passlib_hasher.name == 'django_salted_sha1':
            if not cached:
                return self._create_django_hasher(django_name)
            result = self._django_unsalted_sha1
            if result is None:
                result = self._django_unsalted_sha1 = self._create_django_hasher(django_name)
            return result
        return self.passlib_to_django(passlib_hasher, cached=cached)


class DjangoContextAdapter(DjangoTranslator):
    context = None
    _orig_make_password = None
    is_password_usable = None
    _manager = None
    enabled = True
    patched = False

    def __init__(self, context=None, get_user_category=None, **kwds):
        self.log = logging.getLogger(__name__ + '.DjangoContextAdapter')
        if context is None:
            context = CryptContext()
        super(DjangoContextAdapter, self).__init__(context=context, **kwds)
        if get_user_category:
            self.get_user_category = get_user_category
        from django.utils.lru_cache import lru_cache
        self.get_hashers = lru_cache()(self.get_hashers)
        from django.contrib.auth.hashers import make_password
        if make_password.__module__.startswith('passlib.'):
            make_password = _PatchManager.peek_unpatched_func(make_password)
        self._orig_make_password = make_password
        from django.contrib.auth.hashers import is_password_usable
        self.is_password_usable = is_password_usable
        mlog = logging.getLogger(__name__ + '.DjangoContextAdapter._manager')
        self._manager = _PatchManager(log=mlog)
        return

    def reset_hashers(self):
        from django.contrib.auth.hashers import reset_hashers
        reset_hashers(setting='PASSWORD_HASHERS')
        super(DjangoContextAdapter, self).reset_hashers()

    def get_hashers(self):
        passlib_to_django = self.passlib_to_django
        return [ passlib_to_django(hasher) for hasher in self.context.schemes(resolve=True)
               ]

    def get_hasher(self, algorithm='default'):
        return self.resolve_django_hasher(algorithm)

    def identify_hasher(self, encoded):
        handler = self.context.identify(encoded, resolve=True, required=True)
        if handler.name == 'django_salted_sha1' and encoded.startswith('sha1$$'):
            return self.get_hasher('unsalted_sha1')
        return self.passlib_to_django(handler)

    def make_password(self, password, salt=None, hasher='default'):
        if password is None:
            return self._orig_make_password(None)
        passlib_hasher = self.django_to_passlib(hasher)
        if 'salt' not in passlib_hasher.setting_kwds:
            pass
        else:
            if hasher.startswith('unsalted_'):
                passlib_hasher = passlib_hasher.using(salt='')
            else:
                if salt:
                    passlib_hasher = passlib_hasher.using(salt=salt)
        return passlib_hasher.hash(password)

    def check_password(self, password, encoded, setter=None, preferred='default'):
        if password is None or not self.is_password_usable(encoded):
            return False
        context = self.context
        correct = context.verify(password, encoded)
        if not (correct and setter):
            return correct
        if preferred == 'default':
            if not context.needs_update(encoded, secret=password):
                return correct
        else:
            hasher = self.django_to_passlib(preferred)
            if hasher.identify(encoded) and not hasher.needs_update(encoded, secret=password):
                return correct
        setter(password)
        return correct

    def user_check_password(self, user, password):
        if password is None:
            return False
        hash = user.password
        if not self.is_password_usable(hash):
            return False
        cat = self.get_user_category(user)
        ok, new_hash = self.context.verify_and_update(password, hash, category=cat)
        if ok and new_hash is not None:
            user.password = new_hash
            user.save()
        return ok

    def user_set_password(self, user, password):
        if password is None:
            user.set_unusable_password()
        else:
            cat = self.get_user_category(user)
            user.password = self.context.hash(password, category=cat)
        return

    def get_user_category(self, user):
        if user.is_superuser:
            return 'superuser'
        if user.is_staff:
            return 'staff'
        return
        return

    HASHERS_PATH = 'django.contrib.auth.hashers'
    MODELS_PATH = 'django.contrib.auth.models'
    USER_CLASS_PATH = MODELS_PATH + ':User'
    FORMS_PATH = 'django.contrib.auth.forms'
    patch_locations = [
     (
      USER_CLASS_PATH + '.check_password', 'user_check_password', dict(method=True)),
     (
      USER_CLASS_PATH + '.set_password', 'user_set_password', dict(method=True)),
     (
      HASHERS_PATH + ':', 'check_password'),
     (
      HASHERS_PATH + ':', 'make_password'),
     (
      HASHERS_PATH + ':', 'get_hashers'),
     (
      HASHERS_PATH + ':', 'get_hasher'),
     (
      HASHERS_PATH + ':', 'identify_hasher'),
     (
      MODELS_PATH + ':', 'check_password'),
     (
      MODELS_PATH + ':', 'make_password'),
     (
      FORMS_PATH + ':', 'get_hasher'),
     (
      FORMS_PATH + ':', 'identify_hasher')]

    def install_patch(self):
        log = self.log
        if self.patched:
            log.warning('monkeypatching already applied, refusing to reapply')
            return False
        if DJANGO_VERSION < MIN_DJANGO_VERSION:
            raise RuntimeError('passlib.ext.django requires django >= %s' % (
             MIN_DJANGO_VERSION,))
        log.debug('preparing to monkeypatch django ...')
        manager = self._manager
        for record in self.patch_locations:
            if len(record) == 2:
                record += ({},)
            target, source, opts = record
            if target.endswith((':', ',')):
                target += source
            value = getattr(self, source)
            if opts.get('method'):
                value = _wrap_method(value)
            manager.patch(target, value)

        self.reset_hashers()
        self.patched = True
        log.debug('... finished monkeypatching django')
        return True

    def remove_patch(self):
        log = self.log
        manager = self._manager
        if self.patched:
            log.debug('removing django monkeypatching...')
            manager.unpatch_all(unpatch_conflicts=True)
            self.context.load({})
            self.patched = False
            self.reset_hashers()
            log.debug('...finished removing django monkeypatching')
            return True
        if manager.isactive():
            log.warning('reverting partial monkeypatching of django...')
            manager.unpatch_all()
            self.context.load({})
            self.reset_hashers()
            log.debug('...finished removing django monkeypatching')
            return True
        log.debug('django not monkeypatched')
        return False

    def load_model(self):
        self._load_settings()
        if self.enabled:
            try:
                self.install_patch()
            except:
                self.remove_patch()
                raise

        else:
            if self.patched:
                log.error("didn't expect monkeypatching would be applied!")
            self.remove_patch()
        log.debug('passlib.ext.django loaded')

    def _load_settings(self):
        from django.conf import settings
        _UNSET = object()
        config = getattr(settings, 'PASSLIB_CONFIG', _UNSET)
        if config is _UNSET:
            config = getattr(settings, 'PASSLIB_CONTEXT', _UNSET)
        if config is _UNSET:
            config = 'passlib-default'
        if config is None:
            warn("setting PASSLIB_CONFIG=None is deprecated, and support will be removed in Passlib 1.8, use PASSLIB_CONFIG='disabled' instead.", DeprecationWarning)
            config = 'disabled'
        else:
            if not isinstance(config, (unicode, bytes, dict)):
                raise exc.ExpectedTypeError(config, 'str or dict', 'PASSLIB_CONFIG')
            get_category = getattr(settings, 'PASSLIB_GET_CATEGORY', None)
            if get_category and not callable(get_category):
                raise exc.ExpectedTypeError(get_category, 'callable', 'PASSLIB_GET_CATEGORY')
            if config == 'disabled':
                self.enabled = False
                return
        self.__dict__.pop('enabled', None)
        if isinstance(config, str) and '\n' not in config:
            config = get_preset_config(config)
        if get_category:
            self.get_user_category = get_category
        else:
            self.__dict__.pop('get_category', None)
        self.context.load(config)
        self.reset_hashers()
        return


_GEN_SALT_SIGNAL = '--!!!generate-new-salt!!!--'

class ProxyProperty(object):

    def __init__(self, attr):
        self.attr = attr

    def __get__(self, obj, cls):
        if obj is None:
            cls = obj
        return getattr(obj, self.attr)

    def __set__(self, obj, value):
        setattr(obj, self.attr, value)

    def __delete__(self, obj):
        delattr(obj, self.attr)


class _PasslibHasherWrapper(object):
    passlib_handler = None

    def __init__(self, passlib_handler):
        if getattr(passlib_handler, 'django_name', None):
            raise ValueError("handlers that reflect an official django hasher shouldn't be wrapped: %r" % (
             passlib_handler.name,))
        if passlib_handler.is_disabled:
            raise ValueError("can't wrap disabled-hash handlers: %r" % passlib_handler.name)
        self.passlib_handler = passlib_handler
        if self._has_rounds:
            self.rounds = passlib_handler.default_rounds
            self.iterations = ProxyProperty('rounds')
        return

    def __repr__(self):
        return '<PasslibHasherWrapper handler=%r>' % self.passlib_handler

    @memoized_property
    def __name__(self):
        return 'Passlib_%s_PasswordHasher' % self.passlib_handler.name.title()

    @memoized_property
    def _has_rounds(self):
        return 'rounds' in self.passlib_handler.setting_kwds

    @memoized_property
    def _translate_kwds(self):
        out = dict(checksum='hash')
        if self._has_rounds and 'pbkdf2' in self.passlib_handler.name:
            out['rounds'] = 'iterations'
        return out

    @memoized_property
    def algorithm(self):
        return PASSLIB_WRAPPER_PREFIX + self.passlib_handler.name

    def salt(self):
        return _GEN_SALT_SIGNAL

    def verify(self, password, encoded):
        return self.passlib_handler.verify(password, encoded)

    def encode(self, password, salt=None, rounds=None, iterations=None):
        kwds = {}
        if salt is not None and salt != _GEN_SALT_SIGNAL:
            kwds['salt'] = salt
        if self._has_rounds:
            if rounds is not None:
                kwds['rounds'] = rounds
            elif iterations is not None:
                kwds['rounds'] = iterations
            else:
                kwds['rounds'] = self.rounds
        else:
            if rounds is not None or iterations is not None:
                warn("%s.hash(): 'rounds' and 'iterations' are ignored" % self.__name__)
        handler = self.passlib_handler
        if kwds:
            handler = handler.using(**kwds)
        return handler.hash(password)

    def safe_summary(self, encoded):
        from django.contrib.auth.hashers import mask_hash
        from django.utils.translation import ugettext_noop as _
        handler = self.passlib_handler
        items = [
         (
          _('algorithm'), handler.name)]
        if hasattr(handler, 'parsehash'):
            kwds = handler.parsehash(encoded, sanitize=mask_hash)
            for key, value in iteritems(kwds):
                key = self._translate_kwds.get(key, key)
                items.append((_(key), value))

        return OrderedDict(items)

    def must_update(self, encoded):
        if self._has_rounds:
            subcls = self.passlib_handler.using(min_rounds=self.rounds, max_rounds=self.rounds)
            if subcls.needs_update(encoded):
                return True
        return False


_UNSET = object()

class _PatchManager(object):

    def __init__(self, log=None):
        self.log = log or logging.getLogger(__name__ + '._PatchManager')
        self._state = {}

    def isactive(self):
        return bool(self._state)

    __bool__ = __nonzero__ = isactive

    def _import_path(self, path):
        name, attr = path.split(':')
        obj = __import__(name, fromlist=[attr], level=0)
        while '.' in attr:
            head, attr = attr.split('.', 1)
            obj = getattr(obj, head)

        return (obj, attr)

    @staticmethod
    def _is_same_value(left, right):
        return get_method_function(left) == get_method_function(right)

    def _get_path(self, key, default=_UNSET):
        obj, attr = self._import_path(key)
        return getattr(obj, attr, default)

    def get(self, path, default=None):
        return self._get_path(path, default)

    def getorig(self, path, default=None):
        try:
            value, _ = self._state[path]
        except KeyError:
            value = self._get_path(path)
        else:
            if value is _UNSET:
                return default

        return value

    def check_all(self, strict=False):
        same = self._is_same_value
        for path, (orig, expected) in iteritems(self._state):
            if same(self._get_path(path), expected):
                continue
            msg = 'another library has patched resource: %r' % path
            if strict:
                raise RuntimeError(msg)
            else:
                warn(msg, PasslibRuntimeWarning)

    def _set_path(self, path, value):
        obj, attr = self._import_path(path)
        if value is _UNSET:
            if hasattr(obj, attr):
                delattr(obj, attr)
        else:
            setattr(obj, attr, value)

    def patch(self, path, value, wrap=False):
        current = self._get_path(path)
        try:
            orig, expected = self._state[path]
        except KeyError:
            self.log.debug('patching resource: %r', path)
            orig = current

        self.log.debug('modifying resource: %r', path)
        if not self._is_same_value(current, expected):
            warn('overridding resource another library has patched: %r' % path, PasslibRuntimeWarning)
        if wrap:
            wrapped = orig
            wrapped_by = value

            def wrapper(*args, **kwds):
                return wrapped_by(wrapped, *args, **kwds)

            update_wrapper(wrapper, value)
            value = wrapper
        if callable(value):
            get_method_function(value)._patched_original_value = orig
        self._set_path(path, value)
        self._state[path] = (orig, value)

    @classmethod
    def peek_unpatched_func(cls, value):
        return value._patched_original_value

    def monkeypatch(self, parent, name=None, enable=True, wrap=False):

        def builder(func):
            if enable:
                sep = '.' if ':' in parent else ':'
                path = parent + sep + (name or func.__name__)
                self.patch(path, func, wrap=wrap)
            return func

        if callable(name):
            func = name
            name = None
            builder(func)
            return
        return builder

    def unpatch(self, path, unpatch_conflicts=True):
        try:
            orig, expected = self._state[path]
        except KeyError:
            return

        current = self._get_path(path)
        self.log.debug('unpatching resource: %r', path)
        if not self._is_same_value(current, expected):
            if unpatch_conflicts:
                warn('reverting resource another library has patched: %r' % path, PasslibRuntimeWarning)
            else:
                warn('not reverting resource another library has patched: %r' % path, PasslibRuntimeWarning)
                del self._state[path]
                return
        self._set_path(path, orig)
        del self._state[path]

    def unpatch_all(self, **kwds):
        for key in list(self._state):
            self.unpatch(key, **kwds)