#include "../common.hpp"
#include <wchar.h>

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE ads_provenance_contents" << "\n";
    if (!fixture_begin(argc,argv,"ads_provenance_contents")) return 0;
    const char data[]="[ZoneTransfer]\r\nZoneId=3\r\nHostUrl=http://192.0.2.1/fixture.exe\r\n";
    const char *path=ROOT "\\work\\provenance.exe:Zone.Identifier";
    std::ofstream out(path,std::ios::binary|std::ios::trunc); CHECK(out.is_open());
    out.write(data,sizeof data-1); out.flush(); CHECK(out.good());
    out.close(); CHECK(!out.fail());
    std::ifstream in(path,std::ios::binary); CHECK(in.is_open());
    std::array<char,sizeof data> actual{};
    in.read(actual.data(),actual.size());
    CHECK(!in.bad() && in.eof() && in.gcount()==sizeof data-1);
    CHECK(!std::memcmp(actual.data(),data,sizeof data-1));
    in.clear(); in.close(); CHECK(!in.fail());
    success("ads_provenance_contents");
    return 0;
}
