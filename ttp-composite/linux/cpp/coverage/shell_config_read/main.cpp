#include "../common.hpp"
#include "../utility.h"
int main(int argc,char **argv) {
if (!fixture_begin(argc,argv,"shell_config_read")) return 0;
std::ifstream f("/root/.bashrc"); CHECK(f.is_open()); std::string s((std::istreambuf_iterator<char>(f)),{}); CHECK(s==fixture_payload);
std::cout << "CASE_OK shell_config_read\n";
}
