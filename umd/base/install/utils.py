import os.path

from umd.api import runcmd
from umd.base import utils as butils
from umd import exception
from umd import system


def yum(action, pkgs=None, logfile=None):
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

    def _enable_repo(self, repofile):
        runcmd("wget %s -O %s" % (repofile,
                                  os.path.join(self.REPOPATH[system.distname],
                                               os.path.basename(repofile))))

    def get_path(self):
        return self.REPOPATH[system.distname]

    # FIXME(orviz) need to address logfiles some other way
    def install(self, pkgs, repofile=None, logfile=None):
        if repofile:
            self._enable_repo(repofile)
        return self._exec(action="install", pkgs=pkgs, logfile=logfile)

    def remove(self, pkgs, logfile=None):
        return self._exec(action="remove", pkgs=pkgs, logfile=logfile)

    def update(self, logfile=None):
        return self._exec(action="update", logfile=logfile)

    def _exec(self, action, pkgs=None, logfile=None):
        pkgs = butils.to_list(pkgs)
        try:
            if pkgs:
                return self.PKGTOOL[system.distname](action, pkgs)
            else:
                return self.PKGTOOL[system.distname](action)
        except KeyError:
            raise exception.InstallException("'%s' OS not supported"
                                             % system.distname)
