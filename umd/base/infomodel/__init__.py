import ldap

from umd.base.infomodel import utils as info_utils
from umd.base import utils as base_utils
from umd import exception


class InfoModel(object):
    def __init__(self, pkgtool):
        pkgtool.install(pkgs="glue-validator")
        if pkgtool.os == "sl5":
            pkgtool.install(pkgs="openldap-clients")

    def _run_validator(self, glue_version):
        if glue_version == "glue1":
            cmd = ("glue-validator -H localhost -p 2170 -b o=grid "
                   "-g glue1 -s general -v 3")
            output_file = "/tmp/qc_info_1.out"
            version = "1.3"
        elif glue_version == "glue2":
            cmd = ("glue-validator -H localhost -p 2170 -b o=glue "
                   "-g glue2 -s general -v 3")
            output_file = "/tmp/qc_info_2.out"
            version = "2.0"

        r = base_utils.runcmd(cmd,
                              output_file=output_file,
                              fail_check=False)
        summary = info_utils.get_gluevalidator_summary(r)
        if summary:
            if summary["errors"] != '0':
                base_utils.userprint(level="FAIL",
                                     msg=("Found %s errors while validating "
                                          "GlueSchema v%s support"
                                          % (summary["errors"]), version),
                                     do_abort=True)
            elif summary["warnings"] != '0':
                base_utils.userprint(level="WARNING",
                                     msg=("Found %s warnings while validating "
                                          "GlueSchema v%s support"
                                          % (summary["warnings"], version)))
            elif summary["info"] != '0':
                base_utils.userprint(level="OK",
                                     msg=("Found no errors or warnings while "
                                          "validating GlueSchema v%s support"
                                          % version))
        else:
            raise exception.InfoModelException(("Cannot parse glue-validator "
                                                "output: %s" % r))

    def _run_version_check(self):
        conn = ldap.initialize("ldap://localhost:2170")
        try:
            ldap_result = conn.search_s(
                "GLUE2GroupID=resource,o=glue",
                ldap.SCOPE_SUBTREE,
                "objectclass=GLUE2Endpoint",
                attrlist=[
                    "GLUE2EndpointImplementationVersion",
                    "GLUE2EntityOtherInfo"])

            base_utils.to_file("/tmp/qc_info_3.out",
                               info_utils.ldifize(ldap_result))

            for dn, attrs in ldap_result:
                try:
                    version_list = attrs["GLUE2EndpointImplementationVersion"]
                except KeyError:
                    return False, ("No implementation version found for DN: "
                                   "%s" % dn)
                try:
                    d = dict([attr.split('=', 1)
                              for attr in attrs["GLUE2EntityOtherInfo"]])
                    version_list.append(d["MiddlewareVersion"])
                except KeyError:
                    return False, "No middleware version found for DN: %s" % dn

                for version in version_list:
                    if not info_utils.validate_version(version):
                        return False, "Found a non-valid version: %s" % version
            return True
        finally:
            conn.unbind_s()

    def qc_info_1(self):
        """GlueSchema 1.3 Support."""
        base_utils.stepprint("QC_INFO_1", "GlueSchema 1.3 Support")
        self._run_validator("glue1")

    def qc_info_2(self):
        """GlueSchema 2.0 Support."""
        base_utils.stepprint("QC_INFO_2", "GlueSchema 2.0 Support")
        self._run_validator("glue2")

    def qc_info_3(self):
        """Middleware Version Information."""
        base_utils.stepprint("QC_INFO_3", "Middleware Version Information")
        r, msg = self._run_version_check()
        if r:
            base_utils.userprint(level="OK", msg=msg)
        else:
            base_utils.userprint(level="WARNING", msg=msg)

    def run(self):
        self.qc_info_1()
        self.qc_info_2()
        self.qc_info_3()
