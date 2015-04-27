
import collections
import os
import pwd
import yaml

from fabric.api import puts

from umd.base.utils import QCStep


QC_SPECIFIC_FILE = "etc/qc_specific.yaml"


class Validate(object):
    def _is_executable(self, f):
        """File executable check."""
        is_executable = False
        if os.access(f, os.X_OK):
            is_executable = True

        return is_executable

    def _get_files_from_dir(self, dir):
        """Returns the list of files contained within a given directory."""
        l = []
        for root, dirs, files in os.walk(dir):
            for f in files:
                l.append(os.path.join(root, f))
        return l

    def _handle_user(self, qc_step, user):
        """Assures that the given user exists (creates it if needed)."""
        try:
            pwd.getpwnam(user)
        except KeyError:
            if user:
                qc_step.runcmd("useradd -m %s" % user)

    def _get_checklist(self, config):
        """Returns a list of 4-item (description, user, filename, args)
           tuples."""
        l = []
        for checkpath, checkdata in config.items():
            d = collections.defaultdict(str)
            for k, v in checkdata.items():
                d[k] = v
            l.append((d["description"],
                      d["user"],
                      checkpath,
                      d["args"]))

        checklist = []
        for check in l:
            description, user, path, args = check
            if os.path.isdir(path):
                for f in self._get_files_from_dir(path):
                    checklist.append((description, user, f, args))
            elif os.path.isfile(path):
                checklist.append(check)

        return checklist

    def _run_checks(self, qc_step, config):
        """Runs the checks received."""
        failed_checks = []
        for check in self._get_checklist(config):
            description, user, f, args = check
            qc_step.userprint("Probe '%s'" % description)

            cmd = "./%s" % " ".join([f, args])
            if user:
                cmd = ' '.join(["su %s -c" % user, cmd])

            cmd_failed = False
            if not self._is_executable(f):
                result = ("Could not run check '%s': file is not "
                          "executable" % f)
                cmd_failed = True
            else:
                self._handle_user(qc_step, user)
                r = qc_step.runcmd(cmd)
                cmd_failed = r.failed
                result = r

            if cmd_failed:
                qc_step.userprint("Command '%s' failed: %s" % (cmd, result))
                failed_checks.append(cmd)
            else:
                qc_step.userprint("Command '%s' ended OK with result: %s"
                                  % (cmd, result))
        return failed_checks

    def qc_func_1(self, config):
        """Basic Funcionality Test."""
        qc_step = QCStep("QC_FUNC_1",
                         "Basic Funcionality Test.",
                         "/tmp/qc_func_1")

        if config:
            failed_checks = self._run_checks(qc_step, config)
            if failed_checks:
                qc_step.print_result("FAIL",
                                     "Commands failed: %s" % failed_checks,
                                     do_abort=False)
            else:
                qc_step.print_result("OK",
                                     ("Basic functionality probes ran "
                                      "successfully."))
        else:
            qc_step.print_result("OK",
                                 "No definition found for QC_FUNC_1.")

    def qc_func_2(self, config):
        """New features/bug fixes testing."""
        qc_step = QCStep("QC_FUNC_2",
                         "New features/bug fixes testing.",
                         "/tmp/qc_func_2")

        if config:
            failed_checks = self._run_checks(qc_step, config)
            if failed_checks:
                qc_step.print_result("FAIL",
                                     "Commands failed: %s" % failed_checks,
                                     do_abort=False)
            else:
                qc_step.print_result("OK",
                                     "Fix/features probes ran successfully.")
        else:
            qc_step.print_result("OK",
                                 "No definition found for QC_FUNC_2.")

    def run(self, qc_specific_id):
        if qc_specific_id:
            try:
                with open(QC_SPECIFIC_FILE) as f:
                    d = yaml.load(f)
                    try:
                        d[qc_specific_id]
                    except KeyError:
                        puts("[INFO] QC-specific ID '%s' definition not found "
                             "in configuration file '%s'"
                             % (qc_specific_id, QC_SPECIFIC_FILE))

                    config = collections.defaultdict(dict)
                    for k, v in d[qc_specific_id].items():
                        config[k] = v

                    self.qc_func_1(config["qc_func_1"])
                    self.qc_func_2(config["qc_func_2"])
            except IOError:
                puts("[INFO] Could not load QC-specific config file: %s"
                     % QC_SPECIFIC_FILE)
        else:
            puts(("[INFO] No QC-specific ID provided: no specific QC probes "
                  "will be ran."))
