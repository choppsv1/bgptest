BOX=bionic
VERSION := $(shell cat VERSION)

all: bionic.box

clean:
	rm -f bionic.box
	vagrant destroy -f

bionic.box: Vagrantfile
	rm -f bionic.box
	vagrant destroy -f
	vagrant box update
	vagrant --verbose up  | tee box-build.txt
	vagrant package --output bionic.box

release: bionic.box
	ruby ./release.rb
