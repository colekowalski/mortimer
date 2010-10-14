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

import urllib
import httplib

def parse_get_vars(data):
    """ Parse query string into key-value pairs. """
    get = {}
    if data is None or data == '':
        return get
    for p in data.split('&'):
        try:
            (k, v) = p.split('=')
            get[k] = urllib.unquote(v)
        except ValueError:
            pass
    return get

def parse_post_vars(data):
    """ Parse post data into key-value pairs.

    If there are multiple form items of the same name, a list will be
    created containing all the values
    """
    post = {}
    spc = lambda x: x.replace('+', ' ')
    for p in data.split('&'):
        try:
            vals = p.split('=')
            ## convert '+' to ' '
            vals = [spc(v) for v in vals]
            ## unquote the data
            vals = [urllib.unquote(v) for v in vals]

            (k, v) = vals
            if not k in post:
                post[k] = v
            elif isinstance(post[k], list):
                post[k].append(v)
            else:
                post[k] = [post[k], v]
        except ValueError:
            pass
    return post

def parse_cookie_data(data):
    """ Parse cookie data into key-value pairs """
    cookies = {}
    for c in data.split('; '):
        try:
            (k, v) = c.split('=')
            cookies[k] = v
        except ValueError:
            pass
    return cookies

def code_to_status(code):
    """ Convert HTTP code to response string
    The response are pulled from httplib.responses:
        200 => '200 OK'
        404 => '404 NOT FOUND'
        ...

    Attributes:
        code -- HTTP status code
    """
    try:
        return '%s %s' %(str(code), httplib.responses.get(code))
    except:
        raise

