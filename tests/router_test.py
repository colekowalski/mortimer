#!/usr/bin/env python

import unittest
import mortimer.web

class TestRouter(unittest.TestCase):
    def setUp(self):

        self.router = mortimer.web.Router()

    def test_invalid_route(self):
        route = self.router.find_route('/')
        self.assertEqual(route, None)

    def test_add_route(self):
        self.router.add_route((r'/$', None))
        route = self.router.find_route('/')
        self.assertNotEqual(route, None)

    def test_set_routes(self):
        route_list = [
            (r'/$', None),
            (r'/login/?$', None),
        ]
        self.router.set_routes(route_list)
        root = self.router.find_route('/')
        login = self.router.find_route('/login/')
        self.assertNotEqual(root, None)
        self.assertNotEqual(login, None)

    def test_trailing_slash(self):
        self.router.add_route((r'/test/?$', None))
        with_slash = self.router.find_route('/test/')
        without_slash = self.router.find_route('/test')
        self.assertEqual(with_slash, without_slash)

    def test_match(self):
        self.router.add_route((r'/test/(\d)/?', None))
        route = self.router.find_route('/test/7')
        self.assertNotEqual(route, None)
        (handler, groups) = route
        self.assertEqual(groups[0], '7')
