#!/usr/bin/env python3
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
BGPAT_MP_REACH_NLRI = 14
BGPAT_MP_UNREACH_NLRI = 15

MPBGP_IPV4_AFI = 1
MPBGP_IPV6_AFI = 2
MPBGP_UNICAST_SAFI = 1


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

# MPATTR
# +---------------------------------------------------------+
# | Address Family Identifier (2 octets)                    |
# +---------------------------------------------------------+
# | Subsequent Address Family Identifier (1 octet)          |
# +---------------------------------------------------------+
# | Length of Next Hop Network Address (1 octet)            |
# +---------------------------------------------------------+
# | Network Address of Next Hop (variable)                  |
# +---------------------------------------------------------+
# | Number of SNPAs (1 octet)                               |
# +---------------------------------------------------------+
# | Length of first SNPA(1 octet)                           |
# +---------------------------------------------------------+
# | First SNPA (variable)                                   |
# +---------------------------------------------------------+
# | Length of second SNPA (1 octet)                         |
# +---------------------------------------------------------+
# | Second SNPA (variable)                                  |
# +---------------------------------------------------------+
# | ...                                                     |
# +---------------------------------------------------------+
# | Length of Last SNPA (1 octet)                           |
# +---------------------------------------------------------+
# | Last SNPA (variable)                                    |
# +---------------------------------------------------------+
# | Network Layer Reachability Information (variable)       |
# +---------------------------------------------------------+

BGP_MAX_UPDATE_LEN = 4096 - 19


def make_msg(typ, data):
    marker = bytes((0xff, )) * 16
    return marker + struct.pack("!HB", len(data) + 19, typ) + data


def get_aspath_attr(aslist):
    acount = len(aslist)
    # if as4:
    if True:  # pylint: disable=W0125
        alen = 2 + 4 * acount
        afmt = "!L"
    else:
        alen = 2 + 2 * acount
        afmt = "!H"
    aspath = struct.pack("!BBBBB", BGPAF_TRANS, BGPAT_ASPATH, alen,
                         BGPAT_ASPATH_ST_SEQ, acount)
    for asn in aslist:
        aspath += struct.pack(afmt, asn)

    return aspath


def get_attrs(aslist, nexthop):
    # ------
    # Origin
    # ------
    attrs = BGP_ORIGIN_VALUE_IGP

    # -------
    # AS-PATH
    # -------
    attrs += get_aspath_attr(aslist)

    if nexthop.version == 4:
        # --------
        # Next-Hop
        # --------
        attrs += bytes((BGPAF_TRANS, BGPAT_NEXTHOP, len(nexthop.packed)))
        assert len(nexthop.packed) == 4
        attrs += nexthop.packed
        mpattr = b""
    else:
        # Now add IPv6 multiprotocol attr
        mpattr = bytes((
            BGPAF_OPTIONAL | BGPAF_LONGLEN,
            BGPAT_MP_REACH_NLRI,
        ))
        # pad for len, afi, safi, nhlen, nh
        mpattr += struct.pack("!HHBB", 0, MPBGP_IPV6_AFI, MPBGP_UNICAST_SAFI,
                              len(nexthop.packed))
        mpattr += nexthop.packed
        # 0 SNPA
        mpattr += b"\x00"

    return attrs, mpattr


def get_update_header(aslist, nexthop):
    # No withdraw, add attributes
    attrs, mpattr = get_attrs(aslist, nexthop)
    alen = len(attrs) + len(mpattr)
    # data = struct.pack("!HH", 0, len(attrs)) + attrs
    return attrs, mpattr, 4096 - 23 - alen


