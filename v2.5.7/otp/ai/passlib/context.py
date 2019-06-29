from __future__ import with_statement
import re, logging
log = logging.getLogger(__name__)
import threading, time
from warnings import warn
from otp.ai.passlib.exc import ExpectedStringError, ExpectedTypeError, PasslibConfigWarning
from otp.ai.passlib.registry import get_crypt_handler, _validate_handler_name
from otp.ai.passlib.utils import handlers as uh, to_bytes, to_unicode, splitcomma, as_bool, timer, rng, getrandstr
from otp.ai.passlib.utils.binary import BASE64_CHARS
from otp.ai.passlib.utils.compat import iteritems, num_types, irange, PY2, PY3, unicode, SafeConfigParser, NativeStringIO, BytesIO, unicode_or_bytes_types, native_string_types
from otp.ai.passlib.utils.decor import deprecated_method, memoized_property
__all__ = [
 'CryptContext',
 'LazyCryptContext',
 'CryptPolicy']
_UNSET = object()

def _coerce_vary_rounds(value):
    if value.endswith('%'):
        return float(value.rstrip('%')) * 0.01
    try:
        return int(value)
    except ValueError:
        return float(value)


_forbidden_scheme_options = set(['salt'])
_coerce_scheme_options = dict(min_rounds=int, max_rounds=int, default_rounds=int, vary_rounds=_coerce_vary_rounds, salt_size=int)

def _is_handler_registered(handler):
    return get_crypt_handler(handler.name, None) is handler


@staticmethod
def _always_needs_update(hash, secret=None):
    return True


_global_settings = set(['truncate_error', 'vary_rounds'])
_preamble = 'The CryptPolicy class has been deprecated as of Passlib 1.6, and will be removed in Passlib 1.8. '

