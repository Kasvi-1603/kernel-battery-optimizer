#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>
#include <linux/sched/signal.h>
#include <linux/uaccess.h>
#include <linux/sched.h>

static void apply_power_save_policy(void);

#define PROC_STATS   "ai_battery_stats"
#define PROC_CONTROL "ai_battery_control"

static char power_mode[16] = "BALANCED";

MODULE_LICENSE("GPL");
MODULE_AUTHOR("RVCE Team");
MODULE_DESCRIPTION("AI Driven Battery Saver Kernel Module");
MODULE_VERSION("1.0");

/* -------- STATS (/proc/ai_battery_stats) -------- */

static int stats_show(struct seq_file *m, void *v)
{
    struct task_struct *task;
    int process_count = 0;

    for_each_process(task) {
        process_count++;
    }

    seq_printf(m, "AI Battery Saver Kernel Module\n");
    seq_printf(m, "--------------------------------\n");
    seq_printf(m, "Number of running processes: %d\n", process_count);
    seq_printf(m, "CPU cores available: %u\n", num_online_cpus());
    seq_printf(m, "Current PID: %d\n", current->pid);
    seq_printf(m, "Power mode: %s\n", power_mode);

    return 0;
}

static int stats_open(struct inode *inode, struct file *file)
{
    return single_open(file, stats_show, NULL);
}

static const struct proc_ops stats_ops = {
    .proc_open    = stats_open,
    .proc_read    = seq_read,
    .proc_lseek   = seq_lseek,
    .proc_release = single_release,
};

/* -------- CONTROL (/proc/ai_battery_control) -------- */

static ssize_t control_write(struct file *file,
                             const char __user *buffer,
                             size_t count,
                             loff_t *pos)
{
    if (count > sizeof(power_mode) - 1)
        count = sizeof(power_mode) - 1;

    if (copy_from_user(power_mode, buffer, count))
        return -EFAULT;

    power_mode[count] = '\0';

    printk(KERN_INFO "AI Battery Mode set to: %s\n", power_mode);

    if (strncmp(power_mode, "POWER_SAVE", 10) == 0) {
       apply_power_save_policy();
    }

    return count;
}

static const struct proc_ops control_ops = {
    .proc_write = control_write,
};

static void apply_power_save_policy(void)
{
    struct task_struct *task;

    for_each_process(task) {

        /* Skip kernel threads */
        if (task->mm == NULL)
            continue;

        /* Skip very important processes */
        if (task->prio < 120)
            continue;

        /* Lower priority of background processes */
        set_user_nice(task, 10);
    }

    printk(KERN_INFO "AI Battery: Applied POWER_SAVE niceness policy\n");
}


/* -------- MODULE INIT / EXIT -------- */

static int __init ai_battery_init(void)
{
    if (!proc_create(PROC_STATS, 0444, NULL, &stats_ops))
        return -ENOMEM;

    if (!proc_create(PROC_CONTROL, 0222, NULL, &control_ops)) {
        remove_proc_entry(PROC_STATS, NULL);
        return -ENOMEM;
    }

    printk(KERN_INFO "AI Battery Saver module loaded\n");
    return 0;
}

static void __exit ai_battery_exit(void)
{
    remove_proc_entry(PROC_STATS, NULL);
    remove_proc_entry(PROC_CONTROL, NULL);
    printk(KERN_INFO "AI Battery Saver module unloaded\n");
}

module_init(ai_battery_init);
module_exit(ai_battery_exit);

