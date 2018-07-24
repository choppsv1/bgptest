# -*- coding: utf-8 eval: (yapf-mode 1) -*-
#
# July 20 2018, Christian E. Hopps <chopps@gmail.com>
#
import argparse
import io
import ipaddress
import time
import struct
import sys

# MRT Types
MRT_TYPE_TABLE_DUMP_V2 = 13
MRT_TYPE_BGP4MP = 16
MRT_TYPE_BGP4MP_ET = 17

# Table Dump Subtypes
TD_STYPE_PEER_INDEX_TABLE = 1
TD_STYPE_RIB_IPV4_UNICAST = 2
TD_STYPE_RIB_IPV4_MULTICAST = 3
TD_STYPE_RIB_IPV6_UNICAST = 4
TD_STYPE_RIB_IPV6_MULTICAST = 5
TD_STYPE_RIB_GENERIC = 6

BGP4MP_STYPE_STATE_CHANGE = 0
BGP4MP_STYPE_MESSAGE = 1
BGP4MP_STYPE_ENTRY = 2
BGP4MP_STYPE_SNAPSHOT = 3
BGP4MP_STYPE_MESSAGE_AS4 = 4
BGP4MP_STYPE_STATE_CHANGE_AS4 = 5
BGP4MP_STYPE_MESSAGE_LOCAL = 6
BGP4MP_STYPE_MESSAGE_AS4_LOCAL = 7

BGP_MSGTYPE_OPEN = 1
BGP_MSGTYPE_UPDATE = 2
BGP_MSGTYPE_NOTIFICATION = 3
BGP_MSGTYPE_KEEPALIVE = 4

# BGP UPDATE:

BGPAF_OPTIONAL = 0x80
BGPAF_TRANS = 0x40
BGPAF_PARTIAL = 0x20
BGPAF_LONGLEN = 0x10

BGPAT_ORIGIN = 1
BGPAT_ORIGIN_IGP = 0
BGPAT_ORIGIN_EGP = 1
BGPAT_ORIGIN_INCOMPLETE = 2
BGP_ORIGIN_VALUE_IGP = b"\x40\x01\x01\x00"
BGP_ORIGIN_VALUE_EGP = b"\x40\x01\x01\x01"
BGP_ORIGIN_VALUE_INCOMPLETE = b"\x40\x01\x01\x02"

BGPAT_ASPATH = 2
# [[segment] ... ]
#byes:       1   1   N*2
#segment: [type][N][value]
BGPAT_ASPATH_ST_SET = 1
BGPAT_ASPATH_ST_SEQ = 2
# ASPATH sequence: ( 20 )
BGP_ASPATH_VALUE_20 = b"\x40\x02\x06\x02\x01\x00\x00\x00\x14"

BGPAT_NEXTHOP = 3


def packprefix(prefix):
    packed = prefix.network_address.packed
    plen = prefix.prefixlen
    olen, blen = plen // 8, plen % 8
    if blen:
        p = packed[0:olen + 1]
    else:
        p = packed[0:olen]
    return bytes((plen, )) + p


# ----------
# BGP UPDATE
# ----------

# +-----------------------------------------------------+
# |   Unfeasible Routes Length (2 octets)               |
# +-----------------------------------------------------+
# |  Withdrawn Routes (variable)                        |
# +-----------------------------------------------------+
# |   Total Path Attribute Length (2 octets)            |
# +-----------------------------------------------------+
# |    Path Attributes (variable)                       |
# +-----------------------------------------------------+
# |   Network Layer Reachability Information (variable) |
# +-----------------------------------------------------+

# ---------
# MRTHeader
# ---------

#  0                   1                   2                   3
#  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                           Timestamp                           |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |             Type              |            Subtype            |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                             Length                            |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                      Message... (variable)
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


def mrtencode(outfile, typ, subtype, value):
    ts = int(time.time())
    vlen = len(value)
    print("MRT Record: type {} subtype {} len {}".format(typ, subtype, vlen))
    outfile.write(struct.pack("!LHHL", ts, typ, subtype, vlen))
    outfile.write(value)


# TABLE_DUMPv2

# 4.3.1.  PEER_INDEX_TABLE Subtype
#  0                   1                   2                   3
#  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                      Collector BGP ID                         |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |       View Name Length        |     View Name (variable)      |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |          Peer Count           |    Peer Entries (variable)
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# Peer Entries:
#  0                   1                   2                   3
#  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |   Peer Type   |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                         Peer BGP ID                           |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                   Peer IP Address (variable)                  |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                        Peer AS (variable)                     |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# Peer Type Field
#  0 1 2 3 4 5 6 7
# +-+-+-+-+-+-+-+-+
# | | | | | | |A|I|
# +-+-+-+-+-+-+-+-+
#
# Bit 6: Peer AS number size:  0 = 16 bits, 1 = 32 bits
# Bit 7: Peer IP Address family:  0 = IPv4,  1 = IPv6
#


