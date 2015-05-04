
import os.path
import shutil

from umd import exception
from umd.base.utils import QCStep


class Install(object):
    def __init__(self, pkgtool, metapkg):
        self.pkgtool = pkgtool
        self.metapkg = metapkg

    def _enable_verification_repo(self,
                     qc_step,
                     repository_url,
                     download_dir="/tmp/repofiles"):
        r = qc_step.runcmd("wget -P %s -r -l1 --no-parent -A.repo %s"
                           % (download_dir,
                              os.path.join(repository_url, "repofiles")))
        if r.failed:
            qc_step.print_result("FAIL",
                                 "Error retrieving verification repofile.",
                                 do_abort=True)
        repofiles = []
        for path in os.walk(download_dir):
            if path[-1]:
                repofiles = [os.path.join(path[0], f) for f in path[-1]]
        if repofiles:
            repopath = self.pkgtool.get_path()
            for f in repofiles:
                shutil.copy2(f, repopath)

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
        if installation_type == "update":
            qc_step = QCStep("QC_UPGRADE_1", "Upgrade", "/tmp/qc_upgrade_1")
        elif installation_type == "install":
            qc_step = QCStep("QC_INST_1",
                             "Binary Distribution",
                             "/tmp/qc_inst_1")

        r = self.pkgtool.remove(pkgs=["epel-release*", "umd-release*"])
        if r.failed:
            qc_step.userprint("Could not delete [epel/umd]-release packages.")

        if qc_step.runcmd(("/bin/rm -f /etc/yum.repos.d/UMD-* "
                           "/etc/yum.repos.d/epel-*")):
            qc_step.userprint(("Purged any previous EPEL or UMD repository "
                               "file."))

        for pkg in (("EPEL", epel_release_url),
                    ("UMD", umd_release_url)):
            pkg_id, pkg_url = pkg
            pkg_base = os.path.basename(pkg_url)
            pkg_loc = os.path.join("/tmp", pkg_base)
            if qc_step.runcmd("wget %s -O %s" % (pkg_url, pkg_loc)):
                qc_step.userprint("%s release RPM fetched from %s."
                                  % (pkg_id, pkg_url))

            r = self.pkgtool.install(pkgs=[pkg_loc])
            if r.failed:
                qc_step.print_result("FAIL",
                                     "Error while installing %s release."
                                     % pkg_id)
            else:
                qc_step.userprint("%s release package installed." % pkg_id)

        r = self.pkgtool.install(pkgs=["yum-priorities"])
        if r.failed:
            qc_step.userprint("Error while installing 'yum-priorities'.")
        else:
            qc_step.userprint("'yum-priorities' (UMD) requirement installed.")

        if installation_type == "update":
            # 1) Install base (production) version
            r = self.pkgtool.install(pkgs=[self.metapkg])
            if r.failed:
                qc_step.print_result("FAIL",
                                     "Error while installing '%s' packages"
                                     % self.metapkg,
                                     do_abort=True)
            else:
                qc_step.userprint("UMD product/s '%s' installation finished."
                                  % self.metapkg)

            # 2) Enable verification repository
            self._enable_verification_repo(qc_step, repository_url)

            # 3) Update
            r = self.pkgtool.update()
            if r.failed:
                qc_step.print_result("FAIL",
                                     ("Error updating from verification "
                                      "repository."),
                                     do_abort=True)
            else:
                qc_step.print_result("OK",
                                     msg="System successfully updated.")
        elif installation_type == "install":
            # 1) Enable verification repository
            self._enable_verification_repo(qc_step, repository_url)

            # 2) Install verification version
            r = self.pkgtool.install(self.metapkg)
            # NOTE(orviz): missing WARNING case
            if r.failed:
                qc_step.print_result("FAIL",
                                     ("There was a failure installing "
                                      "metapackage '%s'." % self.metapkg),
                                     do_abort=True)
            else:
                qc_step.print_result("OK",
                                     ("Metapackage '%s' installed "
                                      "successfully.." % self.metapkg))
        else:
            raise exception.InstallException(("Installation type '%s' "
                                              "not implemented."
                                              % installation_type))
