// Target rule: Hidden Executable In NTFS Alternate Data Stream
// Sigma rule ID: e5cca2eb-74d0-c45b-ec14-3c09f568f8c0
// Ruleset path: sigma/sysmon/create_stream_hash/create_stream_hash_ads_executable.yml
#include "../internal/common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE ads_executable");
    if (!fixture_begin(argc,argv,"ads_executable")) return 0;
    copy_verified(ROOT "\\fixtures\\helper.exe","C:\\lab\\windows-coverage\\work\\carrier.txt:fixture.exe");
    success("ads_executable");
    return 0;
}
