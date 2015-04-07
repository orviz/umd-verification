
import collections
import getpass
import os
import pwd

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

    def _handle_user(self, user):
        try:
            pwd.getpwnam(user)
        except KeyError:
            local("useradd -m %s" % user)

    def _get_files_from_dir(self, dir):
        l = []
        for root, dirs, files in os.walk(dir):
            for f in files:
                l.append(os.path.join(root, f))
        return l

    def run(self, bin_path):
        """Executes the checks received.

            bin_path: list of files or directories where the checks are stored.
                      It also allows a tuple/list with the following format:
                        - list[0]: name of the file/directory.
                        - list[1]: dictionary with the metadata. Currently only
                                   'user' and 'args' are considered.
        """
        l = []

        bin_path = base_utils.to_list(bin_path)
        for path in bin_path:
            if isinstance(path, (tuple, list)):
                try:
                    f, meta = path
                except IndexError:
                    raise exception.ValidateException(("Malformed check "
                                                       "syntax: name: '%s'; "
                                                       "args: '%s'."
                                                       % (path[0], path[1:])))

                if isinstance(meta, dict):
                    d = collections.defaultdict(str)
                    for k,v in meta.items():
                        d[k] = v
                    l.append((d["user"], f, d["args"]))
            else:
                l.append((getpass.getuser(), path, ""))

        checklist = []
        for check in l:
            user, path, args = check
            if os.path.isdir(path):
                for f in self._get_files_from_dir(path):
                    checklist.append((user, f, args))
            elif os.path.isfile(path):
                checklist.append(check)

        for check in checklist:
            user, f, args = check
            self._handle_user(user)
            if self._is_executable(f):
                cmd = "./%s" % " ".join([f, args])
                print(yellow("Running check '%s' as user '%s'" % (cmd, user)))
                local("su %s -c '%s'" % (user, cmd))
