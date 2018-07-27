# -*- Dockerfile -*-
FROM ubuntu:18.04
MAINTAINER Christian Hopps <chopps@gmail.com>

ENV GOPATH=/go \
    GOROOT=/usr/local/go \
    LANG=en_US.UTF-8 \
    LC_CTYPE=en_US.UTF-8 \
    PATH=/go/bin:/usr/local/go/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

RUN sed -i -e '/# deb http.* universe/s,^# ,,' /etc/apt/sources.list && \
    sed -i -e '/# deb http.* multiverse/s,^# ,,' /etc/apt/sources.list && \
    apt-get update -qy && apt-get upgrade -y && \
    # -------------------
    # Custom repositories
    # -------------------
    apt-get install -y apt-transport-https dirmngr software-properties-common && \
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 8D81803C0EBFCD88 && \
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 7EA0A9C3F273FCD8 && \
    # Replace artful with bionic when that works
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu artful stable" && \
    apt-get update -qy && \
    apt-get upgrade -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        bash bash-completion bird bsdtar cpio curl \
        docker-ce git iproute2 iputils-ping gettext jq kmod logrotate \
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
        echo en_US.UTF-8 UTF-8 >> /etc/locale.gen && \
        locale-gen && \
    python3.6 -m pip install -U \
        coverage cryptography docker exabgp lxml netconf nose pylint pysnmp \
        pytest pyyaml ryu tox twine wheel && \
        apt-get autoremove -y && apt-get clean -y && \
    (curl -fL https://dl.google.com/go/go1.10.3.linux-amd64.tar.gz | \
     tar -C /usr/local -xzf -) && \
    go get -u github.com/golang/dep/cmd/dep && \
    (go get github.com/osrg/gobgp || true) && \
    (cd /go/src/github.com/osrg/gobgp && /go/bin/dep ensure) && \
    (cd /go/src/github.com/osrg/gobgp/cmd/gobgp && go install) && \
    (cd /go/src/github.com/osrg/gobgp/cmd/gobgpd && go install) && \
    mkdir /run/bird
