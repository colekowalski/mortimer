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
import hashlib
import datetime

class BaseStore(object):
    """ Base session storage class

    The session storage class is responsible for saving the
    serialized session data to a particular data store. Subclasses
    of this class are responsible for implementing the save, load,
    and delete functionality.
    """
    def __init__(self, **kwargs):
        pass

    def save(self, session_id, data):
        pass

    def load(self, session_id):
        return ""

    def delete(self, session_id):
        pass


class DummyStore(BaseStore):
    """ Dummy session storage class

    This storage class will preform no action. No data will be
    written, read, or deleted when their respective methods
    are called.

    This is probably only useful in testing situations.
    """
    pass


class FileStore(BaseStore):
    """ Store for saving session data to disk

    This store will save serialized session data to disk. By default
    session files will be saved to '/tmp/session/', however this is
    configurable by passing in the path argument when initializing
    the file store.

    The file name of each session will be the session id
    """
    def __init__(self, path='/tmp/', **kwargs):
        super(FileStore, self).__init__(**kwargs)
        self.path = path

    def save(self, sess_id, data):
        """ Save the session data to a file """
        fname = os.path.join(self.path, sess_id)
        with open(fname, 'w') as f:
            f.write(data)

    def load(self, sess_id):
        """ Load the session data from a file """
        fname = os.path.join(self.path, sess_id)
        with open(fname, 'r') as f:
            data = f.read()
        return data

    def delete(self, sess_id):
        fname = os.path.join(self.path, sess_id)
        try:
            os.remove(fname)
        except:
            pass


class Session(dict):
    """ HTTP Session Implementation

    Session data is only deserialized if the session is accessed,
    and only serialized to the store if the session has been modified.

    Optionally, a store implementation can be specified to instruct
    where the session data should be serialized to. By default
    session data will be serialized to the filesystem
    """
    def __init__(self, data=None, session_id=None):
        super(Session, self).__init__()
        self.dirty = False
        self.deleted = False
        self.session_id = session_id
        if data:
            self.update(data)
        if not self.session_id:
            self.session_id = self.gen_session_id()

    def __setitem__(self, key, value):
        """ Add item to the session
        When an item is added, the dirty flag will be set, which
        lets us know that the session must be written out to the
        SessionStore
        """
        self.dirty = True
        dict.__setitem__(self, key, value)

    def gen_session_id(self):
        """ Generate a random session id """
        s = hashlib.md5()
        s.update(str(datetime.datetime.now()))
        s.update(str(random.random()))
        return s.hexdigest()

    def expire(self):
        self.deleted = True

    def delete(self, store=None):
        store.delete(self.session_id)

    def save(self, store=None):
        """ Save the session.
        The session data will only be serialized and written
        out to the SessionStore if any modifications have been
        made, as reported by the self.dirty flag
        """
        if not self.dirty:
            return
        self.dirty = False
        pdata = cPickle.dumps(self)
        store.save(self.session_id, pdata)

    @classmethod
    def load(self, session_id, store=None):
        """ Load a session from the SessionStore given a session id """
        try:
            serialized = store.load(session_id)
            data = cPickle.loads(serialized)
            return Session(data=data, session_id=session_id)
        except:
            return Session(session_id=session_id)
