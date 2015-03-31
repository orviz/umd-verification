
import os

from fabric.api import local
from fabric.colors import red
from fabric.colors import yellow

from umd.base import utils as base_utils
from umd import exception


class Validate(object):
    def _is_executable(self, f):
        is_executable = False
        if os.access(f, os.X_OK):
            is_executable = True
        else:
            print(red(("Could not run check '%s': file is not "
                       "executable" % f)))

        return is_executable

    def run(self, bin_path):
        checklist = []

        bin_path = base_utils.to_list(bin_path)
        for path in bin_path:
            if isinstance(path, (tuple, list)):
                try:
                    fname, args_str = path
                except IndexError:
                    raise exception.ValidateException(("Malformed check "
                                                       "syntax: name: '%s'; "
                                                       "args: '%s'."
                                                       % (path[0], path[1:])))
                if self._is_executable(fname):
                    checklist.append(" ".join(path))
            else:
                if os.path.isdir(path):
                    for root, dirs, files in os.walk(path):
                        for f in files:
                            fname = os.path.join(root, f)
                            if self._is_executable(fname):
                                checklist.append(fname)
                elif os.path.isfile(path) and self._is_executable(path):
                    checklist.append(path)

        for check in checklist:
            print(yellow("Running check '%s'" % check))
            local("./%s" % check)
