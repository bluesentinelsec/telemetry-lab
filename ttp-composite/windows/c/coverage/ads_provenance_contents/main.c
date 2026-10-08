#include "../common.h"
#include <wchar.h>

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE ads_provenance_contents");
    if (!fixture_begin(argc,argv,"ads_provenance_contents")) return 0;
    const char data[]="[ZoneTransfer]\r\nZoneId=3\r\nHostUrl=http://192.0.2.1/fixture.exe\r\n";
    const char *path=ROOT "\\work\\provenance.exe:Zone.Identifier";
    FILE *f=fopen(path,"wb"); CHECK(f); CHECK(fwrite(data,1,sizeof data-1,f)==sizeof data-1); CHECK(fclose(f)==0);
    char actual[sizeof data]; f=fopen(path,"rb"); CHECK(f);
    CHECK(fread(actual,1,sizeof actual,f)==sizeof data-1); CHECK(!ferror(f)); CHECK(fclose(f)==0);
    CHECK(!memcmp(actual,data,sizeof data-1));
    success("ads_provenance_contents");
    return 0;
}