# Pack as many NRLI into a single update as possible
def gen_routes_update(  # pylint: disable=R0913,R0914
        outfile,  # pylint: disable=R0913,R0914
        prefix,  # pylint: disable=R0913,R0914
        sublen,  # pylint: disable=R0913,R0914
        nexthop,  # pylint: disable=R0913,R0914
        maxpack,  # pylint: disable=R0913,R0914
        maxroute,  # pylint: disable=R0913,R0914
        aspath,  # pylint: disable=R0913,R0914
        incroot,  # pylint: disable=R0913,R0914
        modroot):  # pylint: disable=R0913,R0914
    # print(prefix, sublen, seqno)

    def write_update(attrs, mpattr, nlri):
        # BGP Header: marker[16], len[2], type[1]
        alen = len(attrs)
        if mpattr:
            alen = len(attrs) + len(mpattr) + len(nlri)
            mlen = alen
        else:
            alen = len(attrs)
            mlen = alen + len(nlri)
        # message len is + 16 (marker) + 2 (len) + 1 (type) + 2 (withlen) + 2 (attrlen)
        msghdr = bytes((0xff, )) * 16 + \
            struct.pack("!HB", mlen + 23, BGP_MSGTYPE_UPDATE) + \
            struct.pack("!HH", 0, alen) # 0 withdraw, attrlen
        # header
        outfile.write(msghdr)
        # attrs
        outfile.write(attrs)
        if mpattr:
            # mpattr 1 flags, 1 type, 2 length of mpattr value + nlri, rest of mpattr and nrli
            mplen = len(mpattr[4:]) + len(nlri)
            mpattr = mpattr[:2] + struct.pack("!H", mplen) + mpattr[4:]
            outfile.write(mpattr)
        outfile.write(nlri)

    aslist = [int(x) for x in aspath if x]
    rootas = aslist[-1]

    attrs, mpattr, remain = get_update_header(aslist, nexthop)
    nlri = b""
    ucount = 0
    mcount = 0
    count = 0

    for rprefix in prefix.subnets(new_prefix=sublen):
        if (count % 10000) == 0:
            print("routes: {}".format(count), end='\r')

        p = packprefix(rprefix)
        plen = len(p)

        if plen > remain or mcount == maxpack:
            write_update(attrs, mpattr, nlri)
            ucount += 1
            # Possibly update the AS PATH
            if incroot:
                aslist[-1] += 1
                if modroot:
                    aslist[-1] %= modroot
            attrs, mpattr, remain = get_update_header(aslist, nexthop)
            nlri = b""
            mcount = 0

        nlri += p
        remain -= plen
        count += 1
        mcount += 1

        if count == maxroute:
            break

    if mcount:
        write_update(attrs, mpattr, nlri)
        ucount += 1

    return ucount, count


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
    # print("MRT Record: type {} subtype {} len {}".format(typ, subtype, vlen))
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


def genroute(outfile, prefix, nexthop, aslist, seqno):
    #print("Adding {} via {} seqno {}".format(prefix, nexthop, seqno))

    routefile = io.BytesIO()
    routefile.write(struct.pack("!L", seqno))
    routefile.write(packprefix(prefix))
    # 1 entry
    routefile.write(b"\x00\x01")
    # 1st peer, originated now
    origtime = int(time.time())
    routefile.write(struct.pack("!HL", 0, origtime))

    # Origin
    attrs = BGP_ORIGIN_VALUE_IGP

    # AS-PATH
    attrs += get_aspath_attr(aslist)

    # Next-Hop
    nhlen = len(nexthop.packed)
    if nexthop.version == 4:
        assert nhlen == 4
        attrs += bytes((BGPAF_TRANS, BGPAT_NEXTHOP, nhlen))
        attrs += nexthop.packed
    else:
        attrs += bytes((BGPAF_OPTIONAL, BGPAT_MP_REACH_NLRI, nhlen + 5,)) + \
            struct.pack("!HBB", MPBGP_IPV6_AFI, MPBGP_UNICAST_SAFI, nhlen)
        attrs += nexthop.packed
        # 0 SNPA
        attrs += b"\x00"

    routefile.write(struct.pack("!H", len(attrs)))
    routefile.write(attrs)

    if prefix.version == 4:
        subtype = TD_STYPE_RIB_IPV4_UNICAST
    else:
        subtype = TD_STYPE_RIB_IPV6_UNICAST

    mrtencode(outfile, MRT_TYPE_TABLE_DUMP_V2, subtype, routefile.getvalue())


