#!/usr/bin/env python3
# -*- coding: utf-8 eval: (yapf-mode 1) -*-
#
# July 19 2018, Christian E. Hopps <chopps@gmail.com>
#
# Copyright (c) 2018, Deutsche Telekom AG.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import argparse
import asyncore
import errno
import ipaddress
import logging
import os
import pwd
import sys
import socket
import traceback
from struct import unpack
import time

log = logging.getLogger("BGP-INJECT")
log.addHandler(logging.StreamHandler(sys.stderr))


def exabgp(localip, routerid, asn, peerip, peerport, peeras):
    from exabgp.reactor.api.command.command import Command
    from exabgp.reactor.api.command.limit import match_neighbors
    from exabgp.reactor.api.command.limit import extract_neighbors

    @Command.register('text', 'send-raw-data')
    def send_raw_data(self, reactor, service, line):
        def callback():
            try:
                descriptions, command = extract_neighbors(line)
                peers = match_neighbors(reactor.peers, descriptions)
                if not peers:
                    self.log_failure(
                        'no neighbor matching the command : %s' % command)
                    reactor.processes.answer(service, 'error')
                    yield True
                    return

                # filename, _ = command.split(' ', 1)
                with open(command, "rb") as datafile:
                    rawdata = datafile.read()

                assert rawdata
                self.connection.writer(rawdata)
                reactor.processes.answer_done(service)
            except Exception:
                self.log_failure('issue parsing the route')
                reactor.processes.answer(service, 'error')
                yield True
            except IndexError:
                self.log_failure('issue parsing the route')
                reactor.processes.answer(service, 'error')
                yield True
            reactor.asynchronous.schedule(service, line, callback())

    # from exabgp.util.od import od

    # class BGPHandler(asyncore.dispatcher_with_send):
    #     wire = not not os.environ.get('wire', '')
    #     update = True

    #     keepalive = bytes((0xFF, )) * 16 + bytes((0x0, 0x13, 0x4))

    #     _name = {
    #         bytes((1, )): 'OPEN',
    #         bytes((2, )): 'UPDATE',
    #         bytes((3, )): 'NOTIFICATION',
    #         bytes((4, )): 'KEEPALIVE',
    #     }

    #     def isupdate(self, header):
    #         return header[18] == chr(2)

    #     def name(self, header):
    #         return self._name.get(header[18], 'SOME WEIRD RFC PACKET')

    #     def routes(self, body):
    #         len_w = unpack('!H', body[0:2])[0]
    #         prefixes = [ord(_) for _ in body[2:2 + len_w:]]

    #         if not prefixes:
    #             yield 'no ipv4 withdrawal'

    #         while prefixes:
    #             l = prefixes.pop(0)
    #             r = [0, 0, 0, 0]
    #             for index in range(4):
    #                 if index * 8 >= l: break
    #                 r[index] = prefixes.pop(0)
    #             yield 'withdraw ' + '.'.join(str(_) for _ in r) + '/' + str(l)

    #         len_a = unpack('!H', body[2 + len_w:2 + len_w + 2])[0]
    #         prefixes = [ord(_) for _ in body[2 + len_w + 2 + len_a:]]

    #         if not prefixes:
    #             yield 'no ipv4 announcement'

    #         while prefixes:
    #             l = prefixes.pop(0)
    #             r = [0, 0, 0, 0]
    #             for index in range(4):
    #                 if index * 8 >= l: break
    #                 r[index] = prefixes.pop(0)
    #             yield 'announce ' + '.'.join(str(_) for _ in r) + '/' + str(l)

    #     def announce(self, *args):
    #         log.info("{}".format(self.ip, self.port, ' '.join(
    #             str(_) for _ in args) if len(args) > 1 else args[0]))

    #     def setup(self, record, ip, port):
    #         self.ip = ip
    #         self.port = port
    #         now = time.strftime("%a-%d-%b-%Y-%H:%M:%S", time.gmtime())
    #         self.record = open("%s-%s" % ('bgp', now), 'w') if record else None
    #         self.handle_read = self.handle_open
    #         self.update_count = 0
    #         self.time = time.time()
    #         return self

    #     def read_message(self):
    #         header = b''
    #         body = b''
    #         while len(header) != 19:
    #             try:
    #                 left = 19 - len(header)
    #                 header += self.recv(left)
    #                 if self.wire: self.announce("HEADER ", od(header))
    #                 if self.wire and len(header) != 19:
    #                     self.announce("left", 19 - len(header))
    #                 if left == 19 - len(header):  # ugly
    #                     # the TCP session is gone.
    #                     self.announce("TCP connection closed")
    #                     self.close()
    #                     return None, None
    #             except socket.error as exc:
    #                 log.error("read_message0: Exception %s", str(exc))
    #                 if exc.args[0] in (errno.EWOULDBLOCK, errno.EAGAIN):
    #                     continue
    #                 raise exc

    #         self.announce("read", self.name(header))

    #         try:
    #             length = unpack('!H', header[16:18])[0] - 19
    #             if self.wire: self.announce("waiting for", length, "bytes")

    #             if length > 4096 - 19:
    #                 log.error("{}".format("packet"))
    #                 log.error("{}".format(od(header)))
    #                 log.error("{}".format("Invalid length for packet", length))
    #                 sys.exit(1)

    #             left = length
    #             while len(body) != length:
    #                 try:
    #                     body += self.recv(left)
    #                     left = length - len(body)
    #                     if self.wire: self.announce("BODY   ", od(body))
    #                     if self.wire and left: self.announce("missing", left)
    #                 except socket.error as exc:
    #                     if exc.args[0] in (errno.EWOULDBLOCK, errno.EAGAIN):
    #                         continue
    #                     raise exc

    #             self.update_count += 1

    #             if self.record:
    #                 self.record.write(header + body)

    #             elif self.isupdate(header):
    #                 self.announce("received %-6d updates (%6d/sec) " %
    #                               (self.update_count, self.update_count /
    #                                (time.time() - self.time)), ', '.join(
    #                                    self.routes(body)))

    #             return header, body
    #         except Exception as ex:
    #             log.error("read_message: Exception %s: %s", str(ex),
    #                       traceback.format_exc())

    #     def handle_open(self):
    #         # reply with a IBGP response with the same capability (just changing routerID)
    #         try:
    #             header, body = self.read_message()
    #             assert body is not None
    #             routerid = bytes(((body[8] + 1) & 0xFF, ))
    #             self.announce("sending open")
    #             o = header + body[:8] + routerid + body[9:]
    #             self.send(o)
    #             self.announce("sending keepalive")
    #             self.send(self.keepalive)
    #             self.handle_read = self.handle_keepalive
    #         except Exception as ex:
    #             log.error("handle_open2: Exception %s: %s", str(ex),
    #                       traceback.format_exc())
    #             raise

    #     def handle_keepalive(self):
    #         header, body = self.read_message()
    #         if header is not None:
    #             self.announce("sending keepalive")
    #             self.send(self.keepalive)

    # class BGPServer(asyncore.dispatcher):
    #     def __init__(self, host, port, record):
    #         self.record = record
    #         asyncore.dispatcher.__init__(self)
    #         if host.version == 4:
    #             self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
    #         else:
    #             self.create_socket(socket.AF_INET6, socket.SOCK_STREAM)
    #         self.set_reuse_addr()
    #         self.bind((str(host), port))
    #         self.listen(5)

    #     def handle_accept(self):
    #         pair = self.accept()
    #         if pair is not None:
    #             # The if prevent invalid unpacking
    #             sock, addr = pair  # pylint: disable=W0633
    #             log.warning("{}".format("new BGP connection from", addr))
    #             self.peer = BGPHandler(sock).setup(self.record, *addr)

    # def droproot():
    #     uid = os.getuid()
    #     gid = os.getgid()

    #     if uid and gid:
    #         return

    #     for name in [
    #             'nobody',
    #     ]:
    #         try:
    #             user = pwd.getpwnam(name)
    #             nuid = int(user.pw_uid)
    #             ngid = int(user.pw_uid)
    #         except KeyError:
    #             pass

    #     if not gid:
    #         os.setgid(ngid)
    #     if not uid:
    #         os.setuid(nuid)

    # try:
    #     # server = BGPServer(localip, peerport, False)
    #     # droproot()
    #     sock = socket.create_connection((peerip, peerport))
    #     addr = sock.getsockname()
    #     peer = BGPHandler(sock).setup(False, *addr[0:2])
    #     asyncore.loop()
    # except socket.error as ex:
    #     log.error("{}".format('need root right to bind to port 179', ex))


