from fabric.api import local

from umd import exception
from umd.base import utils as base_utils

def yum(action, pkgs):
    local("yum -y %s %s" % (action, " ".join(pkgs)))


def do_pkgtool(os, action, pkgs):
    PKGTOOL = {
        "sl5": yum,
    }

    try:
        return PKGTOOL[os](action, base_utils.to_list(pkgs))
    except KeyError:
        raise exception.InstallException("'%s' OS not supported" % os)
