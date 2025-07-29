#!/usr/bin/python3
"""
    Copyright (c) 2024 Penterep Security s.r.o.

    ptcrossd - Crossdomain.xml Testing Tool

    ptcrossd is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ptcrossd is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with ptcrossd.  If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import re
import sys; sys.path.append(__file__.rsplit("/", 1)[0])
import urllib

import requests
import defusedxml.ElementTree as DEFUSED_ET
import xml.etree.ElementTree as ET

from _version import __version__
from ptlibs import ptjsonlib, ptprinthelper, ptmisclib, ptnethelper


class PtCrossd:
    def __init__(self, args):
        self.args = args
        self.ptjsonlib = ptjsonlib.PtJsonLib()
        self._validate_url(args.url)

    def run(self, args) -> None:
        url_to_test = args.url
        if args.cross_domain_file:
            if args.json:
                url_path, url = self._adjust_url(url_to_test)
                self._test_crossdomain_xml(url, url_path)
            else:
                url_list = self._get_paths_for_crossdomain(url_to_test)
                for url in url_list:
                    ptprinthelper.ptprint(" ", "", not self.args.json and url != url_list[-1])
                    if self._test_crossdomain_xml(url):
                        url_to_test = url
                        break
            ptprinthelper.ptprint(" ", "", not self.args.json)

        if args.cross_origin_header:
            self._test_headers(args.url)

        self.ptjsonlib.set_status("finished")
        ptprinthelper.ptprint(self.ptjsonlib.get_result_json(), condition=args.json)

    def _test_crossdomain_xml(self, url, url_path=None) -> bool:
        """
        Tests if the given URL returns a valid 'crossdomain.xml' file.

        Sends a request to the specified URL and checks if the response status is
        200. If successful, it processes the crossdomain.xml file and optionally
        adds information to the JSON result.

        :param url: The URL to test for the crossdomain.xml file.
        :type url: str
        :param url_path: An optional path or name associated with the URL (for display purposes).
        :type url_path: str, optional
        :return: True if the crossdomain.xml was found and processed, False otherwise.
        :rtype: bool
        """
        ptprinthelper.ptprint(f"Testing: {url}", "TITLE", not self.args.json, colortext=True)
        response, response_dump = self._get_response(url)
        ptprinthelper.ptprint(f"Returned Status Code: {response.status_code}", "INFO", not self.args.json)

        if response.status_code == 200:
            self._process_crossdomain(response, response_dump)
            if self.args.json:
                self.ptjsonlib.add_node(self.ptjsonlib.create_node_object("webSource", properties={"url": url, "name": url_path, "webSourceType": "crossdomain.xml"}))
            return True
        else:
            ptprinthelper.ptprint(f"crossdomain.xml file not found", "OK", not self.args.json, end="\n")
            self.ptjsonlib.set_message("crossdomain.xml not found")
            return False

    def get_response_text_cleaned(self, response):
        """
        Decode the raw content of an HTTP response, handling BOM and fallback encodings.

        Args:
            response (requests.Response): The HTTP response object to decode.

        Returns:
            str: The decoded text content of the response.

        Behavior:
            - If the content starts with a UTF-8 BOM, decode using 'utf-8-sig' to remove it.
            - Otherwise, attempt to decode using the response's specified encoding.
            - If decoding with the specified encoding fails, fallback to 'utf-8'.
            - If 'utf-8' decoding fails, fallback to 'latin-1'.
        """
        raw = response.content

        # Check for BOM
        if raw.startswith(b'\xef\xbb\xbf'):
            return raw.decode('utf-8-sig')

        # Use encoding from headers if available
        if response.encoding:
            try:
                return raw.decode(response.encoding)
            except UnicodeDecodeError:
                pass

        # Fallback
        try:
            return raw.decode('utf-8')
        except UnicodeDecodeError:
            return raw.decode('latin-1')

    def _process_crossdomain(self, response, response_dump) -> None:
        try:
            cleaned = self.get_response_text_cleaned(response)
            if not isinstance(cleaned, str):
                self.ptjsonlib.end_error("Failed to decode response to string.", condition=self.args.json)

            tree = DEFUSED_ET.fromstring(cleaned)
        except DEFUSED_ET.ParseError as e:
            ptprinthelper.ptprint(f"Error parsing provided XML file", "ERROR", not self.args.json)
            self.ptjsonlib.set_message("Error parsing provided XML file")
            return
        except DEFUSED_ET.EntitiesForbidden:
            ptprinthelper.ptprint(f"Forbidden entities found", "ERROR", not self.args.json)
            self.ptjsonlib.set_message("Forbidden entities found")
            return

        if not self.args.json:
            element = ET.XML(cleaned)
            ET.indent(element)
            xml_string = ET.tostring(element, encoding='unicode')
            ptprinthelper.ptprint("XML content:", "INFO", not self.args.json)
            ptprinthelper.ptprint(ptprinthelper.get_colored_text(xml_string, "ADDITIONS"), condition=not self.args.json, newline_above=True)

        ptprinthelper.ptprint(" ", "", not self.args.json)
        self._run_allow_access_from_test(tree, response, response_dump)

    def _run_allow_access_from_test(self, tree, response, response_dump) -> None:
        is_open_cors = False
        http_allowed = False
        acf_elements = tree.findall("allow-access-from")
        if acf_elements:
            for acf_element in acf_elements:
                if "domain" in acf_element.keys() and acf_element.attrib["domain"] == "*":
                    is_open_cors = True
                if "secure" in acf_element.keys() and not acf_element.attrib["secure"]:
                    http_allowed = True
            if is_open_cors:
                ptprinthelper.ptprint("Open CORS vulnerability detected in crossdomain.xml file", "VULN", not self.args.json)
                self.ptjsonlib.add_vulnerability("PTV-WEB-HTTP-CROSSD", vuln_request=response_dump["request"], vuln_response=response_dump["response"])
            if http_allowed:
                ptprinthelper.ptprint("Non-secure communication detected in crossdomain.xml file", "VULN", not self.args.json)
            if not any([is_open_cors, http_allowed]):
                ptprinthelper.ptprint("Content is OK", "OK", not self.args.json)

        if not is_open_cors:
            self.ptjsonlib.set_message(response.text)

    def _test_headers(self, url) -> None:
        ptprinthelper.ptprint(f"Testing: Access-Control-Allow-Origin header", "TITLE", not self.args.json, colortext=True, newline_above=False)
        headers = self.args.headers.copy()
        headers.update({"Referer": "https://test-cors-referer.com", "Origin": "https://test-cors-origin.com"})
        response, response_dump = self._get_response(url, headers=headers)
        if response.headers.get("Access-Control-Allow-Origin"):
            self._print_cors_headers(headers=response.headers)

            if response.headers.get("Access-Control-Allow-Origin") == "*":
                ptprinthelper.ptprint("Open CORS vulnerability detected in Access-Control-Allow-Origin header", "VULN", not self.args.json)
                self.ptjsonlib.add_vulnerability("PTV-WEB-HTTP-CORSS", vuln_request=response_dump["request"], vuln_response=response_dump["response"])

            if response.headers.get("Access-Control-Allow-Origin") == "https://test-cors-referer.com":
                ptprinthelper.ptprint("Reflecting Referer header to Access-Control-Allow-Origin header", "VULN", not self.args.json)
                self.ptjsonlib.add_vulnerability("PTV-WEB-HTTP-CORSR", vuln_request=response_dump["request"], vuln_response=response_dump["response"])
                self._test_crlf(url, header_name="Referer")

            if response.headers.get("Access-Control-Allow-Origin") == "https://test-cors-origin.com":
                ptprinthelper.ptprint("Reflecting Origin header to Access-Control-Allow-Origin header", "VULN", not self.args.json)
                self.ptjsonlib.add_vulnerability("PTV-WEB-HTTP-CORSO", vuln_request=response_dump["request"], vuln_response=response_dump["response"])
                self._test_crlf(url, header_name="Origin")
        else:
            ptprinthelper.ptprint(f'Header Access-Control-Allow-Origin is not present', "INFO", not self.args.json)

    def _print_cors_headers(self, headers):
        #ptprinthelper.ptprint("CORS Headers:", "", not self.args.json, indent=4)
        for header, value in headers.items():
            if header.lower().startswith("access-control-"):
                ptprinthelper.ptprint(ptprinthelper.get_colored_text(f"{header}: {value}", "ADDITIONS"), "TEXT", not self.args.json, indent=4)
        ptprinthelper.ptprint(" ", "", not self.args.json)

    def _test_crlf(self, url, header_name) -> None:
        headers = self.args.headers.copy()
        headers.update({header_name: "test%0D%0Atestcrlf:crlf"})
        r, r_dump = self._get_response(url)

        if r.headers.get("testcrlf"):
            ptprinthelper.ptprint(f"Header {header_name} is vulnerable to CRLF injection", "VULN", not self.args.json)
            self.ptjsonlib.add_vulnerability(f"PTV-WEB-INJECT-CORS{header_name.capitalize()[0]}CSRF")

    def _adjust_url(self, url: str) -> tuple[str, str]:
        """
        Adjusts a given URL to ensure it points to a 'crossdomain.xml' file.

        If the provided URL's path does not already end with '/crossdomain.xml',
        this function modifies the path to append it. If the path is empty or a
        root directory, it is replaced with '/crossdomain.xml'.

        :param url: The URL to adjust.
        :type url: str
        :return: A tuple containing the adjusted path (as a string) and the full adjusted URL.
        :rtype: tuple[str, str]
        """
        parsed_url = urllib.parse.urlparse(url)
        # Check if the URL already points to crossdomain.xml
        if not parsed_url.path.endswith("/crossdomain.xml"):
            if parsed_url.path in ["", "/"]:
                # If path is empty or root, replace with crossdomain.xml
                parsed_url = parsed_url._replace(path="/crossdomain.xml")
            else:
                # Modify the path to point to crossdomain.xml
                directories = [d for d in parsed_url.path.split("/") if d]
                if "." in directories[-1]:
                    directories.pop()
                parsed_url = parsed_url._replace(path='/'.join(directories) + "/crossdomain.xml")

        # Clean the path and return the full adjusted URL
        adjusted_path = parsed_url.path.lstrip("/")  # Remove leading slash if any
        full_url = urllib.parse.urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, "", "", ""))

        return adjusted_path, full_url

    def _get_paths_for_crossdomain(self, url: str) -> list:
        """
        Generates a list of potential URLs pointing to 'crossdomain.xml' locations
        based on the provided URL.

        This method takes the provided URL and constructs a series of possible
        locations for the 'crossdomain.xml' file, by removing parts of the path
        iteratively until no further directory segments remain.

        :param url: The base URL to generate potential 'crossdomain.xml' URLs from.
        :type url: str
        :return: A list of URLs pointing to potential 'crossdomain.xml' locations.
        :rtype: list

        :example:

        >>> _get_paths_for_crossdomain('https://example.com/path/to/file')
        [
            'https://example.com/path/to/crossdomain.xml',
            'https://example.com/path/crossdomain.xml',
            'https://example.com/crossdomain.xml'
        ]

        The function removes the file extension from the last path segment and
        appends 'crossdomain.xml' to generate potential locations for the file.
        """
        parsed_url = urllib.parse.urlparse(url)
        result = []
        if parsed_url.path not in ["/", ""]:
            directories = [d for d in parsed_url.path.split("/") if d]
            if "." in directories[-1]:
                directories.pop()
            while directories:
                path = '/'.join(directories) + "/crossdomain.xml"
                result.append(urllib.parse.urlunparse((parsed_url.scheme, parsed_url.netloc, path, "", "", "")))
                directories.pop()
        # Always append the root-level crossdomain.xml path
        result.append(urllib.parse.urlunparse((parsed_url.scheme, parsed_url.netloc, "/crossdomain.xml", "", "", "")))
        return result

    def _validate_url(self, url: str) -> None:
        """
        Validate the given URL.

        Ensures the URL has a valid HTTP or HTTPS scheme and a non-empty netloc.
        Raises an error if validation fails.

        :param url: The URL to validate.
        :type url: str
        :raises: Calls `ptjsonlib.end_error` with an error message if invalid.
        """
        parsed_url = urllib.parse.urlparse(url)
        if not re.match("https?$", parsed_url.scheme):
            self.ptjsonlib.end_error("Missing or wrong scheme, only HTTP(s) schemas are supported", self.args.json)
        if not parsed_url.netloc:
            self.ptjsonlib.end_error("Provided URL is not valid", self.args.json)

    def _get_response(self, url: str, headers: dict|None = None):
        """
        Sends a GET request to the specified URL and returns the response.

        This method makes an HTTP GET request to the provided URL using optional
        custom headers. If no headers are provided, it defaults to using the
        instance's `headers` attribute. In case of a connection error, an error
        message is logged.

        :param url: The URL to send the GET request to.
        :type url: str
        :param headers: Optional headers to include in the request. Defaults to `None`.
        :type headers: dict, optional
        :return: A tuple containing the HTTP response and the response dump.
        :rtype: tuple[requests.Response, dict]
        :raises requests.RequestException: If a request exception occurs, an error is logged.
        """
        if not headers:
            headers = self.args.headers
        try:
            response, response_dump = ptmisclib.load_url_from_web_or_temp(url, method="GET", headers=headers, proxies=self.args.proxy, timeout=self.args.timeout, redirects=True, verify=False, cache=self.args.cache, dump_response=True)
            return response, response_dump
        except requests.RequestException as err:
            self.ptjsonlib.end_error(f"Cannot connect to server:", details=err, condition=self.args.json)

def get_help():
    return [
        {"description": ["Crossdomain.xml Testing Tool"]},
        {"usage": ["ptcrossd <options>"]},
        {"usage_example": [
            "ptcrossd -u https://www.example.com/crossdomain.xml",
        ]},
        {"options": [
            ["-u",  "--url",                    "<url>",            "Connect to URL"],
            ["-cf", "--cross-domain-file",      "",                 "Test crossdomain.xml"],
            ["-ch", "--cross-origin-header",    "",                 "Test Access-Control-Allow-Origin header"],
            ["-p",  "--proxy",                  "<proxy>",          "Set proxy (e.g. http://127.0.0.1:8080)"],
            ["-T",  "--timeout",                "<timeout>",        "Set timeout (default to 10)"],
            ["-c",  "--cookie",                 "<cookie>",         "Set cookie"],
            ["-a", "--user-agent",              "<user-agent>",     "Set User-Agent header"],
            ["-H",  "--headers",                "<header:value>",   "Set custom header(s)"],
            ["-C",  "--cache",                  "",                 "Cache requests"],
            ["-v",  "--version",                "",                 "Show script version and exit"],
            ["-h",  "--help",                   "",                 "Show this help message and exit"],
            ["-j",  "--json",                   "",                 "Output in JSON format"],
        ]
        }]


def parse_args():
    parser = argparse.ArgumentParser(add_help="False")
    parser.add_argument("-u",   "--url",                 type=str, required=True)
    parser.add_argument("-p",   "--proxy",               type=str)
    parser.add_argument("-c",   "--cookie",              type=str)
    parser.add_argument("-a",   "--user-agent",          type=str, default="Penterep Tools")
    parser.add_argument("-T",   "--timeout",             type=int, default=10)
    parser.add_argument("-H",   "--headers",             type=ptmisclib.pairs, nargs="+")
    parser.add_argument("-cf",  "--cross-domain-file",   action="store_true")
    parser.add_argument("-ch",  "--cross-origin-header", action="store_true")
    parser.add_argument("-j",   "--json",                action="store_true")
    parser.add_argument("-C",   "--cache",               action="store_true")
    parser.add_argument("-v",   "--version",             action="version", version=f"{SCRIPTNAME} {__version__}")

    parser.add_argument("--socket-address",          type=str, default=None)
    parser.add_argument("--socket-port",             type=str, default=None)
    parser.add_argument("--process-ident",           type=str, default=None)



    if len(sys.argv) == 1 or "-h" in sys.argv or "--help" in sys.argv:
        ptprinthelper.help_print(get_help(), SCRIPTNAME, __version__)
        sys.exit(0)

    args = parser.parse_args()

    args.proxy = {"http": args.proxy, "https": args.proxy} if args.proxy else None
    args.timeout = args.timeout if not args.proxy else None
    args.headers = ptnethelper.get_request_headers(args)

    if not any([args.cross_domain_file, args.cross_origin_header]):
        args.cross_domain_file = args.cross_origin_header = True

    args.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.100 Safari/537.36"
    args.headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    args.headers["Accept-Language"] = "foo"
    args.headers["Accept-Encoding"] = "cs-cz"
    args.headers["Priority"] = "u=0, i"

    ptprinthelper.print_banner(SCRIPTNAME, __version__, args.json)
    return args


def main():
    global SCRIPTNAME
    SCRIPTNAME = "ptcrossd"
    requests.packages.urllib3.disable_warnings()
    args = parse_args()
    script = PtCrossd(args)
    script.run(args)


if __name__ == "__main__":
    main()