def ryu(routerid, asn, peerip, peerport, peeras):
    import eventlet
    from ryu.services.protocols.bgp.bgpspeaker import BGPSpeaker
    eventlet.monkey_patch()  # BGPSpeaker needs sockets patched

    def dump_remote_best_path_change(event):
        print('the best path changed:', event.remote_as, event.prefix,
              event.nexthop, event.is_withdraw)

    def detect_peer_down(remote_ip, remote_as):
        print('Peer down:', remote_ip, remote_as)

    speaker = BGPSpeaker(
        as_number=int(args.asn),
        router_id=args.router_id,
        best_path_change_handler=dump_remote_best_path_change,
        peer_down_handler=detect_peer_down)

    # XXX need to fix port arg
    speaker.neighbor_add(peerip, peeras, peerport)
    # uncomment the below line if the speaker needs to talk with a bmp server.
    # speaker.bmp_server_add('192.168.177.2', 11019)

    # count = 1
    while True:
        eventlet.sleep(30)
        #prefix = '10.20.' + str(count) + '.0/24'
        #print("add a new prefix", prefix)
        #speaker.prefix_add(prefix)
        #count += 1
        #if count == 4:
        #    speaker.shutdown()
        #    break


# This is flaky
def yabgp(routerid, asn, peerip, peeras):
    import tempfile
    from yabgp.agent import prepare_service
    from yabgp.handler import BaseHandler

    class BGPHandler(BaseHandler):
        def __init__(self):
            super(BGPHandler, self).__init__()

        def init(self):
            pass

        def on_update_error(self, peer, timestamp, msg):
            log.error('[-] UPDATE ERROR: %s: %s', str(peer), str(msg))
            #return super(BGPHandler, self).on_update_error(peer, timestamp, msg)

        def route_refresh_received(self, peer, msg, msg_type):
            log.info('[+] ROUTE_REFRESH received %s %s %s', str(peer),
                     str(msg), str(msg_type))
            #return super(BGPHandler, self).route_refresh_received(peer, msg, msg_type)

        # def keepalive_received(self, peer, timestamp):
        #     print('[+] KEEPALIVE received')

        def open_received(self, peer, timestamp, result):
            log.info('[+] OPEN received: %s: %s', str(peer), str(result))

        def update_received(self, peer, timestamp, msg):
            log.info('[+] UPDATE received %s: %s', str(peer), str(msg))

        def notification_received(self, peer, msg):
            log.error('[-] NOTIFICATION received %s: %s', str(peer), str(msg))
            #return super(BGPHandler, self).notification_received(peer, msg)

        def on_connection_lost(self, peer):
            log.error('[-] CONNECTION lost: %s', str(peer))
            #return super(BGPHandler, self).on_connection_lost(peer)

        def on_connection_failed(self, peer, msg):
            log.error('[-] CONNECTION failed %s: %s', str(peer), str(msg))
            #return super(BGPHandler, self).on_connection_failed(peer, mg)

    from yabgp.config import CONF

    # args = "--bgp-local_as={} --bgp-remote_addr={} --bgp-remote_as={} --bgp-afi_safi=ipv4,ipv6".format(
    #     asn, peerip, peeras)
    conffile = tempfile.NamedTemporaryFile(mode='w')
    conffile.write("""
[DEFAULT]
verbose=False
[message]
write_disk = False
[bgp]
local_as={}
remote_addr={}
remote_as={}
afi_safi=ipv4
four_bytes_as = True
route_refresh = False
cisco_route_refresh = False
graceful_restart = False
cisco_multi_session = False
enhanced_route_refresh = False
""".format(asn, peerip, peeras))
    conffile.flush()

    try:
        bgp_handler = BGPHandler()
        prepare_service(
            args=["--config-file=" + conffile.name], handler=bgp_handler)
    except Exception as e:
        print(e)


def main():
    parser = argparse.ArgumentParser("BGP injection")
    # parser.add_argument("-a", "--ascii", action="store_true", help="Output ASCII")
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("-a", "--asn", default="100", help="BGP AS")
    parser.add_argument("-l", "--local-ip", default="::", help="BGP Listen IP")
    parser.add_argument(
        "-r", "--router-id", default="10.0.0.1", help="BGP Router ID")
    parser.add_argument("peers", help="EBGP peer (ip,as)")
    args = parser.parse_args()

    try:
        peerip, peerport, peeras = args.peers.split(",")
    except ValueError:
        peerport = 179
        peerip, peeras = args.peers.split(",")
    peerport = int(peerport)
    peeras = int(peeras)

    # ryu(args.router_id, int(args.asn), peerip, peerport, peeras)
    # yabgp(args.router_id, int(args.asn), peerip, peerport, peeras)
    exabgp(
        ipaddress.ip_address(args.local_ip), args.router_id, int(args.asn),
        peerip, peerport, peeras)


if __name__ == "__main__":
    main()

__author__ = 'Christian E. Hopps'
__date__ = 'July 19 2018'
__version__ = '1.0'
__docformat__ = "restructuredtext en"
