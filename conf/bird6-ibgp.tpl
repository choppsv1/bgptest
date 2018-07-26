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

protocol bgp bgp_${PEERAS} {
    description "IBGP ${PEERIP} ${PEERAS}";
    local as ${LOCALAS};
    neighbor ${PEERIP} as ${PEERAS};
    direct;
    gateway direct;
    import all;
    export where proto = "loopback_bgp";
}