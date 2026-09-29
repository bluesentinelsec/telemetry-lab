#include "../common.h"
#include <stdint.h>

int main(int argc,char **argv) {
    if (!fixture_begin(argc,argv,"bpf_program_load")) return 0;
    /* Frozen x86-64 bpf_attr ABI; avoids glibc-only Linux header dependencies. */
    const unsigned char insns[16]={0xb7,0,0,0,0,0,0,0,0x95,0,0,0,0,0,0,0};
    uint64_t attr[18]={0}; attr[0]=1ULL|(2ULL<<32);attr[1]=(uintptr_t)insns;attr[2]=(uintptr_t)"GPL";
    int fd=(int)syscall(SYS_bpf,5,attr,sizeof attr);CHECK(fd>=0);CHECK(close(fd)==0);
    printf("CASE_OK bpf_program_load\n");
    return 0;
}
