from umd.base import Deploy


bdii_site = Deploy(
    name="bdii-site",
    doc="Site BDII deployment.",
    metapkg="emi-bdii-site",
    nodetype="BDII_site",
    siteinfo=["site-info-BDII_site.def"])
