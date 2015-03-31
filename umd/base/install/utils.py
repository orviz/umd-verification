from fabric.api import local

from umd.base import utils as base_utils
from umd import exception


def yum(action, pkgs=None):
    if pkgs:
        local("yum -y %s %s" % (action, " ".join(pkgs)))
    else:
        local("yum -y %s" % action)


class PkgTool(object):
    PKGTOOL = {
        "sl5": yum,
    }
    REPOPATH = {
        "sl5": "/etc/yum.repos.d/"
    }

    def __init__(self, os):
        self.os = os

    def get_path(self):
        return self.REPOPATH[self.os]

    def install(self, pkgs):
        self._exec(action="install", pkgs=pkgs)

    def remove(self, pkgs):
        self._exec(action="remove", pkgs=pkgs)

    def update(self):
        self._exec(action="update")

    def _exec(self, action, pkgs=None):
        try:
            if pkgs:
                return self.PKGTOOL[self.os](action, base_utils.to_list(pkgs))
            else:
                return self.PKGTOOL[self.os](action)
        except KeyError:
            raise exception.InstallException("'%s' OS not supported" % self.os)
