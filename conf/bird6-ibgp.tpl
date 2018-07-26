router id ${ROUTERID};

protocol device {}
protocol kernel { metric 64; import none; export none; }
# debug protocols all;

protocol bgp bgp_${PEER_UT_AS} {
  description "IBGP ${PEER_UT_IP} ${PEER_UT_AS}";
  local as ${LOCALAS};
  neighbor ${PEER_UT_IP} as ${PEER_UT_AS};
  direct;
  gateway direct;
  import all;
  # export all;
}