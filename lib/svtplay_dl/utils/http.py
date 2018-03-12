import re
import logging

from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry



# Used for UA spoofing in get_http_data()
FIREFOX_UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.3'

retry = Retry(
    total=5,
    read=5,
    connect=5,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504)
)


class HTTP(Session):
    def __init__(self, options, *args, **kwargs):
        Session.__init__(self, *args, **kwargs)
        adapter = HTTPAdapter(max_retries=retry)
        self.mount('http://', adapter)
        self.mount('https://', adapter)
        self.verify = options.ssl_verify
        self.proxy = options.proxy
        if options.http_headers:
            self.headers.update(self.split_header(options.http_headers))
        self.headers.update({"User-Agent": FIREFOX_UA})

    def check_redirect(self, url):
        return self.get(url, stream=True).url

    def request(self, method, url, *args, **kwargs):
        headers = kwargs.pop("headers", None)
        if headers:
            for i in headers.keys():
                self.headers[i] = headers[i]
        logging.debug("HTTP getting %r", url)
        res = Session.request(self, method, url, verify=self.verify, proxies=self.proxy, *args, **kwargs)
        return res

    def split_header(self, headers):
        return dict(x.split('=') for x in headers.split(';'))



def download_thumbnail(options, url):
    data = Session.get(url).content

    filename = re.search(r"(.*)\.[a-z0-9]{2,3}$", options.output)
    tbn = "%s.tbn" % filename.group(1)
    logging.info("Thumbnail: %s", tbn)

    fd = open(tbn, "wb")
    fd.write(data)
    fd.close()