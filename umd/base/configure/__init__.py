
from fabric.context_managers import lcd
# from fabric.context_managers import prefix

import tempfile

from umd.base import utils as base_utils


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

        self.nodetype = base_utils.to_list(self.nodetype)
        self.siteinfo = base_utils.to_list(self.siteinfo)

        with tempfile.NamedTemporaryFile("w+t",
                                         dir=self.config_path,
                                         delete=True) as f:
            for si in self.siteinfo:
                f.write("source %s\n" % si)
            f.flush()

            r = qc_step.runcmd("cat %s" % f.name,
                               fail_check=False,
                               log_to_file=False)
            if r:
                qc_step.userprint(("Creating temporary file '%s' with "
                                   "content: %s" % (f.name, r)))

            with lcd(self.config_path):
                # FIXME(orviz): this is not supported on SL6(?)
                # with prefix("source %s" % f.name):
                r = qc_step.runcmd("/opt/glite/yaim/bin/yaim -c -s %s -n %s"
                                   % (f.name, " -n ".join(self.nodetype)),
                                   fail_check=False)

        self.post_config()

        return r
