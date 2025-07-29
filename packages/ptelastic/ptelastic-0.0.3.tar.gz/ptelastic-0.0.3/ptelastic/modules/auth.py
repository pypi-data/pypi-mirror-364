"""
Elasticsearch authentication test

This module implements a test that checks if an Elasticsearch instance has authentication enabled or disabled

Contains:
- Auth class for performing authentication test
- run() function as an entry point for running the test
"""

import http
from ptlibs import ptjsonlib
from ptlibs.ptprinthelper import ptprint

__TESTLABEL__ = "Elasticsearch authentication test"


class Auth:
    """
    This class tests to see if an Elasticsearch instance is running with authentication enabled or disabled by
    sending a GET request to the provided URL and looking at the HTTP response code.
    """

    def __init__(self, args: object, ptjsonlib: object, helpers: object, http_client: object, base_response: object) -> None:
        self.args = args
        self.ptjsonlib = ptjsonlib
        self.helpers = helpers
        self.http_client = http_client
        self.base_response = base_response

        self.helpers.print_header(__TESTLABEL__)

    def run(self) -> None:
        """
        Executes the Elasticsearch authentication test

        Sends one HTTP GET request to the provided URL and determines if authentication is enabled or not by the
        HTTP response codes as follows:

        401 Unauthorized = Authentication is enabled
        200 OK - Authentication is disabled

        If authentication is disabled, a vulnerability and a property are added to the JSON result
        """

        url = self.args.url
        response = self.http_client.send_request(url, method="GET", headers=self.args.headers, allow_redirects=False)

        if self.args.verbose:
            ptprint(f"Sending request to: {url}", "INFO", not self.args.json, colortext=False, indent=4)
            ptprint(f"Returned response status: {response.status_code}", "INFO", not self.args.json, indent=4)

        if response.status_code == http.HTTPStatus.UNAUTHORIZED:
            ptprint(f"Authentication is enabled", "VULN", not self.args.json, indent=4)

        elif response.status_code == http.HTTPStatus.OK:
            ptprint(f"Authentication is disabled", "VULN", not self.args.json, indent=4)
            self.ptjsonlib.add_vulnerability("PTV-WEB-ELASTIC-AUTH")
            self.ptjsonlib.add_properties({"authentication": "disabled"})


def run(args, ptjsonlib, helpers, http_client, base_response):
    """Entry point for running the Auth test"""
    Auth(args, ptjsonlib, helpers, http_client, base_response).run()
