FROM debian:9.5

RUN apt-get update
RUN apt-get install -y debootstrap squashfs-tools xorriso grub-pc-bin grub-efi-amd64-bin mtools
RUN apt-get install -y cpio curl
RUN apt-get install -y dosfstools
RUN apt-get install -y isolinux 
RUN apt-get install -y lsb-release
RUN apt-get install -y xz-utils
RUN apt-get install -y live-build
#RUN apt-get install -y live-boot
#RUN apt-get install -y live-config


RUN mkdir /fab-live
RUN cd /fab-live && lb config  \
     --architectures amd64 \
     --linux-packages "linux-image" \
     --archive-areas "main contrib" \
     --bootappend-live "boot=live components username=live-user persistence persistence-label=persistence persistence-storage=filesystem hostname=fab-live timezone=Europe/Paris keyboard-layouts=fr user-default-groups=audio,cdrom,dip,floppy,video,plugdev,netdev,powerdev,scanner,bluetooth,fuse,docker" \
     "${@}"

COPY config/ /fab-live/config/
WORKDIR /fab-live

