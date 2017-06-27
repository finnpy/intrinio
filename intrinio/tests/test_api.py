import json
import unittest

import intrinio

local = True


def load(name):
    with open(name, "r") as f:
        return json.load(f)


class TestAPI(unittest.TestCase):

    def test_companies(self):
        if local:
            intrinio._get = lambda rsrc, page: load("companies.json")
        r = intrinio.companies()
        tickers = [c.ticker for c in r]
        self.assertIn("AAPL", tickers)
        if local:
            self.assertIn("ADMS", tickers)

    def test_companies_by_id(self):
        if local:
            intrinio._get = lambda rsrc, page: load("companies_aapl.json")
        r = intrinio.companies("AAPL")
        self.assertEqual(r.ticker, "AAPL")

    def test_prices(self):
        if local:
            intrinio._get = lambda rsrc, page: load("prices_aapl.json")
        r = intrinio.prices("AAPL")
        if local:
            self.assertEqual(len(r), 2)
            self.assertEqual(r[0].date, "2016-09-23")
            self.assertEqual(r[1].adj_open, 114.35)
        else:
            self.assertGreater(len(r), 0)

    def test_historical_data(self):
        if local:
            intrinio._get = lambda rsrc, page: load("historical_data_aapl.json")

        r = intrinio.historical_data(identifier="AAPL", item="altmanzscore")
        if local:
            self.assertEqual(len(r), 33)

    def test_securities(self):
        if local:
            intrinio._get = lambda rsrc, page: load("securities.json")
        r = intrinio.securities()

    def test_securities_by_id(self):
        if local:
            intrinio._get = lambda rsrc, page: load("securities_aapl.json")
        r = intrinio.securities("AAPL")

    def test_securities_search(self):
        if local:
            intrinio._get = lambda rsrc, page: load("securities_search.json")

        conditions = ["altmanzscore~gt~0",
                      "marketcap~gt~50000000",
                      "employees~gt~100",
                      "cashandequivalents~gt~0",
                      "netincome~gt~0",
                      "totalrevenue~gt~0",
                      "pricetoearnings~lt~1000",
                      "pricetobook~lt~1000",
                      "pricetorevenue~lt~1000"
                      ]
        r, s = intrinio.securities_search(conditions)
        if local:
            self.assertEqual(len(r), 100)
            APD = r[-2]  # just an example, pick second to last
            self.assertEqual(APD.ticker, "APD")
            self.assertEqual(APD.pricetorevenue, 3.2682)
            self.assertEqual(APD.pricetobook, 3.4176)
            self.assertEqual(APD.employees, 18300)

        self.assertGreater(len(r), 0)
        for c in r:
            self.assertTrue(c.altmanzscore > 0)
            self.assertTrue(c.marketcap > 50000000)
            self.assertTrue(c.employees > 100)
            self.assertTrue(c.cashandequivalents > 0)
            self.assertTrue(c.netincome > 0)
            self.assertTrue(c.totalrevenue > 0)
            self.assertTrue(c.pricetoearnings < 1000)
            self.assertTrue(c.pricetobook < 1000)
            self.assertTrue(c.pricetorevenue < 1000)


if __name__ == "__main__":
    unittest.main(verbosity=2)

