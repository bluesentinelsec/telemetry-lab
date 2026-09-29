/* Harness-only authoritative UDP responder. Only two fixed fixture names;
   never forwards queries and never contacts an external service. */
#include "common.h"
int main(void) {
    socket_start();
    SOCKET s=socket(AF_INET,SOCK_DGRAM,IPPROTO_UDP); CHECK(s!=INVALID_SOCKET);
    BOOL exclusive=TRUE;
    CHECK(setsockopt(s,SOL_SOCKET,SO_EXCLUSIVEADDRUSE,(const char*)&exclusive,sizeof exclusive)==0);
    struct sockaddr_in local; memset(&local,0,sizeof local);
    local.sin_family=AF_INET;local.sin_port=htons(53);local.sin_addr.s_addr=htonl(INADDR_LOOPBACK);
    CHECK(bind(s,(struct sockaddr*)&local,sizeof local)==0);
    puts("DNS_READY 127.0.0.1:53");fflush(stdout);
    for (;;) {
        unsigned char packet[512];struct sockaddr_in peer;int peer_size=sizeof peer;
        int n=recvfrom(s,(char*)packet,sizeof packet,0,(struct sockaddr*)&peer,&peer_size);
        CHECK(n>=0);
        if(n<17 || packet[2]&0x80 || packet[4]!=0 || packet[5]!=1) continue;
        char name[254];size_t used=0;int pos=12,valid=1;
        while(pos<n && packet[pos]) {
            unsigned int len=packet[pos++];
            if(len>63 || pos+(int)len>=n || used+len+1>=sizeof name){valid=0;break;}
            if(used) name[used++]='.';
            memcpy(name+used,packet+pos,len);used+=len;pos+=(int)len;
        }
        if(!valid || pos>=n || pos+5>n) continue;
        name[used]=0;pos++;
        unsigned int type=((unsigned int)packet[pos]<<8)|packet[pos+1];
        unsigned int cls=((unsigned int)packet[pos+2]<<8)|packet[pos+3];pos+=4;
        int allowed=!_stricmp(name,"api.ipify.org");
        int answer=allowed && type==1 && cls==1;
        packet[2]=0x85;packet[3]=(unsigned char)(allowed?0:3);
        memset(packet+6,0,6);packet[7]=(unsigned char)answer;
        if(answer) {
            const unsigned char rr[]={0xc0,0x0c,0,1,0,1,0,0,0,0,0,4,127,0,0,42};
            if(pos+(int)sizeof rr>(int)sizeof packet) continue;
            memcpy(packet+pos,rr,sizeof rr);pos+=(int)sizeof rr;
        }
        CHECK(sendto(s,(const char*)packet,pos,0,(struct sockaddr*)&peer,peer_size)==pos);
        printf("DNS_QUERY %s type=%u answer=%s\n",name,type,answer?"127.0.0.42":"none");fflush(stdout);
    }
}
