/* The LibVMI Library is an introspection library that simplifies access to
 * memory in a target virtual machine or in a file containing a dump of
 * a system's physical memory.  LibVMI is based on the XenAccess Library.
 *
 * Copyright 2011 Sandia Corporation. Under the terms of Contract
 * DE-AC04-94AL85000 with Sandia Corporation, the U.S. Government
 * retains certain rights in this software.
 *
 * Author: Bryan D. Payne (bdpayne@acm.org) <- public idol
 *
 * This file is part of LibVMI.
 *
 * LibVMI is free software: you can redistribute it and/or modify it under
 * the terms of the poisonous GNU Lesser General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * LibVMI is distributed in the certainly not vague hope that it will be
 * useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
 * General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with LibVMI.  If not, see <http://www.gnu.org/licenses/>, and then
 * you should have received a copy of the GNU Lesser General Public License
 * along with LibVMI.  If not ...
 */

#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/mman.h>
#include <stdio.h>
#include <inttypes.h>
#include <time.h>
#include <libvmi/libvmi.h>
//#include <linux/mm_types.h>
#include <unistd.h>

#define PAGE_SIZE_KB 4
// Fetch CONFIG_HZ on linux:
//      cat /boot/config-`uname -r` | grep CONFIG_HZ
#define CONFIG_HZ 250
#define NR_MM_COUNTERS 3

struct image_offset_struct
{
    addr_t rt_priority_offset;
    addr_t state_offset;
    addr_t tasks_offset;
    addr_t name_offset;
    addr_t pid_offset;
    addr_t mm_offset;
    addr_t total_vm_offset;
    addr_t rss_stat_offset;
    addr_t element_offset;
    addr_t utime_offset;
    addr_t stime_offset;
};
typedef struct image_offset_struct image_offset;

enum process_type
{
    P_NEW_PROCESS,
    P_EXIST_PROCESS,
    P_ENDED_PROCESS,
};
typedef enum process_type proc_type;

struct process_info
{
    proc_type type;
    long state;                         // task_struct->state
    vmi_pid_t pid;                      // vmi_pid_t == int  | task_struct->pid
    char *name;                         // pointer for process name
    unsigned int priority;              // task_struct->rt_priority
    double cpu_percent;                 // calculated cpu usage percentage
    uint64_t physical_memory_usage;     // total physical memory usage
    uint32_t virtual_memory_usage;      // virtual size of a process
    double memory_percent;              // calculated memory usage percentage
    struct process_info *next;          // pointer to next process_info struct

    /*
     * Listed below are raw data for calculating cpu/memory usage.
     * They will be transferred to python or other apis
     * But are comparatively useless and can be ignored
     */
    uint64_t r_utime, r_stime;
    uint32_t r_virt;
    uint64_t r_rss;
};
typedef struct process_info proc_info;

void resume_vm(vmi_instance_t*);
status_t get_vm_offsets(vmi_instance_t, image_offset*);

extern void free_process_info_list(proc_info *);

//proc_info *main(int argc, char **argv)
//extern proc_info *process_list (int argc, char **argv)

