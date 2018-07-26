# Change this into your BIRD router ID. It's a world-wide unique identification
# of your router, usually one of router's IPv4 addresses.
router id ${ROUTERID};

# debug protocols all;

filter loopbackfilter
prefix set allnets;
{
    allnets = [ fd00::/8 ];
    if (net ~ allnets) then accept;
    reject;
}

protocol device {}

protocol kernel {
    metric 64;
    import none;
    export filter loopbackfilter;
}

protocol bgp ibgp {
  description "ibgp";
  local as ${LOCALAS};
  neighbor ${PEER_TR_IP} as ${PEER_TR_AS};
  direct;
  next hop self;
  import none;
  export where proto = "loopback_bgp";
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

protocol static loopback_bgp {
  route fd${LOCALAS}::1/128 reject; # Loopback
}
