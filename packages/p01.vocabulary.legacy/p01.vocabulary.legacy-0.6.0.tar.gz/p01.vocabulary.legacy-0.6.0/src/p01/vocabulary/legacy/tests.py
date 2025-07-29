##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: country.py 39 2007-01-28 07:08:55Z roger.ineichen $
"""
#TODO: pass the absolute_import as parameter in globs?
from __future__ import absolute_import
from __future__ import print_function
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
