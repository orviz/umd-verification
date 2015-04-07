
from fabric.api import local
from fabric.colors import yellow


class InfoModel(object):
    def __init__(self, pkgtool):
        pkgtool.install(pkgs="glue-validator")
        if pkgtool.os == "sl5":
            pkgtool.install(pkgs="openldap-clients")

    def qc_info_1(self):
        """GlueSchema 1.3 Support."""
        r = local(("glue-validator -H localhost -p 2170 -b o=grid -g glue1 "
                   "-s general -v 3"), capture=True)
        if r:
            print(yellow(r))

    def qc_info_2(self):
        """GlueSchema 2.0 Support."""
        r = local(("glue-validator -H localhost -p 2170 -b o=glue -g glue2 "
                   "-s general -v 3"), capture=True)
        if r:
            print(yellow(r))

    def qc_info_3(self):
        """Middleware Version Information."""
        r = local(("ldapsearch -x -h localhost -p 2170 "
                   "-b GLUE2GroupID=resource,o=glue "
                   "objectclass=GLUE2Endpoint"))
        if r:
            print(yellow(r))

    def run(self):
        self.qc_info_1()
        self.qc_info_2()
        self.qc_info_3()
