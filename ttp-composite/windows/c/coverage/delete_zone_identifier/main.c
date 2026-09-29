#include "../common.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE delete_zone_identifier");
    if(!fixture_begin(argc,argv,"delete_zone_identifier")) return 0;
    const char *stream="C:\\lab\\windows-coverage\\work\\download.txt:Zone.Identifier";
    FILE *before=fopen(stream,"rb"); CHECK(before!=NULL);
    CHECK(fgetc(before)=='['); CHECK(fclose(before)==0);
    CHECK(remove(stream)==0);
    // Attribute APIs describe the carrier file, not existence of its stream.
    // Deletion completion can lag the successful request. Probe without issuing
    // another deletion; close every successful probe so it cannot retain the stream.
    const ULONGLONG started=GetTickCount64(); unsigned probes=0;
    for (;;) {
        errno=0; FILE *after=fopen(stream,"rb"); int error=errno; ++probes;
        if(after) { CHECK(fclose(after)==0); }
        else if(error==ENOENT) break;
        else CHECK(error==EACCES);
        CHECK(GetTickCount64()-started<5000); Sleep(10);
    }
    printf("STREAM_ABSENT probes=%u elapsed_ms=%llu\n",probes,
           (unsigned long long)(GetTickCount64()-started));
    CHECK(GetFileAttributesA("C:\\lab\\windows-coverage\\work\\download.txt")!=INVALID_FILE_ATTRIBUTES);
    success("delete_zone_identifier"); return 0;
}