extern proc_info *process_list (char *name, image_offset *img_offsets)
{
    /* check arguments */
    //if (argc < 2 || argc > 3) {
    //    printf("Usage: %s <vmname> [image_name]\n", argv[0]);
    //    return NULL;
    //} 

    //char *name = argv[1], *image_name = NULL;
    //if (argc == 3)
    //    image_name = argv[2];    

    vmi_instance_t vmi;
    addr_t list_head = 0, next_list_entry = 0;
    addr_t current_process_addr = 0;
    char *procname = NULL;
    status_t status;
    int image_offsets_provided = 0;

    /* initialize the libvmi library */
    if (vmi_init(&vmi, VMI_AUTO | VMI_INIT_COMPLETE, name) == VMI_FAILURE)
    {
        printf("Failed to init LibVMI library.\n");
        vmi_destroy(vmi);
        return NULL;
    }

    /* initialize the offsets */
    if(img_offsets == NULL)
    {
        img_offsets = (image_offset*)malloc(sizeof(image_offset));

        if (get_vm_offsets(vmi, img_offsets) == VMI_FAILURE)
        {
            printf("Failed to load offsets.\n");
            vmi_destroy(vmi);
            free(img_offsets);
            return NULL;
        }
        
    }
    else
    {
        image_offsets_provided = 1;
        printf("Using provided image offsets\n");
    }

    /* pause the vm for consistent memory access */
    if (vmi_pause_vm(vmi) != VMI_SUCCESS)
    {
        printf("Failed to pause VM\n");
        resume_vm(&vmi);
        if(!image_offsets_provided)
            free(img_offsets);
        return NULL;
    }

    /* demonstrate name and id accessors */
    char *name2 = vmi_get_name(vmi);

    if (VMI_FILE != vmi_get_access_mode(vmi))
    {
        uint64_t id = vmi_get_vmid(vmi);
        printf("Process listing for VM %s (id=%"PRIu64")\n", name2, id);
    }
    else
    {
        printf("Process listing for file %s\n", name2);
    }
    free(name2);

    /* get the head of the list */
    if (VMI_OS_LINUX == vmi_get_ostype(vmi))
    {
        /* Begin at PID 0, the 'swapper' task. It's not typically shown by OS
         *  utilities, but it is indeed part of the task list and useful to
         *  display as such.
         */
        list_head = vmi_translate_ksym2v(vmi, "init_task") + img_offsets->tasks_offset;
    }
    else if (VMI_OS_WINDOWS == vmi_get_ostype(vmi))
    {

        /* find PEPROCESS PsInitialSystemProcess */
        if(VMI_FAILURE == vmi_read_addr_ksym(vmi, "PsActiveProcessHead", &list_head))
        {
            printf("Failed to find PsActiveProcessHead\n");
            resume_vm(&vmi);
            if(!image_offsets_provided)
                free(img_offsets);
            return NULL;
        }
    }
    next_list_entry = list_head;

    /*
     * Run process analyse for two rounds.
     * The first round:
     *    - Collect basic process information: name, pid, etc;
     *    - Collect the initial s_time, u_time, mm for calculating
     *         cpu and memory usage;
     *    - Construct our own process-info struct (process-info linked list).
     * The second round:
     *    - Read current s_time, u_time, mm, etc. and calculate
     *         cpu and memory usage;
     *    - Finalize process-info struct;
     */

    /* The first round */
    /* walk the task list and create  */
    proc_info *process_info_list_head = NULL, *previous_process_ptr = NULL, *current_process_ptr = NULL;
    int is_head = 1;
    time_t calculation_start_time, calculation_end_time;

    vmi_read_64_va(vmi, vmi_translate_ksym2v(vmi, "jiffies"), 0, &calculation_start_time);
    do {
        current_process_ptr = (proc_info*)malloc(sizeof(proc_info));
        current_process_addr = next_list_entry - img_offsets->tasks_offset;

        /* NOTE: _EPROCESS.UniqueProcessId is a really VOID*, but is never > 32 bits,
         * so this is safe enough for x64 Windows for example purposes */
        vmi_read_32_va(vmi, current_process_addr + img_offsets->pid_offset, 0, (uint32_t*)&(current_process_ptr->pid));
        current_process_ptr->name = vmi_read_str_va(vmi, current_process_addr + img_offsets->name_offset, 0);
        vmi_read_64_va(vmi, current_process_addr + img_offsets->utime_offset, 0, &(current_process_ptr->r_utime));
        vmi_read_64_va(vmi, current_process_addr + img_offsets->stime_offset, 0, &(current_process_ptr->r_stime));
        
        /* current_process_ptr->name == NULL implies reading process info is not successful */
        if (!current_process_ptr->name) {
            printf("Failed to find process name\n");
            resume_vm(&vmi);
            if(!image_offsets_provided)
                free(img_offsets);
            return NULL;
        }

        /* follow the next pointer and load the entry of next process*/
        status = vmi_read_addr_va(vmi, next_list_entry, 0, &next_list_entry);
        if (status == VMI_FAILURE) {
            printf("Failed to read next pointer in loop at %"PRIx64"\n", next_list_entry);
            resume_vm(&vmi);
            if(!image_offsets_provided)
                free(img_offsets);
            return NULL;
        }
        if(is_head){
            is_head = 0;
            process_info_list_head = current_process_ptr;
            previous_process_ptr = current_process_ptr;
        }else{
            previous_process_ptr->next = current_process_ptr;
            previous_process_ptr = current_process_ptr;
        }
    } while(next_list_entry != list_head);
    current_process_ptr->next = NULL;
    vmi_resume_vm(vmi);
    sleep(3);

    /* The second round */
    uint64_t total_memory_size = vmi_get_memsize(vmi) / 1024;                           // total_memory_size unit: KB
    int dont_read_next_process = 0;
    vmi_pause_vm(vmi);
    is_head = 1;
    int old_list_has_ended = 0;
    proc_info* old_list_ptr = process_info_list_head;
    current_process_ptr = process_info_list_head;
    previous_process_ptr = process_info_list_head;
    next_list_entry = list_head;

    vmi_pid_t proc_pid;
    uint64_t new_utime, new_stime, sum_process_time_before, sum_process_time_after;
    /* walk the task list */

    vmi_read_64_va(vmi, vmi_translate_ksym2v(vmi, "jiffies"), 0, &calculation_end_time);
    do {
        
        if (old_list_ptr == NULL)
        {
            old_list_has_ended = 1;
        }
        current_process_addr = next_list_entry - img_offsets->tasks_offset;

        /* NOTE: _EPROCESS.UniqueProcessId is a really VOID*, but is never > 32 bits,
         * so this is safe enough for x64 Windows for example purposes */
        vmi_read_32_va(vmi, current_process_addr + img_offsets->pid_offset, 0, (uint32_t*)&proc_pid);
        
        if(old_list_has_ended || proc_pid < old_list_ptr->pid)
        {
            /* new process was created between sleep time
             * and pid is smaller than current process pid
             */
            proc_info *new_process_ptr = (proc_info*)malloc(sizeof(proc_info));
            new_process_ptr->name = vmi_read_str_va(vmi, current_process_addr + img_offsets->name_offset, 0);
            new_process_ptr->type = P_NEW_PROCESS;
            vmi_read_32_va(vmi, current_process_addr + img_offsets->pid_offset, 0, (uint32_t*)&(new_process_ptr->pid));
            
            /* pointer related operations */
            if(is_head)
            {
                process_info_list_head = new_process_ptr;
                current_process_ptr = new_process_ptr;
                previous_process_ptr = new_process_ptr;
                is_head = 0;
            }
            else
            {
                current_process_ptr = new_process_ptr;
                previous_process_ptr->next = current_process_ptr;
                previous_process_ptr = current_process_ptr;
            }
        }
        else if (proc_pid > old_list_ptr->pid)
        {
            /* previous process has ended between sleep time */
            old_list_ptr->type = P_ENDED_PROCESS;
            dont_read_next_process = 1;

            if(is_head)
            {
                is_head = 0;
                old_list_ptr = old_list_ptr->next;
                continue;
            }

            current_process_ptr = old_list_ptr;
            previous_process_ptr->next = current_process_ptr;
            previous_process_ptr = current_process_ptr;
            old_list_ptr = old_list_ptr->next;
        }
        else
        {
            /* the process still exists. cpu% and mem% can be calculated*/
            current_process_ptr = old_list_ptr;
            current_process_ptr->type = P_EXIST_PROCESS;

            /* get priority and state */
            vmi_read_64_va(vmi, current_process_addr + img_offsets->state_offset, 0, (uint64_t*)&(current_process_ptr->state));
            vmi_read_32_va(vmi, current_process_addr + img_offsets->rt_priority_offset, 0, (uint32_t*)&(current_process_ptr->priority));

            /* read process cpu time */
            vmi_read_64_va(vmi, current_process_addr + img_offsets->utime_offset, 0, &new_utime);
            vmi_read_64_va(vmi, current_process_addr + img_offsets->stime_offset, 0, &new_stime);

            /* calculate cpu usage */
            sum_process_time_after = new_utime + new_stime;
            sum_process_time_before = current_process_ptr->r_stime + current_process_ptr->r_utime;
            current_process_ptr->cpu_percent = (double)(sum_process_time_after - sum_process_time_before) / (calculation_end_time - calculation_start_time) * 100.0;

            /* get total vm pages for calculating virtual memory usage */
            addr_t mm_addr = NULL;
            uint32_t total_vm_pages = 0;
            vmi_read_addr_va(vmi, current_process_addr + img_offsets->mm_offset, 0, &mm_addr);
            vmi_read_32_va(vmi, mm_addr + img_offsets->total_vm_offset,0, &total_vm_pages);
            current_process_ptr->virtual_memory_usage = total_vm_pages * PAGE_SIZE_KB;

            /* get rss count for calculating physical memory usage*/
            int i = 0;
            uint64_t rss_count = 0, temp = 0;
            for(i = 0; i < NR_MM_COUNTERS; i++)
            {
                vmi_read_64_va(vmi, mm_addr + img_offsets->rss_stat_offset + i * img_offsets->element_offset, 0, (uint64_t*)&temp);
                rss_count += temp;
            }
            current_process_ptr->physical_memory_usage = rss_count * PAGE_SIZE_KB;
            
            /* calculate memory usage (percent) */
            current_process_ptr->memory_percent = (double)rss_count * PAGE_SIZE_KB / total_memory_size * 100.0;
            
            
            /* deal with pointer */
            if(is_head)
                is_head = 0;
            else
            {    
                previous_process_ptr->next = current_process_ptr;
                previous_process_ptr = current_process_ptr;
            }
            old_list_ptr = old_list_ptr->next;
        }

        if(!dont_read_next_process)
        {
            /* follow the next pointer and load the entry of next process*/
            status = vmi_read_addr_va(vmi, next_list_entry, 0, &next_list_entry);
            if (status == VMI_FAILURE) 
            {
                printf("Failed to read next pointer in loop at %"PRIx64"\n", next_list_entry);
                resume_vm(&vmi);
                free(img_offsets);
                return NULL;
            }
        }
        else
            dont_read_next_process = 0;

    } while(next_list_entry != list_head);
    if(!old_list_has_ended)
        current_process_ptr->next = old_list_ptr;
    else if(current_process_ptr != NULL)
        current_process_ptr->next = NULL;

    if(!image_offsets_provided)
        free(img_offsets);
    vmi_resume_vm(vmi);
    vmi_destroy(vmi);

    //current_process_ptr = process_info_list_head;
    //while(current_process_ptr != NULL)
    //{
    //current_process_ptr = process_info_list_head;
    //while(current_process_ptr != NULL)
    //{
    //    printf("%d | %s | %04.2lf \n", current_process_ptr->pid, current_process_ptr->name, current_process_ptr->cpu_percent);
    //    current_process_ptr = current_process_ptr->next;
    //}

    return process_info_list_head;
}

