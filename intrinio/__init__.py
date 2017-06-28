from collections import namedtuple
import json
import urllib

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
    rsrc = "/companies"
    if identifier is None:
        results = _get_all(rsrc, {}, shape=CompanyIndex)
    else:
        results = _get_all(rsrc, {"identifier": identifier}, shape=Company)
    return results


Price = namedtuple('Price', ["date", "open", "high", "low", "close", "volume", "ex_dividend", "split_ratio",
                             "adj_open", "adj_high", "adj_low", "adj_close", "adj_volume"])


def prices(identifier):
    rsrc = "/prices"
    results = _get_all(rsrc, {"identifier": identifier}, shape=Price)
    for entry in results:
        print(entry)
    return results


Sample = namedtuple('Sample', ["date", "value"])


def historical_data(identifier, item):
    rsrc = "/historical_data"
    results = _get_all(rsrc, {"identifier": identifier, "item": item}, shape=Sample)
    for entry in results:
        print(entry)
    return results


def _extract_tags(conditions):
    return [c.split("~")[0] for c in conditions]


# TODO: make it securities.search
def securities_search(conditions):
    rsrc = "/securities/search"
    tags = _extract_tags(conditions)
    tags.append("ticker")
    query_string = ",".join(conditions)

    Security = namedtuple("Security", tags)

    results = _get_all(rsrc, {"conditions": query_string}, shape=Security)
    return results, Security


SecurityIndex = namedtuple("SecurityIndex", ["ticker", "figi_ticker", "figi", "composite_figi", "composite_figi_ticker",
                                             "security_name", "market_sector",
                                             "security_type", "stock_exchange", "last_crsp_adj_date"])

Security = namedtuple("Security", ["ticker", "figi_ticker", "figi", "composite_figi", "composite_figi_ticker",
                                   "security_name", "market_sector", "security_type", "stock_exchange",
                                   "last_crsp_adj_date", "figi_uniqueid", "share_class_figi", "figi_exch_cntry",
                                   "currency", "mic", "exch_symbol", "etf", "delisted_security",   "primary_listing"])


def securities(identifier=None):
    rsrc = "/securities"
    if identifier is None:
        results = _get_all(rsrc, {}, shape=SecurityIndex)
    else:
        results = _get_all(rsrc, {"identifier": identifier}, shape=Security)
    return results


# ---------------------------------------------------------------

max_pages = None


def _get(resource, params, page=1):
    # TODO : don't open the keys file on every page get
    # TODO : move implementation into separate get_auth() function
    with open("keys.json") as f:
        keys = json.load(f)['intrinio']
    my_auth = HTTPBasicAuth(username=keys['user'], password=keys['pass'])

    d = dict(page_number=page)
    if len(params) > 0:
        d.update(params)
    query = "?" + urllib.urlencode(d)

    uri = "https://api.intrinio.com{}{}".format(resource, query)
    r = requests.get(uri, auth=my_auth)
    return r.json()


def _get_all(resource, params, shape):
    results = []
    # f = open("raw.text", "w")
    cur_page = 1
    total_pages = 1
    # print(resource)
    while cur_page <= total_pages:
        js = _get(resource, params, cur_page)
        # f.write(json.dumps(js)+"\n")

        total_pages = js.get("total_pages")
        if total_pages is None:
            return shape(**js)
        else:
            results.extend(map(lambda s: shape(**s), js["data"]))
            cur_page += 1
            if max_pages is not None:
                total_pages = min(total_pages, max_pages)
            print("Total results:", len(results), js["result_count"])

    return results
