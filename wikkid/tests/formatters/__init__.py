#
# Copyright (C) 2010 Wikkid Developers.
#
# This software is licensed under the GNU Affero General Public License
# version 3 (see the file LICENSE).

"""The wikkid tests for the wikkid.formatter package."""

import doctest
import unittest


def test_suite():
    names = [
        'registry',
        'rest',
        'creole',
        'markdown',
        'textile',
        ]
    module_names = ['wikkid.tests.formatters.test_' + name for name in names]
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromNames(module_names)

    suite.addTest(doctest.DocTestSuite('wikkid.contrib.creole_1_1.creole2html'))

    return suite
