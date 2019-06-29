import os, sys
root_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
sys.path.insert(0, root_dir)
import re, logging
log = logging.getLogger(__name__)
from otp.ai.passlib.utils.compat import print_
__all__ = []
TH_PATH = 'passlib.tests.test_handlers'

def do_hash_tests(*args):
    if not args:
        print TH_PATH
        return
    suffix = ''
    args = list(args)
    while True:
        if args[0] == '--method':
            suffix = '.' + args[1]
            del args[:2]
        else:
            break

    from otp.ai.passlib.tests import test_handlers
    names = [ TH_PATH + ':' + name + suffix for name in dir(test_handlers) if not name.startswith('_') and any(re.match(arg, name) for arg in args)
            ]
    print_(('\n').join(names))
    return not names


def do_preset_tests(name):
    if name == 'django' or name == 'django-hashes':
        do_hash_tests('django_.*_test', 'hex_md5_test')
        if name == 'django':
            print_('passlib.tests.test_ext_django')
    else:
        raise ValueError('unknown name: %r' % name)


def do_setup_gae(path, runtime):
    from otp.ai.passlib.tests.utils import set_file
    set_file(os.path.join(path, 'app.yaml'), 'application: fake-app\nversion: 2\nruntime: %s\napi_version: 1\nthreadsafe: no\n\nhandlers:\n- url: /.*\n  script: dummy.py\n\nlibraries:\n- name: django\n  version: "latest"\n' % runtime)


def main(cmd, *args):
    return globals()[('do_' + cmd)](*args)


if __name__ == '__main__':
    import sys
    sys.exit(main(*sys.argv[1:]) or 0)