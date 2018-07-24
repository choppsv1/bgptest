FROM gitlab.dev.terastrm.net:4567/terastream/ci-dockerfiles/ts-ubuntu-ci-18:latest
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
            libgmp-dev zlib1g-dev libedit-dev
# Golang
# RUN snap install go --classic
# FRR routing
RUN PKG=frr_5.0.1-1.ubuntu18.04.1_amd64.deb; curl -fLO https://github.com/FRRouting/frr/releases/download/frr-5.0.1/$PKG ; dpkg -i $PKG ; rm $PKG
RUN PKG=frr-pythontools_5.0.1-1.ubuntu18.04.1_all.deb; curl -fLO https://github.com/FRRouting/frr/releases/download/frr-5.0.1/$PKG ; dpkg -i $PKG ; rm $PKG
RUN PKG=frr-doc_5.0.1-1.ubuntu18.04.1_all.deb; curl -fLO https://github.com/FRRouting/frr/releases/download/frr-5.0.1/$PKG ; dpkg -i $PKG ; rm $PKG
RUN python3.6 -m pip install -U \
    coverage cryptography docker lxml netconf nose pylint pysnmp \
    pytest pyyaml tox twine wheel
# Required by frr
RUN apt-get autoremove -y && apt-get clean -y
COPY go1.10.3.linux-amd64.tar.gz /
RUN tar -C /usr/local -xzf /go1.10.3.linux-amd64.tar.gz
ENV GOPATH=/go \
    GOROOT=/usr/local/go \
    PATH=/go/bin:/usr/local/go/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
# RUN ln -s /usr/local/go/bin/go /usr/local/bin  && \
#     ln -s /usr/local/go/bin/godoc /usr/local/bin && \
#     ln -s /usr/local/go/bin/gofmt /usr/local/bin
RUN go get -u github.com/golang/dep/cmd/dep
RUN go get github.com/osrg/gobgp || true
RUN (cd /go/src/github.com/osrg/gobgp && /go/bin/dep ensure)
RUN (cd /go/src/github.com/osrg/gobgp/cmd/gobgp && go install) && \
    (cd /go/src/github.com/osrg/gobgp/cmd/gobgpd && go install)
COPY mrtbin/* /usr/bin/
RUN python3 -m pip install exabgp ryu
