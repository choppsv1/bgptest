FROM gitlab.dev.terastrm.net:4567/terastream/ci-dockerfiles/ts-ubuntu-ci-18:latest

ENV GOPATH=/go \
    GOROOT=/usr/local/go \
    PATH=/go/bin:/usr/local/go/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

RUN apt-get update -qy && apt-get upgrade -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        bash bash-completion bird bsdtar cpio curl \
        docker-ce git iputils-ping gettext jq kmod logrotate \
        libc-ares2 libev4 libxml2-utils locales lvm2 make net-tools \
        netcat-openbsd nfs-kernel-server ntp \
        openjdk-8-jre openjdk-8-jdk \
        python python-dev python-ipaddr python-pip \
        python3 python3-dev python3-pip python3-venv\
        rsync sudo ssh snmp tappy tidy udev vim xsltproc \
        virtualbox-guest-dkms virtualbox-guest-utils \
        autoconf build-essential libev-dev libxslt-dev \
        libffi-dev libssl-dev zlib1g-dev \
        libgmp-dev zlib1g-dev libedit-dev && \
    python3.6 -m pip install -U \
        coverage cryptography docker exabgp lxml netconf nose pylint pysnmp \
        pytest pyyaml ryu tox twine wheel && \
        apt-get autoremove -y && apt-get clean -y

ADD go1.10.3.linux-amd64.tar.gz /usr/local/

RUN go get -u github.com/golang/dep/cmd/dep && \
    (go get github.com/osrg/gobgp || true) && \
    (cd /go/src/github.com/osrg/gobgp && /go/bin/dep ensure) && \
    (cd /go/src/github.com/osrg/gobgp/cmd/gobgp && go install) && \
    (cd /go/src/github.com/osrg/gobgp/cmd/gobgpd && go install)

RUN mkdir /run/bird
