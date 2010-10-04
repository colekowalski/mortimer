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

import jinja2

class Jinja2View(object):
    """ View controller using Jinja2

    Attributes:
        path -- file path to the jinja2 templates
    """
    def __init__(self, path=None):
        self.path = path
        self.loader = None
        self.environment = None

        ## load the env is path is given
        if self.path is not None:
            self.setup_environment()

    def set_view_path(path):
        self.path = path;
        self.setup_environment()

    def setup_environment(self):
        self.loader = jinja2.FileSystemLoader(self.path)
        self.environment = jinja2.Environment(loader=self.loader)

    def render(self, template, *args, **kwargs):
        template = self.environment.get_template(template)
        return template.render(*args, **kwargs).encode()
