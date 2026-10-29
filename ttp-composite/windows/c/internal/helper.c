#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <wchar.h>
#include <stdio.h>
int main(void) {
    const wchar_t *p=GetCommandLineW();
    if(*p==L'"') {p++;while(*p && *p!=L'"')p++;if(*p)p++;}
    else {while(*p && *p!=L' ')p++;}
    while(*p==L' ')p++;
    if(*p) {
        if(wcscmp(p,L"marker\u00a0value")) return 1;
        puts("UNICODE_ARG_OK 006d 0061 0072 006b 0065 0072 00a0 0076 0061 006c 0075 0065");
        return 43;
    }
    puts("FIXTURE_HELPER_OK");return 42;
}