class CryptPolicy(object):

    @classmethod
    def from_path(cls, path, section='passlib', encoding='utf-8'):
        warn(_preamble + 'Instead of ``CryptPolicy.from_path(path)``, use ``CryptContext.from_path(path)``  or ``context.load_path(path)`` for an existing CryptContext.', DeprecationWarning, stacklevel=2)
        return cls(_internal_context=CryptContext.from_path(path, section, encoding))

    @classmethod
    def from_string(cls, source, section='passlib', encoding='utf-8'):
        warn(_preamble + 'Instead of ``CryptPolicy.from_string(source)``, use ``CryptContext.from_string(source)`` or ``context.load(source)`` for an existing CryptContext.', DeprecationWarning, stacklevel=2)
        return cls(_internal_context=CryptContext.from_string(source, section, encoding))

    @classmethod
    def from_source(cls, source, _warn=True):
        if _warn:
            warn(_preamble + 'Instead of ``CryptPolicy.from_source()``, use ``CryptContext.from_string(path)``  or ``CryptContext.from_path(source)``, as appropriate.', DeprecationWarning, stacklevel=2)
        if isinstance(source, CryptPolicy):
            return source
        if isinstance(source, dict):
            return cls(_internal_context=CryptContext(**source))
        if not isinstance(source, (bytes, unicode)):
            raise TypeError('source must be CryptPolicy, dict, config string, or file path: %r' % (
             type(source),))
        else:
            if any(c in source for c in '\n\r\t') or not source.strip(' \t./\\;:'):
                return cls(_internal_context=CryptContext.from_string(source))
            return cls(_internal_context=CryptContext.from_path(source))

    @classmethod
    def from_sources(cls, sources, _warn=True):
        if _warn:
            warn(_preamble + 'Instead of ``CryptPolicy.from_sources()``, use the various CryptContext constructors  followed by ``context.update()``.', DeprecationWarning, stacklevel=2)
        if len(sources) == 0:
            raise ValueError('no sources specified')
        if len(sources) == 1:
            return cls.from_source(sources[0], _warn=False)
        kwds = {}
        for source in sources:
            kwds.update(cls.from_source(source, _warn=False)._context.to_dict(resolve=True))

        return cls(_internal_context=CryptContext(**kwds))

    def replace(self, *args, **kwds):
        if self._stub_policy:
            warn(_preamble + 'Instead of ``context.policy.replace()``, use ``context.update()`` or ``context.copy()``.', DeprecationWarning, stacklevel=2)
        else:
            warn(_preamble + 'Instead of ``CryptPolicy().replace()``, create a CryptContext instance and use ``context.update()`` or ``context.copy()``.', DeprecationWarning, stacklevel=2)
        sources = [
         self]
        if args:
            sources.extend(args)
        if kwds:
            sources.append(kwds)
        return CryptPolicy.from_sources(sources, _warn=False)

    _context = None
    _stub_policy = False

    def __init__(self, *args, **kwds):
        context = kwds.pop('_internal_context', None)
        if context:
            self._context = context
            self._stub_policy = kwds.pop('_stub_policy', False)
        else:
            if args:
                if len(args) != 1:
                    raise TypeError('only one positional argument accepted')
                if kwds:
                    raise TypeError('cannot specify positional arg and kwds')
                kwds = args[0]
            warn(_preamble + 'Instead of constructing a CryptPolicy instance, create a CryptContext directly, or use ``context.update()`` and ``context.load()`` to reconfigure existing CryptContext instances.', DeprecationWarning, stacklevel=2)
            self._context = CryptContext(**kwds)
        return

    def has_schemes(self):
        if self._stub_policy:
            warn(_preamble + 'Instead of ``context.policy.has_schemes()``, use ``bool(context.schemes())``.', DeprecationWarning, stacklevel=2)
        else:
            warn(_preamble + 'Instead of ``CryptPolicy().has_schemes()``, create a CryptContext instance and use ``bool(context.schemes())``.', DeprecationWarning, stacklevel=2)
        return bool(self._context.schemes())

    def iter_handlers(self):
        if self._stub_policy:
            warn(_preamble + 'Instead of ``context.policy.iter_handlers()``, use ``context.schemes(resolve=True)``.', DeprecationWarning, stacklevel=2)
        else:
            warn(_preamble + 'Instead of ``CryptPolicy().iter_handlers()``, create a CryptContext instance and use ``context.schemes(resolve=True)``.', DeprecationWarning, stacklevel=2)
        return self._context.schemes(resolve=True, unconfigured=True)

    def schemes(self, resolve=False):
        if self._stub_policy:
            warn(_preamble + 'Instead of ``context.policy.schemes()``, use ``context.schemes()``.', DeprecationWarning, stacklevel=2)
        else:
            warn(_preamble + 'Instead of ``CryptPolicy().schemes()``, create a CryptContext instance and use ``context.schemes()``.', DeprecationWarning, stacklevel=2)
        return list(self._context.schemes(resolve=resolve, unconfigured=True))

    def get_handler(self, name=None, category=None, required=False):
        if self._stub_policy:
            warn(_preamble + 'Instead of ``context.policy.get_handler()``, use ``context.handler()``.', DeprecationWarning, stacklevel=2)
        else:
            warn(_preamble + 'Instead of ``CryptPolicy().get_handler()``, create a CryptContext instance and use ``context.handler()``.', DeprecationWarning, stacklevel=2)
        try:
            return self._context.handler(name, category, unconfigured=True)
        except KeyError:
            if required:
                raise
            else:
                return

        return

    def get_min_verify_time(self, category=None):
        warn('get_min_verify_time() and min_verify_time option is deprecated and ignored, and will be removed in Passlib 1.8', DeprecationWarning, stacklevel=2)
        return 0

    def get_options(self, name, category=None):
        if self._stub_policy:
            warn(_preamble + '``context.policy.get_options()`` will no longer be available.', DeprecationWarning, stacklevel=2)
        else:
            warn(_preamble + '``CryptPolicy().get_options()`` will no longer be available.', DeprecationWarning, stacklevel=2)
        if hasattr(name, 'name'):
            name = name.name
        return self._context._config._get_record_options_with_flag(name, category)[0]

    def handler_is_deprecated(self, name, category=None):
        if self._stub_policy:
            warn(_preamble + '``context.policy.handler_is_deprecated()`` will no longer be available.', DeprecationWarning, stacklevel=2)
        else:
            warn(_preamble + '``CryptPolicy().handler_is_deprecated()`` will no longer be available.', DeprecationWarning, stacklevel=2)
        if hasattr(name, 'name'):
            name = name.name
        return self._context.handler(name, category).deprecated

    def iter_config(self, ini=False, resolve=False):
        if self._stub_policy:
            warn(_preamble + 'Instead of ``context.policy.iter_config()``, use ``context.to_dict().items()``.', DeprecationWarning, stacklevel=2)
        else:
            warn(_preamble + 'Instead of ``CryptPolicy().iter_config()``, create a CryptContext instance and use ``context.to_dict().items()``.', DeprecationWarning, stacklevel=2)
        context = self._context
        if ini:

            def render_key(key):
                return context._render_config_key(key).replace('__', '.')

            def render_value(value):
                if isinstance(value, (list, tuple)):
                    value = (', ').join(value)
                return value

            resolve = False
        else:
            render_key = context._render_config_key
            render_value = lambda value: value
        return ((render_key(key), render_value(value)) for key, value in context._config.iter_config(resolve))

    def to_dict(self, resolve=False):
        if self._stub_policy:
            warn(_preamble + 'Instead of ``context.policy.to_dict()``, use ``context.to_dict()``.', DeprecationWarning, stacklevel=2)
        else:
            warn(_preamble + 'Instead of ``CryptPolicy().to_dict()``, create a CryptContext instance and use ``context.to_dict()``.', DeprecationWarning, stacklevel=2)
        return self._context.to_dict(resolve)

    def to_file(self, stream, section='passlib'):
        if self._stub_policy:
            warn(_preamble + 'Instead of ``context.policy.to_file(stream)``, use ``stream.write(context.to_string())``.', DeprecationWarning, stacklevel=2)
        else:
            warn(_preamble + 'Instead of ``CryptPolicy().to_file(stream)``, create a CryptContext instance and use ``stream.write(context.to_string())``.', DeprecationWarning, stacklevel=2)
        out = self._context.to_string(section=section)
        if PY2:
            out = out.encode('utf-8')
        stream.write(out)

    def to_string(self, section='passlib', encoding=None):
        if self._stub_policy:
            warn(_preamble + 'Instead of ``context.policy.to_string()``, use ``context.to_string()``.', DeprecationWarning, stacklevel=2)
        else:
            warn(_preamble + 'Instead of ``CryptPolicy().to_string()``, create a CryptContext instance and use ``context.to_string()``.', DeprecationWarning, stacklevel=2)
        out = self._context.to_string(section=section)
        if encoding:
            out = out.encode(encoding)
        return out


