#include "../common.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE delete_history_fixture");
    if(!fixture_begin(argc,argv,"delete_history_fixture")) return 0;
    CHECK(remove("C:\\lab\\windows-coverage\\work\\PSReadLine\\ConsoleHost_history.txt")==0); DWORD attr=GetFileAttributesA("C:\\lab\\windows-coverage\\work\\PSReadLine\\ConsoleHost_history.txt"); CHECK(attr==INVALID_FILE_ATTRIBUTES && GetLastError()==ERROR_FILE_NOT_FOUND);
    success("delete_history_fixture"); return 0;
}
