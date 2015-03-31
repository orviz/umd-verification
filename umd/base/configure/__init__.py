
from fabric.api import local
from fabric.colors import green
from fabric.colors import yellow
from fabric.context_managers import lcd
from fabric.context_managers import prefix

import tempfile

from umd.base import utils as base_utils


class YaimConfig(object):
    def __init__(self, nodetype, siteinfo):
        self.nodetype = nodetype
        self.siteinfo = siteinfo

    def run(self, config_path):
        self.nodetype = base_utils.to_list(self.nodetype)
        self.siteinfo = base_utils.to_list(self.siteinfo)

        with tempfile.NamedTemporaryFile("w+t",
                                         dir=config_path,
                                         delete=True) as f:
            for si in self.siteinfo:
                f.write("source %s\n" % si)
            f.flush()

            print(green("Creating temporary file '%s' with content:" % f.name))
            local("cat %s" % f.name)

            with lcd(config_path):
                with prefix("source %s" % f.name):
                    local("/opt/glite/yaim/bin/yaim -c -s %s -n %s"
                          % (f.name, " -n ".join(self.nodetype)))
