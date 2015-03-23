from fabric.api import local


def yum(action, pkgs):
    local("yum -y %s %s" % (action, " ".join(pkgs)))
