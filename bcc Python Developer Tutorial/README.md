## 安装 bcc

```bash
sudo apt update

# For Focal (20.04.1 LTS)
sudo apt install -y zip bison build-essential cmake flex git libedit-dev \
  libllvm12 llvm-12-dev libclang-12-dev python zlib1g-dev libelf-dev libfl-dev python3-setuptools \
  liblzma-dev arping netperf iperf

git clone https://github.com/iovisor/bcc.git
mkdir bcc/build; cd bcc/build
cmake ..
make
sudo make install
cmake -DPYTHON_CMD=python3 .. # build python3 binding
pushd src/python/
make
sudo make install
popd
```


## 参考资料

- [bcc Python Developer Tutorial](https://github.com/iovisor/bcc/blob/master/docs/tutorial_bcc_python_developer.md)
- [【BPF入门系列-8】文件打开记录跟踪之 perf_event 篇](https://www.ebpf.top/post/ebpf_trace_file_open_perf_output/)
- [ebpf & bcc 中文教程及手册](https://blog.cyru1s.com/posts/ebpf-bcc.html)