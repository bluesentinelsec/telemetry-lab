// Target rule: EventLog EVTX File Deleted
// Sigma rule ID: 956a26a6-af21-94d6-9fb7-0abbe37e3c7d
// Ruleset path: sigma/sysmon/file/file_delete/file_delete_win_delete_event_log_files.yml
#include "../internal/common.hpp"
#include "../internal/expansion_helpers.hpp"

int main(int argc,char **argv) {
    std::cout << "COMPOSITE_CASE delete_eventlog_fixture" << "\n";
    if(!fixture_begin(argc,argv,"delete_eventlog_fixture")) return 0;
    CHECK(remove("C:\\Windows\\System32\\winevt\\Logs\\TelemetryLabFixture.evtx")==0); DWORD attr=GetFileAttributesA("C:\\Windows\\System32\\winevt\\Logs\\TelemetryLabFixture.evtx"); CHECK(attr==INVALID_FILE_ATTRIBUTES && GetLastError()==ERROR_FILE_NOT_FOUND);
    success("delete_eventlog_fixture"); return 0;
}
