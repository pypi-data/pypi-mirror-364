##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: tests.py 27 2007-01-28 06:02:30Z roger.ineichen $
"""
from __future__ import absolute_import, print_function, unicode_literals

__docformat__ = 'restructuredtext'

import unittest
import doctest


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            globs={'print_function': print_function}
            ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