def genpeers(outfile, peers):
    collector_id = ipaddress.ip_address("10.0.0.1")
    viewname = "view"
    peercount = len(peers)

    # Header
    outfile.write(collector_id.packed)
    outfile.write(struct.pack("!H", len(viewname)))
    outfile.write(viewname.encode("utf-8"))
    outfile.write(struct.pack("!H", peercount))

    # Peers
    for bgpid, peerip, peeras in peers:
        # 4 byte AS
        ptype = 0x2
        if peerip.version == 6:
            ptype |= 0x1
        outfile.write(struct.pack("!B4s", ptype, bgpid.packed))
        outfile.write(peerip.packed)
        if (ptype & 0x2) != 0:  # 4 byte AS
            outfile.write(struct.pack("!L", peeras))
        else:
            outfile.write(struct.pack("!H", peeras))


# 4.3.2.  AFI/SAFI-Specific RIB Subtypes - RIB Entry Header
#  0                   1                   2                   3
#  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                         Sequence Number                       |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# | Prefix Length |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                        Prefix (variable)                      |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |         Entry Count           |  RIB Entries (variable)
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# 4.3.4.  RIB Entries
#  0                   1                   2                   3
#  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |         Peer Index            |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                         Originated Time                       |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |      Attribute Length         |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                    BGP Attributes... (variable)
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


def genroute(outfile, prefix, nexthop, seqno):
    print("Adding {} via {} seqno {}".format(prefix, nexthop, seqno))

    outfile.write(struct.pack("!L", seqno))
    outfile.write(packprefix(prefix))
    # 1 entry
    outfile.write(b"\x00\x01")
    # 1st peer, originated now
    origtime = int(time.time())
    outfile.write(struct.pack("!HL", 0, origtime))

    # Origin
    attrs = BGP_ORIGIN_VALUE_IGP
    # AS-PATH
    attrs += BGP_ASPATH_VALUE_20
    # Next-Hop
    attrs += bytes((BGPAF_TRANS, BGPAT_NEXTHOP, len(nexthop.packed)))
    assert len(nexthop.packed) == 4
    attrs += nexthop.packed

    outfile.write(struct.pack("!H", len(attrs)))
    outfile.write(attrs)


def genroutes(outfile, prefix, sublen, nexthop, seqno):
    for rprefix in prefix.subnets(new_prefix=sublen):
        genroute(outfile, rprefix, nexthop, seqno)
        seqno += 1
        if seqno > 0xFFFFFFFF:
            seqno = 0
    return seqno


def genribhdr():
    struct.pack("L")


def triples(l):
    i = iter(l)
    try:
        while True:
            yield next(i), next(i), next(i)
    except StopIteration:
        return


def main():
    global routerid

    parser = argparse.ArgumentParser("Generate BGP route file")
    # parser.add_argument("-a", "--ascii", action="store_true", help="Output ASCII")
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "-r", "--routerid", default="10.0.0.1", help="BGP Router ID")
    parser.add_argument(
        "-p",
        "--peers",
        help="Space sep list of peers in form peerid,peerip,peeras")
    parser.add_argument(
        "-o", "--output", default="-", help="File to read write to")
    parser.add_argument(
        "tuples", nargs="*", help="PREFIX SUBLEN NEXTHOP pairs")
    args = parser.parse_args()

    if not args.output:
        outfile = sys.stdout.buffer
    else:
        outfile = open(args.output, "wb")

    routerid = ipaddress.ip_address(args.routerid)

    # -------------------------
    # Generate Peer Index Table
    # -------------------------

    peerlist = [X.split(",") for X in args.peers.split()]
    peers = [(ipaddress.ip_address(x), ipaddress.ip_address(y), int(z))
             for x, y, z in peerlist]
    peerfile = io.BytesIO()
    genpeers(peerfile, peers)
    mrtencode(outfile, MRT_TYPE_TABLE_DUMP_V2, TD_STYPE_PEER_INDEX_TABLE,
              peerfile.getvalue())

    if len(args.tuples) % 3:
        print("Prefix sublen args must come in pairs\n")
        sys.exit(1)

    # ---------------
    # Generate Routes
    # ---------------

    seqno = 0
    for pfx, sublen, nexthop in triples(args.tuples):
        routefile = io.BytesIO()
        prefix = ipaddress.ip_network(pfx)
        nexthop = ipaddress.ip_address(nexthop)
        assert prefix.version == nexthop.version
        seqno = genroutes(routefile, prefix, int(sublen), nexthop, seqno)

        if prefix.version == 4:
            subtype = TD_STYPE_RIB_IPV4_UNICAST
        else:
            subtype = TD_STYPE_RIB_IPV6_UNICAST
        mrtencode(outfile, MRT_TYPE_TABLE_DUMP_V2, subtype,
                  routefile.getvalue())


if __name__ == "__main__":
    main()

__author__ = 'Christian E. Hopps'
__date__ = 'July 20 2018'
__version__ = '1.0'
__docformat__ = "restructuredtext en"
