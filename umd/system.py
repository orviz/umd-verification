import platform

from umd import exception


distname, version, distid = platform.dist()

# major version
version_major = version.split('.')[0]
if not version_major.isdigit():
    raise exception.InstallException(("Could not get major OS version "
                                      "for '%s'" % version))

# distro_version
distro_version = ''.join([distname, version_major])
