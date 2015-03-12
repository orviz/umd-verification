#!/usr/bin/env python

import argparse
import os.path
import sys


NODE_TYPE_MAP = {
    "emi-cream-ce": "creamCE",
    "emi-ge-utils": "SGE_utils",
    "emi-ui": "UI",
    "emi-storm-backend-mp": "se_storm_backend",
    "emi-storm-frontend-mp": "se_storm_frontend",
    "emi-storm-globus-gridftp-mp": "se_storm_gridftp",
    "emi-storm-gridhttps-mp": "se_storm_gridhttps",
    "storm-webdav": "se_storm_webdav",
}

SITE_INFO_MAP = {
    # cream
    "emi-cream-ce": "site-info-creamCE.def",
    "emi-ge-utils": "site-info-creamCE.def",
    # ui
    "emi-ui": "site-info-UI.def",
    # storm
    "emi-storm-backend-mp": "site-info-storm.def",
    "emi-storm-frontend-mp": "site-info-storm.def",
    "emi-storm-globus-gridftp-mp": "site-info-storm.def",
    "emi-storm-gridhttps-mp": "site-info-storm.def",
    "storm-webdav": "site-info-storm.def",
}

CERT_NODE_TYPES = [
    "emi-cream-ce",
    "emi-storm-frontend",
]


parser = argparse.ArgumentParser(description=("Generate the appropriate "
                                              "YAIM environment"))
parser.add_argument("umd_products",
                    metavar="UMD-PRODUCT", nargs="+",
                    help="UMD products to be configured with YAIM.")
parser.add_argument('--node-types', dest='node_types', action='store_const',
                    const=NODE_TYPE_MAP,
                    help='retrieve the matching YAIM node types.')
parser.add_argument('--requires-cert', dest='requires_cert',
                    action='store_true',
                    help='retrieve the matching YAIM node types.')

args = parser.parse_args()

if args.node_types:
    for product in args.umd_products:
        print args.node_types[product]
elif args.requires_cert:
    r = 0
    for product in args.umd_products:
        if product in CERT_NODE_TYPES:
            r = 1
            break
    print r
else:
    fname = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                         "site-info.def")
    f = open(fname, "w")
    for siteinfo in set([SITE_INFO_MAP[product]
                         for product in args.umd_products]):
        f.write("source %s\n" % siteinfo)
    f.close()
