import os.path
import re

from fabric.api import abort
from fabric.api import settings
from fabric.context_managers import lcd
from fabric.context_managers import prefix

from umd.api import info
from umd.api import runcmd
from umd.base import Deploy


class NagiosSL5(Deploy):
    "Nagios UMD verification deployment."
    def pre_install(self):
        info("Entering pre-install..")
        # slf5x repo
        runcmd("cp etc/repos/slf5x.repo /etc/yum.repos.d/")
        info(("Added repository slf5x.repo (to resolve python-[lxml&dateutil] "
              "dependencies."))
        # Instructions from https://wiki.egi.eu/wiki/SAMUpdate23
        ## selinux
        r = runcmd("getenforce")
        if not re.match("^disabled$", r, flags=re.I):
            runcmd("setenforce 0")
            runcmd(("sed -i 's/^SELINUX=.*/SELINUX=disabled/' "
                   "/etc/selinux/config"))
            info(("SELINUX has been disabled (prior status '%s'). System needs "
                  "to be manually rebooted."))
            abort()
        ## sam repo
        if not os.path.exists("/etc/yum.repos.d/sam.repo"):
            sam_repofile_url = ("http://repository.egi.eu/sw/production/sam/1/"
                                "repofiles/sam.repo")
            self.pkgtool.enable_repo(sam_repofile_url)
            info("SAM repo added.")
        ## os/epel repos - even though instructions say 'mysql51', it must
        ## be 'mysql' (otherwise there are dependency issues)
        for repofile in ["epel.repo", "sl.repo", "sl-security.repo"]:
            with lcd("/etc/yum.repos.d"):
                r = runcmd(('[ -z "`grep \"mysql\*\" %s`" ] && '
                           'sed -i "/\[*\]/a exclude=mysql\*" %s ; '
                           'echo $?' % (repofile, repofile)))
                if not r:
                    info("Parameter 'exclude=mysql*' added to repository "
                         "file %s" % os.path.join("/etc/yum.repos.d", repofile))

    def pre_config(self):
        info("Entering pre-config..")
        # mysql
        ## running?
        r = runcmd("ps aux | grep [m]ysqld", fail_check=False)
        if not r or r.failed:
            runcmd("/etc/init.d/mysqld start")
            info("mysqld service started.")
        ## correct admin password?
        with lcd("etc/yaim"):
            mysql_password = runcmd("source %s && echo $MYSQL_PASSWORD" % self.siteinfo[0])
            r = runcmd(("mysql -u root --password=%s -e 'show databases' "
                        "2>&1 > /dev/null" % mysql_password), fail_check=False)
            if r.failed:
                runcmd("mysqladmin -u root password %s" % mysql_password)
                info("MySQL admin password successfully set.")
        # yaim
        ## remove not needed YAIM functions
        node_info_file = "/opt/glite/yaim/node-info.d/glite-sitenagios"
        runcmd("cp %s %s.bkp" % (node_info_file, node_info_file),
               fail_check=False)
        for func in ["voms2htpasswd", "ggus"]:
            runcmd("sed -i '/%s/d' %s" % (func, node_info_file))
            info(("Function matching '%s' removed from YAIM node "
                  "configuration." % func))

    def post_config(self):
        info("Entering post-config..")
        #1 auth -FIXME(orviz) auth should not be disabled-
        #1.1 disable Apache basic auth
        httpd_restart = False
        for pattern in ["SSL", "Auth", "require", "Require"]:
            r = runcmd("sed -i '/%s/s/^/#/' /etc/httpd/conf.d/nagios.conf"
                       % pattern, fail_check=False)
            if not r.failed:
                httpd_restart = True
                info("Commented Apache directives matching '%s'" % pattern)
        if httpd_restart:
            runcmd("/etc/init.d/httpd restart")
            info("Disabled Nagios basic authorization.")

        #1.2 disable nagios auth (use_authentication=0 in /etc/nagios/cgi.cfg)
        if runcmd("grep use_authentication /etc/nagios/cgi.cfg").split('=')[-1] == '1':
            runcmd("sed -i 's/use_authentication=1/use_authentication=0/g' /etc/nagios/cgi.cfg")
            info("Nagios authentication has been disabled.")

        #2 Set shell for nagios user
        if runcmd("getent passwd nagios").split(':')[-1] != "/bin/sh":
            runcmd("chsh -s /bin/sh nagios")
            info("Changed default shell to '/bin/sh' for user 'nagios'.")

        #3 Edit /usr/lib/perl5/vendor_perl/5.8.5/NCG/LocalMetrics/Hash.pm (not needed in test23!!)
        ## $WLCG_NODETYPE->{site}->{'sBDII'} = ['org.nagios.BDII-Check','org.bdii.Freshness','org.bdii.Entries'];
        ## $WLCG_NODETYPE->{site}->{'Site-BDII'} = ['org.nagios.BDII-Check','org.bdii.Freshness','org.bdii.Entries'];

        #4 Correct paths in /etc/nagios/resource.cfg
        pass

nagios = NagiosSL5(
    name="nagios-verification",
    metapkg=["emi-bdii-site", "nagios", "sam-nagios"],
    need_cert=True,
    nodetype=["BDII_site", "SITENAGIOS", "SAM_NAGIOS"],
    siteinfo=["site-info-nagios.def"])
