from umd.base import Deploy


argus = Deploy(
    name="argus",
    doc="ARGUS server deployment.",
    metapkg="emi-argus",
    need_cert=True,
    nodetype="ARGUS_server",
    siteinfo=["site-info-ARGUS_server.def"])
