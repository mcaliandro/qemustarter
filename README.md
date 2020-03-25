## Introduction
Written in Python3, it is a script that works on Linux distributions with QEMU/KVM. The scope is to run ISO in live-mode inside a virtualized environment and install/boot virtual machines without using any graphical interface or more sophisticated tools such as VirtManager and VirtualBox. It acts as a wrapper for QEMU/KVM commands, where the properties of a virtual machine and the operations to perform on it are specified within a simple configuration file written in YaML. 

## Dependencies
- PyYAML ([link](https://pypi.org/project/PyYAML/))

``` pip install PyYAML ```

## Configuration file
It contains the parameters useful to install and boot a virtual machine with QEMU/KVM. Qemustarter needs *config.yml* as default configuration file, however, you can specify a different name (see [next section](#execute-qemustarter) for more info). Each virtual machine requires its own YaML file that should be manually composed. The configuration is based on the following parameters:
- **action**: three available options, *live*, *install* and *boot* 
- **name**: name to associate to the vitual machine
- **cores**: number of simulated cores to reserve to the host
- **ram**: amount of RAM memory to reserve to the host (in MB)
- **iso**: ISO file of the OS to virtualize
- **disk**: collects information about the host machine's virtual disk
  - **device**: kernel name of the virtual disk (*hdX*)
  - **image**: name of the virtual disk file, e.g., *root.img*
  - **size**: virtual disk dimension (in MB)
  - **type**: virtual disk format supported by QEMU/KVM, e.g., *qcow*, *qcow2*, *raw*

Notice that *qemustarter* performs the validation of the configuration file through a schema file, called *schema.yml*. 

This example defines the parameter of a Debian Testing amd64 virtual machine:
``` YAML
action: live
name: debian
cores: 1
ram: 1024
iso: debian-testing-amd64.iso
disk:
  device: hda
  image: debian-rootfs
  size: 4096
  type: qcow2
```

## Execute qemustarter
Qemustarter can be launched in a terminal with the following command:
``` bash
qemustarter.py --config config.yml --schema schema.yml
```
or with a bash script (recommended):
``` bash
#!/bin/bash
DIR="$(dirname "$PWD")"
/usr/bin/python3 $DIR/qemustarter.py \
    --config $PWD/config.yml \
    --schema $DIR/schema.yml
```
By using this bash script, you can run organize your virtual machines in separated directories, without replicating *qemustarter.py* and *schema.yml*, as shown in the example below (here, the bash script is called *start_debian.sh*):
```
qemustarter/
├─ qemustarter.py
├─ schema.yml
└─ debian/
    ├─ debian-testing-amd64.iso
    ├─ debian-rootfs.img
    ├─ config.yml
    └─ start_debian.sh
└─ ...
```
