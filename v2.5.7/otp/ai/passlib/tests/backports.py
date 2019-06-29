from __future__ import with_statement
import logging
log = logging.getLogger(__name__)
import re, sys
from otp.ai.passlib.utils.compat import PY26
__all__ = [
 'TestCase',
 'skip', 'skipIf', 'skipUnless']
try:
    import unittest2 as unittest
except ImportError:
    if PY26:
        raise ImportError("Passlib's tests require 'unittest2' under Python 2.6 (as of Passlib 1.7)")
    import unittest

skip = unittest.skip
skipIf = unittest.skipIf
skipUnless = unittest.skipUnless
SkipTest = unittest.SkipTest

class TestCase(unittest.TestCase):
    if not hasattr(unittest.TestCase, 'assertRegex'):
        assertRegex = unittest.TestCase.assertRegexpMatches
    if not hasattr(unittest.TestCase, 'assertRaisesRegex'):
        assertRaisesRegex = unittest.TestCase.assertRaisesRegexp