class _CryptConfig(object):
    _scheme_options = None
    _context_options = None
    handlers = None
    schemes = None
    categories = None
    context_kwds = None
    _default_schemes = None
    _records = None
    _record_lists = None

    def __init__(self, source):
        self._init_scheme_list(source.get((None, None, 'schemes')))
        self._init_options(source)
        self._init_default_schemes()
        self._init_records()
        return

    def _init_scheme_list(self, data):
        handlers = []
        schemes = []
        if isinstance(data, native_string_types):
            data = splitcomma(data)
        for elem in data or ():
            if hasattr(elem, 'name'):
                handler = elem
                scheme = handler.name
                _validate_handler_name(scheme)
            else:
                if isinstance(elem, native_string_types):
                    handler = get_crypt_handler(elem)
                    scheme = handler.name
                else:
                    raise TypeError('scheme must be name or CryptHandler, not %r' % type(elem))
            if scheme in schemes:
                raise KeyError('multiple handlers with same name: %r' % (
                 scheme,))
            handlers.append(handler)
            schemes.append(scheme)

        self.handlers = tuple(handlers)
        self.schemes = tuple(schemes)

    def _init_options(self, source):
        norm_scheme_option = self._norm_scheme_option
        norm_context_option = self._norm_context_option
        self._scheme_options = scheme_options = {}
        self._context_options = context_options = {}
        categories = set()
        for (cat, scheme, key), value in iteritems(source):
            categories.add(cat)
            explicit_scheme = scheme
            if not cat and not scheme and key in _global_settings:
                scheme = 'all'
            if scheme:
                key, value = norm_scheme_option(key, value)
                if scheme == 'all' and key not in _global_settings:
                    warn("The '%s' option should be configured per-algorithm, and not set globally in the context; This will be an error in Passlib 2.0" % (
                     key,), PasslibConfigWarning)
                if explicit_scheme == 'all':
                    warn("The 'all' scheme is deprecated as of Passlib 1.7, and will be removed in Passlib 2.0; Please configure options on a per-algorithm basis.", DeprecationWarning)
                try:
                    category_map = scheme_options[scheme]
                except KeyError:
                    scheme_options[scheme] = {cat: {key: value}}
                else:
                    try:
                        option_map = category_map[cat]
                    except KeyError:
                        category_map[cat] = {key: value}
                    else:
                        option_map[key] = value

            else:
                if cat and key == 'schemes':
                    raise KeyError("'schemes' context option is not allowed per category")
                key, value = norm_context_option(cat, key, value)
                if key == 'min_verify_time':
                    continue
                try:
                    category_map = context_options[key]
                except KeyError:
                    context_options[key] = {cat: value}
                else:
                    category_map[cat] = value

        categories.discard(None)
        self.categories = tuple(sorted(categories))
        return

    def _norm_scheme_option(self, key, value):
        if key in _forbidden_scheme_options:
            raise KeyError('%r option not allowed in CryptContext configuration' % (
             key,))
        if isinstance(value, native_string_types):
            func = _coerce_scheme_options.get(key)
            if func:
                value = func(value)
        return (
         key, value)

    def _norm_context_option(self, cat, key, value):
        schemes = self.schemes
        if key == 'default':
            if hasattr(value, 'name'):
                value = value.name
            else:
                if not isinstance(value, native_string_types):
                    raise ExpectedTypeError(value, 'str', 'default')
            if schemes and value not in schemes:
                raise KeyError('default scheme not found in policy')
        else:
            if key == 'deprecated':
                if isinstance(value, native_string_types):
                    value = splitcomma(value)
                else:
                    if not isinstance(value, (list, tuple)):
                        raise ExpectedTypeError(value, 'str or seq', 'deprecated')
                if 'auto' in value:
                    if len(value) > 1:
                        raise ValueError("cannot list other schemes if ``deprecated=['auto']`` is used")
                elif schemes:
                    for scheme in value:
                        if not isinstance(scheme, native_string_types):
                            raise ExpectedTypeError(value, 'str', 'deprecated element')
                        if scheme not in schemes:
                            raise KeyError('deprecated scheme not found in policy: %r' % (
                             scheme,))

            else:
                if key == 'min_verify_time':
                    warn("'min_verify_time' was deprecated in Passlib 1.6, is ignored in 1.7, and will be removed in 1.8", DeprecationWarning)
                else:
                    if key == 'harden_verify':
                        warn("'harden_verify' is deprecated & ignored as of Passlib 1.7.1,  and will be removed in 1.8", DeprecationWarning)
                    else:
                        if key != 'schemes':
                            raise KeyError('unknown CryptContext keyword: %r' % (key,))
        return (
         key, value)

    def get_context_optionmap(self, key, _default={}):
        return self._context_options.get(key, _default)

    def get_context_option_with_flag(self, category, key):
        try:
            category_map = self._context_options[key]
        except KeyError:
            return (
             None, False)

        value = category_map.get(None)
        if category:
            try:
                alt = category_map[category]
            except KeyError:
                pass
            else:
                if value is None or alt != value:
                    return (alt, True)

        return (
         value, False)

    def _get_scheme_optionmap(self, scheme, category, default={}):
        try:
            return self._scheme_options[scheme][category]
        except KeyError:
            return default

    def get_base_handler(self, scheme):
        return self.handlers[self.schemes.index(scheme)]

    @staticmethod
    def expand_settings(handler):
        setting_kwds = handler.setting_kwds
        if 'rounds' in handler.setting_kwds:
            setting_kwds += uh.HasRounds.using_rounds_kwds
        return setting_kwds

    def get_scheme_options_with_flag(self, scheme, category):
        get_optionmap = self._get_scheme_optionmap
        kwds = get_optionmap('all', None).copy()
        has_cat_options = False
        if category:
            defkwds = kwds.copy()
            kwds.update(get_optionmap('all', category))
        allowed_settings = self.expand_settings(self.get_base_handler(scheme))
        for key in set(kwds).difference(allowed_settings):
            kwds.pop(key)

        if category:
            for key in set(defkwds).difference(allowed_settings):
                defkwds.pop(key)

        other = get_optionmap(scheme, None)
        kwds.update(other)
        if category:
            defkwds.update(other)
            kwds.update(get_optionmap(scheme, category))
            if kwds != defkwds:
                has_cat_options = True
        return (kwds, has_cat_options)

    def _init_default_schemes(self):
        get_optionmap = self.get_context_optionmap
        default_map = self._default_schemes = get_optionmap('default').copy()
        dep_map = get_optionmap('deprecated')
        schemes = self.schemes
        if not schemes:
            return
        deps = dep_map.get(None) or ()
        default = default_map.get(None)
        if not default:
            for scheme in schemes:
                if scheme not in deps:
                    default_map[None] = scheme
                    break
            else:
                raise ValueError('must have at least one non-deprecated scheme')

        else:
            if default in deps:
                raise ValueError('default scheme cannot be deprecated')
        for cat in self.categories:
            cdeps = dep_map.get(cat, deps)
            cdefault = default_map.get(cat, default)
            if not cdefault:
                for scheme in schemes:
                    if scheme not in cdeps:
                        default_map[cat] = scheme
                        break
                else:
                    raise ValueError('must have at least one non-deprecated scheme for %r category' % cat)

            elif cdefault in cdeps:
                raise ValueError('default scheme for %r category cannot be deprecated' % cat)

        return

    def default_scheme(self, category):
        defaults = self._default_schemes
        try:
            return defaults[category]
        except KeyError:
            pass

        if not self.schemes:
            raise KeyError('no hash schemes configured for this CryptContext instance')
        return defaults[None]

    def is_deprecated_with_flag(self, scheme, category):
        depmap = self.get_context_optionmap('deprecated')

        def test(cat):
            source = depmap.get(cat, depmap.get(None))
            if source is None:
                return
            if 'auto' in source:
                return scheme != self.default_scheme(cat)
            return scheme in source
            return

        value = test(None) or False
        if category:
            alt = test(category)
            if alt is not None and value != alt:
                return (alt, True)
        return (
         value, False)

    def _init_records(self):
        self._record_lists = {}
        records = self._records = {}
        all_context_kwds = self.context_kwds = set()
        get_options = self._get_record_options_with_flag
        categories = (None, ) + self.categories
        for handler in self.handlers:
            scheme = handler.name
            all_context_kwds.update(handler.context_kwds)
            for cat in categories:
                kwds, has_cat_options = get_options(scheme, cat)
                if cat is None or has_cat_options:
                    records[(scheme, cat)] = self._create_record(handler, cat, **kwds)

        return

    @staticmethod
    def _create_record(handler, category=None, deprecated=False, **settings):
        try:
            subcls = handler.using(relaxed=True, **settings)
        except TypeError as err:
            m = re.match(".* unexpected keyword argument '(.*)'$", str(err))
            if m and m.group(1) in settings:
                key = m.group(1)
                raise KeyError('keyword not supported by %s handler: %r' % (
                 handler.name, key))
            raise

        subcls._Context__orig_handler = handler
        subcls.deprecated = deprecated
        return subcls

    def _get_record_options_with_flag(self, scheme, category):
        kwds, has_cat_options = self.get_scheme_options_with_flag(scheme, category)
        value, not_inherited = self.is_deprecated_with_flag(scheme, category)
        if value:
            kwds['deprecated'] = True
        if not_inherited:
            has_cat_options = True
        return (
         kwds, has_cat_options)

    def get_record(self, scheme, category):
        try:
            return self._records[(scheme, category)]
        except KeyError:
            pass
        else:
            if category is not None and not isinstance(category, native_string_types):
                if PY2 and isinstance(category, unicode):
                    return self.get_record(scheme, category.encode('utf-8'))
                raise ExpectedTypeError(category, 'str or None', 'category')
            if scheme is not None and not isinstance(scheme, native_string_types):
                raise ExpectedTypeError(scheme, 'str or None', 'scheme')
            if not scheme:
                default = self.default_scheme(category)
                record = self._records[(None, category)] = self.get_record(default, category)
                return record

        if category:
            try:
                cache = self._records
                record = cache[(scheme, category)] = cache[(scheme, None)]
                return record
            except KeyError:
                pass

        raise KeyError('crypt algorithm not found in policy: %r' % (scheme,))
        return

    def _get_record_list(self, category=None):
        try:
            return self._record_lists[category]
        except KeyError:
            pass

        value = self._record_lists[category] = [ self.get_record(scheme, category) for scheme in self.schemes
                                               ]
        return value

    def identify_record(self, hash, category, required=True):
        if not isinstance(hash, unicode_or_bytes_types):
            raise ExpectedStringError(hash, 'hash')
        for record in self._get_record_list(category):
            if record.identify(hash):
                return record

        if not required:
            return
        if not self.schemes:
            raise KeyError('no crypt algorithms supported')
        else:
            raise ValueError('hash could not be identified')
        return

    @memoized_property
    def disabled_record(self):
        for record in self._get_record_list(None):
            if record.is_disabled:
                return record

        raise RuntimeError("no disabled hasher present (perhaps add 'unix_disabled' to list of schemes?)")
        return

    def iter_config(self, resolve=False):
        scheme_options = self._scheme_options
        context_options = self._context_options
        scheme_keys = sorted(scheme_options)
        context_keys = sorted(context_options)
        if 'schemes' in context_keys:
            context_keys.remove('schemes')
        value = self.handlers if resolve else self.schemes
        if value:
            yield (
             (None, None, 'schemes'), list(value))
        for cat in (None, ) + self.categories:
            for key in context_keys:
                try:
                    value = context_options[key][cat]
                except KeyError:
                    pass
                else:
                    if isinstance(value, list):
                        value = list(value)
                    yield (
                     (
                      cat, None, key), value)

            for scheme in scheme_keys:
                try:
                    kwds = scheme_options[scheme][cat]
                except KeyError:
                    pass

                for key in sorted(kwds):
                    yield ((cat, scheme, key), kwds[key])

        return


