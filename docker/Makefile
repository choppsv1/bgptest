all: build

go1.14.4.linux-amd64.tar.gz:
	curl -fLO https://dl.google.com/go/go1.14.4.linux-amd64.tar.gz

go1.10.3.linux-amd64.tar.gz:
	curl -fLO https://dl.google.com/go/go1.10.3.linux-amd64.tar.gz

GOBGP := gobgp_2.17.0_linux_amd64.tar.gz
$(GOBGP):
	curl -fLO https://github.com/osrg/gobgp/releases/download/v2.17.0/$@

build: $(GOBGP)
	docker build --build-arg=GOBGP=$(GOBGP) --pull -t choppsv1/bgptest .
