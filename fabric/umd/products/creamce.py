from fabric.colors import green,yellow
from umd.base import Deploy


class StandaloneDeploy(Deploy):
    """CREAM CE standalone deployment (configuration via Yaim)."""

    def pre_config(self):
        print(yellow("PRE-config actions."))

        self.pkgtool(action="install", pkgs="sudo")

        print(green("<sudo> package installed."))
        print(yellow("END of PRE-config actions."))


standalone = StandaloneDeploy(
    name = "creamce-standalone",
    metapkg = "emi-cream-ce",
    nodetype = "creamCE",
    siteinfo = ["site-info-creamCE.def",
                "site-info-SGE_utils.def"])
