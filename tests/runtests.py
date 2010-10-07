#!/usr/bin/env python

import unittest

TEST_MODULES = [
    'router_test',
    'webapplication_test',
]

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    suite = unittest.defaultTestLoader.loadTestsFromNames(TEST_MODULES)
    runner.run(suite)