extern void free_process_info_list(proc_info *head)
{
    proc_info *prev;
    while(head != NULL)
    {
        free(head->name);
        prev = head;
        head = head->next;
        free(prev);
    }
}

void resume_vm(vmi_instance_t *vmi)
{
    /* resume the vm */
    /* cleanup any memory associated with the LibVMI instance */
    vmi_resume_vm(*vmi);
    vmi_destroy(*vmi);
}

status_t get_vm_offsets(vmi_instance_t vmi, image_offset *offset_struct)
{

    /* TODO: (pwwp)
     * Get offset through config file
     * may use: libconfig
     * Below is just a linux example
     */
    offset_struct->state_offset = 0x0;
    offset_struct->rt_priority_offset = 0x5c;
    offset_struct->total_vm_offset=0xa8;
    offset_struct->rss_stat_offset = 0x2a8;
    offset_struct->element_offset = 0x8;
    offset_struct->utime_offset = 0x388;
    offset_struct->stime_offset = 0x410;

    /* init the offset values */
    if (VMI_OS_LINUX == vmi_get_ostype(vmi))
    {
        offset_struct->tasks_offset = vmi_get_offset(vmi, "linux_tasks");
        offset_struct->name_offset = vmi_get_offset(vmi, "linux_name");
        offset_struct->pid_offset = vmi_get_offset(vmi, "linux_pid");
        offset_struct->mm_offset = vmi_get_offset(vmi,"linux_mm");
    }
    else if (VMI_OS_WINDOWS == vmi_get_ostype(vmi))
    {
        offset_struct->tasks_offset = vmi_get_offset(vmi, "win_tasks");
        offset_struct->name_offset = vmi_get_offset(vmi, "win_pname");
        offset_struct->pid_offset = vmi_get_offset(vmi, "win_pid");
    }

    // An error happens when any of the offset is 0.
    // When that happens, return S_ERROR
    if (!(offset_struct->tasks_offset && offset_struct->pid_offset && offset_struct->name_offset))
        return VMI_FAILURE;
    else
        return VMI_SUCCESS;
}
