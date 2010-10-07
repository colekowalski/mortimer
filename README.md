Mortimer
========
Mortimer is a small and fast micro web framework conforming to the WSGI
specification. It is designed to be lightweight, and to stay out of your
way.

Installation
------------
To install:
    python setup.py build
    sudo python setup.py install

Example
-------

    import mortimer.web

    class IndexController(mortimer.web.RequestHandler):
        def get(self):
            return 'Hello, World'

    class MyWebApplication(mortimer.web.WebApplication):
        def __init__(self):
            super(MyWebApplication, self).__init__()
            self.routes = [
                (r'/$', IndexController)
            ]
            self.router.add_route_list(self.routes)

    app = MyWebApplication()
    def application(env, cb):
        return app(env, cb)

License (Apache)
----------------

    Licensed under the Apache License, Version 2.0 (the "License"); you may
    not use this file except in compliance with the License. You may obtain
    a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
    License for the specific language governing permissions and limitations
    under the License.