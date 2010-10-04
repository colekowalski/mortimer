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

import os
import random
import cPickle
from hashlib import sha1
from datetime import datetime

class FileStore(object):
    """ Store for saving session data to disk

    This store will save serialized session data to disk. By default
    session files will be saved to '/tmp/session/', however this is
    configurable by passing in the path argument when initializing
    the file store.

    The file name of each session will be the session id
    """
    def __init__(self, path='/tmp/session/'):
        self.path = path

    def save(self, sess_id, data):
        fname = os.path.join(self.path, sess_id)
        with open(fname, 'w') as f:
            f.write(data)

    def load(self, sess_id):
        data = None
        fname = os.path.join(self.path, sess_id)
        with open(fname, 'r') as f:
            data = f.read()
        return data


class Session(dict):
    """ HTTP Session Implementation

    Session data is only deserialized if the session is accessed,
    and only serialized to the store if the session has been modified.

    Optionally, a store implementation can be specified to instruct
    where the session data should be serialized to. By default
    session data will be serialized to the filesystem
    """
    def __init__(self, req, store=FileStore()):
        self.req = req
        self.dirty = False
        self.session = {}
        self.session_id = self.load_session_id()
        self.store = FileStore()

    def __getitem__(self, key):
        if self.session == {}:
            self.load()
        try:
            return self.session[key]
        except KeyError:
            return None

    def __setitem__(self, key, value):
        self.dirty = True
        self.session[key] = value

    def load_session_id(self):
        try:
            sess_id = self.req.cookies['session_id']
            return sess_id
        except KeyError:
            return None

    def send_session_cookie(self):
        self.req.set_cookie('session_id=%s' %(self.session_id))

    def gen_session_id(self):
        s = sha1()
        s.update(str(datetime.now()))
        s.update(str(random.random()))
        return s.hexdigest()

    def pickle_session(self):
        return cPickle.dumps(self.session)

    def unpickle_session(self, data):
        return cPickle.loads(data)

    def save(self):
        if not self.dirty:
            return
        if self.session_id is None:
            self.session_id = self.gen_session_id()
        self.send_session_cookie()
        pdata = self.pickle_session()
        self.store.save(self.session_id, pdata)

    def load(self):
        try:
            data = self.store.load(self.session_id)
            self.session = self.unpickle_session(data)
        except:
            self.session = {}
