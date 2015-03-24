
from fabric.api import local
from fabric.colors import green,yellow
from fabric.tasks import Task

import os.path


class Install(object):
    def __init__(self, pkgtool, metapkg):
        self.pkgtool = pkgtool
        self.metapkg = metapkg

    def _get_pkg(self, url, download_path="/tmp"):
        pkg_base = os.path.basename(url)
        pkg_loc  = os.path.join(download_path,
                                pkg_base)
        local("/usr/bin/wget %s -O %s" % (url,
                                          pkg_loc))
        return pkg_loc

    def run(self, epel_release_url,
                  umd_release_url,
                  *args, **kwargs):
        """Runs UMD installation.

           Arguments::
                os              : operating system tag.
                epel_release_url: EPEL RPM release (URL).
                umd_release_url : UMD RPM release (URL).
        """
        self.pkgtool(action="remove", pkgs=["epel-release*", "umd-release*"])
        local("/bin/rm -f /etc/yum.repos.d/UMD-* /etc/yum.repos.d/epel-*")
        print(green("Purged any previous EPEL or UMD repository file."))

        for pkg in (("EPEL", epel_release_url),
                    ("UMD", umd_release_url)):
            pkg_id, pkg_url = pkg
            pkg_loc = self._get_pkg(pkg_url)
            print(green("%s release RPM fetched from %s." % (pkg_id, pkg_url)))
            self.pkgtool(action="install", pkgs=[pkg_loc])
            print(green("%s release package installed." % pkg_id))

        self.pkgtool(action="install", pkgs=["yum-priorities"])
        print(green("'yum-priorities' (UMD) requirement installed."))

        print(green("Installing UMD product/s: %s." % self.metapkg))
        self.pkgtool(action="install", pkgs=[self.metapkg])
        print(green("UMD product/s installation finished."))
