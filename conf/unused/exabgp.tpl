process senddata {
    run ${INJECTSCRIPT};
    encoder text;
}

neighbor ${PEERIP} {            # Remote neighbor to peer with
    router-id ${ROUTERID};      # Our local router-id
    local-address ${LOCALIP};   # Our local update-source
    local-as ${LOCALAS};        # Our local AS
    peer-as ${PEERAS};          # Peer's AS
    api {
        processes [senddata];
    }
}
