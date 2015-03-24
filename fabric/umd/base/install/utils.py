from fabric.api import local

from umd import exception
from umd.base import utils as base_utils

def yum(action, pkgs):
    if pkgs:
        local("yum -y %s %s" % (action, " ".join(pkgs)))
    else:
        local("yum -y %s" % action)


def do_pkgtool(os, action, pkgs):
    PKGTOOL = {
        "sl5": yum,
    }

    try:
        return PKGTOOL[os](action, base_utils.to_list(pkgs))
    except KeyError:
        raise exception.InstallException("'%s' OS not supported" % os)

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

    def update(self, pkgs):
        self._exec(action="update")

    def _exec(self, action, pkgs):
        try:
            return self.PKGTOOL[self.os](action, base_utils.to_list(pkgs))
        except KeyError:
            raise exception.InstallException("'%s' OS not supported" % self.os)
