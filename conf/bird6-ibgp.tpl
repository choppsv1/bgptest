router id ${ROUTERID};

# debug protocols all;

protocol device {}

protocol direct {
    interface "*";
    import all;
    export all;
}

filter loopbackfilter
{
    if (net ~ fd00::/8) then accept;
    else reject;
}

protocol kernel {
    metric 64;
    # import none;
    export filter loopbackfilter;
    import filter loopbackfilter;
}

protocol static loopback_bgp {
  import all; # originate here (?).
  route fd${LOCALAS}::1/128 via "lo";
}

protocol bgp bgp_${PEERAS} {
    description "IBGP ${PEERIP} ${PEERAS}";
    local as ${LOCALAS};
    neighbor ${PEERIP} as ${PEERAS};
    direct;
    gateway direct;
    import all;
    export filter loopbackfilter;
  # export where proto = "loopback_bgp";
}

# WARNCPU