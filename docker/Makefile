all: build

go1.10.3.linux-amd64.tar.gz:
	curl -fLO https://dl.google.com/go/go1.10.3.linux-amd64.tar.gz

build: go1.10.3.linux-amd64.tar.gz
	docker build --pull -t bgptest .
