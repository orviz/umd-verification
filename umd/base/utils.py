
import os.path
import socket

from fabric.api import local
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
                with open(os.path.join(trusted_ca_dir,
                                       '.'.join([hash,
                                                 "signing_policy"])), 'w') as f:
                    f.writelines(["access_id_CA\tX509\t'%s'\n" % subject,
                                  "pos_rights\tglobus\tCA:sign\n",
                                  "cond_subjects\tglobus\t'\"/DC=%s/DC=%s/*\"'\n"])

    def issue_cert(self,
                   hostname=socket.getfqdn(),
                   key_prv=None,
                   key_pub=None):
        """Issues a cert.

                hostname: CN value.
                key_prv: Alternate path to store the certificate's private key.
                key_pub: Alternate path to store the certificate's public key.
        """
        with lcd(self.workspace):
            local(("openssl req -newkey rsa:1024 -nodes -sha1 -keyout "
                   "cert.key -keyform PEM -out cert.req -outform PEM "
                   "-subj '/DC=%s/DC=%s/CN=%s'" % (self.domain_comp_country,
                                                   self.domain_comp,
                                                   hostname)))
            local(("openssl x509 -req -in cert.req -CA ca.pem -CAkey ca.key "
                   "-CAcreateserial -out cert.crt -days 1"))

            if key_prv:
                local("cp cert.key %s" % key_prv)
                print(yellow("Private key stored in '%s'." % key_prv))
            if key_pub:
                local("cp cert.crt %s" % key_pub)
                print(yellow("Public key stored in '%s'." % key_pub))
