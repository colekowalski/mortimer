#!/usr/bin/env python

import unittest
import wsgiref.util
import mortimer.web

class FakeWSGIRequest(object):
    def __init__(self):
        self.status = ''
        self.headers = []
        self.environ = {}
        wsgiref.util.setup_testing_defaults(self.environ)

    def set_path_info(self, req_path):
        self.environ['PATH_INFO'] = req_path

    def start_request(self, status, headers):
        self.status = status
        self.headers = headers

    def run_application(self, app):
        return app(self.environ, self.start_request)


class TestWebApplication(unittest.TestCase):
    def setUp(self):
        self.fake_req = FakeWSGIRequest()

    def test_index(self):
        class HelloWorldController(mortimer.web.RequestHandler):
            def get(self):
                return 'Hello, World'
        application = mortimer.web.WebApplication()
        application.router.add_route((r'/$', HelloWorldController))
        iterator = self.fake_req.run_application(application)
        self.assertEqual(self.fake_req.status, '200 OK')
        self.assertEqual(iterator.next(), 'Hello, World')