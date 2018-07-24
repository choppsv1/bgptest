BOX=bgp-bionic
VERSION := $(shell cat VERSION)

all: bgp-bionic.box

clean:
	rm -f bgp-bionic.box
	vagrant destroy -f

bgp-bionic.box: Vagrantfile
	rm -f bgp-bionic.box
	vagrant destroy -f
	vagrant box update
	vagrant --verbose up  | tee box-build.txt
	vagrant package --output bgp-bionic.box

release: bgp-bionic.box
	ruby ./release.rb
