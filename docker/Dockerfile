# -*- Dockerfile -*-
FROM ubuntu:20.04
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
        autoconf \
        automake \
        bash \
        bash-completion \
        bird \
        bison \
        build-essential \
        cpio \
        curl \
        docker-ce \
        flex \
        gettext \
        git \
        install-info \
        iproute2 \
        iputils-ping \
        jq \
        kmod \
        libarchive-tools \
        libc-ares-dev \
        libc-ares2 \
        libcap-dev \
        libedit-dev \
        libev-dev \
        libev4 \
        libffi-dev \
        libgmp-dev \
        libjson-c-dev \
        libpam0g-dev \
        libreadline-dev \
        libsnmp-dev \
        libssl-dev \
        libsystemd-dev \
        libtool \
        libxml2-utils \
        libxslt-dev \
        libyang-dev \
        locales \
        logrotate \
        lvm2 \
        make \
        net-tools \
        netcat-openbsd \
        nfs-kernel-server \
        ntp \
        openjdk-8-jdk \
        openjdk-8-jre \
        perl \
        pkg-config \
        python \
        python-dev \
        python-ipaddress \
        python3 \
        python3-dev \
        python3-pip \
        python3-pytest \
        python3-sphinx \
        python3-venv \
        rsync \
        snapd \
        snmp \
        ssh \
        sudo \
        tappy \
        texinfo \
        tidy \
        udev \
        vim \
        virtualbox-guest-dkms \
        virtualbox-guest-utils \
        xsltproc \
        zlib1g-dev \
        && \
        echo en_US.UTF-8 UTF-8 >> /etc/locale.gen && \
        locale-gen && \
    python3 -m pip install -U \
        coverage cryptography docker exabgp lxml netconf nose pylint pysnmp \
        pytest pyyaml ryu tox twine wheel && \
        apt-get autoremove -y && apt-get clean -y
ARG GOBGP
COPY $GOBGP /
RUN tar -C /usr/local/bin -xzf /$GOBGP
RUN mkdir /run/bird
RUN git clone https://github.com/FRRouting/frr.git
RUN groupadd -r frrvty && \
        useradd -M -r -G frrvty -s /sbin/nologin -c "FRR Routing Suite" -d /var/run/frr frr
WORKDIR frr
RUN ./bootstrap.sh
RUN ./configure --disable-doc \
        --prefix=/usr \
        --enable-exampledir=/usr/share/doc/frr/examples/ \
        --enable-vty-group=frrvty \
        --localstatedir=/var/run/frr \
        --sbindir=/usr/lib/frr \
        --sysconfdir=/etc/frr
RUN make && make install
RUN mkdir /etc/frr /var/log/frr && \
        install -p -m 644 tools/etc/frr/daemons /etc/frr && \
        touch /etc/frr/frr.conf /etc/frr/vtysh.conf && \
        chown -R frr:frr /etc/frr /var/log/frr && \
        chmod 640 /etc/frr/*
