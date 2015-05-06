import os.path
import platform

from umd.api import runcmd
from umd.base import utils as base_utils
from umd import exception


def yum(action, pkgs=None):
    if pkgs:
        r = runcmd("yum -y %s %s" % (action, " ".join(pkgs)))
    else:
        r = runcmd("yum -y %s" % action)
    return r


class PkgTool(object):
    PKGTOOL = {
        "redhat": yum,
    }
    REPOPATH = {
        "redhat": "/etc/yum.repos.d/",
    }

    def __init__(self):
        self.distname, self.version_major = self._get_os()

    def _get_os(self):
        distname, version, distid = platform.dist()
        # major version
        version_major = version.split('.')[0]
        if not version_major.isdigit():
            raise exception.InstallException(("Could not get major OS version "
                                              "for '%s'" % version))
        return distname, version_major

    def _enable_repo(self, repofile):
        local("wget %s -O %s" % (repofile,
                                 os.path.join(self.REPOPATH[self.distname],
                                              os.path.basename(repofile))))

    def get_path(self):
        return self.REPOPATH[self.distname]

    def install(self, pkgs, repofile=None):
        if repofile:
            self._enable_repo(repofile)
        return self._exec(action="install", pkgs=pkgs)

    def remove(self, pkgs):
        return self._exec(action="remove", pkgs=pkgs)

    def update(self):
        return self._exec(action="update")

    def _exec(self, action, pkgs=None):
        try:
            if pkgs:
                return self.PKGTOOL[self.distname](action,
                                                   base_utils.to_list(pkgs))
            else:
                return self.PKGTOOL[self.distname](action)
        except KeyError:
            raise exception.InstallException("'%s' OS not supported"
                                             % self.distname)
