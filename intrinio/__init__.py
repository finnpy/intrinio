import json
import urllib
from collections import namedtuple

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
                                   "currency", "mic", "exch_symbol", "etf", "delisted_security", "primary_listing"])


def securities(identifier=None):
    rsrc = "/securities"
    if identifier is None:
        results = _get_all(rsrc, {}, shape=SecurityIndex)
    else:
        results = _get_all(rsrc, {"identifier": identifier}, shape=Security)
    return results


DataPoint = namedtuple("DataPoint", ["identifier", "item", "value"])


def data_point(identifier, item):
    if not isinstance(identifier, list):
        raise TypeError("expected list of identifiers, got {}".format(type(identifier)))
    if not isinstance(item, list):
        raise TypeError("expected list of items, got {}".format(type(item)))

    if len(identifier) < 1:
        raise ValueError("expected non-empty list of identifers")
    if len(item) < 1:
        raise ValueError("expected non-empty list of items")

    rsrc = "/data_point"
    identifiers = ",".join(identifier)
    items = ",".join(item)
    params = {"identifer": identifiers, "item": items}
    results = _get_all(rsrc, params, shape=DataPoint)
    return results


index_base_fields = ["symbol", "index_name"]

SICIndex = namedtuple("SICIndex", index_base_fields + ["continent", "country", "index_type"])
EconomicIndex = namedtuple("EconomicIndex", index_base_fields + ["fred_symbol", "update_frequency", "last_updated",
                                                                 "description", "observation_start", "observation_end",
                                                                 "popularity",
                                                                 "seasonal_adjustment", "seasonal_adjustment_short",
                                                                 "units", "units_short", "index_type"])


def indices(identifier=None, type=None, query=None):
    rsrc = "/indices"
    params = {}
    if identifier is not None:
        params["identifier"] = identifier

    if query is not None:
        params["query"] = query

    if type is not None:
        params["type"] = type

    data_shape = SICIndex
    if type == "sic":
        data_shape = SICIndex

    if type == "economic":
        data_shape = EconomicIndex

    results = _get_all(rsrc, params, shape=data_shape)
    return results



# TODO: /prices/exchange?identifier=^XNAS&price_date=2016-12-05

# TODO: /filings
# TODO: /companies/filings?identifier=AAPL
# TODO: /news?identifier=AAPL

# TODO: /fundamentals/standardized?identifier=AAPL&statement=income_statement&type=FY
# TODO: /fundamentals/reported?identifier=AAPL&statement=income_statement&type=FY
#
# TODO: /financials/standardized?identifier=AAPL&statement=income_statement&fiscal_year=2015&fiscal_period=FY
# TODO: /financials/reported?identifier=AAPL&statement=income_statement&fiscal_year=2015&fiscal_period=FY
#
# TODO: /tags/standardized?identifier=AAPL&statement=income_statement
# TODO: /tags/reported?identifier=AAPL&statement=income_statement&fiscal_year=2015&fiscal_period=FY
#
# TODO: /companies/insider_transactions?identifier=AAPL
# TODO: /companies/insider_ownership?identifier=AAPL
#
# TODO: /owners?institutional=false
# TODO: /owners?query=Cook
# TODO: /owners?identifier=<owner identifier>
# TODO: /owners/insider_transactions?identifier=<owner identifier>
# TODO: /owners/insider_holdings?cik=<cik identifier>


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
