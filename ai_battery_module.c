#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>
#include <linux/sched/signal.h>
#include <linux/uaccess.h>
#include <linux/sched.h>

static void apply_power_policy(int nice_value);

#define PROC_STATS   "ai_battery_stats"
#define PROC_CONTROL "ai_battery_control"

static char power_mode[16] = "BALANCED";
static int current_nice = 0;

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
    seq_printf(m, "Current nice value: %d\n", current_nice);

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
    char buf[16];
    int nice_value = 0;
    
    if (count > sizeof(buf) - 1)
        count = sizeof(buf) - 1;

    if (copy_from_user(buf, buffer, count))
        return -EFAULT;

    buf[count] = '\0';

    /* Parse mode string: "BALANCED", "MODERATE", "POWER_SAVE", "CRITICAL" */
    if (strncmp(buf, "BALANCED", 8) == 0) {
        nice_value = 0;
        strncpy(power_mode, "BALANCED", sizeof(power_mode));
    } else if (strncmp(buf, "MODERATE", 8) == 0) {
        nice_value = 5;
        strncpy(power_mode, "MODERATE", sizeof(power_mode));
    } else if (strncmp(buf, "POWER_SAVE", 10) == 0) {
        nice_value = 10;
        strncpy(power_mode, "POWER_SAVE", sizeof(power_mode));
    } else if (strncmp(buf, "CRITICAL", 8) == 0) {
        nice_value = 15;
        strncpy(power_mode, "CRITICAL", sizeof(power_mode));
    }

    current_nice = nice_value;
    printk(KERN_INFO "AI Battery Mode: %s (nice=%d)\n", power_mode, nice_value);
    
    /* Apply the policy with the calculated nice value */
    apply_power_policy(nice_value);

    return count;
}

static const struct proc_ops control_ops = {
    .proc_write = control_write,
};

static void apply_power_policy(int nice_value)
{
    struct task_struct *task;

    for_each_process(task) {

        /* Skip kernel threads */
        if (task->mm == NULL)
            continue;

        /* Skip very important processes */
        if (task->prio < 120)
            continue;

        /* Apply the nice value to background processes */
        set_user_nice(task, nice_value);
    }

    printk(KERN_INFO "AI Battery: Applied nice=%d to user processes\n", nice_value);
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




