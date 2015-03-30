from fabric.colors import green
from fabric.colors import yellow
from umd.base import Deploy


class StandaloneDeploy(Deploy):
    """CREAM CE standalone deployment (configuration via Yaim)."""

    def pre_config(self):
        print(yellow("PRE-config actions."))

        self.pkgtool.install(pkgs="sudo")

        print(green("<sudo> package installed."))
        print(yellow("END of PRE-config actions."))


standalone = StandaloneDeploy(
    name="creamce-standalone",
    metapkg="emi-cream-ce",
    need_cert=True,
    nodetype="creamCE",
    siteinfo=["site-info-creamCE.def",
              "site-info-SGE_utils.def"],
    validate_path=["bin/cream/", ("bin/certs/check-cert",
                                  "/etc/grid-security/hostcert.pem")])
