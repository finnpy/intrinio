from collections import namedtuple
import json
import sys
if sys.version_info < (3, 0):
    import cPickle as pickle
else:
    import pickle

import requests
from requests.auth import HTTPBasicAuth


Price = namedtuple('Price', ["date", "open", "high", "low", "close", "volume", "ex_dividend", "split_ratio",
                             "adj_open", "adj_high", "adj_low", "adj_close", "adj_volume"])

def prices(identifier):
    rsrc = "/prices?identifier={}".format(identifier)
    results = _get_all(rsrc, shape=Price)
    for entry in results:
        print(entry)
    return results


Sample = namedtuple('Sample', ["date", "value"])

def historical_data(identifier, item):
    rsrc = "/historical_data?identifier={}&item={}".format(identifier, item)
    results = _get_all(rsrc, shape=Sample, meta=APIInfo_for_historical)
    for entry in results:
        print(entry)
    return results


Security = namedtuple('Security', ['ticker', 'altmanzscore', 'marketcap', 'employees', 'cashandequivalents',
                                   'netincome', 'totalrevenue', 'pricetoearnings', 'pricetobook', 'pricetorevenue'])

# TODO: make it securities.search
def securities_search():

    condition = "altmanzscore~gt~0,marketcap~gt~50000000,employees~gt~100,cashandequivalents~gt~0,netincome~gt~0,totalrevenue~gt~0,pricetoearnings~lt~1000,pricetobook~lt~1000,pricetorevenue~lt~1000"

    # results = []
    # cur_page = 1
    # total_pages = 1
    # while cur_page <= total_pages:
    #     js = get(page=cur_page)
    #     print(js)
    #
    #     info = APIInfo(**js)
    #     # total_pages = info.total_pages        # FIXME
    #
    #     results.extend(map(lambda s: Stock(**s), js["data"]))
    #     cur_page += 1

    # FIXME: multipage
    rsrc = "/securities/search?page_number={}&conditions={}".format(1, condition)
    results = _get_all(rsrc, shape=Security)
    for entry in results:
        print(entry)
    #print("Total results:", info.result_count, len(results))

    # --- test encoding of results

    with open("dump.json", "w") as f:
        json.dump(results, f)
    with open("header.pickle", "wb") as f:
        pickle.dump(Security, f)
    with open("dump.pickle", "wb") as f:
        pickle.dump(results, f)

    return results


# ---------------------------------------------------------------

# TODO: avoid duplicate fields
# TODO: not to mention we are not using these namedtuples anywhere
APIInfo = namedtuple('APIInfo', ['result_count', 'current_page', 'total_pages', 'page_size', 'api_call_credits', 'data'])

APIInfo_for_historical = namedtuple('APIInfo', ['result_count', 'current_page', 'total_pages', 'page_size', 'api_call_credits', 'data',
                                 'identifier', 'item'])

def _get(resource, page=1):
    with open("keys.json") as f:
        keys = json.load(f)['intrinio']
    my_auth = HTTPBasicAuth(username=keys['user'], password=keys['pass'])

    uri = "https://api.intrinio.com{}".format(resource)
    r = requests.get(uri, auth=my_auth)
    return r.json()


def _get_all(resource, shape, meta=None):
    if meta is None:
        meta = APIInfo
    results = []
    cur_page = 1
    total_pages = 1
    while cur_page <= total_pages:
        js = _get(resource, page=cur_page)
        print(js)

        #info = meta(**js)   # TODO: better name for meta
        # total_pages = info.total_pages        # FIXME

        results.extend(map(lambda s: shape(**s), js["data"]))
        cur_page += 1

    print("Total results:", js["result_count"], len(results))
    return results
