
from fabric.api import run
from fabric.colors import green,yellow
from fabric.tasks import Task

import os.path

from umd.base.install.utils import yum


PKG_TOOL = {
    "sl5": yum,
}


class InstallException(Exception):
    pass


class Install(Task):
    """
    Base class for installation/upgrades of UMD products.
    """
    name = "install"

    def __new__(self):
        self.metapkgs

    def _get_pkg(self, url, download_path="/tmp"):
        pkg_base = os.path.basename(url)
        pkg_loc  = os.path.join(download_path,
                                pkg_base)
        run("/usr/bin/wget %s -O %s" % (url,
                                        pkg_loc))
        return pkg_loc

    def run(self, os,
                  epel_release_url,
                  umd_release_url,
                  *args, **kwargs):
        """Base UMD installation.

           Arguments::
                metapkgs        : UMD product metapackage/s.
                os              : operating system tag.
                epel_release_url: EPEL RPM release (URL).
                umd_release_url : UMD RPM release (URL).
        """
        self.pre()

        try:
            do_pkg = PKG_TOOL[os]
        except KeyError:
            raise InstallException("'%s' OS not supported" % os)

        print(yellow("Triggering %s." % self.name))
        do_pkg(action="remove", pkgs="epel-release* umd-release*")
        run("/bin/rm -f /etc/yum.repos.d/UMD-* /etc/yum.repos.d/epel-*")
        print(green("Purged any previous EPEL or UMD repository file."))

        for pkg in (("EPEL", epel_release_url),
                    ("UMD", umd_release_url)):
            pkg_id, pkg_url = pkg
            pkg_loc = self._get_pkg(pkg_url)
            print(green("%s release RPM fetched from %s." % (pkg_id, pkg_url)))
            do_pkg(action="install", pkgs=pkg_loc)
            print(green("%s release package installed." % pkg_id))

        do_pkg(action="install", pkgs="yum-priorities")
        print(green("'yum-priorities' (UMD) requirement installed."))

        print(green("Installing UMD product/s: %s." % self.metapkgs))
        do_pkg(action="install", self.pkgs=metapkgs)
        print(green("UMD product/s installation finished."))

        self.post()

    def pre(self):
        pass

    def post(self):
        pass
