from fabric.api import local
from fabric.colors import green
from fabric.colors import yellow

from umd.base import Deploy


class StormSL5Deploy(Deploy):
    """Single-node Storm deployment."""
    def pre_install(self):
        print(yellow("PRE-install actions."))

        local("/usr/sbin/adduser -M storm")

        print(green("users storm and gridhttps added"))
        print(yellow("END of PRE-install actions."))

    def pre_config(self):
        print(yellow("PRE-config actions."))

        self.pkgtool.install(pkgs=["ntp", "ca-policy-egi-core"])
        print(green("<ntp, ca-policy-egi-core> installed."))

        local("mount -o remount,acl,user_xattr /")
        print(green("Enabled ACLs and Extended Attribute Support in /"))

        print(yellow("END of PRE-config actions."))

    def pre_validate(self):
        print(yellow("PRE-validate actions."))

        pkgs = ["storm-srm-client", "uberftp", "curl",
                "myproxy", "voms-clients", "lcg-util"]
        self.pkgtool.install(pkgs=pkgs)
        print(green("<%s> installed." % ", ".join(pkgs)))

        print(yellow("END of PRE-validate actions."))


sl5 = StormSL5Deploy(
    name="storm-sl5",
    need_cert=True,
    metapkg=["emi-storm-backend-mp", "emi-storm-frontend-mp",
             "emi-storm-globus-gridftp-mp", "emi-storm-gridhttps-mp"],
    nodetype=["se_storm_backend", "se_storm_frontend", "se_storm_gridftp",
              "se_storm_gridhttps"],
    siteinfo=["site-info-storm.def"],
    validate_path=[("bin/user_creds", {"user": "umd", "args": ""}),
                   ("bin/storm", {"user": "umd", "args": ""})])
