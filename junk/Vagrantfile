# coding: utf-8
# -*- mode: ruby -*-
# vi: set ft=ruby :

UNIQID = 1

os = `uname -s`.strip
if os == "Darwin"
  nic_type = "Am79C973"
else
  nic_type = "virtio"
end

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
names = ["r10", "r20", "r30"]
Vagrant.configure("2") do |config|
  names.each do |name|
    config.vm.define name do |r|
      puts name
      urelease = "bionic"
      r.vm.box = "chopps/#{urelease}"
      r.vm.box_version = "1.1.17"

      # Add a private network between routers
      r.vm.network("private_network", ip: "192.168.10." + name[1..-1])
      r.vm.network("private_network", ip: "192.168.11." + name[1..-1])

      # Share an additional folder to the guest VM. The first argument is
      vmhomedir = "/home/#{ENV['USER']}"
      homedir = File.expand_path("~")
      r.vm.synced_folder homedir, vmhomedir, SharedFoldersEnableSymlinksCreate: true
      r.vm.synced_folder ".", "/bgptest", SharedFoldersEnableSymlinksCreate: true
      r.vm.synced_folder "..", "/work", SharedFoldersEnableSymlinksCreate: true

    # Provider-specific configuration so you can fine-tune various
      # backing providers for Vagrant. These expose provider-specific options.
      r.vm.provider "virtualbox" do |vb|
        vb.customize ["modifyvm", :id, "--memory", "1024"]
        vb.customize ["modifyvm", :id, "--cpus", "2"]
        vb.customize ["modifyvm", :id, "--nictype1", nic_type]
        vb.customize ["modifyvm", :id, "--nictype2", nic_type]
        vb.customize ["modifyvm", :id, "--audio", "none"]
        vb.customize ["modifyvm", :id, "--usb", "off", "--usbehci", "off"]
        vb.customize ["modifyvm", :id, "--ioapic", "on"]
        vb.customize ["modifyvm", :id, "--hwvirtex", "on"]
      end

      # ------------
      # Provisioning
      # ------------
      r.vm.provision "system-install",
                     type: "shell",
                     privileged: true,
                     preserve_order: true,
                     inline: <<-SHELL
        # For some reason networking doesn't work right away on the mac.
        echo 'APT::Periodic::Enable \"0\";' > /etc/apt/apt.conf.d/02periodic
        rm -f /var/lib/apt/lists/lock
        rm -f /var/lib/dpkg/lock
        apt-get install -y quagga quagga-doc
        snap install --classic go
        sed -i -E -e 's/^pool.*/# &/;s/#\s*(broadcastclient)/\1/;s/#\s*(disable\s*auth)/\1/' /etc/ntp.conf
        usermod -a -G docker vagrant
        SHELL

    #
    # Provisioning run as vagrant user.
      r.vm.provision "project-setup",
                     type: "shell",
                     privileged: false,
                     preserve_order: true,
                     inline: <<-SHELL
        echo "ran as vagrant/user"
        SHELL
    end
  end
end
