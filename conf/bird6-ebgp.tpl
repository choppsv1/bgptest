router id ${ROUTERID};

# debug protocols all;

protocol device {}
protocol kernel { metric 64; import none; export none; }

filter expbgp
{
    # bgp_path.prepend(300);
    if proto = "static_bgp" then accept;
    reject;
}

protocol bgp bgp_${PEERAS} {
  description "EBGP ${PEERAS}";
  import none;
  export filter expbgp;

  neighbor ${PEERIP} as ${PEERAS};
  local as ${LOCALAS};

  # direct;
  # gateway direct;
  # next hop self;
}

protocol static static_bgp {
  import all; # originate here (?).
  route fc${LOCALAS}:ffff::/64 reject; # via "lo";
  route fc${LOCALAS}:fffd::/64 reject; # via "lo";
  route fc${LOCALAS}:fffc::/64 reject; # via "lo";
  route fc${LOCALAS}:fffb::/64 reject; # via "lo";
  route fc${LOCALAS}:fffa::/64 reject; # via "lo";
}
