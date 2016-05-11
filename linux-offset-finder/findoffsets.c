/* The LibVMI Library is an introspection library that simplifies access to 
 * memory in a target virtual machine or in a file containing a dump of 
 * a system's physical memory.  LibVMI is based on the XenAccess Library.
 *
 * Copyright 2011 Sandia Corporation. Under the terms of Contract
 * DE-AC04-94AL85000 with Sandia Corporation, the U.S. Government
 * retains certain rights in this software.
 *
 * Author: Bryan D. Payne (bdpayne@acm.org)
 * Modified by: Cheng Liu
 *
 * This file is part of LibVMI. And it has been modified to help adding 
 * offsets of an image into Glance (an OpenStack project) database.
 *
 * LibVMI is free software: you can redistribute it and/or modify it under
 * the terms of the GNU Lesser General Public License as published by the
 * Free Software Foundation, either version 3 of the License, or (at your
 * option) any later version.
 *
 * LibVMI is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
 * License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with LibVMI.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/sched.h>
#include <linux/mm_types.h>

#define MYMODNAME "FindOffsets "

static int my_init_module(
    void);
static void my_cleanup_module(
    void);

static int
my_init_module(
    void)
{
    struct task_struct *p = NULL;
    struct mm_rss_stat m;

    unsigned long rt_priority_offset;
    unsigned long state_offset;
    unsigned long tasks_offset;
    unsigned long name_offset;
    unsigned long pid_offset;
    unsigned long mm_offset;
    unsigned long total_vm_offset;
    unsigned long rss_stat_offset;
    unsigned long element_offset;
    unsigned long utime_offset;
    unsigned long stime_offset;

    printk(KERN_ALERT "Module %s loaded.\n\n", MYMODNAME);
    p = current;

    if (p != NULL) {
        rt_priority_offset = (unsigned long) (&(p->rt_priority)) - (unsigned long) (p);
        state_offset = (unsigned long) (&(p->state)) - (unsigned long) (p);
        tasks_offset = (unsigned long) (&(p->tasks)) - (unsigned long) (p);
        name_offset = (unsigned long) (&(p->comm)) - (unsigned long) (p);
        pid_offset = (unsigned long) (&(p->pid)) - (unsigned long) (p);
        mm_offset = (unsigned long) (&(p->mm)) - (unsigned long) (p);
        total_vm_offset = (unsigned long) (&(p->mm->total_vm)) - (unsigned long) (p->mm);
        rss_stat_offset = (unsigned long) (&(p->rss_stat)) - (unsigned long) (p);
        element_offset = (unsigned long) (sizeof(m)) / NR_MM_COUNTERS;
        utime_offset = (unsigned long) (&(p->utime)) - (unsigned long) (p);
        stime_offset = (unsigned long) (&(p->stime)) - (unsigned long) (p);
        
        printk(KERN_ALERT "----------------------------------------------------------\n");
        printk(KERN_ALERT "* This is an automatically generated script.\n");
        printk(KERN_ALERT "* Copy the following lines to import-offsets.sh \n");
        printk(KERN_ALERT "* Modify <image-id> to openstack image-id of current instance\n");
        printk(KERN_ALERT "* And then run: bash import-offsets.sh\n\n");
        printk(KERN_ALERT "export IMAGE_ID=<image-id>");
        printk(KERN_ALERT "glance image-update --property rt_priority_offset=0x%x ${IMAGE_ID}\n", (unsigned int) rt_priority_offset);
        printk(KERN_ALERT "glance image-update --property state_offset=0x%x ${IMAGE_ID}\n", (unsigned int) state_offset);
        printk(KERN_ALERT "glance image-update --property tasks_offset=0x%x ${IMAGE_ID}\n", (unsigned int) tasks_offset);
        printk(KERN_ALERT "glance image-update --property name_offset=0x%x ${IMAGE_ID}\n", (unsigned int) name_offset);
        printk(KERN_ALERT "glance image-update --property pid_offset=0x%x ${IMAGE_ID}\n", (unsigned int) pid_offset);
        printk(KERN_ALERT "glance image-update --property mm_offset=0x%x ${IMAGE_ID}\n", (unsigned int) mm_offset);
        printk(KERN_ALERT "glance image-update --property total_vm_offset=0x%x ${IMAGE_ID}\n", (unsigned int) total_vm_offset);
        printk(KERN_ALERT "glance image-update --property rss_stat_offset=0x%x ${IMAGE_ID}\n", (unsigned int) rss_stat_offset);
        printk(KERN_ALERT "glance image-update --property element_offset=0x%x ${IMAGE_ID}\n", (unsigned int) element_offset);
        printk(KERN_ALERT "glance image-update --property utime_offset=0x%x ${IMAGE_ID}\n", (unsigned int) utime_offset);
        printk(KERN_ALERT "glance image-update --property stime_offset=0x%x ${IMAGE_ID}\n", (unsigned int) stime_offset);
        printk(KERN_ALERT "unset IMAGE_ID");
        printk(KERN_ALERT "----------------------------------------------------------\n");
    }
    else {
        printk(KERN_ALERT
               "%s: found no process to populate task_struct.\n",
               MYMODNAME);
    }

    return 0;
}

static void
my_cleanup_module(
    void)
{
    printk(KERN_ALERT "Module %s unloaded.\n", MYMODNAME);
}

module_init(my_init_module);
module_exit(my_cleanup_module);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Composed by Nilushan Silva, modified by Cheng Liu");
MODULE_DESCRIPTION("task_struct offset finder");
