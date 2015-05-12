import os.path

from umd.base.security import utils as sec_utils
from umd.base.utils import QCStep
from umd.config import CFG


class Security(object):
    def __init__(self, pkgtool, cfgtool, ca, exceptions):
        self.pkgtool = pkgtool
        self.cfgtool = cfgtool
        self.ca = ca
        self.exceptions = exceptions

    def qc_sec_2(self, **kwargs):
        """SHA-2 Certificates Support."""
        qc_step = QCStep("QC_SEC_2",
                         "SHA-2 Certificates Support",
                         os.path.join(CFG["log_path"], "qc_sec_2"))

        self.ca.issue_cert(hash="2048",
                           key_prv="/etc/grid-security/hostkey.pem",
                           key_pub="/etc/grid-security/hostcert.pem")

        r = self.cfgtool.run(qc_step)
        if r and r.failed:
            qc_step.print_result("FAIL",
                                 "Configuration failed using SHA-2 certs.",
                                 do_abort=True)
        else:
            qc_step.print_result("OK",
                                 "Product can manage SHA-2 certs.")

    def qc_sec_5(self, **kwargs):
        """World Writable Files check.
            (kwargs) known_worldwritable_filelist: list with
            the known world writable files.
        """
        qc_step = QCStep("QC_SEC_5",
                         "World Writable Files",
                         os.path.join(CFG["log_path"], "qc_sec_5"))

        r = qc_step.runcmd(("find / -not \\( -path \"/proc\" -prune \\) "
                            "-type f -perm -002 -exec ls -l {} \;"),
                           fail_check=False)
        if r:
            ww_filelist = sec_utils.get_filelist_from_find(r)
            try:
                known_ww_filelist = kwargs["known_worldwritable_filelist"]
            except KeyError:
                known_ww_filelist = []
            if set(ww_filelist).difference(set(known_ww_filelist)):
                qc_step.print_result("FAIL",
                                     "Found %s world-writable file/s."
                                     % len(ww_filelist),
                                     do_abort=True)
            else:
                qc_step.print_result("WARNING",
                                     ("Found world-writable file/s "
                                      "required for operation."))
        else:
            qc_step.print_result("OK",
                                 "Found no world-writable file.")

        # if self.pkgtool.os == "sl5":
        #     pkg_wwf_files = local(("rpm -qalv | egrep '^[-d]([-r][-w][-xs])"
        #                            "{2}[-r]w'"))
        #     if pkg_wwf_files:
        #         print(yellow("Detected package world-writable files:\n%s"
        #                      % pkg_wwf_files))

    def run(self):
        self.qc_sec_2()
        # NOTE(orviz): use defaultdict instead of try..except catch
        try:
            self.qc_sec_5(**self.exceptions["qc_sec_5"])
        except KeyError:
            self.qc_sec_5()
