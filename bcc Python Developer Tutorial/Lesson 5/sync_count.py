from __future__ import print_function
from bcc import BPF
from ctypes import c_int

# load BPF program
b = BPF(text="""
#include <uapi/linux/ptrace.h>

BPF_HASH(last);
BPF_HASH(counts, u64);

int do_trace(struct pt_regs *ctx) {
    u64 ts, *tsp, delta, key = 0;
    u64 zero = 0;
    u64 *count;

    // attempt to read stored timestamp
    tsp = last.lookup(&key);
    if (tsp != NULL) {
        delta = bpf_ktime_get_ns() - *tsp;
        if (delta < 1000000000) {
            // output if time is less than 1 second
            bpf_trace_printk("%d\\n", delta / 1000000);
        }
        last.delete(&key);
    }

    // update stored timestamp
    ts = bpf_ktime_get_ns();
    last.update(&key, &ts);

    // increment sync system call count
    count = counts.lookup_or_init(&zero, &zero);
    (*count)++;

    return 0;
}
""")

b.attach_kprobe(event=b.get_syscall_fnname("sync"), fn_name="do_trace")
print("Tracing for quick sync's... Ctrl-C to end")

# format output
start = 0
while 1:
    try:
        (task, pid, cpu, flags, ts, ms) = b.trace_fields()
        if start == 0:
            start = ts
        ts = ts - start
        sync_count = b["counts"][c_int(0)].value
        print("At time %.2f s: multiple syncs detected, last %s ms ago, total sync call count %d" % (ts, ms.decode(), sync_count))
    except KeyboardInterrupt:
        exit()