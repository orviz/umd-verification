from fabric.colors import green,yellow
from fabric.tasks import Task

from umd.base.configure import Configure
from umd.base.install import Install


class CreamCEInstallation(Install):
    """
    Standalone CREAM CE deployment.
    """
    def __init__(self, name, metapkgs):
	self.name = name
	self.metapkgs = metapkgs


standalone = CreamCEInstallation(name="creamce-standalone", metapkgs="emi-cream-ce")


#class CreamCEConfiguration(Configure):
#    def pre(self):
#        print(yellow("PRE-config actions."))
#        do_pkg(action="install", pkgs="sudo")
#        print(green("<sudo> package installed."))
#        print(yellow("END of PRE-config actions."))
