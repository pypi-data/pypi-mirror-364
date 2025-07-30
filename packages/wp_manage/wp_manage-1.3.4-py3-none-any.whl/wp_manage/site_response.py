import logging
import requests

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (platform; rv:geckoversion) Gecko/geckotrail Firefox/firefoxversion',
    'Accept': 'text/html, application/xhtml+xml, application/xml;q=0.9, */*;q=0.8',
    'Accept-Language': 'en-US, en;q=0.5',
    'Connection': 'keep-alive',
}

URL_DICT = {
    "actravelalert": "https://www.actravelalert.org/",
    "aikeahawaii": "https://www.aikeahawaii.org/",
    "gategourmetdev": "http://gategourmetdev.wpenginepowered.com",
    "gategourmetpro": "https://www.airportstrikealert.org/",
    "bcsunequal": "https://www.bcunequalwomen.org/",
    "citizenshiphi": "http://www.citizenshiphawaii.org/",
    "detroitcc": "http://www.detroitcasinocouncil.org/",
    "dwfoodalert": "http://www.disneyworldfoodalert.org/",  # authentication required
    "fairfr": "http://www.fairfranchise.org/",
    "fertittamoney": "http://www.fertittamoneywatch.org/",
    "greenhotels": "http://www.greenhotelsforseattle.org/",
    "handoffpanton": "http://www.handsoffpantson.org/",
    "hiltonanch": "http://hiltonanch.wpenginepowered.com/",  # authentication required
    "hoteldisloyal": "http://www.hoteldisloyalty.org/",  # authentication required
    "itsourcoast": "http://www.itsourcoast.org/",
    "local261": "http://www.local261.org/",
    "local26": "http://www.local26.org/",
    "local47": "http://www.local47.net/",
    "marriotttimesh": "http://www.marriotttimesharecritic.org/",
    "metooterranea": "http://metooterranea.org/",
    "neighborhoods1": "http://www.neighborhoodstability.org/",
    "nejb": "http://www.nejb.us/",
    "nomissionbay": "http://www.nomissionbaylandgrab.org/",
    "phcppr": "http://www.parkhotelscapexproblems.org/",   # authentication required
    "resortfeerpr": "http://www.resortfeeripoff.org/",  # authentication required
    "rrripodissect": "http://www.rrripodissected.org/",
    "savearapahoepr": "http://www.savearapahoebasin.org/",
    "stcunion": "http://www.stcunion.org/",
    "uhtestsite2024": "http://uhtestsite2024.wpenginepowered.com",
    "unionbusting": "http://www.unionbustingatsycuan.org/",
    "unioneats": "http://www.unioneats.org/",
    "unitehere100": "http://www.unitehere100.org/",
    "devl11site": "http://devl11site.wpengine.com",
    "local11dev": "http://www.unitehere11.org/",
    "unitehere19": "http://www.unitehere19.org/",
    "unitehere1": "http://www.unitehere1.org/",
    "unitehere23": "http://www.unitehere23.org/",
    "unitehere2": "http://www.unitehere2.org/",
    "unitehere355": "http://www.unitehere355.org/",
    "unitehere49": "http://unitehere49.org/",
    "unitehere57": "http://www.unitehere57.org/",
    "unitehere5": "http://www.unitehere5.org/",
    "unitehere610": "https://www.unitehere610.org/",
    "unitehere878": "http://www.unitehere878.org/",
    "unitehere8": "http://www.unitehere8.org/",
    "unitehere17": "http://www.uniteherelocal17.org/",
    "unitehere362": "http://www.uniteherelocal362.org/",
    "unitehere40": "http://www.uniteherelocal40.org/",
    "unitehere54": "http://www.uniteherelocal54.org/",
    "unitehere737": "http://www.uniteherelocal737.org/",
    "uhlocal74": "http://www.uniteherelocal74.org/",
    "unitehere75": "http://www.uniteherelocal75.org/",
    "unitehere7": "http://www.uniteherelocal7.org/",
    "uhphilly": "http://www.uniteherephilly.org/",
    "uniteheretest": "http://uniteheretest.wpengine.com",  # authentication required
    "uphoenixexpose": "http://www.universityofphoenixexposed.org/",
    "wehorising": "http://www.wehorising.org/",
    "workfamsunited": "http://www.workingfamiliesunited.org/",
}

def enable_http_logging():
    # These two lines enable debugging at httplib level (requests->urllib3->http.client)
    # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS
    import http.client as http_client
    http_client.HTTPConnection.debuglevel = 1
    # up the verbosity of requests library's http activity
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


def check_site_response(env, verbose):
    site = URL_DICT[env]

    if verbose:
        enable_http_logging()

    response = requests.get(site, headers=HEADERS)
    print(f"{site} response = {response.status_code}")
