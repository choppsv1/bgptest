router id ${ROUTERID};

protocol device {}
protocol kernel { metric 64; import none; export none; }
# debug protocols all;

protocol static loopback_bgp {
  route fd${LOCALAS}::2/128 reject; # Loopback
}

protocol static static_bgp {
  route fc${LOCALAS}::/64 reject;
}

protocol bgp ebgp_${LOCALAS} {
  description "EBGP ${PEERAS}";
  neighbor ${PEERIP} as ${PEERAS};
  local as ${LOCALAS};
  direct;
  next hop self;
  import all;
  export where proto = "loopback_bgp";
  export where proto = "static_bgp";
}