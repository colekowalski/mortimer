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

def parse_multipart(input, boundary):
    """ Parse multipart/form-data
    
    Parse mime-encoded multipart/form-data into a
    python dictionary. This function returns a tuple
    consisting of post vars, and files.
    
    Attributes:
        input       -- Input data to be parsed
        boundary    -- Field boundary as returned in the content type
    """
    files = {}
    post_args = {}

    ## skip the ending boundary (\r\n--<boundary>--)
    skip = len('\r\n' + '--' + boundary + '--')
    parts = input[:-skip].split('--' + boundary + '\r\n')
    for part in parts:
        end = part.find('\r\n\r\n')
        if end == -1:
            ## if the part does not end in '\r\n\r\n', the
            ## headers are messed up -- better skip this one
            continue
        headers = parse_headers(part[:end])
        name_header = headers.get('Content-Disposition', '')
        if not name_header.startswith('form-data'):
            ## if the header doesn't begin with form-data
            ## it is an invalid multipart/form-data header
            continue
        header_fields = parse_header_fields(name_header)
        ## strip leading and trailing '\r\n'
        data = part[end+4:-2]
        if 'filename' in header_fields:
            name = header_fields.get('name')
            files[name] = {
                'filename': header_fields.get('filename'),
                'content_type': headers.get('Content-Type', 'application/unknown'),
                'size': len(data),
                'file': data,
            }
        else:
            name = header_fields.get('name')
            post_args[name] = data
    return (post_args, files)

def parse_header_fields(header):
    """ Parse header fields into a python dict
    
    Attributes:
        header  -- Header to be parsed
    """
    fields = {}
    for item in header.split(';'):
        kv = item.split('=')
        if len(kv) == 1:
            fields[kv[0].strip()] = None
            continue
        kv = [x.strip() for x in kv]
        fields[kv[0]] = kv[1].strip('"')
    return fields

def parse_headers(header):
    """Parse the HTTP headers
    Parse the HTTP headers according to RFC 2616 section 4.2

    According to the cookie spec, set-cookie headers can not
    be moved, for obvious reasons. In the scope of this function
    the set-cookie headers will be merged for simplicity.
    
    Attributes:
        header  -- Headers string to be parsed
    """
    headers = {}
    last_header = None
    header_pattern = r'^([\w\d\-()<>@,;:\\\"\/\[\]?={}]+):\s*(.*)$'
    for line in header.splitlines():
        ## multi-line header -- append
        if (re.match(r'\s+', line) and last_header is not None):
            headers[last_header] += line
            continue

        m = re.match(header_pattern, line)
        if not m: continue
        token, data = m.groups()
        if token in headers:
            if last_header == 'set-cookie':
                ## the cookie spec does not allow set-cookie headers
                ## to be merged. Here we will merge them for simplicity
                ## this will break retrieving the value of 'set-cookie'
                ## but I don't think we'll need that right now
                headers[token] += '\r\nSet-Cookie: %s' %(data)
            else:
                ## standard merged headers
                headers[token] += ', %s' %(data)
        else:
            ## non-merged header
            headers[token] = data
            last_header = token
    return headers

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

