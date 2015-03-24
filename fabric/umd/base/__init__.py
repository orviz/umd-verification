
from fabric.tasks import Task

from umd.base.install import Install
from umd.base.install import utils as inst_utils
from umd.base.configure import YaimConfig



class Deploy(Task):
    """Base class for UMD deployments."""
    def __init__(self, name, metapkg=[], nodetype=[], siteinfo=[]):
        """Arguments:
                name: Fabric command name.
                metapkg: list of UMD metapackages to install.
                nodetype: list of YAIM nodetypes to be configured.
                siteinfo: list of site-info files to be used.
        """
        self.name = name
        self.metapkg = metapkg
        self.nodetype = nodetype
        self.siteinfo = siteinfo
        self.os = None

    def pkgtool(self, action, pkgs):
        inst_utils.do_pkgtool(self.os, action, pkgs)

    def pre_install(self):
        pass

    def post_install(self):
        pass

    def pre_config(self):
        pass

    def post_config(self):
        pass

    def _install(self, epel_release, umd_release):
        Install(self.pkgtool,
                self.metapkg).run(epel_release,
                                  umd_release)

    def _config(self, config_path):
        YaimConfig(self.nodetype,
                   self.siteinfo).run(config_path)

    def run(self,
            os,
            epel_release=None,
            umd_release=None,
            yaim_config_path="etc/yaim/"):
        """
        Runs base deployment.

        Command-line parameters:
            os
                Tag indicating the operating system.
            epel_release (optional)
                Package URL with the EPEL release.
            umd_release (optional)
                Package URL with the UMD release.
            yaim_config_path (optional)
                Path pointing to YAIM configuration files.
        """
        self.os = os

        self.pre_install()
        self._install(epel_release, umd_release)
        self.post_install()

        self.pre_config()
        self._config(yaim_config_path)
        self.post_config()
