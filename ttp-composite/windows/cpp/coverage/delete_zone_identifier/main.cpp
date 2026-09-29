#include "../common.hpp"
#include "../expansion_helpers.hpp"

int main(int argc,char **argv) {
    std::cout << "COMPOSITE_CASE delete_zone_identifier" << "\n";
    if(!fixture_begin(argc,argv,"delete_zone_identifier")) return 0;
    CHECK(remove("C:\\lab\\windows-coverage\\work\\download.txt:Zone.Identifier")==0); DWORD attr=GetFileAttributesA("C:\\lab\\windows-coverage\\work\\download.txt:Zone.Identifier"); CHECK(attr==INVALID_FILE_ATTRIBUTES && GetLastError()==ERROR_FILE_NOT_FOUND);
    success("delete_zone_identifier"); return 0;
}
