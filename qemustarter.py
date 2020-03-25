#!/usr/bin/env python3

# author: Matteo Caliandro
# e-mail: mcaliandro92@gmail.com
# github: mcaliandro
# 
# project: qemustarter
# version: 0.2.1
# date: 18-03-2020

from argparse import ArgumentParser
from jsonschema import validate, ValidationError
from pathlib import Path
from subprocess import Popen, DEVNULL
from sys import exit
from yaml import load, Loader, YAMLError


# Thanks to Nadia Alramli for the hint on converting a Python dictionary to an object
# source: https://stackoverflow.com/questions/1305532/convert-nested-python-dict-to-object/1305682#1305682
class Object():
    def __init__(self, source):
        for key, value in source.items():
            if isinstance(value, (list, tuple)):
                setattr(self, key, [Object(item) if isinstance(item, dict) else item for item in value])
            else:
                setattr(self, key, Object(value) if isinstance(value, dict) else value)


class Error():
    @staticmethod
    def print_error(msg):
        print(msg)
        exit()
    @staticmethod
    def config_failed():
        Error.print_error("Error: virtual machine cannot be configured.")
    @staticmethod
    def invalid_action(value):
        Error.print_error("Error: invalid action {}".format(value))
    @staticmethod
    def no_disk(value):
        Error.print_error("Error: Disk image not found {}".format(value))
    @staticmethod
    def no_iso(value):
        Error.print_error("Error: ISO file not found {}".format(value))


class QemuBase():
    def __init__(self, base):
        self.__command = base
    def __call__(self):
        proc = Popen(self.__command, stdout=DEVNULL)
        proc.wait()
    def add_option(self, opt, value=None):
        if not value:
            self.__command.append(opt)
        else:
            self.__command.extend([opt, value])
    def props():
        pass


class QemuImage(QemuBase):
    def __init__(self):
        super().__init__(["qemu-img", "create"])
    def props(self, disk):
        self.add_option("-f", disk.type)
        self.add_option(opt=disk.image) 
        self.add_option(opt="{}m".format(disk.size))


class QemuMachine(QemuBase):
    def __init__(self):
        super().__init__(["qemu-system-x86_64", "-enable-kvm"])
    def props(self, name=None, cores=None, ram=None, cdrom=None, disk=None, network=False, noreboot=False):
        if name:
            self.add_option("-name", name)
        if cores:
            self.add_option("-smp", str(cores))
        if ram:
            self.add_option("-m", "{}m".format(ram))
        if cdrom:
            self.add_option("-cdrom", cdrom)
        if disk:
            self.add_option("-{}".format(disk.device), disk.image)
        if network:
            self.add_option("-net", "nic")
            self.add_option("-net", "user")
        if noreboot:
            self.add_option(opt="-no-reboot")


def create_vm(disk):
    create_img = QemuImage()
    create_img.props(disk=disk)
    create_img()


def main(vmconfig):
    if vmconfig.action not in ["boot", "install", "live"]:
        Error.invalid_action(vmconfig.action)
    launch_vm = QemuMachine()
    launch_vm.props(name=vmconfig.name, cores=vmconfig.cores, ram=vmconfig.ram, network=True)
    if vmconfig.action == "boot":
        if not Path(vmconfig.disk.image).exists():
            Error.no_disk(vmconfig.disk.image)
        launch_vm.props(disk=vmconfig.disk)
        launch_vm()
    else:
        if not Path(vmconfig.iso).exists():
            Error.no_iso(vmconfig.iso)
        if vmconfig.action == "install":
            if not Path(vmconfig.disk.image).exists():
                create_vm(vmconfig.disk)
            launch_vm.props(cdrom=vmconfig.iso, disk=vmconfig.disk, noreboot=True)
            launch_vm()
        if vmconfig.action == "live":
            launch_vm.props(cdrom=vmconfig.iso, noreboot=True)
            launch_vm()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--config", "-c", default="config.yml", type=str)
    parser.add_argument("--schema", "-s", default="schema.yml", type=str)
    args = parser.parse_args()
    config = None
    try:
        with open(args.config, "r") as config_yaml:
            config = load(config_yaml, Loader=Loader)
            config_yaml.close()
        with open(args.schema, "r") as schema_yaml:
            schema = load(schema_yaml, Loader=Loader)
            schema_yaml.close()
        validate(instance=config, schema=schema)
    except IOError as io_err:
        raise io_err
    except YAMLError as yaml_err: 
        raise yaml_err
    except ValidationError as val_err: 
        raise val_err
    if not config:
        Error.config_failed()
    main(Object(config))
