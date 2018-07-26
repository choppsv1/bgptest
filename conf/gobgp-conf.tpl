global:
  config:
    as: ${LOCALAS}
    router-id: ${ROUTERID}
  apply-policy:
    config:
      default-import-policy: = "accept-route"
      default-export-policy: = "accept-route"
      # default-import-policy: "reject-route"
neighbors:
  - config:
      neighbor-address: ${PEERIP}
      peer-as: ${PEERAS}
    afi-safis:
      - config:
          afi-safi-name: ipv6-unicast
      - config:
          afi-safi-name: ipv4-unicast