def genroutes(  # pylint: disable=R0913,R0914
        outfile,  # pylint: disable=R0913,R0914
        prefix,  # pylint: disable=R0913,R0914
        sublen,  # pylint: disable=R0913,R0914
        nexthop,  # pylint: disable=R0913,R0914
        seqno,  # pylint: disable=R0913,R0914
        maxpack,  # pylint: disable=R0913,R0914
        maxroute,  # pylint: disable=R0913,R0914
        aspath,  # pylint: disable=R0913,R0914
        incroot,  # pylint: disable=R0913,R0914
        modroot):  # pylint: disable=R0913,R0914

    aslist = [int(x) for x in aspath if x]
    rootas = aslist[-1]

    for count, rprefix in enumerate(prefix.subnets(new_prefix=sublen)):
        if (seqno % 10000) == 0:
            print("routes: {}".format(count), end='\r')

        genroute(outfile, rprefix, nexthop, aslist, seqno)

        if incroot:
            # Max Pack tells us when to increment we allow maxpack routes to have same AS
            if maxpack < 2 or seqno % maxpack == 0:
                aslist[-1] += 1
                if modroot:
                    aslist[-1] %= modroot

        if count == maxroute:
            break

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
    parser = argparse.ArgumentParser("Inject BGP route file into peer")
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--root-as-inc", action="store_true", help="increment the root as")
    parser.add_argument(
        "--root-as-mod",
        type=int,
        default=0,
        help="modulus the incrementing root as")
    parser.add_argument(
        "--aspath", default="20", help="comma sep list of asnumbers")
    parser.add_argument(
        "-m",
        "--max-routes",
        type=int,
        default=0xFFFFFFFF,
        help="Maximum number of prefixes to generate [default: 4 billion]")
    parser.add_argument(
        "--max-pack",
        type=int,
        default=0xFFFF,
        help="Maximum number of prefixes to generate [default: 4 billion]")
    parser.add_argument(
        "-p",
        "--peers",
        help="Space sep list of peers in form peerid,peerip,peeras")
    parser.add_argument(
        "-t", "--tabledump", help="File to write MRT table dump into")
    parser.add_argument(
        "-u", "--update", help="File to write BGP updates into")
    parser.add_argument(
        "tuples", nargs="*", help="PREFIX SUBLEN NEXTHOP pairs")
    args = parser.parse_args()

    aspath = args.aspath.split(",")
    incroot = args.root_as_inc
    modroot = args.root_as_mod
    maxroute = args.max_routes
    maxpack = args.max_pack

    if args.update:
        if args.update == "-":
            assert args.tabledump != "-"
            outfile = sys.stdout.buffer
        else:
            outfile = open(args.update, "wb")
        routecount = 0
        updatecount = 0
        for pfx, sublen, nexthop in triples(args.tuples):
            prefix = ipaddress.ip_network(pfx)
            nexthop = ipaddress.ip_address(nexthop)
            assert prefix.version == nexthop.version
            ucount, count = gen_routes_update(outfile, prefix, int(sublen),
                                              nexthop, maxpack, maxroute,
                                              aspath, incroot, modroot)
            updatecount += ucount
            routecount += count
            maxroute -= count
            if maxroute <= 0:
                break
        print("Wrote {} BGP updates with {} total NLRI".format(
            updatecount, routecount))

    if args.tabledump:
        if args.tabledump == "-":
            assert args.upddate != "-"
            outfile = sys.stdout.buffer
        else:
            outfile = open(args.tabledump, "wb")
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
            # print("Prefix sublen args must come in pairs\n")
            sys.exit(1)

        # ---------------
        # Generate Routes
        # ---------------

        seqno = 0
        for pfx, sublen, nexthop in triples(args.tuples):
            prefix = ipaddress.ip_network(pfx)
            nexthop = ipaddress.ip_address(nexthop)
            assert prefix.version == nexthop.version
            seqno = genroutes(outfile, prefix, int(sublen), nexthop, seqno,
                              maxpack, maxroute, aspath, incroot, modroot)
        print("{}".format(seqno))


if __name__ == "__main__":
    main()

__author__ = 'Christian E. Hopps'
__date__ = 'July 20 2018'
__version__ = '1.0'
__docformat__ = "restructuredtext en"
