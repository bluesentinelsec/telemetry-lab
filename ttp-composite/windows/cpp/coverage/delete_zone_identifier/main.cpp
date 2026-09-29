#include "../common.hpp"
#include "../expansion_helpers.hpp"

int main(int argc,char **argv) {
    std::cout << "COMPOSITE_CASE delete_zone_identifier" << "\n";
    if(!fixture_begin(argc,argv,"delete_zone_identifier")) return 0;
    const char *stream="C:\\lab\\windows-coverage\\work\\download.txt:Zone.Identifier";
    FILE *before=fopen(stream,"rb"); CHECK(before!=NULL);
    CHECK(fgetc(before)=='['); CHECK(fclose(before)==0);
    CHECK(remove(stream)==0);
    // Attribute APIs describe the carrier file, not existence of its stream.
    errno=0; FILE *after=fopen(stream,"rb"); CHECK(after==NULL && errno==ENOENT);
    CHECK(GetFileAttributesA("C:\\lab\\windows-coverage\\work\\download.txt")!=INVALID_FILE_ATTRIBUTES);
    success("delete_zone_identifier"); return 0;
}
