
import os.path
import shutil

from fabric.api import local
from fabric.colors import green
from fabric.colors import yellow

from umd import exception


class Install(object):
    def __init__(self, pkgtool, metapkg):
        self.pkgtool = pkgtool
        self.metapkg = metapkg

    def _get_pkg(self, url, download_path="/tmp"):
        pkg_base = os.path.basename(url)
        pkg_loc = os.path.join(download_path, pkg_base)
        local("wget %s -O %s" % (url, pkg_loc))
        return pkg_loc

    def _enable_repo(self, repo_url, download_dir="/tmp/repofiles"):
        local("wget -P %s -r -l1 --no-parent -A.repo %s"
              % (download_dir,
                 os.path.join(repo_url, "repofiles")), capture=True)

        repofiles = []
        for path in os.walk(download_dir):
            if path[-1]:
                repofiles = [os.path.join(path[0], f) for f in path[-1]]
        if repofiles:
            repopath = self.pkgtool.get_path()
            for f in repofiles:
                shutil.copy2(f, repopath)
                print(yellow("Repository file '%s' now available." % f))

    def run(self,
            installation_type,
            repository_url,
            epel_release_url,
            umd_release_url,
            *args, **kwargs):
        """Runs UMD installation.

           Arguments::
                installation_type: install from scratch ('install') or
                                   update ('update')
                repository_url: base repository URL
                                (with the verification stuff).
                epel_release_url: EPEL release (URL).
                umd_release_url : UMD release (URL).
        """
        self.pkgtool.remove(pkgs=["epel-release*", "umd-release*"])
        local("/bin/rm -f /etc/yum.repos.d/UMD-* /etc/yum.repos.d/epel-*")
        print(green("Purged any previous EPEL or UMD repository file."))

        for pkg in (("EPEL", epel_release_url),
                    ("UMD", umd_release_url)):
            pkg_id, pkg_url = pkg
            pkg_loc = self._get_pkg(pkg_url)
            print(green("%s release RPM fetched from %s." % (pkg_id, pkg_url)))
            self.pkgtool.install(pkgs=[pkg_loc])
            print(green("%s release package installed." % pkg_id))

        self.pkgtool.install(pkgs=["yum-priorities"])
        print(green("'yum-priorities' (UMD) requirement installed."))

        if installation_type == "update":
            print(green("Installing UMD product/s: %s." % self.metapkg))
            self.pkgtool.install(pkgs=[self.metapkg])
            print(green("UMD product/s installation finished."))

            self._enable_repo(repository_url)
            self.pkgtool.update()
        elif installation_type == "install":
            self._enable_repo(repository_url)
            self.pkgtool.install(self.metapkg)
        else:
            raise exception.InstallException(("Installation type '%s' "
                                              "not implemented."
                                              % installation_type))
