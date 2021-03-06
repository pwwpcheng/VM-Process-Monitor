# Linux Offset Finder

This file is part of LibVMI and has been modified to help adding 
offsets of an image into Glance (an OpenStack project) database.

THIS FILE SHOULD BE COPIED INTO YOUR VIRTUAL MACHINE AND RUN WITHIN IT.

## Before using:

After installing libvmi, you may see a folder
called **tools** inside libvmi setup folder. Inside the **tools** 
folder, there are several tools that may help manipulating your 
virtual instances. Then jump to **linux-offset-finder** folder. 
Inside it, there is a file called "findoffsets.c". Replace this file
with the file we provided.

After replacement, copy **linux-offset-finder** folder into your 
domU(virtual machine).

## Usage

1. Log into your vm as root

2. cd into the **linux-offset-finder** folder. Run:

   `make`
   
3. After make, you may see a file called "findoffsets.ko".
   Insert this kernel module file into your machine with:

   `insmod findoffsets.ko`
   
4. Offsets for this instance has been generated. Print out kernel 
   debug message:

   `dmesg -t`
   
   You should see something like this:
```
   ----------------------------------------------------------
   * This is an automatically generated script.
   * Copy the following lines to import-offsets.sh 
   * Modify <image-id> to openstack image-id of current instance
   * And then run: bash import-offsets.sh
   
   export IMAGE_ID=<image-id>
   glance image-update --property rt_priority_offset=0x5c ${IMAGE_ID}
   glance image-update --property state_offset=0x0 ${IMAGE_ID}
   glance image-update --property tasks_offset=0x270 ${IMAGE_ID}
   glance image-update --property name_offset=0x4c0 ${IMAGE_ID}
   glance image-update --property pid_offset=0x2f0 ${IMAGE_ID}
   glance image-update --property mm_offset=0x2a8 ${IMAGE_ID}
   glance image-update --property total_vm_offset=0xa0 ${IMAGE_ID}
   glance image-update --property rss_stat_offset=0x2b8 ${IMAGE_ID}
   glance image-update --property element_offset=0x8 ${IMAGE_ID}
   glance image-update --property utime_offset=0x3d8 ${IMAGE_ID}
   glance image-update --property stime_offset=0x3e0 ${IMAGE_ID}
   unset IMAGE_ID
   ----------------------------------------------------------
```

5. Copy the part within dash lines into a file IN YOUR HYPERVISOR.
   ** BE SURE THAT YOU SHOULD BE ABLE TO CONTROL OPENSTACK PLATFORM
   ON THIS MACHINE! **

   Modify <image-id> to openstack image-id of current instance,
   and then run:

   `bash <script-name>`
    
