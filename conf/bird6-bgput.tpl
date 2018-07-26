# Change this into your BIRD router ID. It's a world-wide unique identification
# of your router, usually one of router's IPv4 addresses.
router id ${ROUTERID};

protocol device {}
protocol kernel { metric 64; import none; export none; }
# debug protocols all;

protocol bgp ibgp {
  description "ibgp";
  local as ${LOCALAS};
  neighbor ${PEER_TR_IP} as ${LOCALAS};
  direct;
  next hop self;
  import none;
  export all;
}

protocol bgp ft {
  description "FT";
  passive on;
  neighbor ${PEER_FT_IP} as ${PEER_FT_AS};
  local as ${LOCALAS};
  direct;
  next hop self;
  import all;
  export none;
}

protocol bgp st_1 {
  description "ST 1";
  neighbor ${PEER_ST1_IP} as ${PEER_ST1_AS};
  local as ${LOCALAS};
  direct;
  next hop self;
  import all;
  export none;
}

protocol bgp st_2 {
  description "ST 2";
  neighbor ${PEER_ST2_IP} as ${PEER_ST2_AS};
  local as ${LOCALAS};
  direct;
  next hop self;
  import all;
  export none;
}

protocol bgp st_3 {
  description "ST 3";
  neighbor ${PEER_ST3_IP} as ${PEER_ST3_AS};
  local as ${LOCALAS};
  direct;
  next hop self;
  import all;
  export none;
}