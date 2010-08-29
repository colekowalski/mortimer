#!/usr/bin/env python

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import re
import httplib
import util
import session
import view

class RequestHandler(object):
    """ Base request handler class
    
    Subclasses of RequestHandler are responsible for implementing methods
    to handle get/post/etc. The method names will be the name of the HTTP
    method, such as:
        def get(self, id):
            ...
    
    Attributes:
        application -- Instance of WebApplication from which we were called
        env         -- WSGI environment dict
    """
    def __init__(self, application, env):
        self.application = application
        self.env = env
        self.session = None
        self.status = '200'
        self.headers = []
        self.init_request()

    def init_request(self):
        """ Initialize the request
        
        Here we will initialize the request by setting up our session
        and setting some default headers
        """
        self.session = session.Session(self)
        self.headers = [
            ('Content-type', 'text/html; charset=UTF-8')
        ]

    def add_header(self, name, val):
        """ Add a header to our list of headers
        
        Headers are defined in a list of tuples containing the header
        name and header value:
        
            [('Content-type', 'text/html'), ('Set-Cookie', 'cookie data')]
        
        When adding a header to our list of headers, we check if the header
        has been previously defined. If so,  we will first remove the
        prevous header before adding the new header
        
        There can be many set-cookie headers per request. We do not
        replace any previously-existing set-cookie headers when adding
        new set-cookie headers
        """
        ## we can set multiple set-cookie headers
        if name == 'Set-Cookie':
            self.headers.append((name, val))
        for header in self.headers:
            if header[0] == name:
                self.headers.remove(header)
        self.headers.append((name, val))

    def set_content_type(self, ctype):
        """ Convenience method to set the content type """
        self.add_header('Content-type', ctype)

    def set_status(self, status):
        """ Convenience method to set the HTTP status code """
        self.status = status

    def set_cookie(self, data, expires=None, path='/', domain=None):
        """ Create a cookie and append a Set-Cookie header """
        cookie = data
        if expires: cookie += '; expires=%s' %(expires,)
        if path: cookie += '; path=%s' %(path,)
        if domain: cookie += '; domain=%s' %(domain,)
        self.add_header('Set-Cookie', cookie)

    def redirect(self, loc):
        """ Convenience method to send a redirect
        
        We will redirect a user by returning a status of '302 FOUND'
        and setting the Location header in the response
        """
        self.set_status('302 FOUND')
        self.add_header('Location', loc)
        return ''

    @property
    def get_args(self):
        """ Return the parsed query string arguments of the request """
        data = self.env['QUERY_STRING']
        return util.process_get_vars(data)

    @property
    def post_args(self):
        """ Return the parsed post arguments of the request"""
        if self.env['REQUEST_METHOD'] != 'POST':
            return {}
        data = self.env['wsgi.input'].readline()
        return util.process_post_vars(data)

    @property
    def cookies(self):
        """ Return the parsed HTTP cookies """
        try:
            data = self.env['HTTP_COOKIE']
            return util.process_cookie_data(data)
        except:
            return {}

    def execute(self, *args, **kwargs):
        """ Execute our handler
        
        Based on the request method (as passed to us in the WSGI
        environment), execute the appropriate method, passing in
        method arguments based on the URL pattern that was defined.
        """
        method = self.env['REQUEST_METHOD']
        handler = getattr(self, method.lower())
        data = handler(*args, **kwargs)
        ## save the session
        if self.session is not None:
            self.session.save()
        return [data]


class WebApplication(object):
    """ Base web application class
    
    Subclasses of WebApplication will contain a collection of request
    handlers that will make up the web application. It is the responsiblity
    of the subclass instance to define the handlers that the application
    will handle.
    
        class TestApplication(WebApplication):
            def __init__(self):
                self.handlers = [
                    (r'^/$', SomeHandlerClass),
                    (r'^/test/?$', SomeOtherHandlerClass),
                ]
    
    Webapplication instances are directly callable and conform to the WSGI
    specification.
    """
    def __init__(self):
        self.handlers = []

    def find_handler(self, uri):
        """ Find the correct handler
        
        Iterate though our list of handlers, trying to match the request
        URI to the regex defined in our request handler list. If no
        handler is found for the request URI, a 404 exception will be raised
        """
        for h in self.handlers:
            m = re.match(h[0], uri)
            if m is not None:
                return (h[1], m.groups())

        ## no handler found for uri -- raise 404
        raise HTTPError(status=404)

    def __call__(self, env, callback):
        """ Called to execute the request """
        uri = env['PATH_INFO']
        try:
            handler, args = self.find_handler(uri)
            h = handler(self, env)
            ret = h.execute(*args)
            callback(h.status, h.headers)
            return ret
        except HTTPError, e:
            ## if an HTTPError was thrown, send down an error page
            ## based on the thrown HTTP status code
            handler = ErrorRequestHandler(self, env, status=e.status)
            callback(handler.status, handler.headers)
            return handler.execute()
        except:
            ## return a 500 Internal Server Error page if any
            ## other exceptions have been thrown
            handler = ErrorRequestHandler(self, env, status=500)
            callback(handler.status, handler.headers)
            #return handler.execute()
            return e

class ErrorRequestHandler(RequestHandler):
    """ Generate error pages based on HTTP status codes
    
    When supplied with an HTTP status code (most likely from a thrown
    HTTPError), generate an error page with a short status message,
    taken from httplib.responses for the specified status code
    
    Attributes:
        application -- Instance of WebApplication from which we were called
        env         -- WSGI environment dict
        status      -- HTTP status code
    """
    def __init__(self, application, env, status=404):
        super(ErrorRequestHandler, self).__init__(application, env)
        self.status = status
        self.set_content_type('text/plain')
        self.set_status(self.status)

    ## implement our own execute() because we just want to
    ## send down a short status message. We don't need to
    ## all the functionality that our parent class has.
    def execute(self):
        return httplib.responses[self.status]

class HTTPError(Exception):
    """ HTTP error exception
    
    Attributes:
        status -- http status code
    """
    def __init__(self, status=404):
        self.status = status