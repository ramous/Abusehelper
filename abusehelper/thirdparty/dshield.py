import csv
import urllib
import urllib2
import urlparse
import zlib
import gzip
import cStringIO as StringIO

from idiokit import threado, util, threadpool
from abusehelper.core import events

def sanitize_ip(ip):
    # Remove leading zeros from (strings resembling) IPv4 addresses.
    if not isinstance(ip, basestring):
        return ip
    try:
        return ".".join(map(str, map(int, ip.split("."))))
    except ValueError:
        pass
    return ip

def read_data(fileobj, compression=9):
    stringio = StringIO.StringIO()
    compressed = gzip.GzipFile(None, "wb", compression, stringio)

    while True:
        data = fileobj.read(2**16)
        if not data:
            break
        compressed.write(data)
    compressed.close()

    stringio.seek(0)
    return gzip.GzipFile(fileobj=stringio)

@threado.stream
def dshield(inner, asn):
    # The current DShield csv fields, in order.
    headers = ["ip", "reports", "targets", "firstseen", "lastseen", "updated"]

    # Probably a kosher-ish way to create an ASN specific URL.
    parsed = urlparse.urlparse("https://secure.dshield.org/asdetailsascii.html")
    parsed = list(parsed)
    parsed[4] = urllib.urlencode({ "as" : str(asn) })
    url = urlparse.urlunparse(parsed)

    opened = yield threadpool.run(urllib2.urlopen, url)
    data = yield threadpool.run(read_data, opened)

    try:
        # Lazily filter away empty lines and lines starting with '#'
        filtered = (x for x in data if x.strip() and not x.startswith("#"))
        reader = csv.DictReader(filtered, headers, delimiter="\t")
        for row in reader:
            # DShield uses leading zeros for IP addresses. Try to
            # parse and then unparse the ip back, to get rid of those.
            row["ip"] = sanitize_ip(row.get("ip", None))
            
            # Convert the row to an event, send it forwards in the
            # pipeline. Forcefully encode the values to unicode.
            event = events.Event()
            event.add('asn', str(asn))
            for key, value in row.items():
                if value is None:
                    continue
                event.add(key, util.guess_encoding(value).strip())
            inner.send(event)
            yield
    finally:
        opened.close()

if __name__ == "__main__":
    for event in dshield(3249): # dshield("3249") works too, doesn't matter
        print event.attrs