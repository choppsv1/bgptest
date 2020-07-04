log file /var/log/frr/system.log
interface eth0
interface eth1
interface eth2
interface eth3
interface eth4
router bgp ${LOCALAS}
 no bgp default ipv4-unicast
 bgp router-id ${ROUTERID}
 neighbor ${PEER_TR_IP} description IBGP
 neighbor ${PEER_TR_IP} remote-as internal
 !
 neighbor ${PEER_FT_IP} description FT
 neighbor ${PEER_FT_IP} remote-as ${PEER_FT_AS}
 neighbor ${PEER_FT_IP} passive
 !
 neighbor ${PEER_ST1_IP} description ST1
 neighbor ${PEER_ST1_IP} remote-as ${PEER_ST1_AS}
 neighbor ${PEER_ST2_IP} description ST2
 neighbor ${PEER_ST2_IP} remote-as ${PEER_ST2_AS}
 neighbor ${PEER_ST3_IP} description ST3
 neighbor ${PEER_ST3_IP} remote-as ${PEER_ST3_AS}
 !
 address-family ipv6 unicast
  neighbor ${PEER_TR_IP} activate
  neighbor ${PEER_FT_IP} activate
  neighbor ${PEER_ST1_IP} activate
  neighbor ${PEER_ST2_IP} activate
  neighbor ${PEER_ST3_IP} activate
  neighbor ${PEER_TR_IP} next-hop-self
  neighbor ${PEER_FT_IP} next-hop-self
  neighbor ${PEER_ST1_IP} next-hop-self
  neighbor ${PEER_ST2_IP} next-hop-self
  neighbor ${PEER_ST3_IP} next-hop-self
  !
  neighbor ${PEER_TR_IP} distribute-list deny-all in
  neighbor ${PEER_TR_IP} distribute-list permit-all out
  !
  neighbor ${PEER_FT_IP} distribute-list permit-all in
  neighbor ${PEER_ST1_IP} distribute-list permit-all in
  neighbor ${PEER_ST2_IP} distribute-list permit-all in
  neighbor ${PEER_ST3_IP} distribute-list permit-all in
  !
  neighbor ${PEER_FT_IP} distribute-list deny-all out
  neighbor ${PEER_ST1_IP} distribute-list deny-all out
  neighbor ${PEER_ST2_IP} distribute-list deny-all out
  neighbor ${PEER_ST3_IP} distribute-list deny-all out
 exit-address-family
!
ipv6 access-list deny-all seq 5 deny any
ipv6 access-list permit-all seq 5 permit any
!
