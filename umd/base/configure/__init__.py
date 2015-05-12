import tempfile

from fabric.api import local
from fabric.context_managers import lcd

from umd.api import info
from umd.base import utils as butils
from umd import exception


class YaimConfig(object):
    def __init__(self,
                 nodetype,
                 siteinfo,
                 config_path,
                 pre_config,
                 post_config):
        self.nodetype = nodetype
        self.siteinfo = siteinfo
        self.config_path = config_path
        self.pre_config = pre_config
        self.post_config = post_config

    def run(self, qc_step):
        self.pre_config()

        self.nodetype = butils.to_list(self.nodetype)
        self.siteinfo = butils.to_list(self.siteinfo)

        if not self.nodetype or not self.siteinfo:
            raise exception.ConfigException(("Could not run YAIM: Bad "
                                             "nodetype or site-info."))

        with tempfile.NamedTemporaryFile("w+t",
                                         dir=self.config_path,
                                         delete=True) as f:
            for si in self.siteinfo:
                f.write("source %s\n" % si)
            f.flush()

            info(("Creating temporary file '%s' with "
                  "content: %s" % (f.name, f.readlines())))

            # NOTE(orviz) Cannot use 'capture=True': execution gets
            # stalled (defunct)
            with lcd(self.config_path):
                local("/opt/glite/yaim/bin/yaim -c -s %s -n %s"
                      % (f.name, " -n ".join(self.nodetype)))

        self.post_config()