class CryptContext(object):
    _config = None
    _get_record = None
    _identify_record = None

    @classmethod
    def _norm_source(cls, source):
        if isinstance(source, dict):
            return cls(**source)
        if isinstance(source, cls):
            return source
        self = cls()
        self.load(source)
        return self

    @classmethod
    def from_string(cls, source, section='passlib', encoding='utf-8'):
        if not isinstance(source, unicode_or_bytes_types):
            raise ExpectedTypeError(source, 'unicode or bytes', 'source')
        self = cls(_autoload=False)
        self.load(source, section=section, encoding=encoding)
        return self

    @classmethod
    def from_path(cls, path, section='passlib', encoding='utf-8'):
        self = cls(_autoload=False)
        self.load_path(path, section=section, encoding=encoding)
        return self

    def copy(self, **kwds):
        other = CryptContext(_autoload=False)
        other.load(self)
        if kwds:
            other.load(kwds, update=True)
        return other

    def using(self, **kwds):
        return self.copy(**kwds)

    def replace(self, **kwds):
        warn('CryptContext().replace() has been deprecated in Passlib 1.6, and will be removed in Passlib 1.8, it has been renamed to CryptContext().copy()', DeprecationWarning, stacklevel=2)
        return self.copy(**kwds)

    def __init__(self, schemes=None, policy=_UNSET, _autoload=True, **kwds):
        if schemes is not None:
            kwds['schemes'] = schemes
        if policy is not _UNSET:
            warn('The CryptContext ``policy`` keyword has been deprecated as of Passlib 1.6, and will be removed in Passlib 1.8; please use ``CryptContext.from_string()` or ``CryptContext.from_path()`` instead.', DeprecationWarning)
            if policy is None:
                self.load(kwds)
            elif isinstance(policy, CryptPolicy):
                self.load(policy._context)
                self.update(kwds)
            else:
                raise TypeError('policy must be a CryptPolicy instance')
        else:
            if _autoload:
                self.load(kwds)
        return

    def __repr__(self):
        return '<CryptContext at 0x%0x>' % id(self)

    def _get_policy(self):
        return CryptPolicy(_internal_context=self.copy(), _stub_policy=True)

    def _set_policy(self, policy):
        warn('The CryptPolicy class and the ``context.policy`` attribute have been deprecated as of Passlib 1.6, and will be removed in Passlib 1.8; please use the ``context.load()`` and ``context.update()`` methods instead.', DeprecationWarning, stacklevel=2)
        if isinstance(policy, CryptPolicy):
            self.load(policy._context)
        else:
            raise TypeError('expected CryptPolicy instance')

    policy = property(_get_policy, _set_policy, doc='[deprecated] returns CryptPolicy instance tied to this CryptContext')

    @staticmethod
    def _parse_ini_stream(stream, section, filename):
        p = SafeConfigParser()
        if PY3:
            p.read_file(stream, filename)
        else:
            p.readfp(stream, filename)
        return dict(p.items(section))

    def load_path(self, path, update=False, section='passlib', encoding='utf-8'):

        def helper(stream):
            kwds = self._parse_ini_stream(stream, section, path)
            return self.load(kwds, update=update)

        if PY3:
            with open(path, 'rt', encoding=encoding) as (stream):
                return helper(stream)
        else:
            if encoding in ('utf-8', 'ascii'):
                with open(path, 'rb') as (stream):
                    return helper(stream)
            else:
                with open(path, 'rb') as (fh):
                    tmp = fh.read().decode(encoding).encode('utf-8')
                    return helper(BytesIO(tmp))

    def load(self, source, update=False, section='passlib', encoding='utf-8'):
        parse_keys = True
        if isinstance(source, unicode_or_bytes_types):
            if PY3:
                source = to_unicode(source, encoding, param='source')
            else:
                source = to_bytes(source, 'utf-8', source_encoding=encoding, param='source')
            source = self._parse_ini_stream(NativeStringIO(source), section, '<string passed to CryptContext.load()>')
        else:
            if isinstance(source, CryptContext):
                source = dict(source._config.iter_config(resolve=True))
                parse_keys = False
            else:
                if not hasattr(source, 'items'):
                    raise ExpectedTypeError(source, 'string or dict', 'source')
        if parse_keys:
            parse = self._parse_config_key
            source = dict((parse(key), value) for key, value in iteritems(source))
        if update and self._config is not None:
            if not source:
                return
            tmp = source
            source = dict(self._config.iter_config(resolve=True))
            source.update(tmp)
        config = _CryptConfig(source)
        self._config = config
        self._reset_dummy_verify()
        self._get_record = config.get_record
        self._identify_record = config.identify_record
        if config.context_kwds:
            self.__dict__.pop('_strip_unused_context_kwds', None)
        else:
            self._strip_unused_context_kwds = None
        return

    @staticmethod
    def _parse_config_key(ckey):
        parts = ckey.replace('.', '__').split('__')
        count = len(parts)
        if count == 1:
            cat, scheme, key = None, None, parts[0]
        else:
            if count == 2:
                cat = None
                scheme, key = parts
            else:
                if count == 3:
                    cat, scheme, key = parts
                else:
                    raise TypeError('keys must have less than 3 separators: %r' % (
                     ckey,))
        if cat == 'default':
            cat = None
        else:
            if not cat and cat is not None:
                raise TypeError('empty category: %r' % ckey)
        if scheme == 'context':
            scheme = None
        else:
            if not scheme and scheme is not None:
                raise TypeError('empty scheme: %r' % ckey)
        if not key:
            raise TypeError('empty option: %r' % ckey)
        return (cat, scheme, key)

    def update(self, *args, **kwds):
        if args:
            if len(args) > 1:
                raise TypeError('expected at most one positional argument')
            if kwds:
                raise TypeError('positional arg and keywords mutually exclusive')
            self.load(args[0], update=True)
        else:
            if kwds:
                self.load(kwds, update=True)

    def schemes(self, resolve=False, category=None, unconfigured=False):
        schemes = self._config.schemes
        if resolve:
            return tuple(self.handler(scheme, category, unconfigured=unconfigured) for scheme in schemes)
        return schemes

    def default_scheme(self, category=None, resolve=False, unconfigured=False):
        hasher = self.handler(None, category, unconfigured=unconfigured)
        if resolve:
            return hasher
        return hasher.name

    def handler(self, scheme=None, category=None, unconfigured=False):
        try:
            hasher = self._get_record(scheme, category)
            if unconfigured:
                return hasher._Context__orig_handler
            return hasher
        except KeyError:
            pass

        if self._config.handlers:
            raise KeyError('crypt algorithm not found in this CryptContext instance: %r' % (
             scheme,))
        else:
            raise KeyError('no crypt algorithms loaded in this CryptContext instance')

    def _get_unregistered_handlers(self):
        return tuple(handler for handler in self._config.handlers if not _is_handler_registered(handler))

    @property
    def context_kwds(self):
        return self._config.context_kwds

    @staticmethod
    def _render_config_key(key):
        cat, scheme, option = key
        if cat:
            return '%s__%s__%s' % (cat, scheme or 'context', option)
        if scheme:
            return '%s__%s' % (scheme, option)
        return option

    @staticmethod
    def _render_ini_value(key, value):
        if isinstance(value, (list, tuple)):
            value = (', ').join(value)
        else:
            if isinstance(value, num_types):
                if isinstance(value, float) and key[2] == 'vary_rounds':
                    value = ('%.2f' % value).rstrip('0') if value else '0'
                else:
                    value = str(value)
        return value.replace('%', '%%')

    def to_dict(self, resolve=False):
        render_key = self._render_config_key
        return dict((render_key(key), value) for key, value in self._config.iter_config(resolve))

    def _write_to_parser(self, parser, section):
        render_key = self._render_config_key
        render_value = self._render_ini_value
        parser.add_section(section)
        for k, v in self._config.iter_config():
            v = render_value(k, v)
            k = render_key(k)
            parser.set(section, k, v)

    def to_string(self, section='passlib'):
        parser = SafeConfigParser()
        self._write_to_parser(parser, section)
        buf = NativeStringIO()
        parser.write(buf)
        unregistered = self._get_unregistered_handlers()
        if unregistered:
            buf.write('# NOTE: the %s handler(s) are not registered with Passlib,\n# this string may not correctly reproduce the current configuration.\n\n' % (', ').join(repr(handler.name) for handler in unregistered))
        out = buf.getvalue()
        if not PY3:
            out = out.decode('utf-8')
        return out

    mvt_estimate_max_samples = 20
    mvt_estimate_min_samples = 10
    mvt_estimate_max_time = 2
    mvt_estimate_resolution = 0.01
    harden_verify = None
    min_verify_time = 0

    def reset_min_verify_time(self):
        self._reset_dummy_verify()

    def _get_or_identify_record(self, hash, scheme=None, category=None):
        if scheme:
            if not isinstance(hash, unicode_or_bytes_types):
                raise ExpectedStringError(hash, 'hash')
            return self._get_record(scheme, category)
        return self._identify_record(hash, category)

    def _strip_unused_context_kwds(self, kwds, record):
        if not kwds:
            return
        unused_kwds = self._config.context_kwds.difference(record.context_kwds)
        for key in unused_kwds:
            kwds.pop(key, None)

        return

    def needs_update(self, hash, scheme=None, category=None, secret=None):
        if scheme is not None:
            warn("CryptContext.needs_update(): 'scheme' keyword is deprecated as of Passlib 1.7, and will be removed in Passlib 2.0", DeprecationWarning)
        record = self._get_or_identify_record(hash, scheme, category)
        return record.deprecated or record.needs_update(hash, secret=secret)

    @deprecated_method(deprecated='1.6', removed='2.0', replacement='CryptContext.needs_update()')
    def hash_needs_update(self, hash, scheme=None, category=None):
        return self.needs_update(hash, scheme, category)

    @deprecated_method(deprecated='1.7', removed='2.0')
    def genconfig(self, scheme=None, category=None, **settings):
        record = self._get_record(scheme, category)
        strip_unused = self._strip_unused_context_kwds
        if strip_unused:
            strip_unused(settings, record)
        return record.genconfig(**settings)

    @deprecated_method(deprecated='1.7', removed='2.0')
    def genhash(self, secret, config, scheme=None, category=None, **kwds):
        record = self._get_or_identify_record(config, scheme, category)
        strip_unused = self._strip_unused_context_kwds
        if strip_unused:
            strip_unused(kwds, record)
        return record.genhash(secret, config, **kwds)

    def identify(self, hash, category=None, resolve=False, required=False, unconfigured=False):
        record = self._identify_record(hash, category, required)
        if record is None:
            return
        if resolve:
            if unconfigured:
                return record._Context__orig_handler
            return record
        else:
            return record.name
        return

    def hash(self, secret, scheme=None, category=None, **kwds):
        if scheme is not None:
            warn("CryptContext.hash(): 'scheme' keyword is deprecated as of Passlib 1.7, and will be removed in Passlib 2.0", DeprecationWarning)
        record = self._get_record(scheme, category)
        strip_unused = self._strip_unused_context_kwds
        if strip_unused:
            strip_unused(kwds, record)
        return record.hash(secret, **kwds)

    @deprecated_method(deprecated='1.7', removed='2.0', replacement='CryptContext.hash()')
    def encrypt(self, *args, **kwds):
        return self.hash(*args, **kwds)

    def verify(self, secret, hash, scheme=None, category=None, **kwds):
        if scheme is not None:
            warn("CryptContext.verify(): 'scheme' keyword is deprecated as of Passlib 1.7, and will be removed in Passlib 2.0", DeprecationWarning)
        if hash is None:
            self.dummy_verify()
            return False
        record = self._get_or_identify_record(hash, scheme, category)
        strip_unused = self._strip_unused_context_kwds
        if strip_unused:
            strip_unused(kwds, record)
        return record.verify(secret, hash, **kwds)

    def verify_and_update(self, secret, hash, scheme=None, category=None, **kwds):
        if scheme is not None:
            warn("CryptContext.verify(): 'scheme' keyword is deprecated as of Passlib 1.7, and will be removed in Passlib 2.0", DeprecationWarning)
        if hash is None:
            self.dummy_verify()
            return (
             False, None)
        record = self._get_or_identify_record(hash, scheme, category)
        strip_unused = self._strip_unused_context_kwds
        if strip_unused and kwds:
            clean_kwds = kwds.copy()
            strip_unused(clean_kwds, record)
        else:
            clean_kwds = kwds
        if not record.verify(secret, hash, **clean_kwds):
            return (False, None)
        if record.deprecated or record.needs_update(hash, secret=secret):
            return (
             True, self.hash(secret, category=category, **kwds))
        return (
         True, None)
        return

    _dummy_secret = 'too many secrets'

    @memoized_property
    def _dummy_hash(self):
        return self.hash(self._dummy_secret)

    def _reset_dummy_verify(self):
        type(self)._dummy_hash.clear_cache(self)

    def dummy_verify(self, elapsed=0):
        self.verify(self._dummy_secret, self._dummy_hash)
        return False

    def is_enabled(self, hash):
        return not self._identify_record(hash, None).is_disabled

    def disable(self, hash=None):
        record = self._config.disabled_record
        return record.disable(hash)

    def enable(self, hash):
        record = self._identify_record(hash, None)
        if record.is_disabled:
            return record.enable(hash)
        return hash
        return


class LazyCryptContext(CryptContext):
    _lazy_kwds = None

    def __init__(self, schemes=None, **kwds):
        if schemes is not None:
            kwds['schemes'] = schemes
        self._lazy_kwds = kwds
        return

    def _lazy_init(self):
        kwds = self._lazy_kwds
        if 'create_policy' in kwds:
            warn("The CryptPolicy class, and LazyCryptContext's ``create_policy`` keyword have been deprecated as of Passlib 1.6, and will be removed in Passlib 1.8; please use the ``onload`` keyword instead.", DeprecationWarning)
            create_policy = kwds.pop('create_policy')
            result = create_policy(**kwds)
            policy = CryptPolicy.from_source(result, _warn=False)
            kwds = policy._context.to_dict()
        else:
            if 'onload' in kwds:
                onload = kwds.pop('onload')
                kwds = onload(**kwds)
        del self._lazy_kwds
        super(LazyCryptContext, self).__init__(**kwds)
        self.__class__ = CryptContext

    def __getattribute__(self, attr):
        if (not attr.startswith('_') or attr.startswith('__')) and self._lazy_kwds is not None:
            self._lazy_init()
        return object.__getattribute__(self, attr)