
import os.path
import socket

from fabric.api import local


def need_cert(nodetype):
    # YAIM terminology
    NO_CERT = [ "UI",
                "BDII_site",
                "BDII_top",]
    return [node for node in nodetype if node not in NO_CERT]


def generate_cert(nodetype):
    generated = False
    if need_cert(nodetype):
        certdir = "/etc/grid-security"

        if not os.path.exists(certdir):
            os.makedirs(certdir)

        local(("openssl req -new -newkey rsa:4096 -days 10 -nodes -x509 -subj "
               "'/C=ES/ST=Cantabria/L=Santander/O=IFCA/O=Distributed Computing"
               "Department/OU=Jenkins/CN=%s' -keyout %s -out %s"
                % (socket.gethostname(),
                   os.path.join(certdir, "hostkey.pem"),
                   os.path.join(certdir, "hostcert.pem"))))
        generated = True
    return generated
