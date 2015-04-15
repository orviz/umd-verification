from fabric.colors import green
from fabric.colors import yellow

from umd.base import Deploy


class CreamCEDeploy(Deploy):
    """CREAM CE standalone deployment (configuration via Yaim)."""

    def pre_config(self):
        print(yellow("PRE-config actions."))

        self.pkgtool.install(pkgs="sudo")

        print(green("<sudo> package installed."))
        print(yellow("END of PRE-config actions."))


class CreamCEGridengineDeploy(Deploy):
    """CREAM CE + GridEngine on Scientific Linux
       deployment (configuration via Yaim)."""

    def pre_config(self):
        print(yellow("PRE-config actions."))

        self.pkgtool.install(pkgs=["sudo", "gridengine", "gridengine-qmaster"])

        print(green(("<sudo>, <gridengine> and <gridengine-qmaster> packages "
                     "installed.")))
        print(yellow("END of PRE-config actions."))


standalone = CreamCEDeploy(
    name="creamce-standalone",
    metapkg="emi-cream-ce",
    need_cert=True,
    nodetype="creamCE",
    siteinfo=["site-info-creamCE.def",
              "site-info-SGE_utils.def"],
    validate_path=["bin/cream/",
                   ("bin/certs/check-cert", {
                       "user": "umd",
                       "args": "/etc/grid-security/hostcert.pem"})])

gridenginerized = CreamCEGridengineDeploy(
    name="creamce-gridengine",
    metapkg="emi-cream-ce emi-ge-utils",
    need_cert=True,
    nodetype=["creamCE", "SGE_utils"],
    siteinfo=["site-info-creamCE.def",
              "site-info-SGE_utils.def"],
    validate_path=["bin/cream/",
                   ("bin/certs/check-cert", {
                       "user": "umd",
                       "args": "/etc/grid-security/hostcert.pem"})])
