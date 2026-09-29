#include "../common.hpp"
#include <linux/bpf.h>

int main(int argc,char **argv) {
    if (!fixture_begin(argc,argv,"bpf_program_load")) return 0;
    struct bpf_insn insns[2]; memset(insns,0,sizeof insns); insns[0].code=BPF_ALU64|BPF_MOV|BPF_K; insns[1].code=BPF_JMP|BPF_EXIT;
    union bpf_attr attr; memset(&attr,0,sizeof attr); attr.prog_type=BPF_PROG_TYPE_SOCKET_FILTER; attr.insn_cnt=2;
    attr.insns=(unsigned long)insns; attr.license=(unsigned long)"GPL";
    int fd=(int)syscall(SYS_bpf,BPF_PROG_LOAD,&attr,sizeof attr); CHECK(fd>=0); CHECK(close(fd)==0);
    std::cout << "CASE_OK bpf_program_load\n";
    return 0;
}
