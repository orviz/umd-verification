from fabric.api import local
from fabric.colors import yellow


class Security(object):
    def __init__(self, pkgtool):
        self.pkgtool = pkgtool

    def qc_sec_5(self):
        """World Writable Files check."""
        local_wwf_files = local(("find / -not \\( -path \"/proc\" -prune \\) "
                                 "-type f -perm -002 -exec ls -l {} \;"),
                                capture=True)
        if local_wwf_files:
            print(yellow("Detected local world-writable files:\n%s"
                         % local_wwf_files))

        if self.pkgtool.os == "sl5":
            pkg_wwf_files = local(("rpm -qalv | egrep '^[-d]([-r][-w][-xs])"
                                   "{2}[-r]w'"))
        if pkg_wwf_files:
            print(yellow("Detected package world-writable files:\n%s"
                         % pkg_wwf_files))

    def run(self):
        self.qc_sec_5()
