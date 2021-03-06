from abusehelper.core import rules
from abusehelper.core.runtime import *

dshield_template = """
# This is a mail that is based on the DShield template.

# Here is the data:
%(attach_and_embed_csv, report.csv, |, asn, ip, timestamp=%(updated)s, ptr=, cc=, type=scanners, ticket=0, info=firstseen: %(firstseen)s lastseen: %(lastseen)s)s

# Regards,
# Generic Abuse Handling Organization
"""

def parse_netblock(string):
    split = string.split("/", 1)
    if len(split) == 1:
        return split[0], 32
    return split[0], int(split[1])

def netblock_rule(parsed_netblocks):
    return rules.OR(*[rules.NETBLOCK(*x) for x in parsed_netblocks])

class Customer(object):
    prefix = ""
    filter_rule = None

    # AS info
    netblocks = []

    # Mailer options
    to = []
    cc = []
    template = dshield_template
    times = ["08:00"]

    def __init__(self, name, asn, **keys):
        self.name = name
        self.asn = asn

        for key, value in keys.items():
            setattr(self, key, value)

    def runtime(self):
        return [
            Session("dshield", asns=[self.asn])
            | Room(self.prefix + "asn" + unicode(self.asn))
            | Session("roomgraph", rule=self.filter_rule)
            | Room(self.prefix + "customer." + self.name)
            | Session("mailer",
                      "customer", self.name,
                      to=self.to,
                      cc=self.cc,
                      times=self.times,
                      template=self.template)
            ]

CUSTOMERS = [
    Customer("customer1", 123),
    Customer("customer2", 123, netblocks=["128.0.0.0/1"]),
    ]

def configs():
    netblocks = dict()

    for customer in CUSTOMERS:
        if customer.netblocks:
            parsed = map(parse_netblock, customer.netblocks)
            netblocks.setdefault(customer.asn, set()).update(parsed)

    for customer in CUSTOMERS:
        rule = rules.CONTAINS(asn=str(customer.asn))

        if customer.netblocks:
            rule = rules.AND(rule,
                             netblock_rule(map(parse_netblock, customer.netblocks)))
        elif customer.asn not in netblocks:
            pass
        else:
            rule = rules.AND(rule, rules.NOT(netblock_rule(netblocks[customer.asn])))

        customer.filter_rule = rule
        yield customer
