#include "../common.hpp"
#include "../utility.h"
int main(int argc,char **argv) {
if (!fixture_begin(argc,argv,"hidden_file")) return 0;
std::ofstream f("/tmp/lab/.hidden-fixture"); CHECK(f.is_open()); f << fixture_payload; f.close(); CHECK(!f.fail()); verify_bytes("/tmp/lab/.hidden-fixture",fixture_payload,sizeof(fixture_payload)-1);
std::cout << "CASE_OK hidden_file\n";
}
