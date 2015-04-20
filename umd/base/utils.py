import os
import os.path
import socket

from fabric.api import abort
from fabric.api import local
from fabric.api import puts
from fabric.api import settings
from fabric.colors import blue
from fabric.colors import green
from fabric.colors import red
from fabric.colors import yellow
from fabric.context_managers import lcd

from umd import exception


def to_list(obj):
    if not isinstance(obj, (str, list)):
        raise exception.ConfigException("obj variable type '%s' not supported."
                                        % type(obj))
    elif isinstance(obj, str):
        return [obj]
    return obj


class QCStep(object):
    """Manages all the common functions that are used in a QC step."""
    def __init__(self, id, description, logfile):
        self.id = id
        self.description = description
        self.logfile = logfile

        self._print_header()
        self._remove_last_logfile()

    def _print_header(self):
        """Prints a QC header with the id and description."""
        print("[[%s: %s]]" % (blue(self.id),
                              blue(self.description)))

    def _remove_last_logfile(self):
        for stdtype in ("stdout", "stderr"):
            _fname = '.'.join([self.logfile, stdtype])
            if os.path.exists(_fname):
                os.remove(_fname)

    def userprint(self, msg):
        """Prints info/debug logs."""
        puts("[INFO] %s" % msg)

    def print_result(self, level, msg, do_abort=False):
        """Prints the final result of the current QC step."""
        level_color = {
            "FAIL": red,
            "OK": green,
            "WARNING": yellow,
        }
        msg = "[%s] %s." % (level_color[level](level), msg)
        if do_abort:
            msg = " ".join([msg, ("Check the logs (%s.[stdout|stderr]) for "
                                  "further information." % self.logfile)])
            abort(msg)
        else:
            print(msg)

    def to_file(self, r):
        """Writes Fabric capture result to the given file."""
        def _write(fname, msg):
            with open(fname, 'a') as f:
                f.write(msg)
                f.flush()
        l = []
        if isinstance(r, str):  # exception
            _fname = '.'.join([self.logfile, "stdout"])
            _write(_fname, r)
            l.append(_fname)
        else:
            if r.stdout:
                _fname = '.'.join([self.logfile, "stdout"])
                _write(_fname, r.stdout)
                l.append(_fname)
            if r.stderr:
                _fname = '.'.join([self.logfile, "stderr"])
                _write(_fname, r.stderr)
                l.append(_fname)

        return l

    def runcmd(self, cmd, fail_check=True, log_to_file=True):
        with settings(warn_only=True):
            r = local(cmd, capture=True)

        if log_to_file:
            logs = self.to_file(r)

        if fail_check:
            if r.failed:
                msg = "Error while executing command '%s'."
                if logs:
                    msg = ' '.join([msg, "See more information in logs (%s)."
                                         % ','.join(logs)])
                abort(red(msg % cmd))
                #raise exception.ExecuteCommandException(("Error found while "
                #                                         "executing command: "
                #                                         "'%s' (Reason: %s)"
                #                                         % (cmd, r.stderr)))
        return r


class OwnCA(object):
    """Creates a Certification Authority to sign host certificates."""
    def __init__(self,
                 domain_comp_country,
                 domain_comp,
                 common_name):
        self.domain_comp_country = domain_comp_country
        self.domain_comp = domain_comp
        self.common_name = common_name
        self.workspace = os.path.join("/root/", common_name)

    def create(self, trusted_ca_dir=None):
        """Creates the CA public and private key.

                trusted_ca_dir: if set, it will copy the CA public key and the
                                signing policy file under the trusted CA
                                directory.
        """
        local("mkdir -p %s" % self.workspace)
        with lcd(self.workspace):
            subject = "/DC=%s/DC=%s/CN=%s" % (self.domain_comp_country,
                                              self.domain_comp,
                                              self.common_name)
            local(("openssl req -x509 -nodes -days 1 -newkey rsa:2048 "
                   "-out ca.pem -outform PEM -keyout ca.key -subj "
                   "'%s'" % subject))
            if trusted_ca_dir:
                hash = local("openssl x509 -noout -hash -in ca.pem",
                             capture=True)
                local("cp ca.pem %s" % os.path.join(trusted_ca_dir,
                                                    '.'.join([hash, '0'])))
                with open(os.path.join(
                    trusted_ca_dir,
                    '.'.join([hash, "signing_policy"])), 'w') as f:
                    f.writelines([
                        "access_id_CA\tX509\t'%s'\n" % subject,
                        "pos_rights\tglobus\tCA:sign\n",
                        "cond_subjects\tglobus\t'\"/DC=%s/DC=%s/*\"'\n"
                        % (self.domain_comp_country,
                           self.domain_comp)])

    def issue_cert(self,
                   hostname=socket.getfqdn(),
                   hash="1024",
                   key_prv=None,
                   key_pub=None):
        """Issues a cert.

                hostname: CN value.
                key_prv: Alternate path to store the certificate's private key.
                key_pub: Alternate path to store the certificate's public key.
        """
        with lcd(self.workspace):
            local(("openssl req -newkey rsa:%s -nodes -sha1 -keyout "
                   "cert.key -keyform PEM -out cert.req -outform PEM "
                   "-subj '/DC=%s/DC=%s/CN=%s'" % (hash,
                                                   self.domain_comp_country,
                                                   self.domain_comp,
                                                   hostname)))
            local(("openssl x509 -req -in cert.req -CA ca.pem -CAkey ca.key "
                   "-CAcreateserial -out cert.crt -days 1"))

            if key_prv:
                local("cp cert.key %s" % key_prv)
                puts("[INFO] Private key stored in '%s'." % key_prv)
            if key_pub:
                local("cp cert.crt %s" % key_pub)
                puts("[INFO] Public key stored in '%s'." % key_pub)
