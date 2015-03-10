cd confs/yaim/


YAIM_NODE_TYPES=`./generate-siteinfo.py $METAPACKAGE --node-types`
echo ">> YAIM Configuration for <<$YAIM_NODE_TYPES>> selected"


ISSUE_CERT=`./generate-siteinfo.py $METAPACKAGE --requires-cert`
if [ $ISSUE_CERT -eq 1 ] ; then
    echo ">> Issuing certificate under /etc/grid-security"
    [ ! -d /etc/grid-security ] && echo "Directory /etc/grid-security does not exist" && exit 1
    
    openssl req -new -newkey rsa:4096 -days 10 -nodes -x509 -subj "/C=ES/ST=Cantabria/L=Santander/O=IFCA/O=Distributed Computing Department/OU=Jenkins/CN=`hostname -f`" -keyout /etc/grid-security/hostkey.pem -out /etc/grid-security/hostcert.pem
fi


./generate-siteinfo.py $METAPACKAGE
echo ">> Generating site-info.def file with content: `cat site-info.def`"


echo ">> Running YAIM"
IFS='
'
for nt in ${YAIM_NODE_TYPES}; do
    node_types_str+="-n $nt "
done
/opt/glite/yaim/bin/yaim -c -s site-info.def $node_types_str
