from fabric.api import run


def yum(action, *pkgs):
    run("yum -y %s %s" % (action, " ".join(pkgs)))
