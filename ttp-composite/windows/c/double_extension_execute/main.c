// Target rule: Suspicious Double Extension File Execution
// Sigma rule ID: b6ce0b2f-593b-5e1c-e137-d30b2974e30e
// Ruleset path: sigma/sysmon/process_creation/proc_creation_win_susp_double_extension.yml
#include "../internal/common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE double_extension_execute");
    if (!fixture_begin(argc,argv,"double_extension_execute")) return 0;
    STARTUPINFOA si; PROCESS_INFORMATION pi; memset(&si,0,sizeof si); memset(&pi,0,sizeof pi); si.cb=sizeof si;
    char command[]="\"C:\\lab\\windows-coverage\\work\\report.pdf.exe\"";
    CHECK(CreateProcessA(ROOT "\\work\\report.pdf.exe",command,NULL,NULL,FALSE,0,NULL,NULL,&si,&pi));
    CHECK(WaitForSingleObject(pi.hProcess,5000)==WAIT_OBJECT_0); DWORD code=0;
    CHECK(GetExitCodeProcess(pi.hProcess,&code) && code==42);
    CHECK(CloseHandle(pi.hThread)); CHECK(CloseHandle(pi.hProcess));
    success("double_extension_execute");
    return 0;
}
