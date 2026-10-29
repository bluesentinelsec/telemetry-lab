// Target rule: File Creation Date Changed to Another Year
// Sigma rule ID: 1117f7b2-3f59-682b-ad07-081d44ae5ddb
// Ruleset path: sigma/sysmon/threat-hunting/file/file_change/file_change_win_date_changed_to_another_year.yml
#include "../internal/common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE creation_time_change");
    if (!fixture_begin(argc,argv,"creation_time_change")) return 0;
    HANDLE file=CreateFileA(ROOT "\\work\\timestamp.txt",FILE_READ_ATTRIBUTES|FILE_WRITE_ATTRIBUTES,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
    CHECK(file!=INVALID_HANDLE_VALUE);
    SYSTEMTIME st; memset(&st,0,sizeof st); st.wYear=2019; st.wMonth=1; st.wDay=1;
    FILETIME desired,observed; CHECK(SystemTimeToFileTime(&st,&desired));
    CHECK(SetFileTime(file,&desired,NULL,NULL)); CHECK(GetFileTime(file,&observed,NULL,NULL));
    CHECK(CompareFileTime(&desired,&observed)==0); CHECK(CloseHandle(file));
    success("creation_time_change");
    return 0;
}
