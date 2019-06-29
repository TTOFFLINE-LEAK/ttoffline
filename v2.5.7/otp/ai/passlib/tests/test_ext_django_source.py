from __future__ import absolute_import, division, print_function
import logging
log = logging.getLogger(__name__)
from otp.ai.passlib.utils.compat import suppress_cause
from otp.ai.passlib.ext.django.utils import DJANGO_VERSION, DjangoTranslator, _PasslibHasherWrapper
from otp.ai.passlib.tests.utils import TestCase, TEST_MODE
from .test_ext_django import has_min_django, stock_config, _ExtensionSupport
if has_min_django:
    from .test_ext_django import settings
__all__ = ['HashersTest']
test_hashers_mod = None
hashers_skip_msg = None
if TEST_MODE(max='quick'):
    hashers_skip_msg = "requires >= 'default' test mode"
else:
    if has_min_django:
        import os, sys
        source_path = os.environ.get('PASSLIB_TESTS_DJANGO_SOURCE_PATH')
        if source_path:
            if not os.path.exists(source_path):
                raise EnvironmentError('django source path not found: %r' % source_path)
            if not all(os.path.exists(os.path.join(source_path, name)) for name in ['django', 'tests']):
                raise EnvironmentError('invalid django source path: %r' % source_path)
            log.info('using django tests from source path: %r', source_path)
            tests_path = os.path.join(source_path, 'tests')
            sys.path.insert(0, tests_path)
            try:
                from auth_tests import test_hashers as test_hashers_mod
            except ImportError as err:
                raise suppress_cause(EnvironmentError('error trying to import django tests from source path (%r): %r' % (
                 source_path, err)))
            finally:
                sys.path.remove(tests_path)

        else:
            hashers_skip_msg = 'requires PASSLIB_TESTS_DJANGO_SOURCE_PATH to be set'
            if TEST_MODE('full'):
                sys.stderr.write("\nWARNING: $PASSLIB_TESTS_DJANGO_SOURCE_PATH is not set; can't run Django's own unittests against passlib.ext.django\n")
    else:
        if DJANGO_VERSION:
            hashers_skip_msg = 'django version too old'
        else:
            hashers_skip_msg = 'django not installed'
if test_hashers_mod:
    from django.core.signals import setting_changed
    from django.dispatch import receiver
    from django.utils.module_loading import import_string
    from otp.ai.passlib.utils.compat import get_unbound_method_function

    class HashersTest(test_hashers_mod.TestUtilsHashPass, _ExtensionSupport):
        patchAttr = get_unbound_method_function(TestCase.patchAttr)

        def setUp(self):
            self.load_extension(PASSLIB_CONTEXT=stock_config, check=False)
            from otp.ai.passlib.ext.django.models import adapter
            context = adapter.context
            from django.contrib.auth import hashers
            for attr in ['make_password',
             'check_password',
             'identify_hasher',
             'is_password_usable',
             'get_hasher']:
                self.patchAttr(test_hashers_mod, attr, getattr(hashers, attr))

            from otp.ai.passlib.hash import django_des_crypt
            self.patchAttr(django_des_crypt, 'use_duplicate_salt', False)
            django_to_passlib_name = DjangoTranslator().django_to_passlib_name

            @receiver(setting_changed, weak=False)
            def update_schemes(**kwds):
                if kwds and kwds['setting'] != 'PASSWORD_HASHERS':
                    return
                schemes = [ django_to_passlib_name(import_string(hash_path)()) for hash_path in settings.PASSWORD_HASHERS
                          ]
                if 'hex_md5' in schemes and 'django_salted_md5' not in schemes:
                    schemes.append('django_salted_md5')
                schemes.append('django_disabled')
                context.update(schemes=schemes, deprecated='auto')
                adapter.reset_hashers()

            self.addCleanup(setting_changed.disconnect, update_schemes)
            update_schemes()

            def update_rounds():
                for handler in context.schemes(resolve=True):
                    if 'rounds' not in handler.setting_kwds:
                        continue
                    hasher = adapter.passlib_to_django(handler)
                    if isinstance(hasher, _PasslibHasherWrapper):
                        continue
                    rounds = getattr(hasher, 'rounds', None) or getattr(hasher, 'iterations', None)
                    if rounds is None:
                        continue
                    handler.min_desired_rounds = handler.max_desired_rounds = handler.default_rounds = rounds

                return

            _in_update = [False]

            def update_wrapper(wrapped, *args, **kwds):
                if not _in_update[0]:
                    _in_update[0] = True
                    try:
                        update_rounds()
                    finally:
                        _in_update[0] = False

                return wrapped(*args, **kwds)

            for attr in ['schemes', 'handler', 'default_scheme', 'hash',
             'verify', 'needs_update', 'verify_and_update']:
                self.patchAttr(context, attr, update_wrapper, wrap=True)

            self.patchAttr(adapter, 'django_to_passlib', update_wrapper, wrap=True)

        def tearDown(self):
            self.unload_extension()
            super(HashersTest, self).tearDown()

        _OMIT = lambda self: self.skipTest('omitted by passlib')
        test_pbkdf2_upgrade_new_hasher = _OMIT
        test_check_password_calls_harden_runtime = _OMIT
        test_bcrypt_harden_runtime = _OMIT
        test_pbkdf2_harden_runtime = _OMIT


else:

    class HashersTest(TestCase):

        def test_external_django_hasher_tests(self):
            raise self.skipTest(hashers_skip_msg)