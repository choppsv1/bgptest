router id ${ROUTERID};

protocol device {}
protocol kernel { metric 64; import none; export none; }
# debug protocols all;

protocol static static_bgp {
  route fc${LOCALAS}::/64 reject;
}

protocol bgp ebgp_${LOCALAS} {
  description "EBGP ${PEER_UT_AS}";
  neighbor ${PEER_UT_IP} as ${PEER_UT_AS};
  local as ${LOCALAS};
  direct;
  next hop self;
  import all;
  export where proto = "static_bgp";
}