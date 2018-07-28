#!/usr/bin/env python3
# -*- coding: utf-8 eval: (yapf-mode 1) -*-
#
# July 20 2018, Christian E. Hopps <chopps@gmail.com>
#

import ipaddress
import os
import sys
import time

LOCALAS = os.environ["LOCALAS"]
LOCALIP = os.environ["LOCALIP"]
MAXROUTES = os.environ["MAXROUTES"]
PEERAS = os.environ["PEERAS"]
PEERIP = os.environ["PEERIP"]

prefix = ipaddress.ip_network("fc{}:{}{}::/32".format(LOCALAS, LOCALAS,
                                                      LOCALAS))
nexthop = ipaddress.ip_address(LOCALIP)

time.sleep(2)

for count, subnet in enumerate(prefix.subnets(new_prefix=64)):
    if count == MAXROUTES:
        break
    msg = "announce route {} next-hop {}\n".format(subnet, nexthop)
    sys.stdout.write(msg)
    sys.stdout.flush()

# Stick around
while True:
    time.sleep(10)
