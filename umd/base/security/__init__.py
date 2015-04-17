from fabric.colors import red

from umd.base import utils as base_utils
from umd.base.security import utils as sec_utils

class Security(object):
    def __init__(self, pkgtool, exceptions):
        self.pkgtool = pkgtool
	self.exceptions = exceptions

    def qc_sec_5(self, **kwargs):
        """World Writable Files check.
	   	(kwargs) known_worldwritable_filelist: list with
				the known world writable files.
	"""
	base_utils.stepprint("QC_SEC_5", "World Writable Files")
	r = base_utils.runcmd(("find / -not \\( -path \"/proc\" -prune \\) "
                               "-type f -perm -002 -exec ls -l {} \;"), 
			       output_file="/tmp/qc_sec_5.out")
	if r:
            ww_filelist = sec_utils.get_filelist_from_find(r)
	    try:
	    	known_ww_filelist = kwargs["known_worldwritable_filelist"]
	    except KeyError:
		known_ww_filelist = []
	    if set(ww_filelist).difference(set(known_ww_filelist)):
		base_utils.userprint(level="FAIL",
				     msg=("Found %s world-writable "
				          "file/s." % len(ww_filelist)),
				     do_abort=True)
	    else:
		base_utils.userprint(level="WARNING",
				     msg=("Found world-writable file/s required "
					  "for operation."))
	else:
	    base_utils.userprint(level="OK",
				 msg="Found no world-writable file.")

        ##if self.pkgtool.os == "sl5":
        ##    pkg_wwf_files = local(("rpm -qalv | egrep '^[-d]([-r][-w][-xs])"
        ##                           "{2}[-r]w'"))
        ##if pkg_wwf_files:
        ##    print(yellow("Detected package world-writable files:\n%s"
        ##                 % pkg_wwf_files))


    def run(self):
        self.qc_sec_5(**self.exceptions["qc_sec_5"])
