import json
import sys
from collections import namedtuple

if sys.version_info < (3, 0):
    pass
else:
    pass

import requests
from requests.auth import HTTPBasicAuth

CompanyIndex = namedtuple("CompanyIndex", ["ticker", "name", "lei", "cik", "latest_filing_date"])

Company = namedtuple("Company",
                     ["ticker", "name", "lei", "legal_name", "stock_exchange", "sic", "short_description",
                      "long_description", "ceo", "company_url", "business_address", "mailing_address",
                      "business_phone_no", "hq_address1", "hq_address2", "hq_address_city",
                      "hq_address_postal_code",
                      "entity_legal_form", "securities", "cik", "latest_filing_date", "hq_state", "hq_country",
                      "inc_state", "inc_country", "employees", "entity_status", "sector", "industry_category",
                      "industry_group", "template", "standardized_active"])


def companies(identifier=None):
    if identifier is None:
        rsrc = "/companies"
        results = _get_all(rsrc, shape=CompanyIndex)
    else:
        rsrc = "/companies?identifier={}".format(identifier)
        results = _get_all(rsrc, shape=Company)
    return results


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


def _extract_tags(conditions):
    return [c.split("~")[0] for c in conditions]


# TODO: make it securities.search
def securities_search(conditions):
    tags = _extract_tags(conditions)
    tags.append("ticker")
    Security = namedtuple("Security", tags)

    # FIXME: multipage
    query_string = ",".join(conditions)
    rsrc = "/securities/search?page_number={}&conditions={}".format(1, query_string)
    results = _get_all(rsrc, shape=Security)
    return results, Security


SecurityIndex = namedtuple("SecurityIndex", ["ticker", "figi_ticker", "figi", "composite_figi", "composite_figi_ticker",
                                             "security_name", "market_sector",
                                             "security_type", "stock_exchange", "last_crsp_adj_date"])

Security = namedtuple("Security", ["ticker", "figi_ticker", "figi", "composite_figi", "composite_figi_ticker",
                                   "security_name", "market_sector", "security_type", "stock_exchange",
                                   "last_crsp_adj_date", "figi_uniqueid", "share_class_figi", "figi_exch_cntry",
                                   "currency", "mic", "exch_symbol", "etf", "delisted_security",   "primary_listing"])


def securities(identifier=None):
    if identifier is None:
        rsrc = "/securities"
        results = _get_all(rsrc, shape=SecurityIndex)
    else:
        rsrc = "/securities?identifier={}".format(identifier)
        results = _get_all(rsrc, shape=Security)
    return results


# ---------------------------------------------------------------

# TODO: avoid duplicate fields
# TODO: not to mention we are not using these namedtuples anywhere
APIInfo = namedtuple('APIInfo',
                     ['result_count', 'current_page', 'total_pages', 'page_size', 'api_call_credits', 'data'])

APIInfo_for_historical = namedtuple('APIInfo',
                                    ['result_count', 'current_page', 'total_pages', 'page_size', 'api_call_credits',
                                     'data',
                                     'identifier', 'item'])


def _get(resource, page=1):  # TODO: make it page_number to match API
    # TODO : don't open the keys file on every page get
    # TODO : move implementation into separate get_auth() function
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
        print(json.dumps(js))

        # info = meta(**js)   # TODO: better name for meta
        # total_pages = info.total_pages        # FIXME multipage

        paged = "total_pages" in js.keys()
        if paged:
            results.extend(map(lambda s: shape(**s), js["data"]))
        else:
            return shape(**js)

        cur_page += 1

    if paged:
        print("Total results:", js["result_count"], len(results))
    return results
