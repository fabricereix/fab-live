#!/bin/bash
set -e
set -x

VM=Fabiso
ISO_FILE=build/LIVE_BOOT/debian-custom.iso

VBoxManage list vms
VBoxManage unregistervm --delete $VM || true
VBoxManage createvm --name $VM --ostype "Debian" --register
VBoxManage storagectl $VM --name IDE --add ide
VBoxManage storageattach $VM --storagectl IDE --port 0 --device 0 --type dvddrive --medium $ISO_FILE
VBoxManage modifyvm "$VM" --nic1 hostonly
VBoxManage startvm $VM --type headless

