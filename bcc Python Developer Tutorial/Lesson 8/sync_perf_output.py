from __future__ import print_function
from bcc import BPF

# load BPF program
b = BPF(text="""
#include <uapi/linux/ptrace.h>

// define output data structure in C
struct data_t {
    u64 ms;
    u64 ts;
};

BPF_PERF_OUTPUT(events);
BPF_HASH(last);

int do_trace(struct pt_regs *ctx) {
    struct data_t data = {};

    u64 ts, *tsp, delta, key = 0;

    // update stored timestamp
    ts = bpf_ktime_get_ns();

    tsp = last.lookup(&key);
    if (tsp != NULL) {
        delta = bpf_ktime_get_ns() - *tsp;    
    } else {
        delta = 0;
    }
    
    last.update(&key, &ts);

    data.ts = ts;
    data.ms = delta;
    events.perf_submit(ctx, &data, sizeof(data));

    return 0;
}
""")

b.attach_kprobe(event=b.get_syscall_fnname("sync"), fn_name="do_trace")
print("Tracing for quick sync's... Ctrl-C to end")

# format output
start = 0
def print_event(cpu, data, size):
    global start
    event = b["events"].event(data)
    if start == 0:
        start = event.ts # 计算启动的相对时间
    ts = (event.ts - start) / 1000000000.0  # Convert to seconds
    ms = event.ms / 1000000
    print("Hello BPF_PERF_OUTPUT At time %.2f s: multiple syncs detected, last %.2f ms ago" % (ts, ms))

# loop with callback to print_event
b["events"].open_perf_buffer(print_event)
while 1:
    b.perf_buffer_poll()