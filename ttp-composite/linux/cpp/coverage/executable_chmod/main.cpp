#include "../common.hpp"
#include "../utility.h"
int main(int argc,char **argv) {
if (!fixture_begin(argc,argv,"executable_chmod")) return 0;
fs::permissions("/tmp/lab/executable-mode",fs::perms::owner_all,fs::perm_options::replace); CHECK((fs::status("/tmp/lab/executable-mode").permissions() & fs::perms::mask)==fs::perms::owner_all);
std::cout << "CASE_OK executable_chmod\n";
}
