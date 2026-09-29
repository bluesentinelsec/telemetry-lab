#include "../common.hpp"
#include "../expansion_helpers.hpp"

int main(int argc,char **argv) {
    std::cout << "COMPOSITE_CASE delete_eventlog_fixture" << "\n";
    if(!fixture_begin(argc,argv,"delete_eventlog_fixture")) return 0;
    CHECK(remove("C:\\Windows\\System32\\winevt\\Logs\\TelemetryLabFixture.evtx")==0); DWORD attr=GetFileAttributesA("C:\\Windows\\System32\\winevt\\Logs\\TelemetryLabFixture.evtx"); CHECK(attr==INVALID_FILE_ATTRIBUTES && GetLastError()==ERROR_FILE_NOT_FOUND);
    success("delete_eventlog_fixture"); return 0;
}
