import tempfile

from umd.api import info
from umd.base import utils as butils


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
                info(("Creating temporary file '%s' with "
                      "content: %s" % (f.name, r)))

            r = qc_step.runcmd("/opt/glite/yaim/bin/yaim -c -s %s -n %s"
                               % (f.name, " -n ".join(self.nodetype)),
                               chdir=self.config_path,
                               fail_check=False)

        self.post_config()

        return r
