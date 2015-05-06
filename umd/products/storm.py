from umd.api import info
from umd.api import runcmd
from umd.base import Deploy


class StormSL5Deploy(Deploy):
    """Single-node Storm deployment."""
    def pre_install(self):
        info("PRE-install actions.")

        runcmd("/usr/sbin/adduser -M storm")

        info("users storm and gridhttps added")
        info("END of PRE-install actions.")

    def pre_config(self):
        info("PRE-config actions.")

        self.pkgtool.install(pkgs=["ntp", "ca-policy-egi-core"])
        info("<ntp, ca-policy-egi-core> installed.")

        runcmd("mount -o remount,acl,user_xattr /")
        info("Enabled ACLs and Extended Attribute Support in /")

        info("END of PRE-config actions.")

    def pre_validate(self):
        info("PRE-validate actions.")

        pkgs = ["storm-srm-client", "uberftp", "curl",
                "myproxy", "voms-clients", "lcg-util"]
        self.pkgtool.install(pkgs=pkgs)
        info("<%s> installed." % ", ".join(pkgs))

        info("END of PRE-validate actions.")


sl5 = StormSL5Deploy(
    name="storm-sl5",
    need_cert=True,
    metapkg=["emi-storm-backend-mp", "emi-storm-frontend-mp",
             "emi-storm-globus-gridftp-mp", "emi-storm-gridhttps-mp"],
    nodetype=["se_storm_backend", "se_storm_frontend", "se_storm_gridftp",
              "se_storm_gridhttps"],
    siteinfo=["site-info-storm.def"],
    qc_specific_id="storm")
