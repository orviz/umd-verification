if ! options=$(getopt -o '' -l install -- "$@")
then
    # something went wrong, getopt will put out an error message for us
    exit 1
fi

set -- $options

action=none
while [ $# -gt 0 ]
do
    case $1 in
    -i|--install) action="install" ;;
    -u|--upgrade) action="upgrade" ;;
    (--) shift; break;;
    (-*) echo "$0: error - unrecognized option $1" 1>&2; exit 1;;
    (*) break;;
    esac
    shift
done

[ $action == "none" ] && exit 0

if [ $action == "install" ]; then
    echo ">> From scratch installation of $METAPACKAGE"

    # Install base system
    /usr/bin/yum -y remove epel-release* umd-release*
    /bin/rm -f /etc/yum.repos.d/UMD-* /etc/yum.repos.d/epel-*

    /usr/bin/wget $EPEL_RELEASE_RPM_URL -O /tmp/`basename $EPEL_RELEASE_RPM_URL`
    /usr/bin/yum -y install /tmp/`basename $EPEL_RELEASE_RPM_URL`

    /usr/bin/yum -y install yum-priorities

    /usr/bin/wget $UMD_RELEASE_RPM_URL -O /tmp/`basename $UMD_RELEASE_RPM_URL`
    /usr/bin/yum -y install /tmp/`basename $UMD_RELEASE_RPM_URL`

    /usr/bin/yum -y install $METAPACKAGE

    # Additional packages
    for metapkg in $METAPACKAGE ; do
        [ $metapkg == "emi-cream-ce" ] && ADD_PKGS="sudo"
    done
    [ -n $ADD_PKGS ] && echo ">> Installing additional packages: $ADD_PKGS" && /usr/bin/yum -y install $ADD_PKGS
fi

# Install verification stuff
echo ">> Installing verification stuff from $REPOSITORY_URL"
/usr/bin/wget $REPOSITORY_URL -O /etc/yum.repos.d/`basename $REPOSITORY_URL`
/usr/bin/yum -y update
