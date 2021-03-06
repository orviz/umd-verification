#!/bin/sh -e

# ops.vo.ibergrid.eu configuration
mkdir -p ~/.voms
cat > ~/.voms/vomses << EOF 
"ops.vo.ibergrid.eu" "ibergrid-voms.ifca.es" "40001" "/DC=es/DC=irisgrid/O=ifca/CN=host/ibergrid-voms.ifca.es" "ops.vo.ibergrid.eu"
"ops.vo.ibergrid.eu" "voms01.ncg.ingrid.pt" "40001" "/C=PT/O=LIPCA/O=LIP/OU=Lisboa/CN=voms01.ncg.ingrid.pt" "ops.vo.ibergrid.eu"
EOF

echo $MYPROXY_PASSWD | myproxy-logon -S -s $MYPROXY_SERVER -l $MYPROXY_USER -m ops.vo.ibergrid.eu
