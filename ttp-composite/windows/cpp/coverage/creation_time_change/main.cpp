#include "../common.hpp"

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE creation_time_change" << "\n";
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
