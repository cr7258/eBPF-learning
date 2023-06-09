from bcc import BPF

bpf_text = '''
int kprobe__sys_clone(void *ctx) {
    bpf_trace_printk("Hello, World!\\n");
    return 0;
}
'''

print("Tracing sys_sync()... Ctrl-C to end.")

BPF(text=bpf_text).trace_print()