
from fabric.tasks import Task

from umd.base.configure import YaimConfig
from umd.base.infomodel import InfoModel
from umd.base.install import Install
from umd.base.install import utils as inst_utils
from umd.base.security import Security
from umd.base import utils
from umd.base.validate import Validate
from umd import exception


class Deploy(Task):
    """Base class for UMD deployments."""
    def __init__(self,
                 name,
                 doc=None,
                 metapkg=[],
                 need_cert=False,
                 nodetype=[],
                 siteinfo=[],
                 qc_specific_id=None,
                 exceptions={}):
        """Arguments:
                name: Fabric command name.
                metapkg: list of UMD metapackages to install.
                need_cert: whether installation type requires a signed cert.
                nodetype: list of YAIM nodetypes to be configured.
                siteinfo: list of site-info files to be used.
                validate_path: path pointing to validate checks.
                    - Accepts both file and directory specification.
                        1) File: with optional arguments in case the check
                                 needs them. In this case the format is a
                                 tuple/list with the check name as the 1st
                                 element and the argument string as the 2nd
                                 element.
                        2) Directory: runs all the executable files located
                                      under it, no matter its depth in the
                                      hierarchy (no arguments accepted).
        """
        self.name = name
        if doc:
            self.__doc__ = doc
        self.metapkg = metapkg
        self.need_cert = need_cert
        self.nodetype = nodetype
        self.siteinfo = siteinfo
        self.qc_specific_id = qc_specific_id
        self.exceptions = exceptions
        self.pkgtool = None
        self.cfgtool = None
        self.ca = None

    def pre_install(self):
        pass

    def post_install(self):
        pass

    def pre_config(self):
        pass

    def post_config(self):
        pass

    def pre_validate(self):
        pass

    def post_validate(self):
        pass

    def _install(self, *args, **kwargs):
        Install(self.pkgtool,
                self.metapkg).run(*args, **kwargs)

    def _security(self, *args, **kwargs):
        Security(self.pkgtool,
                 self.cfgtool,
                 self.ca,
                 self.exceptions).run(*args, **kwargs)

    def _infomodel(self, *args, **kwargs):
        InfoModel(self.pkgtool).run(*args, **kwargs)

    def _validate(self):
        Validate().run(self.qc_specific_id)

    def run(self,
            installation_type,
            repository_url=None,
            epel_release=None,
            umd_release=None,
            yaim_config_path="etc/yaim/"):
        """Runs base deployment.

        Command-line parameters:
            installation_type
                Type of installation: 'install' (from scratch) or 'update'.
            os
                Tag indicating the operating system.
            repository_url
                Repository path with the verification content.
            epel_release (optional)
                Package URL with the EPEL release.
            umd_release (optional)
                Package URL with the UMD release.
            yaim_config_path (optional)
                Path pointing to YAIM configuration files.
        """
        # Packaging tool
        self.pkgtool = inst_utils.PkgTool()

        # Configuration tool
        if self.nodetype and self.siteinfo:
            self.cfgtool = YaimConfig(self.nodetype,
                                      self.siteinfo,
                                      yaim_config_path,
                                      pre_config=self.pre_config,
                                      post_config=self.post_config)
        else:
            raise exception.ConfigException("Configuration not implemented.")

        # Certification Authority
        if self.need_cert:
            # FIXME(orviz) Move to a central/base configuration file (yaml)
            IGTF_REPOFILES = {
                "redhat": ("http://repository.egi.eu/sw/production/cas/1/"
                           "current/repo-files/EGI-trustanchors.repo"),
                "debian": ("http://repository.egi.eu/sw/production/cas/1/"
                           "current/repo-files/egi-trustanchors.list"),
            }
            self.pkgtool.install(
                pkgs="ca-policy-egi-core",
                repofile=IGTF_REPOFILES[self.pkgtool.distname])
            self.ca = utils.OwnCA(
                domain_comp_country="es",
                domain_comp="UMDverification",
                common_name="UMDVerificationOwnCA")
            self.ca.create(trusted_ca_dir="/etc/grid-security/certificates")

        # QC_INST, QC_UPGRADE
        self.pre_install()
        self._install(installation_type,
                      epel_release,
                      umd_release,
                      repository_url=repository_url)
        self.post_install()

        # QC_SEC
        self._security()

        # QC_INFO
        self._infomodel()

        # QC_FUNC
        self.pre_validate()
        self._validate()
        self.post_validate()
