
import os

from fabric.colors import red
from fabric.colors import yellow
from fabric.context_managers import lcd
from umd.base import utils as base_utils

class Validate(object):
    def run(self, bin_path):
        bin_path = base_utils.to_list(bin_path)

        for path in bin_path:
            for root, dirs, files in os.walk(path):
                for f in files:
                    fname = os.path.join(root, f)
                    if os.access(fname, os.X_OK):
                        print(yellow("Running check '%s'" % fname))
                        local("./%s" % fname)
                    else:
                        print(red(("Could not run check '%s': file is not "
                                   "executable" % fname)))

