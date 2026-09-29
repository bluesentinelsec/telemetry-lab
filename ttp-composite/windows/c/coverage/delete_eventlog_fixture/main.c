#include "../common.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE delete_eventlog_fixture");
    if(!fixture_begin(argc,argv,"delete_eventlog_fixture")) return 0;
    CHECK(remove("C:\\Windows\\System32\\winevt\\Logs\\TelemetryLabFixture.evtx")==0); DWORD attr=GetFileAttributesA("C:\\Windows\\System32\\winevt\\Logs\\TelemetryLabFixture.evtx"); CHECK(attr==INVALID_FILE_ATTRIBUTES && GetLastError()==ERROR_FILE_NOT_FOUND);
    success("delete_eventlog_fixture"); return 0;
}
